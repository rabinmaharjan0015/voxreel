from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import store, tasks
from .catalog import VIDEO_TYPES, PROVIDERS, VOICES, LANGUAGES
from .config import ALLOWED_ORIGINS, OUTPUT_DIR
from .schemas import JobRequest
from .deps import cid as _cid
from .routes_publish import router as publish_router

app = FastAPI(title="VoxReel API")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])
app.mount("/files", StaticFiles(directory=OUTPUT_DIR), name="files")

app.include_router(publish_router)


@app.get("/api/health")
def health():
    store.r.ping()
    # Opportunistic disk GC: at most once per hour, sweep orphaned output dirs.
    k = "gc:ran"
    if not store.r.exists(k):
        store.r.set(k, "1", ex=3600)
        store.gc_outputs()
    return {"ok": True}


@app.get("/api/catalog")
def catalog():
    return {"video_types": VIDEO_TYPES, "providers": PROVIDERS, "voices": VOICES, "languages": LANGUAGES}


@app.post("/api/jobs")
def create_job(req: JobRequest, x_client_id: str = Header(default="")):
    cid = _cid(x_client_id)
    if not any(v["id"] == req.video_type for v in VIDEO_TYPES):
        raise HTTPException(400, "Unknown video type")
    used = {}
    for kind, pid in (("llm", req.llm), ("tts", req.tts), ("visuals", req.visuals)):
        p = next((p for p in PROVIDERS[kind] if p["id"] == pid), None)
        if not p:
            raise HTTPException(400, f"Unknown {kind} provider: {pid}")
        if p["needs_key"]:
            if pid not in req.keys:
                raise HTTPException(400, f"{p['name']} needs your API key (API keys page)")
            used[pid] = req.keys[pid].get_secret_value()   # only keys this job uses
    if not store.allow_new_job(cid):
        raise HTTPException(429, "Hourly video limit reached. Try again later.")
    jid = store.create_job(cid, req.video_type, req.topic)
    store.put_keys(jid, used)
    tasks.enqueue(jid, req.model_dump(exclude={"keys"}))
    return {"id": jid}


@app.get("/api/jobs")
def list_jobs(x_client_id: str = Header(default="")):
    return store.list_for_client(_cid(x_client_id))


@app.get("/api/jobs/{jid}")
def get_job(jid: str, x_client_id: str = Header(default="")):
    cid = _cid(x_client_id)
    job = store.get(jid)
    if not job or not store.owns_job(cid, jid):
        raise HTTPException(404, "Job not found")
    return job


@app.delete("/api/jobs/{jid}")
def delete_job(jid: str, x_client_id: str = Header(default="")):
    cid = _cid(x_client_id)
    if not store.owns_job(cid, jid):
        raise HTTPException(404, "Job not found")
    store.delete_job(cid, jid)
    return {"ok": True}
