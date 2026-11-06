"""Redis-backed job state, history, rate limiting and short-lived encrypted key hand-off."""
import base64, hashlib, json, os, time, uuid
import redis
from cryptography.fernet import Fernet
from . import config

r = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)   # app state

_NULLABLE = ("title", "video_url", "thumbnail_url", "error")


def _fernet() -> Fernet:
    if config.KEY_ENCRYPTION_SECRET:
        key = base64.urlsafe_b64encode(hashlib.sha256(config.KEY_ENCRYPTION_SECRET.encode()).digest())
    else:
        p = config.DATA_DIR / "secret.key"
        if not p.exists():
            try:
                fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as f:
                    f.write(Fernet.generate_key())
            except FileExistsError:
                pass
        key = p.read_bytes()
    return Fernet(key)


def create_job(cid: str, video_type: str, topic: str) -> str:
    jid = uuid.uuid4().hex[:16]
    now = time.time()
    r.hset(f"job:{jid}", mapping={
        "id": jid, "status": "queued", "step": "script", "progress": "0",
        "title": "", "video_url": "", "thumbnail_url": "", "error": "",
        "topic": topic[:200], "video_type": video_type, "created_at": str(now),
    })
    r.expire(f"job:{jid}", config.JOB_TTL)
    r.zadd(f"client:{cid}:jobs", {jid: now})
    r.expire(f"client:{cid}:jobs", config.JOB_TTL)
    return jid


def update(jid: str, **kw):
    r.hset(f"job:{jid}", mapping={k: ("" if v is None else str(v)) for k, v in kw.items()})


def _decode(h: dict) -> dict | None:
    if not h:
        return None
    for k in _NULLABLE:
        h[k] = h.get(k) or None
    h["progress"] = float(h.get("progress", 0))
    h["created_at"] = float(h.get("created_at", 0))
    return h


def get(jid: str) -> dict | None:
    return _decode(r.hgetall(f"job:{jid}"))


def list_for_client(cid: str, limit: int = 30) -> list[dict]:
    ids = r.zrevrange(f"client:{cid}:jobs", 0, limit - 1)
    pipe = r.pipeline()
    for i in ids:
        pipe.hgetall(f"job:{i}")
    return [j for j in (_decode(h) for h in pipe.execute()) if j]


def allow_new_job(cid: str) -> bool:
    k = f"rl:{cid}:{int(time.time() // 3600)}"
    n = r.incr(k)
    if n == 1:
        r.expire(k, 3600)
    return n <= config.RATE_LIMIT_PER_HOUR


def put_keys(jid: str, keys: dict[str, str]):
    if keys:
        r.set(f"jobkeys:{jid}", _fernet().encrypt(json.dumps(keys).encode()).decode(), ex=config.KEYS_TTL)


def take_keys(jid: str) -> dict[str, str]:
    """Read AND delete: keys leave Redis the moment a worker picks the job up."""
    raw = r.getdel(f"jobkeys:{jid}")
    return json.loads(_fernet().decrypt(raw.encode())) if raw else {}


# ---------- publishing ----------
def owns_job(cid: str, jid: str) -> bool:
    return r.zscore(f"client:{cid}:jobs", jid) is not None


def save_oauth(cid: str, platform: str, tok: dict):
    r.set(f"oauth:{cid}:{platform}", _fernet().encrypt(json.dumps(tok).encode()).decode(),
          ex=config.OAUTH_TTL)


def get_oauth(cid: str, platform: str) -> dict | None:
    raw = r.get(f"oauth:{cid}:{platform}")
    return json.loads(_fernet().decrypt(raw.encode())) if raw else None


def delete_oauth(cid: str, platform: str):
    r.delete(f"oauth:{cid}:{platform}")


def put_state(state: str, cid: str, platform: str):
    r.set(f"oauthstate:{state}", f"{cid}|{platform}", ex=600)


def take_state(state: str) -> tuple[str, str] | None:
    raw = r.getdel(f"oauthstate:{state}")
    return tuple(raw.split("|", 1)) if raw else None  # type: ignore[return-value]


def create_pub(jid: str, platform: str) -> str:
    pid = uuid.uuid4().hex[:16]
    r.hset(f"pub:{pid}", mapping={"id": pid, "job_id": jid, "platform": platform,
                                  "status": "queued", "url": "", "note": "", "error": ""})
    r.expire(f"pub:{pid}", config.JOB_TTL)
    return pid


def update_pub(pid: str, **kw):
    r.hset(f"pub:{pid}", mapping={k: ("" if v is None else str(v)) for k, v in kw.items()})


def get_pub(pid: str) -> dict | None:
    h = r.hgetall(f"pub:{pid}")
    if not h:
        return None
    for k in ("url", "note", "error"):
        h[k] = h.get(k) or None
    return h


def owns_pub(cid: str, pid: str) -> bool:
    """A publication belongs to a client if the underlying job does."""
    h = r.hgetall(f"pub:{pid}")
    jid = h.get("job_id")
    return bool(jid) and owns_job(cid, jid)


def delete_job(cid: str, jid: str) -> None:
    """Remove a job from Redis state and its output files from disk."""
    import shutil
    r.delete(f"job:{jid}")
    r.zrem(f"client:{cid}:jobs", jid)
    r.delete(f"jobkeys:{jid}")
    try:
        shutil.rmtree(config.OUTPUT_DIR / jid, ignore_errors=True)
    except Exception:
        pass


def gc_outputs(max_dirs: int = 200) -> int:
    """Sweep OUTPUT_DIR and remove job directories no longer tracked in Redis.
    Returns the number of directories removed. Safe to call opportunistically."""
    import shutil
    removed = 0
    try:
        for entry in config.OUTPUT_DIR.iterdir():
            if not entry.is_dir():
                continue
            jid = entry.name
            # remove if the job record is gone from Redis, or it's older than FILE_TTL
            if not r.exists(f"job:{jid}") or entry.stat().st_mtime < time.time() - config.FILE_TTL:
                shutil.rmtree(entry, ignore_errors=True)
                removed += 1
            if removed >= max_dirs:
                break
    except Exception:
        pass
    return removed


# ---------- auth ----------

def user_cid(email: str) -> str:
    """Stable client-id derived from an email so a logged-in user's jobs are scoped to them."""
    return f"user:{hashlib.sha256(email.encode()).hexdigest()[:24]}"


def create_user(email: str) -> None:
    r.hset(f"user:{email}", mapping={
        "email": email, "password_hash": "", "verified": "0",
        "created_at": str(time.time()),
    })


def get_user(email: str) -> dict | None:
    h = r.hgetall(f"user:{email}")
    if not h:
        return None
    h["verified"] = h.get("verified") == "1"
    return h


def set_user_verified(email: str) -> None:
    r.hset(f"user:{email}", "verified", "1")


def set_user_password(email: str, hashed: str) -> None:
    r.hset(f"user:{email}", "password_hash", hashed)


def put_verify_token(token: str, email: str) -> None:
    r.set(f"verify:{token}", email, ex=config.VERIFY_TOKEN_TTL)


def take_verify_token(token: str) -> str | None:
    return r.getdel(f"verify:{token}")


def put_setup_token(token: str, email: str) -> None:
    r.set(f"setup:{token}", email, ex=config.SETUP_TOKEN_TTL)


def take_setup_token(token: str) -> str | None:
    return r.getdel(f"setup:{token}")
