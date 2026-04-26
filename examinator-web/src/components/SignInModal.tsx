// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "@/hooks/useAuth";
import { useSignInModal } from "@/hooks/useSignInModal";

export default function SignInModal() {
  const { isOpen, redirectTo, close } = useSignInModal();
  const { user, login } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Auto-close + redirect once authenticated.
  useEffect(() => {
    if (isOpen && user) {
      close();
      if (redirectTo) router.push(redirectTo);
    }
  }, [isOpen, user, redirectTo, close, router]);

  // Lock body scroll while open + ESC to close.
  useEffect(() => {
    if (!isOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") close();
    }
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener("keydown", onKey);
    };
  }, [isOpen, close]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="signin-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-primary-dark/80 backdrop-blur-sm"
        onClick={close}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md rounded-2xl bg-surface border border-surface-lighter shadow-2xl shadow-black/50 p-8">
        {/* Close */}
        <button
          onClick={close}
          aria-label="Close sign-in"
          className="absolute top-4 right-4 w-8 h-8 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-light transition flex items-center justify-center"
        >
          ✕
        </button>

        {/* Branding */}
        <div className="flex flex-col items-center text-center">
          <div className="w-12 h-12 rounded-2xl bg-secondary flex items-center justify-center shadow-lg shadow-secondary/25 mb-4">
            <Image
              src="/examinator-icon.png"
              alt=""
              width={38}
              height={50}
              className="w-7 h-7 object-contain"
            />
          </div>
          <h2 id="signin-title" className="text-2xl font-bold tracking-tight">
            Sign in to Examinator
          </h2>
          <p className="mt-2 text-sm text-text-secondary">
            Continue with Google to upload PDFs and generate your study notes.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="mt-5 bg-error/10 border border-error/20 text-error text-sm rounded-xl px-4 py-3">
            {error}
          </div>
        )}

        {/* Google button */}
        <div className="mt-6 flex justify-center min-h-[44px]">
          {submitting ? (
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <svg className="animate-spin h-4 w-4 text-secondary" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Signing you in…
            </div>
          ) : (
            <GoogleLogin
              theme="filled_black"
              shape="pill"
              size="large"
              text="continue_with"
              onSuccess={async (cred) => {
                setError(null);
                if (!cred.credential) {
                  setError("Google did not return a credential. Please try again.");
                  return;
                }
                try {
                  setSubmitting(true);
                  await login(cred.credential);
                } catch (e: unknown) {
                  setError(e instanceof Error ? e.message : "Sign-in failed.");
                } finally {
                  setSubmitting(false);
                }
              }}
              onError={() => setError("Google sign-in was cancelled or failed.")}
            />
          )}
        </div>

        <p className="mt-6 text-center text-xs text-text-muted">
          By continuing you agree to our terms. We never post to your account.
        </p>
      </div>
    </div>
  );
}

