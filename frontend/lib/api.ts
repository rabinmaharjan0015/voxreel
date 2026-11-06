"use client";
import { useEffect, useState } from "react";
import { getClientId } from "./client";
import type { Catalog, Connections, Job, Publication } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ---- catalog ----
export async function getCatalog(): Promise<Catalog> {
  const r = await fetch(`${API}/api/catalog`);
  if (!r.ok) throw new Error("Could not load catalog");
  return r.json();
}
export function useCatalog() {
  const [data, setData] = useState<Catalog | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { getCatalog().then(setData).catch((e) => setError(e.message)); }, []);
  return { data, error };
}

// ---- jobs ----
export async function createJob(body: unknown): Promise<{ id: string }> {
  const r = await fetch(`${API}/api/jobs`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Client-Id": getClientId() }, body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail ?? "Could not start job");
  return r.json();
}
export async function getJob(id: string): Promise<Job> {
  const r = await fetch(`${API}/api/jobs/${id}`, { headers: { "X-Client-Id": getClientId() } });
  if (!r.ok) throw new Error("Job not found");
  return r.json();
}
export async function listJobs(): Promise<Job[]> {
  const r = await fetch(`${API}/api/jobs`, { headers: { "X-Client-Id": getClientId() } });
  if (!r.ok) throw new Error("Could not load projects");
  return r.json();
}
export async function deleteJob(id: string): Promise<void> {
  const r = await fetch(`${API}/api/jobs/${id}`, { method: "DELETE", headers: { "X-Client-Id": getClientId() } });
  if (!r.ok) throw new Error("Could not delete project");
}

/** Hook that polls the jobs list — live status updates on the projects page. */
export function useJobs(pollMs = 3000) {
  const [jobs, setJobs] = useState<Job[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let stop = false;
    const tick = async () => {
      try {
        const list = await listJobs();
        if (stop) return;
        setJobs(list);
        // keep polling while any job is queued or running
        if (list.some((j) => j.status === "queued" || j.status === "running")) {
          setTimeout(tick, pollMs);
        }
      } catch (e) {
        if (stop) return;
        setError((e as Error).message);
      }
    };
    tick();
    return () => { stop = true; };
  }, [pollMs]);
  return { jobs, error, refresh: () => { void listJobs().then(setJobs); } };
}

// ---- publishing ----
const hdr = () => ({ "Content-Type": "application/json", "X-Client-Id": getClientId() });
async function ok<T>(r: Response, fallback: string): Promise<T> {
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail ?? fallback);
  return r.json();
}
export const getConnections = async () => ok<Connections>(await fetch(`${API}/api/connections`, { headers: hdr() }), "Could not load accounts");
export const startOAuth = async (p: string) => ok<{ url: string }>(await fetch(`${API}/api/oauth/${p}/start`, { headers: hdr() }), "Could not start sign-in");
export const disconnect = async (p: string) => ok<{ ok: boolean }>(await fetch(`${API}/api/connections/${p}`, { method: "DELETE", headers: hdr() }), "Could not disconnect");
export const publishJob = async (jid: string, body: unknown) =>
  ok<{ id: string }>(await fetch(`${API}/api/jobs/${jid}/publish`, { method: "POST", headers: hdr(), body: JSON.stringify(body) }), "Could not start publishing");
export const getPublication = async (id: string) => ok<Publication>(await fetch(`${API}/api/publications/${id}`, { headers: hdr() }), "Not found");
