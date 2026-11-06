import re
from fastapi import Header, HTTPException
from .auth import decode_token

CID_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")


def cid(x_client_id: str = Header(default=""), authorization: str = Header(default="")) -> str:
    """Resolve a client identity. Prefers a JWT (logged-in user), falls back to
    the anonymous X-Client-Id header so the app still works without auth."""
    if authorization.startswith("Bearer "):
        email = decode_token(authorization[7:])
        if email:
            from . import store
            return store.user_cid(email)
    if CID_RE.match(x_client_id or ""):
        return x_client_id
    raise HTTPException(400, "Missing or invalid X-Client-Id")


# Alias used by the publish router.
cid_dep = cid


def current_user(authorization: str = Header(default="")) -> str:
    """Require a valid JWT. Returns the user's email."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    email = decode_token(authorization[7:])
    if not email:
        raise HTTPException(401, "Invalid or expired session")
    return email
