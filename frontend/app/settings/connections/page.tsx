"use client";
import { disconnect, getConnections, startOAuth } from "@/lib/api";
import type { Connections } from "@/lib/types";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

const META = {
  youtube: {
    name: "YouTube",
    emoji: "▶️",
    note: "Uploads until your Google Cloud project passes YouTube's API audit are forced to private.",
  },
  tiktok: {
    name: "TikTok",
    emoji: "🎵",
    note: "Until your TikTok app passes audit, Direct Post is private-only. 'Send to inbox' works now: you tap Publish in the TikTok app.",
  },
} as const;

function Inner() {
  const q = useSearchParams();
  const [c, setC] = useState<Connections | null>(null);
  const [err, setErr] = useState<string | null>(
    q.get("error") ? `Couldn't connect ${q.get("error")}. Try again.` : null,
  );
  const load = () => getConnections().then(setC).catch((e) => setErr(e.message));
  useEffect(() => {
    load();
  }, []);

  async function connect(p: string) {
    try {
      const { url } = await startOAuth(p);
      window.location.href = url;
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6 pt-8">
      <div>
        <h1 className="font-display text-3xl font-bold">Connected accounts</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Connect once, then publish finished videos from the project page. Access tokens are stored
          encrypted on the server and can be removed any time.
        </p>
      </div>

      {q.get("connected") && (
        <p className="rounded-xl bg-emerald-500/10 p-3 text-sm text-emerald-300">
          Connected {q.get("connected")} ✓
        </p>
      )}
      {err && <p className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-300">{err}</p>}

      <div className="space-y-4">
        {(Object.keys(META) as (keyof typeof META)[]).map((p) => {
          const s = c?.[p];
          const m = META[p];
          return (
            <div key={p} className="glass flex items-start justify-between gap-4 p-5">
              <div>
                <p className="font-display text-lg font-semibold">
                  {m.emoji} {m.name}
                </p>
                <p className="mt-1 text-xs text-zinc-500">{m.note}</p>
                {s && !s.configured && (
                  <p className="mt-2 text-xs text-amber-300">
                    Not configured on this server. Add your developer-app credentials to the backend
                    .env.
                  </p>
                )}
                {s?.connected && (
                  <p className="mt-2 text-xs text-emerald-300">● Connected</p>
                )}
              </div>
              {s?.connected ? (
                <button className="btn-ghost shrink-0" onClick={() => disconnect(p).then(load)}>
                  Disconnect
                </button>
              ) : (
                <button
                  className="btn-primary shrink-0"
                  disabled={!s?.configured}
                  onClick={() => connect(p)}
                >
                  Connect
                </button>
              )}
            </div>
          );
        })}
      </div>

      <p className="text-xs text-zinc-500">
        No developer apps? Skip this and use a posting service: add its key on the API keys page and
        choose it when publishing.
      </p>
    </div>
  );
}

export default function Connections() {
  return (
    <Suspense>
      <Inner />
    </Suspense>
  );
}
