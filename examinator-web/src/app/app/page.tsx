// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Image from "next/image";
import Link from "next/link";
import AuthGuard from "@/components/AuthGuard";
import UserAvatar from "@/components/UserAvatar";
import { useAuth } from "@/hooks/useAuth";

export default function Page() {
  return (
    <AuthGuard>
      <Dashboard />
    </AuthGuard>
  );
}

function Dashboard() {
  const { user } = useAuth();
  const firstName = user?.first_name?.trim() || "there";

  return (
    <div className="min-h-screen flex flex-col bg-primary text-text-primary">
      <AppHeader />

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-10 space-y-12">
        {/* Welcome */}
        <section>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
            Your library
          </p>
          <h1 className="mt-2 text-3xl sm:text-4xl font-bold tracking-tight">
            Welcome back, {firstName}.
          </h1>
          <p className="mt-2 text-text-secondary max-w-xl">
            Upload a PDF to generate structured notes, key terms, and flashcards —
            or jump back into practice.
          </p>
        </section>

        {/* Primary upload CTA */}
        <UploadCard />

        {/* Notes library (empty state for now) */}
        <NotesLibraryEmpty />

        {/* Quick links */}
        <QuickLinks />
      </main>

      <AppFooter />
    </div>
  );
}

/* ---------------- Header ---------------- */
function AppHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-surface-light/30 bg-primary/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/app" className="flex items-center gap-3">
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

        <nav className="hidden md:flex items-center gap-6 text-sm text-text-secondary">
          <Link href="/app" className="text-text-primary font-medium">
            Home
          </Link>
          <Link href="/practice" className="hover:text-text-primary transition">
            Practice
          </Link>
          <Link href="/practice/exams" className="hover:text-text-primary transition">
            Exams
          </Link>
        </nav>

        <UserAvatar />
      </div>
    </header>
  );
}

/* ---------------- Upload CTA ---------------- */
function UploadCard() {
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
          onClick={() =>
            alert(
              "PDF upload is coming next. Stay tuned — your library will populate here.",
            )
          }
          className="px-6 py-3.5 rounded-xl bg-secondary hover:bg-secondary-light text-white font-semibold shadow-lg shadow-secondary/30 transition whitespace-nowrap"
        >
          Upload PDF →
        </button>
      </div>
    </section>
  );
}

/* ---------------- Notes library (empty state) ---------------- */
function NotesLibraryEmpty() {
  return (
    <section>
      <div className="flex items-end justify-between mb-4">
        <div>
          <h2 className="text-xl font-semibold">Your notes</h2>
          <p className="text-sm text-text-muted">All the notes you generate will land here.</p>
        </div>
      </div>

      <div className="rounded-2xl border border-dashed border-surface-lighter bg-surface/40 p-10 text-center">
        <div className="mx-auto w-12 h-12 rounded-2xl bg-secondary/15 text-secondary flex items-center justify-center text-2xl">
          📄
        </div>
        <h3 className="mt-4 font-semibold">No notes yet</h3>
        <p className="mt-1 text-sm text-text-secondary max-w-md mx-auto">
          Upload your first PDF to start building your personal study library.
        </p>
      </div>
    </section>
  );
}

/* ---------------- Quick links ---------------- */
function QuickLinks() {
  const links = [
    {
      href: "/practice",
      icon: "🎯",
      title: "Practice by subject",
      body: "Drill curated questions across topics and difficulty levels.",
    },
    {
      href: "/practice/exams",
      icon: "📝",
      title: "Practice by exam",
      body: "Prepare in exam context with subject-wise question sets.",
    },
  ];
  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Keep practising</h2>
      <div className="grid sm:grid-cols-2 gap-4">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className="group rounded-2xl bg-surface border border-surface-lighter p-6 hover:border-secondary/50 hover:bg-surface-light transition flex items-start gap-4"
          >
            <div className="w-11 h-11 rounded-xl bg-secondary/15 text-secondary-light flex items-center justify-center text-xl shrink-0">
              {l.icon}
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">{l.title}</h3>
              <p className="mt-1 text-sm text-text-secondary">{l.body}</p>
            </div>
            <span className="text-text-muted group-hover:text-secondary transition">→</span>
          </Link>
        ))}
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

