import subprocess, shutil
from pathlib import Path
import soundfile as sf
from .celery_app import celery
from .catalog import VIDEO_TYPES
from . import store
from .config import OUTPUT_DIR
from .schemas import JobRequest
from .providers import llm, tts, visuals, captions

STEPS = ["script", "voice", "visuals", "assemble", "captions", "done"]
_KEEP = {"final.mp4", "thumb.jpg"}  # finished video + thumbnail stay on disk


def _ffmpeg(args: list[str], cwd: Path, timeout: int = 600):
    """Run ffmpeg with a timeout so a stuck encode can't hang the worker forever."""
    try:
        p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"ffmpeg timed out after {timeout}s")
    if p.returncode:
        raise RuntimeError(p.stderr[-400:])


def _cleanup(work: Path) -> None:
    """Remove every intermediate file except the final video."""
    if not work.exists():
        return
    for f in work.iterdir():
        if f.name not in _KEEP:
            try:
                if f.is_dir():
                    shutil.rmtree(f, ignore_errors=True)
                else:
                    f.unlink(missing_ok=True)
            except Exception:
                pass


@celery.task(name="app.pipeline.run_job")
def run_job(jid: str, payload: dict):
    # Keys are decrypted from Redis (and deleted there) here; never written to disk or logged.
    keys = store.take_keys(jid)
    req = JobRequest(**payload, keys=keys)
    key = lambda pid: (req.keys[pid].get_secret_value() if pid in req.keys else None)
    work = OUTPUT_DIR / jid
    work.mkdir(parents=True, exist_ok=True)
    try:
        vt = next(v for v in VIDEO_TYPES if v["id"] == req.video_type)
        W, H = (1080, 1920) if vt["aspect"] == "9:16" else (1280, 720)

        store.update(jid, status="running", step="script", progress=0.05)
        script = llm.generate_script(req, vt, key(req.llm))
        store.update(jid, title=script.get("title"))
        scenes = script["scenes"]
        n = len(scenes)

        clips, wavs = [], []
        for i, sc in enumerate(scenes):
            store.update(jid, step="voice", progress=0.1 + 0.3 * i / n)
            wav = tts.synthesize(req, sc["narration"], work / f"s{i}.wav", key(req.tts))
            wavs.append(wav)
            dur = sf.info(wav).duration + 0.25

            store.update(jid, step="visuals", progress=0.4 + 0.3 * i / n)
            img = visuals.fetch_visual(req, sc["image_prompt"], (W, H), work / f"s{i}.jpg", key(req.visuals))

            store.update(jid, step="assemble", progress=0.7 + 0.15 * i / n)
            frames = int(dur * 30)
            vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                  f"zoompan=z='min(zoom+0.0007,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={frames}:s={W}x{H}:fps=30,format=yuv420p")
            clip = f"c{i}.mp4"
            _ffmpeg(["-i", img.name, "-i", wav.name, "-vf", vf, "-t", f"{dur:.2f}",
                     "-c:v", "libx264", "-c:a", "aac", "-shortest", clip], work)
            clips.append(clip)

        (work / "list.txt").write_text("".join(f"file '{c}'\n" for c in clips))
        _ffmpeg(["-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "raw.mp4"], work)

        final = "final.mp4"
        if req.captions:
            store.update(jid, step="captions", progress=0.88)
            _ffmpeg(["-i", "raw.mp4", "-vn", "-ac", "1", "-ar", "16000", "narration.wav"], work)
            captions.make_srt(work / "narration.wav", work / "subs.srt", req.language)
            style = "FontName=Arial,FontSize=%d,Bold=1,Outline=2,Alignment=2,MarginV=%d" % (
                14 if W > H else 18, 40 if W > H else 220)
            _ffmpeg(["-i", "raw.mp4", "-vf", f"subtitles=subs.srt:force_style='{style}'",
                     "-c:a", "copy", final], work)
        else:
            (work / "raw.mp4").rename(work / final)

        # Extract a thumbnail frame at 2s into the video for preview cards.
        try:
            _ffmpeg(["-i", final, "-ss", "2", "-vframes", "1", "-q:v", "2", "thumb.jpg"],
                    work, timeout=60)
            thumb = f"/files/{jid}/thumb.jpg"
        except Exception:
            thumb = ""  # thumbnail is best-effort; don't fail the job

        store.update(jid, status="done", step="done", progress=1.0,
                     video_url=f"/files/{jid}/{final}", thumbnail_url=thumb)
        # Free disk: keep only the finished MP4, drop all intermediate artifacts.
        _cleanup(work)
    except Exception as e:  # readable error with any key scrubbed
        msg = str(e)
        for v in keys.values():
            msg = msg.replace(v, "***")
        store.update(jid, status="error", error=msg[:400])
        _cleanup(work)  # don't leave a partial job's files lying around either
