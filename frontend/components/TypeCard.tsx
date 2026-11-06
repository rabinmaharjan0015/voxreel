import type { VideoType } from "@/lib/types";
import Link from "next/link";

export default function TypeCard({ t }: { t: VideoType }) {
  return (
    <Link
      href={`/create/${t.id}`}
      className="glass glass-hover group relative flex flex-col p-6 transition hover:-translate-y-1"
    >
      <div className="mb-4 flex items-center justify-between">
        <span className="grid h-12 w-12 place-items-center rounded-xl bg-white/5 text-2xl ring-1 ring-line transition group-hover:scale-110 group-hover:bg-white/10">
          {t.emoji}
        </span>
        <span className="rounded-full border border-line px-2.5 py-1 text-[11px] text-zinc-400">
          {t.aspect}
        </span>
      </div>
      <h3 className="font-display text-lg font-semibold">{t.name}</h3>
      <p className="mt-1 flex-1 text-sm leading-relaxed text-zinc-400">{t.blurb}</p>
      <span className="mt-4 inline-block text-sm font-medium text-violet-300 transition group-hover:translate-x-1">
        Start →
      </span>
    </Link>
  );
}
