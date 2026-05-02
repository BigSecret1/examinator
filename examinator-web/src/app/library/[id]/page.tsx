// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import remarkBreaks from "remark-breaks";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { AppFooter, AppHeader } from "@/components/AppShell";
import AuthGuard from "@/components/AuthGuard";
import {
  getNote,
  type NoteFlashcard,
  type NoteFull,
  type NoteKeyTerm,
  type NoteSection,
} from "@/lib/api";

type Tab = "notes" | "terms" | "cards";

export default function Page() {
  return (
    <AuthGuard>
      <NoteViewer />
    </AuthGuard>
  );
}

function NoteViewer() {
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const [note, setNote] = useState<NoteFull | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("notes");

  const load = useCallback(() => {
    if (!id) return;
    setError(null);
    getNote(id)
      .then(setNote)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Failed to load note."),
      );
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="min-h-screen flex flex-col bg-primary text-text-primary">
      <AppHeader />

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-10 space-y-8">
        <BackToLibrary />

        {error && (
          <div className="rounded-xl bg-error/10 border border-error/20 text-error text-sm px-5 py-4 flex items-center justify-between">
            <span>{error}</span>
            <button onClick={load} className="text-xs font-medium hover:underline">
              Retry
            </button>
          </div>
        )}

        {!note && !error && <SkeletonNote />}

        {note && (
          <>
            <NoteHero note={note} />
            <Tabs tab={tab} setTab={setTab} note={note} />

            {tab === "notes" && <NotesTab sections={note.sections} />}
            {tab === "terms" && <TermsTab terms={note.key_terms} />}
            {tab === "cards" && <CardsTab cards={note.flashcards} />}
          </>
        )}
      </main>

      <AppFooter />
    </div>
  );
}

/* ---------------- Shared bits ---------------- */
function BackToLibrary() {
  return (
    <Link
      href="/library"
      className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary transition"
    >
      ← Back to library
    </Link>
  );
}

function SkeletonNote() {
  return (
    <div className="space-y-6">
      <div className="h-10 w-2/3 rounded-lg bg-surface animate-pulse" />
      <div className="h-4 w-1/2 rounded bg-surface animate-pulse" />
      <div className="h-40 rounded-2xl bg-surface animate-pulse" />
      <div className="grid sm:grid-cols-2 gap-4">
        <div className="h-32 rounded-2xl bg-surface animate-pulse" />
        <div className="h-32 rounded-2xl bg-surface animate-pulse" />
      </div>
    </div>
  );
}

/* ---------------- Hero ---------------- */
function NoteHero({ note }: { note: NoteFull }) {
  return (
    <section className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <Badge label={note.status === "completed" ? "Ready" : note.status} kind={note.status} />
        <ModeChip mode={note.generation_mode} />
        {note.page_count > 0 && (
          <span className="text-xs text-text-muted">{note.page_count} pages</span>
        )}
        <span className="text-xs text-text-muted" aria-hidden>·</span>
        <span className="text-xs text-text-muted">
          {new Date(note.created_at).toLocaleDateString(undefined, {
            month: "short",
            day: "numeric",
            year: "numeric",
          })}
        </span>
      </div>

      <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
        {note.title || note.source_filename || "Untitled note"}
      </h1>

      {note.source_filename && (
        <p className="text-xs text-text-muted truncate" title={note.source_filename}>
          📎 {note.source_filename}
        </p>
      )}

      {note.summary && (
        <p className="text-text-secondary max-w-3xl leading-relaxed">{note.summary}</p>
      )}

      {note.learning_objectives && note.learning_objectives.length > 0 && (
        <div className="rounded-2xl border border-secondary/30 bg-secondary/5 p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
            Learning objectives
          </p>
          <ul className="mt-3 space-y-2">
            {note.learning_objectives.map((o, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-text-primary">
                <span className="mt-1 w-1.5 h-1.5 rounded-full bg-secondary shrink-0" />
                {o}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function Badge({ label, kind }: { label: string; kind: NoteFull["status"] }) {
  const cls: Record<NoteFull["status"], string> = {
    completed: "bg-success/15 text-success border-success/30",
    processing: "bg-warning/15 text-warning border-warning/30",
    pending: "bg-secondary/15 text-secondary border-secondary/30",
    failed: "bg-error/15 text-error border-error/30",
  };
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${cls[kind]}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {label[0].toUpperCase() + label.slice(1)}
    </span>
  );
}

function ModeChip({ mode }: { mode: NoteFull["generation_mode"] }) {
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

/* ---------------- Tabs ---------------- */
function Tabs({
  tab,
  setTab,
  note,
}: {
  tab: Tab;
  setTab: (t: Tab) => void;
  note: NoteFull;
}) {
  const items: { key: Tab; label: string; count: number }[] = [
    { key: "notes", label: "Notes", count: note.sections?.length ?? 0 },
    { key: "terms", label: "Key terms", count: note.key_terms?.length ?? 0 },
    { key: "cards", label: "Flashcards", count: note.flashcards?.length ?? 0 },
  ];
  return (
    <div className="border-b border-surface-light/40">
      <div className="flex gap-1">
        {items.map((it) => {
          const active = tab === it.key;
          return (
            <button
              key={it.key}
              onClick={() => setTab(it.key)}
              className={`relative px-4 py-3 text-sm font-medium transition ${
                active
                  ? "text-text-primary"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {it.label}
              <span
                className={`ml-1.5 inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-semibold ${
                  active
                    ? "bg-secondary text-white"
                    : "bg-surface-light text-text-muted"
                }`}
              >
                {it.count}
              </span>
              {active && (
                <span className="absolute left-3 right-3 -bottom-px h-[2px] bg-secondary rounded-full" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/* ---------------- Notes tab ---------------- */
function NotesTab({ sections }: { sections: NoteSection[] }) {
  if (!sections || sections.length === 0) {
    return <EmptyTab message="No sections in this note." />;
  }
  return (
    <div className="grid lg:grid-cols-[220px_1fr] gap-8">
      {/* TOC */}
      <aside className="hidden lg:block">
        <div className="sticky top-24 space-y-1">
          <p className="px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-text-muted">
            On this page
          </p>
          {sections.map((s) => (
            <a
              key={s.id}
              href={`#section-${s.id}`}
              className="block px-3 py-1.5 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-surface-light/60 truncate"
              title={s.heading}
            >
              {s.heading}
            </a>
          ))}
        </div>
      </aside>

      <div className="space-y-10 min-w-0">
        {sections.map((section, i) => (
          <SectionBlock key={section.id} section={section} index={i} />
        ))}
      </div>
    </div>
  );
}

function SectionBlock({ section, index }: { section: NoteSection; index: number }) {
  return (
    <section id={`section-${section.id}`} className="scroll-mt-24">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
        Section {index + 1}
      </p>
      <h2 className="mt-2 text-2xl font-bold tracking-tight">{section.heading}</h2>
      {section.overview && (
        <p className="mt-3 text-text-secondary leading-relaxed">{section.overview}</p>
      )}

      <div className="mt-6 space-y-5">
        {section.subtopics?.map((sub) => (
          <div
            key={sub.id}
            className="rounded-2xl bg-surface border border-surface-lighter p-5"
          >
            <h3 className="font-semibold text-text-primary">{sub.heading}</h3>
            {sub.content_md && (
              <RichText text={sub.content_md} className="mt-3 text-sm text-text-secondary" />
            )}
            {sub.examples && sub.examples.length > 0 && (
              <div className="mt-4">
                <p className="text-[10px] uppercase tracking-[0.18em] text-text-muted">
                  Examples
                </p>
                <ul className="mt-2 space-y-1.5">
                  {sub.examples.map((ex, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-text-secondary flex items-start gap-2"
                    >
                      <span className="mt-2 w-1 h-1 rounded-full bg-accent shrink-0" />
                      <RichText text={ex} className="flex-1" />
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {sub.key_takeaways && sub.key_takeaways.length > 0 && (
              <div className="mt-4 rounded-xl bg-accent/5 border border-accent/20 p-3">
                <p className="text-[10px] uppercase tracking-[0.18em] text-accent">
                  Key takeaways
                </p>
                <ul className="mt-2 space-y-1.5">
                  {sub.key_takeaways.map((k, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-text-primary flex items-start gap-2"
                    >
                      <span className="text-accent">✓</span>
                      <span>{k}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

/** Markdown renderer with LaTeX (KaTeX), tables, bold, italic, and lists. */
function RichText({ text, className }: { text: string; className?: string }) {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
        rehypePlugins={[[rehypeKatex, { output: 'html' }]]}
        components={{
          p: ({ children }) => (
            <p className="my-2 leading-relaxed">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="list-disc list-outside pl-5 space-y-1 my-2">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-outside pl-5 space-y-1 my-2">{children}</ol>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-text-primary">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-text-secondary">{children}</em>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-3">
              <table className="min-w-full text-sm border border-surface-lighter rounded-lg">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="px-3 py-2 text-left font-semibold bg-surface-light border-b border-surface-lighter">{children}</th>
          ),
          td: ({ children }) => (
            <td className="px-3 py-2 border-b border-surface-lighter">{children}</td>
          ),
          code: ({ children }) => (
            <code className="px-1.5 py-0.5 rounded bg-surface-light text-xs font-mono text-accent">{children}</code>
          ),
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  );
}

/* ---------------- Key terms tab ---------------- */
function TermsTab({ terms }: { terms: NoteKeyTerm[] }) {
  if (!terms || terms.length === 0) {
    return <EmptyTab message="No key terms in this note." />;
  }
  return (
    <div className="grid sm:grid-cols-2 gap-4">
      {terms.map((t) => (
        <div
          key={t.id}
          className="rounded-2xl bg-surface border border-surface-lighter p-5"
        >
          <p className="text-[10px] uppercase tracking-[0.18em] text-secondary">
            Key term
          </p>
          <h3 className="mt-1 font-semibold text-lg">{t.term}</h3>
          <p className="mt-2 text-sm text-text-secondary leading-relaxed">
            {t.definition}
          </p>
        </div>
      ))}
    </div>
  );
}

/* ---------------- Flashcards tab ---------------- */
function CardsTab({ cards }: { cards: NoteFlashcard[] }) {
  const [revealed, setRevealed] = useState<Record<number, boolean>>({});

  if (!cards || cards.length === 0) {
    return <EmptyTab message="No flashcards in this note." />;
  }

  function toggle(id: number) {
    setRevealed((r) => ({ ...r, [id]: !r[id] }));
  }
  function revealAll() {
    setRevealed(Object.fromEntries(cards.map((c) => [c.id, true])));
  }
  function hideAll() {
    setRevealed({});
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted">Click a card to flip it.</span>
        <div className="flex gap-3">
          <button onClick={revealAll} className="text-secondary hover:text-secondary-light">
            Reveal all
          </button>
          <button onClick={hideAll} className="text-text-secondary hover:text-text-primary">
            Hide all
          </button>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {cards.map((c, i) => {
          const open = revealed[c.id];
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => toggle(c.id)}
              className={`text-left rounded-2xl p-5 border transition ${
                open
                  ? "bg-accent/10 border-accent/40"
                  : "bg-surface border-surface-lighter hover:border-secondary/50 hover:bg-surface-light"
              }`}
            >
              <p className="text-[10px] uppercase tracking-[0.18em] text-text-muted">
                Card {i + 1}
              </p>
              <p className="mt-2 font-medium leading-snug">{c.question}</p>
              <div
                className={`mt-3 text-sm transition-all overflow-hidden ${
                  open ? "max-h-96 opacity-100 mt-3" : "max-h-0 opacity-0 mt-0"
                }`}
              >
                <div className="border-t border-accent/20 pt-3 text-text-secondary leading-relaxed whitespace-pre-wrap">
                  {c.answer}
                </div>
              </div>
              {!open && (
                <p className="mt-3 text-[11px] text-text-muted">Click to reveal answer</p>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/* ---------------- Empty tab ---------------- */
function EmptyTab({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-surface-lighter bg-surface/40 p-10 text-center text-sm text-text-secondary">
      {message}
    </div>
  );
}

