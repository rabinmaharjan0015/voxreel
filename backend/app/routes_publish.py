import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, SecretStr
from .celery_app import celery
from . import config, store
from .deps import cid as cid_dep
from .publish import tiktok, youtube
from .publish.net import PublishError

router = APIRouter(prefix="/api")
MODS = {"youtube": youtube, "tiktok": tiktok}


class PublishRequest(BaseModel):
    target: str                       # youtube | tiktok | ayrshare
    title: str = ""
    description: str = ""
    tags: list[str] = []
    privacy: str = "private"          # youtube: private | unlisted | public
    tiktok_mode: str = "inbox"        # inbox | direct
    tiktok_privacy: str = "SELF_ONLY"
    ai_generated: bool = True
    platforms: list[str] = ["youtube", "tiktok"]   # ayrshare
    keys: dict[str, SecretStr] = {}


@router.get("/connections")
def connections(cid: str = Depends(cid_dep)):
    return {p: {"configured": m.configured(), "connected": store.get_oauth(cid, p) is not None}
            for p, m in MODS.items()}


@router.get("/oauth/{platform}/start")
def oauth_start(platform: str, cid: str = Depends(cid_dep)):
    m = MODS.get(platform)
    if not m:
        raise HTTPException(404, "Unknown platform")
    if not m.configured():
        raise HTTPException(400, f"{platform.title()} isn't configured on this server (missing app credentials).")
    state = secrets.token_urlsafe(24)
    store.put_state(state, cid, platform)
    return {"url": m.auth_url(state)}


@router.get("/oauth/{platform}/callback")
def oauth_callback(platform: str, code: str = "", state: str = "", error: str = ""):
    back = f"{config.FRONTEND_URL}/settings/connections"
    st = store.take_state(state) if state else None
    if error or not code or not st or st[1] != platform:
        return RedirectResponse(f"{back}?error={platform}")
    try:
        store.save_oauth(st[0], platform, MODS[platform].exchange(code))
    except PublishError:
        return RedirectResponse(f"{back}?error={platform}")
    return RedirectResponse(f"{back}?connected={platform}")


@router.delete("/connections/{platform}")
def disconnect(platform: str, cid: str = Depends(cid_dep)):
    if platform not in MODS:
        raise HTTPException(404, "Unknown platform")
    store.delete_oauth(cid, platform)
    return {"ok": True}


@router.post("/jobs/{jid}/publish")
def publish(jid: str, req: PublishRequest, cid: str = Depends(cid_dep)):
    if not store.owns_job(cid, jid):
        raise HTTPException(404, "Job not found")
    job = store.get(jid)
    if not job or job["status"] != "done":
        raise HTTPException(400, "Video isn't ready yet")
    if req.target in MODS and store.get_oauth(cid, req.target) is None:
        raise HTTPException(400, f"Connect your {req.target.title()} account first")
    if req.target == "ayrshare":
        if "ayrshare" not in req.keys:
            raise HTTPException(400, "Ayrshare needs your API key (API keys page)")
    elif req.target not in MODS:
        raise HTTPException(400, "Unknown target")
    if req.privacy not in ("private", "unlisted", "public"):
        raise HTTPException(400, "Invalid privacy")
    pid = store.create_pub(jid, req.target)
    if req.target == "ayrshare":
        store.put_keys(pid, {"ayrshare": req.keys["ayrshare"].get_secret_value()})
    opts = req.model_dump(exclude={"keys", "target"})
    celery.send_task("app.publisher.run_publish",
                     args=[pid, cid, jid, req.target, opts], queue="videos")
    return {"id": pid}


@router.get("/publications/{pid}")
def get_publication(pid: str, cid: str = Depends(cid_dep)):
    p = store.get_pub(pid)
    if not p or not store.owns_pub(cid, pid):
        raise HTTPException(404, "Not found")
    return p
