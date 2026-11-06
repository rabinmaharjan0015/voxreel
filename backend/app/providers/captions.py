from pathlib import Path
from ..config import WHISPER_MODEL

_model = None


def _fmt(t: float) -> str:
    h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
    return f"{int(h):02}:{int(m):02}:{s:06.3f}".replace(".", ",")


def make_srt(audio: Path, out: Path, language: str = "en") -> Path:
    """Whisper transcribes the narration to get exact word timing for captions."""
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL, compute_type="int8")
    segments, _ = _model.transcribe(str(audio), language=language, word_timestamps=True)
    lines, i = [], 1
    for seg in segments:
        words = seg.words or []
        for k in range(0, len(words), 5):
            grp = words[k:k + 5]
            lines.append(f"{i}\n{_fmt(grp[0].start)} --> {_fmt(grp[-1].end)}\n{' '.join(w.word.strip() for w in grp)}\n")
            i += 1
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
