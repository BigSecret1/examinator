// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import { useState } from "react";
import { AppFooter, AppHeader } from "@/components/AppShell";
import AuthGuard from "@/components/AuthGuard";
import { submitFeedback } from "@/lib/api";

export default function Page() {
  return (
    <AuthGuard>
      <FeedbackPage />
    </AuthGuard>
  );
}

function FeedbackPage() {
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!message.trim()) return;
    setStatus("loading");
    setError(null);
    try {
      await submitFeedback(message.trim());
      setStatus("success");
      setMessage("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-primary text-text-primary">
      <AppHeader />

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-16 flex flex-col gap-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
            Feedback
          </p>
          <h1 className="mt-2 text-3xl sm:text-4xl font-bold tracking-tight">
            Tell us what you think.
          </h1>
          <p className="mt-3 text-text-secondary">
            Got a bug, idea, or just want to say hi? We read every message.
          </p>
        </div>

        {status === "success" ? (
          <div className="rounded-2xl bg-success/10 border border-success/30 px-6 py-8 text-center space-y-3">
            <p className="text-2xl">🎉</p>
            <p className="font-semibold text-text-primary">Thanks for your feedback!</p>
            <p className="text-sm text-text-secondary">We appreciate you taking the time.</p>
            <button
              onClick={() => setStatus("idle")}
              className="mt-2 text-sm text-secondary hover:text-secondary-light underline-offset-2 hover:underline"
            >
              Send another
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Share your thoughts, report a bug, or suggest a feature…"
              rows={6}
              className="w-full rounded-xl bg-surface border border-surface-lighter text-sm placeholder:text-text-muted px-4 py-3 focus:outline-none focus:border-secondary/50 focus:ring-2 focus:ring-secondary/20 transition resize-none"
            />

            {status === "error" && error && (
              <p className="text-sm text-error">{error}</p>
            )}

            <button
              type="submit"
              disabled={status === "loading" || !message.trim()}
              className="px-6 py-2.5 rounded-xl bg-secondary hover:bg-secondary-light disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold shadow-lg shadow-secondary/25 transition"
            >
              {status === "loading" ? "Sending…" : "Send feedback"}
            </button>
          </form>
        )}
      </main>

      <AppFooter />
    </div>
  );
}
