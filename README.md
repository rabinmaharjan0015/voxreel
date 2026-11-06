# VoxReel
AI video platform: pick a video type → script → human-sounding voice → visuals → captions → MP4 → repurpose for TikTok, YouTube Shorts, and more.

- **Backend** (`backend/`): FastAPI + ffmpeg. Voices: Kokoro (free, local), OpenAI, ElevenLabs. Whisper (faster-whisper) times the captions.
- **Frontend** (`frontend/`): Next.js 14 App Router (TSX) + Tailwind. Routing is file-based: `/`, `/create/[type]`, `/projects`, `/projects/[id]`, `/settings/connections`, `/settings/keys`.
- **Redis**: job state + history (7-day TTL), an RQ worker queue, per-client rate limiting. Keys wait in Redis encrypted (Fernet) for at most 1h and are deleted the instant a worker starts the job.
- **Keys**: bring your own. Stored in browser localStorage, sent per job, never logged or written to disk.

Free path (no paid key): Ollama + Kokoro + Pollinations.

**Docker (recommended, runs everywhere incl. Windows):**
```
docker compose up --build              # redis + api + worker
cd frontend && cp .env.example .env.local && npm i && npm run dev
```
Scale throughput with `docker compose up --scale worker=3`. Set `KEY_ENCRYPTION_SECRET` in production.

**Manual:**
```
redis-server &
cd backend && pip install -r requirements.txt && cp .env.example .env
uvicorn app.main:app --reload --port 8000
rq worker videos            # second terminal (Linux/macOS/WSL; RQ does not run natively on Windows)
```
System deps: `ffmpeg`, `espeak-ng`.

## Publishing to YouTube / TikTok
Two routes, pick either (or both):

**1. Direct** (your own developer apps; credentials go in `backend/.env`, never in code)
- YouTube: Google Cloud → enable *YouTube Data API v3* → OAuth client (Web). Redirect URI: `{API_PUBLIC_URL}/api/oauth/youtube/callback`. Set `GOOGLE_CLIENT_ID/SECRET`.
- TikTok: developers.tiktok.com → add *Login Kit* + *Content Posting API* (+ Direct Post). Redirect URI: `{API_PUBLIC_URL}/api/oauth/tiktok/callback`. Set `TIKTOK_CLIENT_KEY/SECRET`.
- Then open **Accounts** in the app and connect.

**2. Posting service (bring your own key)**: Ayrshare. Add the key on **API keys**, and set `PUBLIC_MEDIA_BASE` to a public HTTPS address (it downloads the video from there).

### Limits to know before you go live
- **YouTube**: API uploads from an unaudited Google Cloud project are forced to *private*; apply for the YouTube API Services audit. `videos.insert` costs 1,600 quota units of the 10,000/day default (~6 uploads/day).
- **TikTok**: unaudited apps can only post privately (and for max 5 users/24h). **"Send to inbox"** works immediately — you tap Publish in the TikTok app. The audit takes weeks; posts made before it passes stay private.
- Videos are AI-generated: use the AI label on TikTok and YouTube's altered/synthetic-content disclosure in Studio where it applies.

## Production hardening

**Security**
- All job endpoints (`get_job`, `list_jobs`, `delete_job`, `publish`, `get_publication`) validate ownership via `X-Client-Id` — no IDOR.
- OAuth access tokens stored in Redis with a 30-day TTL; users reconnect when they expire.
- API keys are Fernet-encrypted in Redis with a 1h TTL and atomically deleted (`getdel`) the moment a worker picks up the job.

**Reliability**
- LLM script generation retries up to 3× on malformed JSON and transient HTTP 5xx/timeouts (4xx fail fast — bad key).
- TTS calls retry transient errors; 4xx (bad key) fail immediately.
- Visuals retry transient failures; if Pexels returns no results it falls back to Pollinations (free, no key) so a stock-search miss never kills a job.
- Intermediate files (per-scene wavs, images, clips, subtitle data) are cleaned up after the final MP4 is produced.
- Opportunistic disk GC on the health endpoint sweeps orphaned output directories (once/hour).

**UI/UX**
- Language selector (English, Spanish, French, Italian, Portuguese, Hindi) and per-LLM model picker in the create form.
- Duration slider supports the full 15–300s range.
- Projects list polls live while jobs are running; delete projects from the list.
- Skeleton shimmer loading states, entrance animations, and a responsive sticky header with active-link highlighting.
