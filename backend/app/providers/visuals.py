from pathlib import Path
from urllib.parse import quote
import httpx, time


def _pollinations(prompt: str, size: tuple[int, int], out: Path, c: httpx.Client) -> None:
    w, h = size
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width={w}&height={h}&nologo=true"
    r = c.get(url)
    r.raise_for_status()
    out.write_bytes(r.content)


def _pexels(prompt: str, size: tuple[int, int], out: Path, key: str | None, c: httpx.Client) -> None:
    w, h = size
    orient = "portrait" if h > w else "landscape"
    r = c.get("https://api.pexels.com/v1/search", headers={"Authorization": key or ""},
              params={"query": prompt[:80], "per_page": 1, "orientation": orient})
    r.raise_for_status()
    photos = r.json().get("photos") or []
    if not photos:
        raise ValueError(f"No Pexels result for: {prompt[:40]}")
    img = c.get(photos[0]["src"]["large2x"])
    img.raise_for_status()
    out.write_bytes(img.content)


def fetch_visual(req, prompt: str, size: tuple[int, int], out: Path, key: str | None) -> Path:
    """Fetch a visual with transient-retry and a Pollinations fallback when stock search comes up empty."""
    with httpx.Client(timeout=180, follow_redirects=True) as c:
        for attempt in range(3):
            try:
                if req.visuals == "pollinations":
                    _pollinations(prompt, size, out, c)
                elif req.visuals == "pexels":
                    _pexels(prompt, size, out, key, c)
                else:
                    raise ValueError(f"Unsupported visuals provider {req.visuals}")
                return out
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500:
                    raise  # 4xx (bad key) — don't retry
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                else:
                    raise
            except (httpx.HTTPError, ValueError) as e:
                # Pexels "no results" or transient network issue — fall back to Pollinations
                if isinstance(e, ValueError) and "No Pexels result" in str(e):
                    _pollinations(prompt, size, out, c)
                    return out
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                else:
                    raise
    return out
