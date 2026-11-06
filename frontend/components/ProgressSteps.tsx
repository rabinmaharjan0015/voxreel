const STEPS = [
  ["script", "Writing script"],
  ["voice", "Recording voice"],
  ["visuals", "Creating visuals"],
  ["assemble", "Editing video"],
  ["captions", "Adding captions"],
  ["done", "Ready"],
] as const;

const STEP_ICONS: Record<string, string> = {
  script: "✍️", voice: "🎙️", visuals: "🎨", assemble: "🎬", captions: "💬", done: "✨",
};

export default function ProgressSteps({
  step,
  progress,
  failed,
}: {
  step: string;
  progress: number;
  failed: boolean;
}) {
  const idx = STEPS.findIndex(([k]) => k === step);
  return (
    <div>
      {/* progress bar */}
      <div className="mb-6 h-2.5 overflow-hidden rounded-full bg-white/5">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${failed ? "bg-rose-500" : "bg-brand"
            }`}
          style={{ width: `${Math.round(progress * 100)}%` }}
        />
      </div>

      {/* step list */}
      <ol className="space-y-2.5">
        {STEPS.map(([k, label], i) => {
          const done = i < idx || step === "done";
          const active = i === idx && step !== "done";
          return (
            <li
              key={k}
              className={`flex items-center gap-3 text-sm transition ${done ? "animate-fade-in" : ""}`}
            >
              <span
                className={`grid h-7 w-7 shrink-0 place-items-center rounded-full text-xs ${done
                    ? "bg-emerald-500/20 text-emerald-300"
                    : active
                      ? failed
                        ? "bg-rose-500/20 text-rose-300"
                        : "bg-violet-500/25 text-violet-200"
                      : "bg-white/5 text-zinc-600"
                  } ${active && !failed ? "animate-pulse" : ""}`}
              >
                {done ? "✓" : active ? STEP_ICONS[k] : i + 1}
              </span>
              <span className={done || active ? "text-zinc-100" : "text-zinc-600"}>
                {label}
                {active && !failed && <span className="ml-1.5 text-zinc-500">…</span>}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
