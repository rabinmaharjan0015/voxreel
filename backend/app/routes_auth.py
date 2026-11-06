"""Email-based auth: signup → verify email → set password → login.

Flow:
  1. POST /signup {email}         → sends verification link
  2. POST /verify {token}         → marks email verified, returns setup_token
  3. POST /set-password {email, token, password} → stores password, returns JWT
  4. POST /login {email, password} → checks password, returns JWT
  5. GET  /me                      → current user (requires JWT)
"""
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException
from . import auth, config, mail, store
from .deps import current_user
from .schemas import LoginRequest, SetPasswordRequest, SignupRequest, VerifyRequest

router = APIRouter(prefix="/api/auth")


def _rate_limit(key: str, limit: int, window: int = 3600):
    """Simple per-key rate limiter. Raises 429 on overflow."""
    from . import store as _s
    k = f"rl:{key}"
    n = _s.r.incr(k)
    if n == 1:
        _s.r.expire(k, window)
    if n > limit:
        raise HTTPException(429, "Too many attempts. Try again later.")


@router.post("/signup")
def signup(req: SignupRequest):
    email = req.email.lower().strip()
    _rate_limit(f"signup:{email}", 5)
    user = store.get_user(email)
    if user and user.get("verified") and user.get("password_hash"):
        raise HTTPException(409, "Already registered. Log in instead.")
    if not user:
        store.create_user(email)
    token = secrets.token_urlsafe(32)
    store.put_verify_token(token, email)
    link = f"{config.FRONTEND_URL}/verify?token={token}"
    try:
        mail.send_verification(email, link)
    except Exception:
        raise HTTPException(500, "Could not send verification email. Check mail config.")
    return {"ok": True, "message": f"Verification link sent to {email}"}


@router.post("/verify")
def verify(req: VerifyRequest):
    _rate_limit(f"verify:{req.token[:16]}", 20)
    email = store.take_verify_token(req.token)
    if not email:
        raise HTTPException(400, "Invalid or expired verification link")
    store.set_user_verified(email)
    setup_token = secrets.token_urlsafe(32)
    store.put_setup_token(setup_token, email)
    return {"email": email, "setup_token": setup_token}


@router.post("/set-password")
def set_password(req: SetPasswordRequest):
    email = req.email.lower().strip()
    token_email = store.take_setup_token(req.token)
    if not token_email or token_email != email:
        raise HTTPException(400, "Invalid or expired setup token")
    user = store.get_user(email)
    if not user or not user.get("verified"):
        raise HTTPException(400, "Email not verified")
    store.set_user_password(email, auth.hash_password(req.password))
    jwt_token = auth.make_token(email)
    return {"token": jwt_token, "email": email}


@router.post("/login")
def login(req: LoginRequest):
    email = req.email.lower().strip()
    _rate_limit(f"login:{email}", 10)
    user = store.get_user(email)
    if not user or not user.get("password_hash"):
        raise HTTPException(401, "Invalid email or password")
    if not user.get("verified"):
        raise HTTPException(403, "Please verify your email first")
    if not auth.verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {"token": auth.make_token(email), "email": email}


@router.get("/me")
def me(user: str = Depends(current_user)):
    return {"email": user}
