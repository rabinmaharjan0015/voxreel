"use client";
// Keys stay in this browser (localStorage) and are sent only with a job request.
const K = "voxreel_keys";
export type Keys = Record<string, string>;
export function loadKeys(): Keys {
  try { return JSON.parse(localStorage.getItem(K) ?? "{}"); } catch { return {}; }
}
export function saveKeys(keys: Keys) {
  const clean = Object.fromEntries(Object.entries(keys).filter(([, v]) => v.trim()));
  localStorage.setItem(K, JSON.stringify(clean));
}
