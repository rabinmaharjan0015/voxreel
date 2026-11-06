"use client";
import { useState } from "react";
import Link from "next/link";
import { authSignup } from "@/lib/api";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      await authSignup(email);
      setSent(true);
    } catch (x) {
      setErr((x as Error).message);
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <div className="mx-auto max-w-sm space-y-6 pt-16 text-center">
        <div className="glass p-8 animate-fade-up">
          <p className="text-4xl">📧</p>
          <h1 className="mt-4 font-display text-2xl font-bold">Check your email</h1>
          <p className="mt-3 text-sm text-zinc-400">
            We sent a verification link to <b className="text-zinc-200">{email}</b>. Click it to
            confirm your email and set your password.
          </p>
          <p className="mt-4 text-xs text-zinc-600">
            Using the console mail provider? The link is printed in the backend terminal.
          </p>
        </div>
        <p className="text-sm text-zinc-400">
          Already verified?{" "}
          <Link href="/login" className="text-violet-300 underline">
            Log in
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-sm space-y-6 pt-16">
      <div className="text-center">
        <h1 className="font-display text-3xl font-bold">Create your account</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Enter your email — we&apos;ll send a link to verify it before you set a password.
        </p>
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
        {err && <p className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-300">{err}</p>}
        <button disabled={busy} className="btn-primary w-full">
          {busy ? "Sending…" : "Send verification link"}
        </button>
      </form>

      <p className="text-center text-sm text-zinc-400">
        Already have an account?{" "}
        <Link href="/login" className="text-violet-300 underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
