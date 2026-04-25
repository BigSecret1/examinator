// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Dashboard from "@/components/Dashboard";
import Landing from "@/components/Landing";
import { useAuth } from "@/hooks/useAuth";

export default function RootPage() {
  const { user, loading } = useAuth();

  // While we don't yet know the auth state (no cached user, /me/ in flight),
  // render nothing to avoid a brief landing → dashboard flash.
  if (loading && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <svg className="animate-spin h-8 w-8 text-secondary" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    );
  }

  return user ? <Dashboard /> : <Landing />;
}

