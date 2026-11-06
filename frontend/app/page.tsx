"use client";
import TypeCard from "@/components/TypeCard";
import { useCatalog } from "@/lib/api";

const STEPS = [
  { n: 1, emoji: "✍️", title: "Describe your idea", desc: "Pick a video type and type your topic. Set the tone, language, and length." },
  { n: 2, emoji: "🎙️", title: "We write & narrate", desc: "AI writes a natural script and records a human-sounding voice-over with your chosen engine." },
  { n: 3, emoji: "🎬", title: "Get a finished video", desc: "Visuals, Ken Burns motion, and captions are burned in automatically. Download or publish." },
];

export default function Home() {
  const { data, error } = useCatalog();
  return (
    <>
      {/* hero */}
      <section className="pt-14 pb-16 text-center sm:pt-24">
        <p className="mx-auto mb-5 w-fit rounded-full border border-line bg-white/5 px-4 py-1.5 text-xs text-zinc-300 animate-fade-in">
          Human-sounding voice · Free options · Your keys, your control
        </p>
        <h1 className="mx-auto max-w-3xl font-display text-4xl font-bold leading-[1.05] tracking-tight sm:text-6xl animate-fade-up">
          Turn an idea into a video that{" "}
          <span className="bg-brand bg-clip-text text-transparent">sounds like a person</span>
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-zinc-400 animate-fade-up [animation-delay:0.1s]">
          Pick a video type, type your topic, and get a script, natural voice-over, visuals, and
          captions in one go — then repurpose it for TikTok, YouTube, and more.
        </p>
      </section>

      {/* video type grid */}
      <h2 className="mb-5 font-display text-xl font-semibold">What do you want to make?</h2>
      {error && (
        <div className="glass p-5 text-sm text-rose-300">
          {error}. Start the backend on port 8000.
        </div>
      )}
      {!data && !error && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton h-44" />
          ))}
        </div>
      )}
      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.video_types.map((t) => (
            <TypeCard key={t.id} t={t} />
          ))}
        </div>
      )}

      {/* how it works */}
      <section className="mt-20">
        <h2 className="mb-2 text-center font-display text-xl font-semibold">How it works</h2>
        <p className="mb-8 text-center text-sm text-zinc-500">Three steps from idea to finished video.</p>
        <div className="grid gap-4 sm:grid-cols-3">
          {STEPS.map((s) => (
            <div key={s.n} className="glass p-6">
              <div className="mb-3 flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-white/5 text-xl ring-1 ring-line">
                  {s.emoji}
                </span>
                <span className="font-display text-2xl font-bold text-white/20">{s.n}</span>
              </div>
              <h3 className="font-display text-base font-semibold">{s.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-zinc-400">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
