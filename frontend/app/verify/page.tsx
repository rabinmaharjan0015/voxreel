"use client";
import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { authVerify, authSetPassword } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type Phase = "verifying" | "verified" | "error" | "manual";

function VerifyInner() {
  const router = useRouter();
  const params = useSearchParams();
  const { login } = useAuth();
  const [phase, setPhase] = useState<Phase>("verifying");
  const [err, setErr] = useState("");
  const [email, setEmail] = useState("");
  const [setupToken, setSetupToken] = useState("");
  const [manualToken, setManualToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);

  const tokenFromUrl = params.get("token");

  // Auto-verify the token from the email link on first load.
  useEffect(() => {
    if (!tokenFromUrl) {
      setPhase("manual");
      return;
    }
    (async () => {
      try {
        const res = await authVerify(tokenFromUrl);
        setEmail(res.email);
        setSetupToken(res.setup_token);
        setPhase("verified");
      } catch (x) {
        setErr((x as Error).message);
        setPhase("error");
      }
    })();
  }, [tokenFromUrl]);

  // Manual token entry (when no ?token= in URL or the link expired).
  async function verifyManual(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr("");
    try {
      const res = await authVerify(manualToken);
      setEmail(res.email);
      setSetupToken(res.setup_token);
      setPhase("verified");
    } catch (x) {
      setErr((x as Error).message);
    }
    setBusy(false);
  }

  async function setPasswordSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password !== confirm) {
      setErr("Passwords don't match");
      return;
    }
    setBusy(true);
    setErr("");
    try {
      const res = await authSetPassword(email, setupToken, password);
      login(res.token, res.email);
      router.push("/");
    } catch (x) {
      setErr((x as Error).message);
      setBusy(false);
    }
  }

  // --- verifying (auto from URL) ---
  if (phase === "verifying") {
    return (
      <div className="mx-auto max-w-sm pt-20 text-center">
        <div className="skeleton mx-auto h-16 w-16 rounded-full" />
        <p className="mt-4 text-sm text-zinc-400">Verifying your email…</p>
      </div>
    );
  }

  // --- error (link expired/invalid) ---
  if (phase === "error") {
    return (
      <div className="mx-auto max-w-sm space-y-4 pt-16">
        <div className="glass p-6 text-center">
          <p className="text-3xl">⚠️</p>
          <h1 className="mt-3 font-display text-xl font-bold">Link expired or invalid</h1>
          <p className="mt-2 text-sm text-rose-300/80">{err}</p>
        </div>
        <form onSubmit={verifyManual} className="glass space-y-4 p-6">
          <p className="text-sm text-zinc-400">
            Enter your verification token manually, or{" "}
            <a href="/signup" className="text-violet-300 underline">
              request a new link
            </a>
            .
          </p>
          <input
            className="field"
            placeholder="Paste token"
            value={manualToken}
            onChange={(e) => setManualToken(e.target.value)}
          />
          <button className="btn-primary w-full" disabled={busy || !manualToken}>
            Verify
          </button>
        </form>
      </div>
    );
  }

  // --- manual (no token in URL) ---
  if (phase === "manual") {
    return (
      <div className="mx-auto max-w-sm space-y-4 pt-16">
        <div className="text-center">
          <h1 className="font-display text-2xl font-bold">Verify your email</h1>
          <p className="mt-2 text-sm text-zinc-400">
            Paste the verification token from your email to continue.
          </p>
        </div>
        <form onSubmit={verifyManual} className="glass space-y-4 p-6">
          <input
            className="field"
            placeholder="Verification token"
            value={manualToken}
            onChange={(e) => setManualToken(e.target.value)}
          />
          <button className="btn-primary w-full" disabled={busy || !manualToken}>
            {busy ? "Verifying…" : "Verify"}
          </button>
        </form>
        <p className="text-center text-sm text-zinc-500">
          Don&apos;t have a token?{" "}
          <a href="/signup" className="text-violet-300 underline">
            Sign up
          </a>
        </p>
      </div>
    );
  }

  // --- verified → set password ---
  return (
    <div className="mx-auto max-w-sm space-y-6 pt-16">
      <div className="text-center">
        <p className="text-4xl">✅</p>
        <h1 className="mt-3 font-display text-2xl font-bold">Email verified!</h1>
        <p className="mt-2 text-sm text-zinc-400">
          Set a password for <b className="text-zinc-200">{email}</b> to finish.
        </p>
      </div>
      <form onSubmit={setPasswordSubmit} className="glass space-y-4 p-6">
        <label className="block">
          <span className="field-label mb-1.5 block">Password</span>
          <input
            type="password"
            required
            minLength={8}
            className="field"
            placeholder="At least 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="field-label mb-1.5 block">Confirm password</span>
          <input
            type="password"
            required
            minLength={8}
            className="field"
            placeholder="Repeat password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
        </label>
        {err && <p className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-300">{err}</p>}
        <button disabled={busy || !password || password !== confirm} className="btn-primary w-full">
          {busy ? "Creating account…" : "Create account"}
        </button>
      </form>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense>
      <VerifyInner />
    </Suspense>
  );
}
