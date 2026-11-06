import type { Provider } from "@/lib/types";

type Props = {
  label: string;
  options: Provider[];
  value: string;
  onChange: (v: string) => void;
  hasKey: (id: string) => boolean;
};

export default function ProviderPicker({ label, options, value, onChange, hasKey }: Props) {
  return (
    <div>
      <p className="field-label mb-2.5">{label}</p>
      <div className="grid gap-2 sm:grid-cols-2">
        {options.map((p) => {
          const missing = p.needs_key && !hasKey(p.id);
          const active = value === p.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onChange(p.id)}
              className={`group relative rounded-xl border p-3 text-left transition ${active
                  ? "border-violet-400/70 bg-violet-500/10"
                  : "border-line bg-white/[0.03] hover:bg-white/[0.06] hover:border-white/15"
                }`}
            >
              {active && (
                <span className="absolute right-3 top-3 grid h-5 w-5 place-items-center rounded-full bg-violet-500 text-[10px] text-white">
                  ✓
                </span>
              )}
              <div className="flex items-center gap-2 pr-7">
                <span className="text-sm font-medium">{p.name}</span>
              </div>
              <div className="mt-1.5 flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${p.free ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"
                    }`}
                >
                  {p.free ? "FREE" : "BYOK"}
                </span>
                {missing && (
                  <span className="text-xs text-rose-300/80">Key needed</span>
                )}
              </div>
              {p.note && <p className="mt-1 text-xs text-zinc-500">{p.note}</p>}
            </button>
          );
        })}
      </div>
    </div>
  );
}
