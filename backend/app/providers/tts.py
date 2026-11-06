"""Human-sounding voices. Whisper is speech-to-text, so it is used for captions
(see captions.py); voices come from Kokoro (local) or ElevenLabs/OpenAI (BYOK)."""
from pathlib import Path
import httpx, numpy as np, soundfile as sf, time

_kokoro = {}


def _kokoro_pipe(lang: str):
    from kokoro import KPipeline
    code = {"en": "a", "es": "e", "fr": "f", "hi": "h", "it": "i", "pt": "p"}.get(lang, "a")
    if code not in _kokoro:
        _kokoro[code] = KPipeline(lang_code=code)
    return _kokoro[code]


def _retry(fn, attempts: int = 3):
    """Retry transient HTTP errors (timeouts, 5xx); fail fast on 4xx (bad key)."""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500:
                raise
            last = e
            if i < attempts - 1:
                time.sleep(2 * (i + 1))
        except httpx.HTTPError as e:
            last = e
            if i < attempts - 1:
                time.sleep(2 * (i + 1))
    raise last


def synthesize(req, text: str, out: Path, key: str | None) -> Path:
    if req.tts == "kokoro":
        pipe = _kokoro_pipe(req.language)
        chunks = [np.asarray(a) for _, _, a in pipe(text, voice=req.voice or "af_heart", speed=1.0)]
        sf.write(out, np.concatenate(chunks), 24000)
    elif req.tts == "openai_tts":
        def _call():
            r = httpx.post("https://api.openai.com/v1/audio/speech", timeout=120,
                           headers={"Authorization": f"Bearer {key}"},
                           json={"model": "gpt-4o-mini-tts", "voice": req.voice or "nova",
                                 "input": text, "response_format": "wav",
                                 "instructions": "Speak naturally and conversationally, like a real person."})
            r.raise_for_status(); return r.content
        out.write_bytes(_retry(_call))
    elif req.tts == "elevenlabs":
        vid = req.voice or "21m00Tcm4TlvDq8ikWAM"
        def _call():
            r = httpx.post(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=pcm_24000",
                           timeout=120, headers={"xi-api-key": key or ""},
                           json={"text": text, "model_id": "eleven_multilingual_v2"})
            r.raise_for_status(); return r.content
        pcm = np.frombuffer(_retry(_call), dtype=np.int16)
        sf.write(out, pcm, 24000, subtype="PCM_16")
    else:
        raise ValueError(f"Unknown TTS provider {req.tts}")
    return out
