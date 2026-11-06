import re
from fastapi import Header, HTTPException

CID_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def cid(x_client_id: str = Header(default="")) -> str:
    if not CID_RE.match(x_client_id or ""):
        raise HTTPException(400, "Missing or invalid X-Client-Id")
    return x_client_id
