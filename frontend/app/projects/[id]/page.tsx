"use client";
import ProgressSteps from "@/components/ProgressSteps";
import PublishPanel from "@/components/PublishPanel";
import { getJob } from "@/lib/api";
import type { Job } from "@/lib/types";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ProjectPage() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);

  useEffect(() => {
    let stop = false;
    const tick = async () => {
      try {
        const j = await getJob(id);
        if (stop) return;
        setJob(j);
        if (j.status === "done" || j.status === "error") return;
      } catch {
        /* retry */
      }
      setTimeout(tick, 1500);
    };
    tick();
    return () => {
      stop = true;
    };
  }, [id]);

  if (!job)
    return (
      <div className="mx-auto mt-10 max-w-2xl">
        <div className="skeleton h-72" />
      </div>
    );

  const url = job.video_url ? `${API}${job.video_url}` : null;

  return (
    <div className="mx-auto max-w-3xl space-y-6 pt-8">
      <Link href="/projects" className="inline-block text-sm text-zinc-500 transition hover:text-zinc-300">
        ← All projects
      </Link>

      <h1 className="font-display text-3xl font-bold">{job.title ?? "Creating your video…"}</h1>

      {url ? (
        <div className="space-y-4 animate-fade-up">
          <video
            src={url}
            controls
            className="mx-auto max-h-[70vh] w-full rounded-2xl border border-line bg-black shadow-2xl shadow-black/50"
          />
          <div className="flex gap-3">
            <a href={url} download className="btn-primary flex-1">
              ↓ Download MP4
            </a>
            <Link href="/" className="btn-ghost flex-1">
              Make another
            </Link>
          </div>
          <PublishPanel job={job} />
        </div>
      ) : (
        <div className="glass p-6 animate-fade-up">
          {job.status === "queued" && (
            <p className="mb-4 text-sm text-zinc-400">
              ⏳ In the queue — a worker will pick this up shortly.
            </p>
          )}
          <ProgressSteps step={job.step} progress={job.progress} failed={job.status === "error"} />
          {job.error && (
            <div className="mt-5 rounded-xl bg-rose-500/10 p-4">
              <p className="text-sm font-medium text-rose-300">Something went wrong</p>
              <p className="mt-1 text-sm text-rose-300/80">{job.error}</p>
            </div>
          )}
          {job.status === "error" && (
            <Link href="/" className="mt-4 inline-block text-sm text-violet-300 underline">
              Try again with different settings
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
