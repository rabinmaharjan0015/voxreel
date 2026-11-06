"use client";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

const TOKEN_COOKIE = "voxreel_token";
const EMAIL_COOKIE = "voxreel_email";
const MAX_AGE = 30 * 86400; // 30 days, matching JWT_TTL

function setCookie(name: string, value: string) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${MAX_AGE}; SameSite=Lax`;
}

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const m = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return m ? decodeURIComponent(m[1]) : null;
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; path=/; max-age=0`;
}

type User = { email: string } | null;
type AuthContextType = {
  user: User;
  loading: boolean;
  login: (token: string, email: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => { },
  logout: () => { },
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = getCookie(TOKEN_COOKIE);
    const e = getCookie(EMAIL_COOKIE);
    if (t && e) setUser({ email: e });
    setLoading(false);
  }, []);

  const login = (token: string, email: string) => {
    setCookie(TOKEN_COOKIE, token);
    setCookie(EMAIL_COOKIE, email);
    setUser({ email });
  };

  const logout = () => {
    deleteCookie(TOKEN_COOKIE);
    deleteCookie(EMAIL_COOKIE);
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

/** Returns auth headers for fetch calls — reads from cookie. */
export function authHeaders(): Record<string, string> {
  const t = getCookie(TOKEN_COOKIE);
  return t ? { Authorization: `Bearer ${t}` } : {};
}
