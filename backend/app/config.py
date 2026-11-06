import os
from pathlib import Path

try:  # load backend/.env for both the API and the RQ worker
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs")).resolve()   # served publicly at /files
DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()          # private (never served)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
KEY_ENCRYPTION_SECRET = os.getenv("KEY_ENCRYPTION_SECRET", "")
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "10"))
JOB_TTL = 7 * 86400          # redis job records expire after 7 days
KEYS_TTL = 3600              # queued key hand-off expires after 1h
OAUTH_TTL = 30 * 86400       # OAuth access tokens expire from Redis after 30 days
FILE_TTL = 7 * 86400         # generated MP4s cleaned from disk after 7 days

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- Publishing: these are YOUR OWN developer-app credentials (never hardcoded) ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://localhost:8000").rstrip("/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
PUBLIC_MEDIA_BASE = (os.getenv("PUBLIC_MEDIA_BASE") or API_PUBLIC_URL).rstrip("/")  # for posting services
