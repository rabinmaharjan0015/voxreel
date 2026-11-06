"use client";
import ProviderPicker from "@/components/ProviderPicker";
import { createJob, useCatalog } from "@/lib/api";
import { loadKeys, type Keys } from "@/lib/keys";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Create() {
  const { type } = useParams<{ type: string }>();
  const router = useRouter();
  const { data, error } = useCatalog();
  const [keys, setKeys] = useState<Keys>({});
  const [f, setF] = useState({
    topic: "",
    duration_sec: 60,
    tone: "friendly",
    language: "en",
    llm: "ollama",
    llm_model: "",
    tts: "kokoro",
    visuals: "pollinations",
    voice: "",
    captions: true,
  });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => setKeys(loadKeys()), []);

  if (error) return <p className="glass p-5 text-sm text-rose-300">{error}</p>;
  if (!data) return <div className="skeleton h-96" />;
  const vt = data.video_types.find((v) => v.id === type);
  if (!vt) return <p className="glass p-5">Unknown video type.</p>;

  const voices = data.voices[f.tts] ?? [];
  const llmProvider = data.providers.llm.find((p) => p.id === f.llm);
  const models = llmProvider?.models ?? [];
  const set = <K extends keyof typeof f>(k: K, v: (typeof f)[K]) =>
    setF((p) => ({ ...p, [k]: v }));
  const hasKey = (id: string) => !!keys[id];

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const { id } = await createJob({
        ...f,
        video_type: vt!.id,
        voice: f.voice || voices[0] || "",
        llm_model: f.llm_model || undefined,
        keys,
      });
      router.push(`/projects/${id}`);
    } catch (x) {
      setErr((x as Error).message);
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="mx-auto max-w-3xl space-y-6 pt-6">
      {/* header */}
      <div className="animate-fade-up">
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <span className="text-lg">{vt.emoji}</span>
          <span>{vt.name}</span>
          <span className="text-zinc-700">·</span>
          <span>{vt.aspect}</span>
        </div>
        <h1 className="mt-1 font-display text-3xl font-bold">What&apos;s the video about?</h1>
      </div>

      {/* topic + settings */}
      <div className="glass space-y-5 p-6 animate-fade-up [animation-delay:0.05s]">
        <textarea
          required
          minLength={3}
          rows={3}
          className="field resize-none"
          placeholder="e.g. How black holes form, explained for a curious 12-year-old"
          value={f.topic}
          onChange={(e) => set("topic", e.target.value)}
        />
        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="field-label mb-1.5 block">
              Length: <b className="text-zinc-200">{f.duration_sec}s</b>
            </span>
            <input
              type="range"
              min={15}
              max={300}
              step={15}
              value={f.duration_sec}
              onChange={(e) => set("duration_sec", +e.target.value)}
              className="mt-2 w-full accent-violet-500"
            />
          </label>
          <label className="block">
            <span className="field-label mb-1.5 block">Tone</span>
            <select
              className="field"
              value={f.tone}
              onChange={(e) => set("tone", e.target.value)}
            >
              {["friendly", "professional", "energetic", "calm", "dramatic", "humorous"].map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="field-label mb-1.5 block">Language</span>
            <select
              className="field"
              value={f.language}
              onChange={(e) => set("language", e.target.value)}
            >
              {data.languages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="field-label mb-1.5 block">Voice</span>
            <select
              className="field"
              value={f.voice || voices[0] || ""}
              onChange={(e) => set("voice", e.target.value)}
            >
              {voices.length === 0 && <option value="">Default</option>}
              {voices.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label className="flex items-center gap-2 text-sm text-zinc-300">
          <input
            type="checkbox"
            className="h-4 w-4 accent-violet-500"
            checked={f.captions}
            onChange={(e) => set("captions", e.target.checked)}
          />
          Burn in captions (Whisper word timing)
        </label>
      </div>

      {/* providers */}
      <div className="glass space-y-6 p-6 animate-fade-up [animation-delay:0.1s]">
        <ProviderPicker
          label="Script (LLM)"
          options={data.providers.llm}
          value={f.llm}
          onChange={(v) => set("llm", v)}
          hasKey={hasKey}
        />
        {models.length > 0 && (
          <label className="block max-w-sm">
            <span className="field-label mb-1.5 block">Model (optional)</span>
            <select
              className="field"
              value={f.llm_model}
              onChange={(e) => set("llm_model", e.target.value)}
            >
              <option value="">Default for provider</option>
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>
        )}
        <ProviderPicker
          label="Voice engine"
          options={data.providers.tts}
          value={f.tts}
          onChange={(v) => {
            set("tts", v);
            set("voice", "");
          }}
          hasKey={hasKey}
        />
        <ProviderPicker
          label="Visuals"
          options={data.providers.visuals}
          value={f.visuals}
          onChange={(v) => set("visuals", v)}
          hasKey={hasKey}
        />
      </div>

      {err && <p className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-300">{err}</p>}
      <button disabled={busy} className="btn-primary w-full !py-4 text-base">
        {busy ? "Starting…" : "Generate video ✨"}
      </button>
    </form>
  );
}
