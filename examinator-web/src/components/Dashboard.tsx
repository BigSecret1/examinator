// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import UploadModal from "@/components/UploadModal";
import UserAvatar from "@/components/UserAvatar";
import { useAuth } from "@/hooks/useAuth";

export default function Dashboard() {
  const { user } = useAuth();
  const firstName = user?.first_name?.trim() || "there";
  const [uploadOpen, setUploadOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-primary text-text-primary">
      <AppHeader />

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-10 space-y-12">
        <section>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
            Your library
          </p>
          <h1 className="mt-2 text-3xl sm:text-4xl font-bold tracking-tight">
            Welcome back, {firstName}.
          </h1>
          <p className="mt-2 text-text-secondary max-w-xl">
            Upload a PDF to generate structured notes, key terms, and flashcards.
          </p>
        </section>

        <UploadCard onOpen={() => setUploadOpen(true)} />
      </main>

      <AppFooter />

      <UploadModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={() => {
          // Library wiring will refresh here in a follow-up.
        }}
      />
    </div>
  );
}

/* ---------------- Header ---------------- */
function AppHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-surface-light/30 bg-primary/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-secondary flex items-center justify-center shadow-lg shadow-secondary/25">
            <Image
              src="/examinator-icon.png"
              alt=""
              width={38}
              height={50}
              className="w-6 h-6 object-contain"
              priority
            />
          </div>
          <span className="text-xl font-bold tracking-tight">Examinator</span>
          <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-secondary/20 text-secondary border border-secondary/30">
            Beta
          </span>
        </Link>

        <UserAvatar />
      </div>
    </header>
  );
}

/* ---------------- Upload CTA ---------------- */
function UploadCard({ onOpen }: { onOpen: () => void }) {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-secondary/30 bg-gradient-to-br from-secondary/15 via-surface to-accent/10 p-8 sm:p-10">
      <div className="grid lg:grid-cols-[1fr_auto] items-center gap-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
            New note
          </p>
          <h2 className="mt-2 text-2xl sm:text-3xl font-bold tracking-tight">
            Upload a PDF and get notes in minutes.
          </h2>
          <p className="mt-2 text-text-secondary max-w-xl text-sm">
            Drop in a textbook chapter, lecture slides, or paper. Examinator builds
            sections, key terms, and flashcards for you. Scanned PDFs supported.
          </p>
        </div>
        <button
          type="button"
          onClick={onOpen}
          className="px-6 py-3.5 rounded-xl bg-secondary hover:bg-secondary-light text-white font-semibold shadow-lg shadow-secondary/30 transition whitespace-nowrap"
        >
          Upload PDF →
        </button>
      </div>
    </section>
  );
}

/* ---------------- Footer ---------------- */
function AppFooter() {
  return (
    <footer className="border-t border-surface-light/30 py-8 text-xs text-text-muted">
      <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <span>Examinator © {new Date().getFullYear()} · Apache 2.0</span>
        <span>Made for learners who want to remember.</span>
      </div>
    </footer>
  );
}

