import time
from pathlib import Path
from urllib.parse import urlencode
from .. import config
from .net import client, PublishError

BASE = "https://open.tiktokapis.com"
SCOPES = "user.info.basic,video.publish,video.upload"
MB = 1024 * 1024


def configured() -> bool:
    return bool(config.TIKTOK_CLIENT_KEY and config.TIKTOK_CLIENT_SECRET)


def redirect_uri() -> str:
    return f"{config.API_PUBLIC_URL}/api/oauth/tiktok/callback"


def auth_url(state: str) -> str:
    return "https://www.tiktok.com/v2/auth/authorize/?" + urlencode({
        "client_key": config.TIKTOK_CLIENT_KEY, "scope": SCOPES, "response_type": "code",
        "redirect_uri": redirect_uri(), "state": state})


def _tok(d: dict) -> dict:
    if "access_token" not in d:
        raise PublishError(f"TikTok sign-in failed: {d.get('error_description') or d}")
    return {"access_token": d["access_token"], "refresh_token": d.get("refresh_token"),
            "open_id": d.get("open_id"), "expires_at": time.time() + int(d.get("expires_in", 86400))}


def _form(c, data: dict) -> dict:
    r = c.post(f"{BASE}/v2/oauth/token/", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return _tok(r.json())


def exchange(code: str) -> dict:
    with client(30) as c:
        return _form(c, {"client_key": config.TIKTOK_CLIENT_KEY, "client_secret": config.TIKTOK_CLIENT_SECRET,
                         "code": code, "grant_type": "authorization_code", "redirect_uri": redirect_uri()})


def fresh(tok: dict) -> tuple[dict, bool]:
    if tok["expires_at"] - time.time() > 60:
        return tok, False
    if not tok.get("refresh_token"):
        raise PublishError("TikTok session expired. Reconnect your account.")
    with client(30) as c:
        new = _form(c, {"client_key": config.TIKTOK_CLIENT_KEY, "client_secret": config.TIKTOK_CLIENT_SECRET,
                        "grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
    new["refresh_token"] = new.get("refresh_token") or tok["refresh_token"]
    return new, True


FRIENDLY = {
    "unaudited_client_can_only_post_to_private_accounts":
        "Your TikTok app hasn't passed TikTok's audit, so it can only post to a private account. "
        "Use 'Send to TikTok inbox' instead, or complete the audit.",
    "spam_risk_too_many_posts": "TikTok's daily API post limit for this account was reached.",
    "reached_active_user_cap": "Your TikTok app reached its daily user cap.",
}


def _ok(resp) -> dict:
    try:
        body = resp.json()
    except Exception:
        raise PublishError(f"TikTok error {resp.status_code}: {resp.text[:200]}")
    code = (body.get("error") or {}).get("code", "ok")
    if code != "ok":
        raise PublishError(FRIENDLY.get(code) or f"TikTok: {code} - {(body['error'].get('message') or '')[:200]}")
    return body.get("data") or {}


def post(access_token: str, path: Path, *, caption: str, privacy: str, mode: str, ai_generated: bool,
         poll_seconds: int = 120, poll_every: float = 3.0) -> dict:
    size = path.stat().st_size
    if size <= 64 * MB:
        chunk, n = size, 1
    else:
        chunk = 32 * MB
        n = size // chunk  # final chunk absorbs the remainder
    source = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": n}
    auth = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"}
    with client() as c:
        if mode == "direct":
            info = _ok(c.post(f"{BASE}/v2/post/publish/creator_info/query/", headers=auth))
            options = info.get("privacy_level_options") or []
            if options and privacy not in options:
                raise PublishError(f"TikTok doesn't allow '{privacy}' for this account. Allowed: {', '.join(options)}")
            body = {"post_info": {"title": caption[:2200], "privacy_level": privacy, "disable_duet": False,
                                  "disable_comment": False, "disable_stitch": False,
                                  "video_cover_timestamp_ms": 1000, "is_aigc": ai_generated},
                    "source_info": source}
            init = _ok(c.post(f"{BASE}/v2/post/publish/video/init/", headers=auth, json=body))
        else:
            init = _ok(c.post(f"{BASE}/v2/post/publish/inbox/video/init/", headers=auth, json={"source_info": source}))
        pub_id, upload_url = init["publish_id"], init["upload_url"]

        with path.open("rb") as f:
            for i in range(n):
                start = i * chunk
                end = size - 1 if i == n - 1 else start + chunk - 1
                f.seek(start)
                data = f.read(end - start + 1)
                r = c.put(upload_url, content=data, headers={
                    "Content-Type": "video/mp4", "Content-Length": str(len(data)),
                    "Content-Range": f"bytes {start}-{end}/{size}"})
                if r.status_code >= 400:
                    raise PublishError(f"TikTok upload failed ({r.status_code}): {r.text[:200]}")

        deadline = time.time() + poll_seconds
        while time.time() < deadline:
            st = _ok(c.post(f"{BASE}/v2/post/publish/status/fetch/", headers=auth, json={"publish_id": pub_id}))
            status = st.get("status", "")
            if status == "FAILED":
                raise PublishError(f"TikTok rejected the video: {st.get('fail_reason', 'unknown reason')}")
            if status == "PUBLISH_COMPLETE":
                return {"url": None, "note": "Published on TikTok. It may take a minute to appear on your profile."}
            if status == "SEND_TO_USER_INBOX":
                return {"url": None, "note": "Sent. Open TikTok, tap the notification and publish it within 24 hours."}
            time.sleep(poll_every)
    return {"url": None, "note": f"Uploaded; TikTok is still processing it (id {pub_id}). Check the TikTok app shortly."}
