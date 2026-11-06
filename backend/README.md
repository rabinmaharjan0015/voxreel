# VoxReel backend
Requires: Python 3.10+, ffmpeg, espeak-ng (for Kokoro).
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Keys are sent per request from the browser, kept in memory for the job, never stored or logged.
