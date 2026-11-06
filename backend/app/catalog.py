"""Single source of truth for video types and providers (served to the UI)."""

# Languages supported by Kokoro (and most TTS engines). Whisper uses these for captions too.
LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "it", "name": "Italian"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "hi", "name": "Hindi"},
]

VIDEO_TYPES = [
    {"id": "explainer", "name": "Explainer", "emoji": "💡", "aspect": "16:9", "scenes": 6,
     "blurb": "Break down any topic into a clear, friendly walkthrough.",
     "style": "Clear, structured, curious. Open with a hook, end with a takeaway."},
    {"id": "shorts", "name": "Faceless Shorts", "emoji": "⚡", "aspect": "9:16", "scenes": 7,
     "blurb": "Punchy vertical videos for Reels, Shorts and TikTok.",
     "style": "Fast hook in the first sentence, short punchy lines, strong ending."},
    {"id": "story", "name": "Story Narration", "emoji": "📖", "aspect": "16:9", "scenes": 8,
     "blurb": "Cinematic storytelling with a warm narrator.",
     "style": "Vivid, emotional, show-don't-tell. Natural pauses."},
    {"id": "promo", "name": "Product Promo", "emoji": "🛍️", "aspect": "16:9", "scenes": 5,
     "blurb": "Launch and ad videos that sell the benefit, not the feature.",
     "style": "Benefit-led, confident, one clear call to action."},
    {"id": "news", "name": "News Recap", "emoji": "📰", "aspect": "16:9", "scenes": 6,
     "blurb": "Quick, neutral summaries of a topic or event.",
     "style": "Neutral, factual, concise, no hype."},
    {"id": "tutorial", "name": "Tutorial", "emoji": "🧭", "aspect": "16:9", "scenes": 7,
     "blurb": "Step-by-step how-to videos.",
     "style": "Numbered steps, direct instructions, friendly tone."},
]

PROVIDERS = {
    "llm": [
        {"id": "ollama", "name": "Ollama (local)", "free": True, "needs_key": False,
         "note": "Runs on your machine. Install Ollama and pull a model.",
         "models": ["llama3.2", "llama3.1", "qwen2.5", "phi3"]},
        {"id": "groq", "name": "Groq", "free": True, "needs_key": True,
         "note": "Free-tier key from console.groq.com",
         "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]},
        {"id": "openrouter", "name": "OpenRouter", "free": True, "needs_key": True,
         "note": "Use ':free' models with a free key",
         "models": ["meta-llama/llama-3.3-70b-instruct:free", "google/gemini-2.0-flash-exp:free"]},
        {"id": "openai", "name": "OpenAI", "free": False, "needs_key": True, "note": "",
         "models": ["gpt-4o-mini", "gpt-4o"]},
        {"id": "anthropic", "name": "Anthropic", "free": False, "needs_key": True, "note": "",
         "models": ["claude-sonnet-4-5", "claude-haiku-4-5"]},
    ],
    "tts": [
        {"id": "kokoro", "name": "Kokoro (local, natural)", "free": True, "needs_key": False,
         "note": "Open-source, human-sounding, runs locally.", "models": []},
        {"id": "openai_tts", "name": "OpenAI Voice", "free": False, "needs_key": True, "note": "", "models": []},
        {"id": "elevenlabs", "name": "ElevenLabs", "free": False, "needs_key": True,
         "note": "Most lifelike voices.", "models": []},
    ],
    "visuals": [
        {"id": "pollinations", "name": "Pollinations (AI images)", "free": True, "needs_key": False,
         "note": "Free AI-generated images.", "models": []},
        {"id": "pexels", "name": "Pexels (stock photos)", "free": True, "needs_key": True,
         "note": "Free key from pexels.com/api", "models": []},
    ],
    "publish": [
        {"id": "ayrshare", "name": "Ayrshare (posting service)", "free": False, "needs_key": True,
         "note": "Posts through an already-audited app. Video needs a paid plan.", "models": []},
    ],
}

VOICES = {
    "kokoro": ["af_heart", "af_bella", "am_michael", "am_puck", "bf_emma", "bm_george"],
    "openai_tts": ["alloy", "nova", "onyx", "shimmer"],
    "elevenlabs": ["21m00Tcm4TlvDq8ikWAM"],
}
