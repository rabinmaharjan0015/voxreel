"""Runs in the RQ worker: uploads a finished video to a platform."""
from . import config, store
from .config import OUTPUT_DIR
from .publish import ayrshare, tiktok, youtube
from .publish.net import PublishError

PLATFORMS = {"youtube": youtube, "tiktok": tiktok}


def _fresh_tokens(cid: str, platform: str):
    tok = store.get_oauth(cid, platform)
    if not tok:
        raise PublishError(f"Connect your {platform.title()} account first (Accounts page).")
    tok, changed = PLATFORMS[platform].fresh(tok)
    if changed:
        store.save_oauth(cid, platform, tok)
    return tok


def run_publish(pid: str, cid: str, jid: str, target: str, opts: dict):
    keys = store.take_keys(pid)
    try:
        store.update_pub(pid, status="running")
        job = store.get(jid)
        path = OUTPUT_DIR / jid / "final.mp4"
        if not job or not path.exists():
            raise PublishError("Video file not found.")
        vertical = job["video_type"] == "shorts"
        title = (opts.get("title") or job.get("title") or job["topic"])
        desc = opts.get("description", "")
        tags = opts.get("tags", [])
        if target == "youtube":
            tok = _fresh_tokens(cid, "youtube")
            res = youtube.upload(tok["access_token"], path, title=title, description=desc, tags=tags,
                                 privacy=opts.get("privacy", "private"), vertical=vertical)
        elif target == "tiktok":
            tok = _fresh_tokens(cid, "tiktok")
            caption = (title + " " + " ".join("#" + t.lstrip("#") for t in tags)).strip()
            res = tiktok.post(tok["access_token"], path, caption=caption,
                              privacy=opts.get("tiktok_privacy", "SELF_ONLY"),
                              mode=opts.get("tiktok_mode", "inbox"),
                              ai_generated=bool(opts.get("ai_generated", True)))
        elif target == "ayrshare":
            if "ayrshare" not in keys:
                raise PublishError("Add your Ayrshare key on the API keys page.")
            text = (title + "\n\n" + desc + " " + " ".join("#" + t.lstrip("#") for t in tags)).strip()
            res = ayrshare.post(keys["ayrshare"], media_url=f"{config.PUBLIC_MEDIA_BASE}/files/{jid}/final.mp4",
                                text=text, platforms=opts.get("platforms") or ["youtube", "tiktok"], yt_title=title)
        else:
            raise PublishError("Unknown target")
        store.update_pub(pid, status="done", url=res.get("url"), note=res.get("note"))
    except PublishError as e:
        store.update_pub(pid, status="error", error=str(e)[:400])
    except Exception as e:
        msg = str(e)
        for v in keys.values():
            msg = msg.replace(v, "***")
        store.update_pub(pid, status="error", error=f"Unexpected error: {msg[:300]}")
