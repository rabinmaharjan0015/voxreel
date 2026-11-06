"""Password hashing and JWT session tokens."""
import time
import bcrypt
import jwt
from . import config


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False


def make_token(email: str) -> str:
    return jwt.encode(
        {"sub": email, "exp": int(time.time()) + config.JWT_TTL},
        config.JWT_SECRET,
        algorithm="HS256",
    )


def decode_token(token: str) -> str | None:
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])["sub"]
    except Exception:
        return None
