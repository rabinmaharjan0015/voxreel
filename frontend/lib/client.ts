"use client";
// Anonymous per-browser id: scopes your project history and rate limit. Not a login.
export function getClientId(): string {
  let id = localStorage.getItem("voxreel_client");
  if (!id) { id = crypto.randomUUID(); localStorage.setItem("voxreel_client", id); }
  return id;
}
