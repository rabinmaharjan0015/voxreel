"use client";
import { authOAuthStart, authSignup } from "@/lib/api";
import { useToast } from "@/lib/toast";
import Link from "next/link";
import { useState } from "react";

export default function SignupPage() {
  const toast = useToast();
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [oauthBusy, setOauthBusy] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await authSignup(email);
      setSent(true);
      toast.success("Verification link sent!");
    } catch (x) {
      toast.error((x as Error).message);
      setBusy(false);
    }
  }

  async function oauth(provider: string) {
    setOauthBusy(provider);
    try {
      const { url } = await authOAuthStart(provider);
      window.location.href = url;
    } catch (x) {
      toast.error((x as Error).message);
      setOauthBusy(null);
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
          <Link href="/login" className="text-violet-300 underline">Log in</Link>
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

      {/* OAuth buttons */}
      <div className="grid grid-cols-2 gap-3">
        <button onClick={() => oauth("google")} disabled={!!oauthBusy} className="btn-ghost flex items-center justify-center gap-2">
          {oauthBusy === "google" ? "…" : (
            <>
              <svg className="h-4 w-4" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" /><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" /><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" /><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" /></svg>
              Google
            </>
          )}
        </button>
        <button onClick={() => oauth("github")} disabled={!!oauthBusy} className="btn-ghost flex items-center justify-center gap-2">
          {oauthBusy === "github" ? "…" : (
            <>
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.34-.255-4.815-1.17-4.815-5.205 0-1.155.405-2.1 1.065-2.85-.105-.255-.465-1.35.105-2.805 0 0 .87-.27 2.85 1.095a9.845 9.845 0 012.55-.345c.87 0 1.74.12 2.55.345 1.98-1.365 2.85-1.095 2.85-1.095.57 1.455.21 2.55.105 2.805.66.75 1.065 1.695 1.065 2.85 0 4.05-2.475 4.95-4.815 5.205.375.33.705.945.705 1.905 0 1.38-.015 2.49-.015 2.835 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" /></svg>
              GitHub
            </>
          )}
        </button>
      </div>

      <div className="flex items-center gap-3 text-xs text-zinc-600">
        <div className="h-px flex-1 bg-line" /> OR <div className="h-px flex-1 bg-line" />
      </div>

      <form onSubmit={submit} className="glass space-y-4 p-6">
        <label className="block">
          <span className="field-label mb-1.5 block">Email</span>
          <input type="email" required className="field" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <button disabled={busy} className="btn-primary w-full">{busy ? "Sending…" : "Send verification link"}</button>
      </form>

      <p className="text-center text-sm text-zinc-400">
        Already have an account?{" "}
        <Link href="/login" className="text-violet-300 underline">Log in</Link>
      </p>
    </div>
  );
}
