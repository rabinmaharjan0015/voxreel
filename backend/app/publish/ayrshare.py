from .net import client, PublishError


def post(api_key: str, *, media_url: str, text: str, platforms: list[str], yt_title: str) -> dict:
    if not media_url.startswith("https://"):
        raise PublishError("Posting services pull your video from a public HTTPS URL. "
                           "Set PUBLIC_MEDIA_BASE to your public https address.")
    body = {"post": text, "platforms": platforms, "mediaUrls": [media_url]}
    if "youtube" in platforms:
        body["youTubeOptions"] = {"title": yt_title[:100]}
    with client(120) as c:
        r = c.post("https://api.ayrshare.com/api/post", headers={"Authorization": f"Bearer {api_key}"}, json=body)
    try:
        data = r.json()
    except Exception:
        raise PublishError(f"Ayrshare error {r.status_code}: {r.text[:200]}")
    if r.status_code >= 400 or data.get("status") == "error":
        msg = data.get("message") or "; ".join(str(e.get("message", e)) for e in data.get("errors", [])) or r.text[:200]
        raise PublishError(f"Ayrshare: {msg}")
    urls = [p.get("postUrl") for p in data.get("postIds", []) if isinstance(p, dict) and p.get("postUrl")]
    return {"url": urls[0] if urls else None, "note": "Submitted via Ayrshare." }
