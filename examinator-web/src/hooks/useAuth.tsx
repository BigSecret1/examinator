// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import type { ReactNode } from "react";
import type { User } from "@/types";
import {
  clearAuthStorage,
  getAccessToken,
  getCurrentUser,
  googleLogin,
  setTokens,
} from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (credential: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const USER_KEY = "user";

function readCachedUser(): User | null {
  if (typeof window === "undefined") return null;
  const stored = localStorage.getItem(USER_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored) as User;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Hydrate from cache + validate token via /auth/me/.
  useEffect(() => {
    let cancelled = false;
    const cached = readCachedUser();
    if (cached) setUser(cached);

    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }

    getCurrentUser()
      .then((fresh) => {
        if (cancelled) return;
        setUser(fresh);
        localStorage.setItem(USER_KEY, JSON.stringify(fresh));
      })
      .catch(() => {
        // Token couldn't be refreshed → user is logged out.
        if (cancelled) return;
        clearAuthStorage();
        setUser(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // React to global logout events fired by the API layer when refresh fails.
  useEffect(() => {
    function handleLogout() {
      setUser(null);
    }
    window.addEventListener("auth:logout", handleLogout);
    return () => window.removeEventListener("auth:logout", handleLogout);
  }, []);

  const login = useCallback(async (credential: string) => {
    const data = await googleLogin(credential);
    setTokens(data.access, data.refresh);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    setUser(data.user);
  }, []);

  const logout = useCallback(() => {
    clearAuthStorage();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

