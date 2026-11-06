"use client";
import { deleteJob, useJobs } from "@/lib/api";
import type { Job } from "@/lib/types";
import Link from "next/link";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const badge: Record<Job["status"], { cls: string; label: string }> = {
  queued: { cls: "bg-zinc-500/20 text-zinc-300", label: "Queued" },
  running: { cls: "bg-violet-500/20 text-violet-200", label: "Processing" },
  done: { cls: "bg-emerald-500/15 text-emerald-300", label: "Done" },
  error: { cls: "bg-rose-500/15 text-rose-300", label: "Failed" },
};

export default function Projects() {
  const { jobs, error } = useJobs();
  const [deleting, setDeleting] = useState<string | null>(null);

  async function del(jid: string) {
    setDeleting(jid);
    try {
      await deleteJob(jid);
      window.location.reload();
    } catch {
      setDeleting(null);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-5 pt-8">
      <div className="flex items-end justify-between">
        <h1 className="font-display text-3xl font-bold">Your projects</h1>
        {jobs && jobs.length > 0 && (
          <span className="text-sm text-zinc-500">{jobs.length} video{jobs.length !== 1 ? "s" : ""}</span>
        )}
      </div>

      {error && <p className="glass p-5 text-sm text-rose-300">{error}</p>}
      {!jobs && !error && (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton h-16" />
          ))}
        </div>
      )}
      {jobs?.length === 0 && (
        <div className="glass p-10 text-center">
          <p className="text-3xl">🎬</p>
          <p className="mt-3 text-zinc-400">No videos yet.</p>
          <Link href="/" className="mt-4 inline-block text-sm text-violet-300 underline">
            Make your first one
          </Link>
        </div>
      )}
      <ul className="space-y-3">
        {jobs?.map((j) => (
          <li key={j.id} className="group glass glass-hover flex items-center justify-between gap-4 p-4">
            <Link href={`/projects/${j.id}`} className="flex min-w-0 flex-1 items-center gap-3">
              {j.thumbnail_url ? (
                <img
                  src={`${API}${j.thumbnail_url}`}
                  alt=""
                  className="h-12 w-12 shrink-0 rounded-lg object-cover"
                />
              ) : (
                <span className="grid h-12 w-12 shrink-0 place-items-center rounded-lg bg-white/5 text-lg">
                  {j.status === "done" ? "🎬" : j.status === "error" ? "⚠️" : "⏳"}
                </span>
              )}
              <div className="min-w-0">
                <p className="truncate font-medium">{j.title ?? j.topic}</p>
                <p className="text-xs text-zinc-500">
                  {j.video_type} · {new Date(j.created_at * 1000).toLocaleString()}
                </p>
              </div>
            </Link>
            <div className="flex shrink-0 items-center gap-2">
              {(j.status === "queued" || j.status === "running") && (
                <span className="h-2 w-2 animate-pulse rounded-full bg-violet-400" />
              )}
              <span
                className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${badge[j.status].cls}`}
              >
                {badge[j.status].label}
              </span>
              <button
                onClick={() => del(j.id)}
                disabled={deleting === j.id}
                className="text-zinc-600 transition hover:text-rose-400 disabled:opacity-30"
                title="Delete project"
              >
                ✕
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
