"use client";
import { getConnections, getPublication, publishJob } from "@/lib/api";
import { loadKeys } from "@/lib/keys";
import type { Connections, Job, Publication } from "@/lib/types";
import Link from "next/link";
import { useEffect, useState } from "react";

type Target = "youtube" | "tiktok" | "ayrshare";
const TARGETS: Record<Target, { label: string; emoji: string }> = {
  youtube: { label: "YouTube", emoji: "▶️" },
  tiktok: { label: "TikTok", emoji: "🎵" },
  ayrshare: { label: "Posting service", emoji: "📤" },
};

export default function PublishPanel({ job }: { job: Job }) {
  const [conn, setConn] = useState<Connections | null>(null);
  const [target, setTarget] = useState<Target>("youtube");
  const [f, setF] = useState({
    title: job.title ?? job.topic,
    description: "",
    tags: "",
    privacy: "private",
    tiktok_mode: "inbox",
    ai_generated: true,
  });
  const [pub, setPub] = useState<Publication | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    getConnections().then(setConn).catch(() => setConn(null));
  }, []);

  const connected = target === "ayrshare" ? !!loadKeys()["ayrshare"] : !!conn?.[target]?.connected;

  async function go() {
    setBusy(true);
    setErr(null);
    setPub(null);
    try {
      const { id } = await publishJob(job.id, {
        target,
        title: f.title,
        description: f.description,
        tags: f.tags.split(/[ ,#]+/).filter(Boolean),
        privacy: f.privacy,
        tiktok_mode: f.tiktok_mode,
        tiktok_privacy: f.tiktok_mode === "direct" ? "PUBLIC_TO_EVERYONE" : "SELF_ONLY",
        ai_generated: f.ai_generated,
        keys: target === "ayrshare" ? { ayrshare: loadKeys()["ayrshare"] } : {},
      });
      const tick = async () => {
        const p = await getPublication(id);
        setPub(p);
        if (p.status === "done" || p.status === "error") {
          setBusy(false);
          return;
        }
        setTimeout(tick, 2000);
      };
      tick();
    } catch (e) {
      setErr((e as Error).message);
      setBusy(false);
    }
  }

  return (
    <div className="glass space-y-5 p-6">
      <div>
        <h2 className="font-display text-xl font-semibold">Publish to socials</h2>
        <p className="mt-1 text-xs text-zinc-500">Repurpose your video for another platform.</p>
      </div>

      {/* target picker */}
      <div className="grid grid-cols-3 gap-2">
        {(Object.keys(TARGETS) as Target[]).map((t) => (
          <button
            key={t}
            onClick={() => setTarget(t)}
            className={`flex flex-col items-center gap-1.5 rounded-xl border p-3 text-center transition ${target === t
                ? "border-violet-400/70 bg-violet-500/10"
                : "border-line bg-white/[0.03] hover:bg-white/[0.06]"
              }`}
          >
            <span className="text-lg">{TARGETS[t].emoji}</span>
            <span className="text-xs font-medium text-zinc-200">{TARGETS[t].label}</span>
          </button>
        ))}
      </div>

      <div className="space-y-3">
        <label className="block">
          <span className="field-label mb-1 block">Title</span>
          <input
            className="field"
            value={f.title}
            maxLength={100}
            onChange={(e) => setF({ ...f, title: e.target.value })}
            placeholder="Video title"
          />
        </label>
        <label className="block">
          <span className="field-label mb-1 block">Description</span>
          <textarea
            className="field resize-none"
            rows={3}
            value={f.description}
            onChange={(e) => setF({ ...f, description: e.target.value })}
            placeholder="Video description"
          />
        </label>
        <label className="block">
          <span className="field-label mb-1 block">Tags</span>
          <input
            className="field"
            value={f.tags}
            onChange={(e) => setF({ ...f, tags: e.target.value })}
            placeholder="ai, explainer, learn"
          />
        </label>
      </div>

      {target === "youtube" && (
        <label className="block">
          <span className="field-label mb-1 block">Privacy</span>
          <select className="field" value={f.privacy} onChange={(e) => setF({ ...f, privacy: e.target.value })}>
            <option value="private">Private</option>
            <option value="unlisted">Unlisted</option>
            <option value="public">Public</option>
          </select>
        </label>
      )}
      {target === "tiktok" && (
        <label className="block">
          <span className="field-label mb-1 block">Posting mode</span>
          <select className="field" value={f.tiktok_mode} onChange={(e) => setF({ ...f, tiktok_mode: e.target.value })}>
            <option value="inbox">Send to inbox (you tap Publish in app)</option>
            <option value="direct">Direct post (needs audited app)</option>
          </select>
        </label>
      )}
      {target === "tiktok" && (
        <label className="flex items-center gap-2 text-sm text-zinc-300">
          <input
            type="checkbox"
            className="h-4 w-4 accent-violet-500"
            checked={f.ai_generated}
            onChange={(e) => setF({ ...f, ai_generated: e.target.checked })}
          />
          Label as AI-generated
        </label>
      )}

      {target === "ayrshare" && (
        <p className="rounded-xl bg-white/5 p-3 text-xs text-zinc-500">
          Needs your Ayrshare key and a public HTTPS address for this server (PUBLIC_MEDIA_BASE).
        </p>
      )}

      {!connected && (
        <p className="text-sm text-amber-300">
          {target === "ayrshare" ? "Add your Ayrshare key on the " : "Connect your account on the "}
          <Link
            className="underline hover:text-amber-200"
            href={target === "ayrshare" ? "/settings/keys" : "/settings/connections"}
          >
            {target === "ayrshare" ? "API keys" : "Accounts"} page
          </Link>
          .
        </p>
      )}

      {err && <p className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-300">{err}</p>}

      {pub && (
        <div
          className={`rounded-xl p-3 text-sm ${pub.status === "error"
              ? "bg-rose-500/10 text-rose-300"
              : pub.status === "done"
                ? "bg-emerald-500/10 text-emerald-300"
                : "bg-white/5 text-zinc-300"
            }`}
        >
          {pub.status === "done" ? "✓ " : pub.status === "error" ? "✗ " : "⏳ Uploading… "}
          {pub.error ?? pub.note}
          {pub.url && (
            <>
              {" "}
              <a className="underline" href={pub.url} target="_blank" rel="noreferrer">
                Open
              </a>
            </>
          )}
        </div>
      )}

      <button className="btn-primary w-full" disabled={busy || !connected} onClick={go}>
        {busy ? "Publishing…" : `Publish to ${TARGETS[target].label}`}
      </button>
    </div>
  );
}
