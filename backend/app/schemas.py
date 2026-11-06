from pydantic import BaseModel, EmailStr, Field, SecretStr


class JobRequest(BaseModel):
    video_type: str
    topic: str = Field(min_length=3, max_length=500)
    duration_sec: int = Field(default=60, ge=15, le=300)
    tone: str = "friendly"
    language: str = "en"
    llm: str = "local"
    llm_model: str | None = None
    tts: str = "kokoro"
    voice: str | None = None
    visuals: str = "pollinations"
    captions: bool = True
    # Bring-your-own-key: keyed by provider id. Held in memory for the job only.
    keys: dict[str, SecretStr] = {}


# ---- Auth ----

class SignupRequest(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    token: str


class SetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
