// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AppFooter, AppHeader } from "@/components/AppShell";
import AuthGuard from "@/components/AuthGuard";
import UploadModal from "@/components/UploadModal";
import { getNotes, type NoteListItem } from "@/lib/api";

export default function Page() {
  return (
    <AuthGuard>
      <Library />
    </AuthGuard>
  );
}

function Library() {
  const [notes, setNotes] = useState<NoteListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [uploadOpen, setUploadOpen] = useState(false);

  const refresh = useCallback(() => {
    setError(null);
    getNotes()
      .then(setNotes)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load notes."),
      );
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const filtered = useMemo(() => {
    if (!notes) return null;
    const q = query.trim().toLowerCase();
    if (!q) return notes;
    return notes.filter(
      (n) =>
        n.title.toLowerCase().includes(q) ||
        n.source_filename.toLowerCase().includes(q) ||
        n.summary.toLowerCase().includes(q),
    );
  }, [notes, query]);

  const totals = useMemo(() => {
    if (!notes) return null;
    const completed = notes.filter((n) => n.status === "completed").length;
    const inFlight = notes.filter(
      (n) => n.status === "pending" || n.status === "processing",
    ).length;
    const pages = notes.reduce((sum, n) => sum + (n.page_count || 0), 0);
    return { count: notes.length, completed, inFlight, pages };
  }, [notes]);

  return (
    <div className="min-h-screen flex flex-col bg-primary text-text-primary">
      <AppHeader />

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-10 space-y-8">
        {/* Heading + new note */}
        <section className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
              Your library
            </p>
            <h1 className="mt-2 text-3xl sm:text-4xl font-bold tracking-tight">
              All your notes, in one place.
            </h1>
            {totals && (
              <p className="mt-2 text-sm text-text-secondary">
                {totals.count} {totals.count === 1 ? "note" : "notes"}
                {totals.inFlight > 0 && (
                  <>
                    {" · "}
                    <span className="text-warning">{totals.inFlight} in progress</span>
                  </>
                )}
                {totals.pages > 0 && <> · {totals.pages} pages processed</>}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={() => setUploadOpen(true)}
            className="px-5 py-2.5 rounded-xl bg-secondary hover:bg-secondary-light text-white text-sm font-semibold shadow-lg shadow-secondary/25 transition whitespace-nowrap self-start sm:self-auto"
          >
            + New note
          </button>
        </section>

        {/* Search */}
        {notes && notes.length > 0 && (
          <div className="relative w-full">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by title, filename, or summary…"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-surface border border-surface-lighter text-sm placeholder:text-text-muted focus:outline-none focus:border-secondary/50 focus:ring-2 focus:ring-secondary/20 transition"
            />
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-4.35-4.35m0 0A7 7 0 1 0 6.35 6.35a7 7 0 0 0 10.3 10.3Z" />
            </svg>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-xl bg-error/10 border border-error/20 text-error text-sm px-5 py-4 flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={refresh}
              className="text-xs font-medium hover:underline"
            >
              Retry
            </button>
          </div>
        )}

        {/* States */}
        {notes === null && !error && <SkeletonGrid />}
        {notes && notes.length === 0 && (
          <EmptyState onUpload={() => setUploadOpen(true)} />
        )}
        {filtered && filtered.length === 0 && notes && notes.length > 0 && (
          <NoMatches onClear={() => setQuery("")} />
        )}
        {filtered && filtered.length > 0 && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((note) => (
              <NoteCard key={note.id} note={note} />
            ))}
          </div>
        )}
      </main>

      <AppFooter />

      <UploadModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={() => refresh()}
      />
    </div>
  );
}

/* ---------------- Card ---------------- */
function NoteCard({ note }: { note: NoteListItem }) {
  const isClickable = note.status === "completed";
  const cardCls =
    "group h-full rounded-2xl bg-surface border border-surface-lighter p-5 transition flex flex-col";
  const interactiveCls = isClickable
    ? "hover:border-secondary/50 hover:bg-surface-light hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/30"
    : "opacity-90";

  const inner = (
    <>
      <div className="flex items-start justify-between gap-3">
        <div className="w-10 h-10 rounded-xl bg-secondary/15 text-secondary flex items-center justify-center text-lg shrink-0">
          📄
        </div>
        <StatusBadge status={note.status} />
      </div>

      <h3 className="mt-4 font-semibold text-text-primary line-clamp-2 leading-snug">
        {note.title || note.source_filename || "Untitled note"}
      </h3>

      {note.summary && (
        <p className="mt-2 text-sm text-text-secondary line-clamp-3">
          {note.summary}
        </p>
      )}

      <div className="mt-4 pt-4 border-t border-surface-lighter/60 flex flex-wrap items-center gap-2 text-[11px] text-text-muted">
        {note.page_count > 0 && <span>{note.page_count} pages</span>}
        {note.page_count > 0 && <span aria-hidden>·</span>}
        <ModeBadge mode={note.generation_mode} />
        <span aria-hidden>·</span>
        <span>{relativeDate(note.created_at)}</span>
      </div>

      {note.source_filename && (
        <p
          className="mt-2 text-[11px] text-text-muted truncate"
          title={note.source_filename}
        >
          {note.source_filename}
        </p>
      )}
    </>
  );

  if (isClickable) {
    return (
      <Link href={`/library/${note.id}`} className={`${cardCls} ${interactiveCls}`}>
        {inner}
      </Link>
    );
  }
  return <div className={`${cardCls} ${interactiveCls}`}>{inner}</div>;
}

function StatusBadge({ status }: { status: NoteListItem["status"] }) {
  const map: Record<NoteListItem["status"], { label: string; cls: string }> = {
    completed: {
      label: "Ready",
      cls: "bg-success/15 text-success border-success/30",
    },
    processing: {
      label: "Processing",
      cls: "bg-warning/15 text-warning border-warning/30",
    },
    pending: {
      label: "Queued",
      cls: "bg-secondary/15 text-secondary border-secondary/30",
    },
    failed: {
      label: "Failed",
      cls: "bg-error/15 text-error border-error/30",
    },
  };
  const { label, cls } = map[status];
  const dotCls =
    status === "processing" ? "bg-warning animate-pulse" : "bg-current";
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${cls}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotCls}`} />
      {label}
    </span>
  );
}

function ModeBadge({ mode }: { mode: NoteListItem["generation_mode"] }) {
  const isVision = mode === "vision";
  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-medium border ${
        isVision
          ? "bg-accent/10 text-accent border-accent/30"
          : "bg-surface-light text-text-secondary border-surface-lighter"
      }`}
    >
      {isVision ? "👁 vision" : "📝 text"}
    </span>
  );
}

/* ---------------- Empty / no-match / skeleton ---------------- */
function EmptyState({ onUpload }: { onUpload: () => void }) {
  return (
    <div className="rounded-2xl border border-dashed border-surface-lighter bg-surface/40 p-12 text-center">
      <div className="mx-auto w-14 h-14 rounded-2xl bg-secondary/15 text-secondary flex items-center justify-center text-2xl">
        📚
      </div>
      <h3 className="mt-5 text-lg font-semibold">Your library is empty.</h3>
      <p className="mt-2 text-sm text-text-secondary max-w-md mx-auto">
        Upload your first PDF and Examinator will turn it into structured notes,
        key terms, and flashcards.
      </p>
      <button
        type="button"
        onClick={onUpload}
        className="mt-6 px-5 py-2.5 rounded-xl bg-secondary hover:bg-secondary-light text-white text-sm font-semibold shadow-lg shadow-secondary/25 transition"
      >
        Upload your first PDF →
      </button>
    </div>
  );
}

function NoMatches({ onClear }: { onClear: () => void }) {
  return (
    <div className="rounded-2xl border border-surface-lighter bg-surface/40 p-10 text-center">
      <p className="text-sm text-text-secondary">No notes match your search.</p>
      <button
        onClick={onClear}
        className="mt-3 text-sm text-secondary hover:text-secondary-light"
      >
        Clear search
      </button>
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="h-44 rounded-2xl bg-surface border border-surface-lighter animate-pulse"
        />
      ))}
    </div>
  );
}

/* ---------------- helpers ---------------- */
function relativeDate(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  const diff = Date.now() - then;
  const sec = Math.round(diff / 1000);
  if (sec < 60) return "just now";
  const min = Math.round(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const day = Math.round(hr / 24);
  if (day < 30) return `${day}d ago`;
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

