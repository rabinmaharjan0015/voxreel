"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authLogin } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      const res = await authLogin(email, password);
      login(res.token, res.email);
      router.push("/");
    } catch (x) {
      setErr((x as Error).message);
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm space-y-6 pt-16">
      <div className="text-center">
        <h1 className="font-display text-3xl font-bold">Welcome back</h1>
        <p className="mt-2 text-sm text-zinc-400">Log in to your VoxReel account.</p>
      </div>

      <form onSubmit={submit} className="glass space-y-4 p-6">
        <label className="block">
          <span className="field-label mb-1.5 block">Email</span>
          <input
            type="email"
            required
            className="field"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="field-label mb-1.5 block">Password</span>
          <input
            type="password"
            required
            className="field"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {err && <p className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-300">{err}</p>}
        <button disabled={busy} className="btn-primary w-full">
          {busy ? "Logging in…" : "Log in"}
        </button>
      </form>

      <p className="text-center text-sm text-zinc-400">
        No account yet?{" "}
        <Link href="/signup" className="text-violet-300 underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
