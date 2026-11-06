"use client";
import { useCatalog } from "@/lib/api";
import { loadKeys, saveKeys, type Keys } from "@/lib/keys";
import { useEffect, useState } from "react";

export default function KeysPage() {
  const { data } = useCatalog();
  const [keys, setKeys] = useState<Keys>({});
  const [saved, setSaved] = useState(false);
  useEffect(() => setKeys(loadKeys()), []);

  const paid = data
    ? [
      ...data.providers.llm,
      ...data.providers.tts,
      ...data.providers.visuals,
      ...data.providers.publish,
    ].filter((p) => p.needs_key)
    : [];

  return (
    <div className="mx-auto max-w-2xl space-y-6 pt-8">
      <div>
        <h1 className="font-display text-3xl font-bold">Your API keys</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Keys are stored only in this browser and sent with each video job. While a job waits in
          the queue they are held encrypted in Redis, and they are deleted the moment a worker
          starts it. They are never logged or written to disk.
        </p>
      </div>

      <div className="glass space-y-5 p-6">
        {paid.length === 0 && <p className="text-sm text-zinc-500">Loading providers…</p>}
        {paid.map((p) => (
          <label key={p.id} className="block text-sm">
            <span className="mb-1 flex items-center justify-between">
              <span className="font-medium text-zinc-200">{p.name}</span>
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${p.free ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"
                  }`}
              >
                {p.free ? "FREE TIER" : "PAID"}
              </span>
            </span>
            <input
              type="password"
              autoComplete="off"
              className="field"
              placeholder="Paste key"
              value={keys[p.id] ?? ""}
              onChange={(e) => {
                setSaved(false);
                setKeys({ ...keys, [p.id]: e.target.value });
              }}
            />
            {p.note && <span className="mt-1 block text-xs text-zinc-500">{p.note}</span>}
          </label>
        ))}
      </div>

      <button
        className="btn-primary w-full"
        onClick={() => {
          saveKeys(keys);
          setSaved(true);
          setTimeout(() => setSaved(false), 2000);
        }}
      >
        {saved ? "Saved ✓" : "Save keys"}
      </button>
    </div>
  );
}
