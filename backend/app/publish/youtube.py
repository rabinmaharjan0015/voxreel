import time
from pathlib import Path
from urllib.parse import urlencode
from .. import config
from .net import client, PublishError

AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def configured() -> bool:
    return bool(config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET)


def redirect_uri() -> str:
    return f"{config.API_PUBLIC_URL}/api/oauth/youtube/callback"


def auth_url(state: str) -> str:
    return AUTH + "?" + urlencode({
        "client_id": config.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri(), "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent", "state": state})


def _tok(d: dict, old: dict | None = None) -> dict:
    return {"access_token": d["access_token"],
            "refresh_token": d.get("refresh_token") or (old or {}).get("refresh_token"),
            "expires_at": time.time() + int(d.get("expires_in", 3600))}


def exchange(code: str) -> dict:
    with client(30) as c:
        r = c.post(TOKEN, data={"code": code, "client_id": config.GOOGLE_CLIENT_ID,
                                "client_secret": config.GOOGLE_CLIENT_SECRET,
                                "redirect_uri": redirect_uri(), "grant_type": "authorization_code"})
    if r.status_code >= 400:
        raise PublishError(f"Google sign-in failed: {r.text[:200]}")
    return _tok(r.json())


def fresh(tok: dict) -> tuple[dict, bool]:
    if tok["expires_at"] - time.time() > 60:
        return tok, False
    if not tok.get("refresh_token"):
        raise PublishError("YouTube session expired. Reconnect your account.")
    with client(30) as c:
        r = c.post(TOKEN, data={"client_id": config.GOOGLE_CLIENT_ID, "client_secret": config.GOOGLE_CLIENT_SECRET,
                                "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"})
    if r.status_code >= 400:
        raise PublishError("YouTube session expired. Reconnect your account.")
    return _tok(r.json(), tok), True


def _stream(path: Path, step: int = 1 << 20):
    with path.open("rb") as f:
        while chunk := f.read(step):
            yield chunk


def upload(access_token: str, path: Path, *, title: str, description: str, tags: list[str],
           privacy: str, vertical: bool) -> dict:
    size = path.stat().st_size
    if vertical and "#shorts" not in (title + description).lower():
        description = (description + "\n\n#Shorts").strip()
    meta = {"snippet": {"title": title[:100], "description": description[:5000],
                        "tags": [t for t in tags if t][:15], "categoryId": "22"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}
    with client() as c:
        r = c.post("https://www.googleapis.com/upload/youtube/v3/videos",
                   params={"uploadType": "resumable", "part": "snippet,status"},
                   headers={"Authorization": f"Bearer {access_token}", "X-Upload-Content-Type": "video/mp4",
                            "X-Upload-Content-Length": str(size)}, json=meta)
        if r.status_code >= 400:
            msg = r.text[:300]
            if "quotaExceeded" in r.text:
                msg = "YouTube daily API quota reached (about 6 uploads/day per project). Try tomorrow."
            raise PublishError(msg)
        loc = r.headers["Location"]
        up = c.put(loc, content=_stream(path), headers={"Content-Length": str(size), "Content-Type": "video/mp4"})
    if up.status_code >= 400:
        raise PublishError(f"YouTube upload failed: {up.text[:300]}")
    data = up.json()
    actual = (data.get("status") or {}).get("privacyStatus", privacy)
    note = None
    if privacy != "private" and actual == "private":
        note = ("YouTube kept this video private because your Google Cloud project hasn't passed "
                "YouTube's API audit yet. You can change it manually only after the audit.")
    return {"url": f"https://youtu.be/{data['id']}", "note": note or f"Uploaded as {actual}."}
