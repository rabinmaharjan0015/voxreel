"use client";
import { useToast } from "@/lib/toast";

const STYLES: Record<string, string> = {
  success: "bg-emerald-500/15 border-emerald-500/30 text-emerald-200",
  error: "bg-rose-500/15 border-rose-500/30 text-rose-200",
  info: "bg-white/10 border-line text-zinc-200",
};
const ICONS: Record<string, string> = { success: "✓", error: "✕", info: "ℹ" };

export function Toaster() {
  const { toasts, dismiss } = useToast();
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <button
          key={t.id}
          onClick={() => dismiss(t.id)}
          className={`flex items-center gap-2 rounded-xl border px-4 py-3 text-sm shadow-lg backdrop-blur-xl animate-fade-up ${STYLES[t.type]}`}
        >
          <span className="font-bold">{ICONS[t.type]}</span>
          {t.message}
        </button>
      ))}
    </div>
  );
}
