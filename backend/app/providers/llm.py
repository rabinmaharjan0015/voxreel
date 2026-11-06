import json, re
import httpx
from .. import config

OPENAI_COMPAT = {
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini"),
    "groq": ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
    "openrouter": ("https://openrouter.ai/api/v1", "meta-llama/llama-3.3-70b-instruct:free"),
}

SYSTEM = """You write voice-over scripts for videos. Write exactly how a real person talks:
contractions, varied sentence length, no stage directions, no emojis, no markdown.
Return ONLY JSON: {"title": str, "scenes": [{"narration": str, "image_prompt": str}]}.
image_prompt is a concrete visual description (no text in image)."""


def _extract_json(text: str) -> dict:
    # Strip markdown code fences (```json ... ```) that some models add.
    text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    # Try a direct parse first (clean JSON with no surrounding prose).
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: extract the outermost { ... } block (handles prose-wrapped JSON).
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("LLM did not return JSON")
    return json.loads(m.group(0))


# ---- Local Hugging Face model (free path, no external service needed) ----

_hf_cache: dict[str, tuple] = {}


def _hf_generate(req, user: str) -> str:
    """Generate text using a Hugging Face model loaded in-process.

    The model is cached after first load so subsequent jobs are fast.
    Works on CPU (float32) and GPU (bfloat16). First run downloads model
    weights (~2-6 GB depending on model) to the HF cache directory."""
    model_id = req.llm_model or config.HF_MODEL
    if model_id not in _hf_cache:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)
        if torch.cuda.is_available():
            model = model.cuda()
        model.eval()
        _hf_cache[model_id] = (tokenizer, model)

    import torch
    tokenizer, model = _hf_cache[model_id]
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    pad_id = tokenizer.pad_token_id or tokenizer.eos_token_id
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=2000,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=pad_id,
        )
    input_len = inputs["input_ids"].shape[1]
    return tokenizer.decode(output[0][input_len:], skip_special_tokens=True)


def generate_script(req, vt: dict, key: str | None) -> dict:
    words = int(req.duration_sec * 2.6)
    user = (
        f"Video type: {vt['name']}. Style: {vt['style']}\n"
        f"Topic: {req.topic}\nTone: {req.tone}\nLanguage: {req.language}\n"
        f"Target ~{words} words total across {vt['scenes']} scenes."
    )
    last_err = None
    for attempt in range(3):
        try:
            if req.llm == "local":
                text = _hf_generate(req, user)
            elif req.llm == "anthropic":
                with httpx.Client(timeout=120) as c:
                    r = c.post("https://api.anthropic.com/v1/messages",
                               headers={"x-api-key": key or "", "anthropic-version": "2023-06-01"},
                               json={"model": req.llm_model or "claude-sonnet-4-5", "max_tokens": 2000,
                                     "system": SYSTEM, "messages": [{"role": "user", "content": user}]})
                    r.raise_for_status()
                    text = r.json()["content"][0]["text"]
            else:
                base, default_model = OPENAI_COMPAT[req.llm]
                with httpx.Client(timeout=120) as c:
                    headers = {"Authorization": f"Bearer {key}"} if key else {}
                    r = c.post(f"{base}/chat/completions", headers=headers,
                               json={"model": req.llm_model or default_model,
                                     "messages": [{"role": "system", "content": SYSTEM},
                                                  {"role": "user", "content": user}]})
                    r.raise_for_status()
                    text = r.json()["choices"][0]["message"]["content"]
            data = _extract_json(text)
            if not data.get("scenes"):
                raise ValueError("Script has no scenes")
            return data
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e  # JSON parse error — retry, the model may produce valid JSON next time
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500:
                raise  # 4xx (bad key, bad request) — don't retry
            last_err = e
        except httpx.HTTPError as e:
            last_err = e  # transient network/timeout — retry
    raise RuntimeError(f"Script generation failed after retries: {last_err}")
