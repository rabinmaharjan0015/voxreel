"use client";
import { useAuth } from "@/lib/auth";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Create" },
  { href: "/projects", label: "Projects" },
  { href: "/settings/connections", label: "Accounts" },
  { href: "/settings/keys", label: "🔑 Keys" },
];

export default function Header() {
  const path = usePathname();
  const { user, logout } = useAuth();
  const isActive = (href: string) =>
    href === "/" ? path === "/" : path.startsWith(href);

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-ink/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-3.5">
        <Link href="/" className="font-display text-xl font-bold tracking-tight transition hover:opacity-90">
          Vox<span className="bg-brand bg-clip-text text-transparent">Reel</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`rounded-lg px-3 py-1.5 transition ${isActive(l.href)
                  ? "bg-white/10 text-white"
                  : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                }`}
            >
              {l.label}
            </Link>
          ))}
          {user ? (
            <div className="ml-2 flex items-center gap-2">
              <span className="hidden max-w-[140px] truncate text-xs text-zinc-400 sm:inline">
                {user.email}
              </span>
              <button
                onClick={logout}
                className="rounded-lg border border-line px-3 py-1.5 text-zinc-400 transition hover:border-white/15 hover:text-zinc-200"
              >
                Log out
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="ml-2 rounded-lg bg-brand px-4 py-1.5 font-semibold text-white transition hover:brightness-110"
            >
              Log in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
