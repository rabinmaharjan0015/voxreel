from pydantic import BaseModel, Field, SecretStr


class JobRequest(BaseModel):
    video_type: str
    topic: str = Field(min_length=3, max_length=500)
    duration_sec: int = Field(default=60, ge=15, le=300)
    tone: str = "friendly"
    language: str = "en"
    llm: str = "ollama"
    llm_model: str | None = None
    tts: str = "kokoro"
    voice: str | None = None
    visuals: str = "pollinations"
    captions: bool = True
    # Bring-your-own-key: keyed by provider id. Held in memory for the job only.
    keys: dict[str, SecretStr] = {}
