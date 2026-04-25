// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

import Image from "next/image";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Examinator — Turn any PDF into smart study notes",
  description:
    "Upload your textbook, lecture slides, or research paper. Examinator generates structured notes, a key-term glossary, and active-recall flashcards in minutes.",
};

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-primary text-text-primary">
      <SiteHeader />
      <main className="flex-1">
        <Hero />
        <HowItWorks />
        <Features />
        <ValueProps />
        <FAQ />
        <FinalCTA />
      </main>
      <SiteFooter />
    </div>
  );
}

/* ---------------- Header ---------------- */
function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-surface-light/30 bg-primary/80 backdrop-blur-md">
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

        <nav className="hidden md:flex items-center gap-8 text-sm text-text-secondary">
          <a href="#how" className="hover:text-text-primary transition">How it works</a>
          <a href="#features" className="hover:text-text-primary transition">Features</a>
          <a href="#faq" className="hover:text-text-primary transition">FAQ</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/practice"
            className="hidden sm:inline text-sm text-text-secondary hover:text-text-primary transition"
          >
            Sign in
          </Link>
          <Link
            href="/practice"
            className="px-4 py-2 rounded-xl bg-secondary hover:bg-secondary-light text-white text-sm font-semibold shadow-lg shadow-secondary/25 transition"
          >
            Get started
          </Link>
        </div>
      </div>
    </header>
  );
}

/* ---------------- Hero ---------------- */
function Hero() {
  return (
    <section className="relative overflow-hidden">
      {/* glow */}
      <div className="pointer-events-none absolute inset-0 -z-0">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[700px] rounded-full bg-secondary/20 blur-[140px]" />
        <div className="absolute top-40 right-0 w-[400px] h-[400px] rounded-full bg-accent/10 blur-[120px]" />
      </div>

      <div className="relative max-w-6xl mx-auto px-4 pt-20 pb-24 grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-light/60 border border-surface-lighter text-xs font-medium text-text-secondary">
            <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
            AI-powered study notes
          </span>

          <h1 className="mt-6 text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.05]">
            Turn any PDF into{" "}
            <span className="bg-gradient-to-r from-secondary-light to-accent bg-clip-text text-transparent">
              notes that actually stick.
            </span>
          </h1>

          <p className="mt-6 text-lg text-text-secondary max-w-xl">
            Upload your textbook, lecture slides, or research paper.
            Examinator generates structured notes, a key-term glossary,
            and active-recall flashcards — in minutes.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/practice"
              className="px-6 py-3 rounded-xl bg-secondary hover:bg-secondary-light text-white font-semibold shadow-lg shadow-secondary/25 transition"
            >
              Upload your first PDF →
            </Link>
            <Link
              href="#features"
              className="px-6 py-3 rounded-xl bg-surface-light hover:bg-surface-lighter text-text-primary font-semibold border border-surface-lighter transition"
            >
              See how it works
            </Link>
          </div>

          <p className="mt-5 text-xs text-text-muted">
            Works with scanned PDFs · Free during beta · No credit card needed
          </p>
        </div>

        {/* Mock note preview */}
        <NotePreviewMock />
      </div>
    </section>
  );
}

function NotePreviewMock() {
  return (
    <div className="relative">
      <div className="rounded-2xl bg-surface border border-surface-lighter shadow-2xl shadow-black/40 p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="w-2.5 h-2.5 rounded-full bg-error/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-warning/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-success/70" />
          <span className="ml-3 text-xs text-text-muted">organic-chemistry-ch4.pdf</span>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-xs uppercase tracking-wider text-text-muted">Note</p>
            <h3 className="text-lg font-semibold">Alkenes &amp; Alkynes — Reactions and Mechanisms</h3>
          </div>

          <div className="rounded-xl bg-primary-light/60 border border-surface-lighter p-4">
            <p className="text-xs uppercase tracking-wider text-accent mb-2">Section 1</p>
            <p className="font-medium">Electrophilic addition</p>
            <ul className="mt-2 text-sm text-text-secondary space-y-1 list-disc list-inside">
              <li>Markovnikov vs anti-Markovnikov</li>
              <li>Carbocation stability</li>
            </ul>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-secondary/10 border border-secondary/30 p-3">
              <p className="text-[10px] uppercase tracking-wider text-secondary-light mb-1">Key term</p>
              <p className="text-sm font-semibold">Carbocation</p>
              <p className="text-xs text-text-secondary mt-1">A carbon atom with a positive charge…</p>
            </div>
            <div className="rounded-xl bg-accent/10 border border-accent/30 p-3">
              <p className="text-[10px] uppercase tracking-wider text-accent mb-1">Flashcard</p>
              <p className="text-sm font-semibold">Q: What stabilizes a 3° carbocation?</p>
            </div>
          </div>
        </div>
      </div>

      {/* floating chip */}
      <div className="absolute -bottom-4 -left-4 hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl bg-surface-light border border-surface-lighter shadow-xl">
        <span className="w-6 h-6 rounded-md bg-accent/20 text-accent flex items-center justify-center text-xs">✓</span>
        <span className="text-xs text-text-secondary">12 flashcards generated</span>
      </div>
    </div>
  );
}

/* ---------------- How it works ---------------- */
function HowItWorks() {
  const steps = [
    {
      n: "01",
      title: "Upload your PDF",
      body: "Drop in a textbook chapter, lecture slides, or a paper. Scanned PDFs work too.",
    },
    {
      n: "02",
      title: "AI reads & structures it",
      body: "Examinator extracts sections, subtopics, key terms, and learning objectives.",
    },
    {
      n: "03",
      title: "Study & remember",
      body: "Review structured notes, drill key terms, and quiz yourself with flashcards.",
    },
  ];
  return (
    <section id="how" className="py-20 border-t border-surface-light/30">
      <div className="max-w-6xl mx-auto px-4">
        <SectionHeading eyebrow="How it works" title="From PDF to mastery in three steps." />
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          {steps.map((s) => (
            <div key={s.n} className="rounded-2xl bg-surface border border-surface-lighter p-6">
              <span className="text-sm font-mono text-secondary">{s.n}</span>
              <h3 className="mt-3 text-lg font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-text-secondary">{s.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------------- Features ---------------- */
function Features() {
  const features = [
    { icon: "📚", title: "Structured sections & subtopics", body: "Long PDFs become an outline you can actually navigate." },
    { icon: "🔑", title: "Key-term glossary", body: "Every important term, defined in plain language." },
    { icon: "🧠", title: "Active-recall flashcards", body: "Auto-generated Q&A pairs to drill what matters." },
    { icon: "🎯", title: "Learning objectives", body: "Know what you should be able to do after each note." },
    { icon: "🖼️", title: "Scanned PDFs supported", body: "Vision mode reads handwriting and image-based PDFs." },
    { icon: "🗂️", title: "Your personal library", body: "All your notes, organized and searchable in one place." },
  ];
  return (
    <section id="features" className="py-20 border-t border-surface-light/30">
      <div className="max-w-6xl mx-auto px-4">
        <SectionHeading eyebrow="Features" title="Everything you need to learn from a PDF." />
        <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="group rounded-2xl bg-surface border border-surface-lighter p-6 hover:border-secondary/50 hover:bg-surface-light transition"
            >
              <div className="w-11 h-11 rounded-xl bg-secondary/15 text-secondary-light flex items-center justify-center text-xl">
                {f.icon}
              </div>
              <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-text-secondary">{f.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------------- Value props ---------------- */
function ValueProps() {
  const items = [
    "Stop re-reading. Start recalling.",
    "Spend study time on understanding — not summarising.",
    "Cover more material in less time.",
    "Built for students, researchers, and lifelong learners.",
  ];
  return (
    <section className="py-20 border-t border-surface-light/30">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <SectionHeading eyebrow="Why Examinator" title="Built for serious learners." center />
        <ul className="mt-10 grid sm:grid-cols-2 gap-4">
          {items.map((t) => (
            <li
              key={t}
              className="flex items-start gap-3 rounded-xl bg-surface border border-surface-lighter p-4 text-left"
            >
              <span className="mt-0.5 w-5 h-5 rounded-full bg-accent/20 text-accent flex items-center justify-center text-xs">✓</span>
              <span className="text-sm text-text-secondary">{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

/* ---------------- FAQ ---------------- */
function FAQ() {
  const qa = [
    { q: "What kinds of PDFs work?", a: "Textbook chapters, lecture slides, journal articles, even scanned/handwritten notes (vision mode)." },
    { q: "Is there a file size limit?", a: "Daily upload limits apply during beta to keep things fair. Quotas reset every 24 hours." },
    { q: "Is my data private?", a: "Your PDFs are used only to generate your notes. We don't sell your data." },
    { q: "How much does it cost?", a: "Examinator is free during beta. Paid tiers will come later for power users." },
  ];
  return (
    <section id="faq" className="py-20 border-t border-surface-light/30">
      <div className="max-w-3xl mx-auto px-4">
        <SectionHeading eyebrow="FAQ" title="Questions, answered." center />
        <div className="mt-10 space-y-3">
          {qa.map((item) => (
            <details
              key={item.q}
              className="group rounded-2xl bg-surface border border-surface-lighter p-5 open:border-secondary/40 transition"
            >
              <summary className="flex items-center justify-between cursor-pointer list-none">
                <span className="font-medium">{item.q}</span>
                <span className="text-secondary group-open:rotate-45 transition-transform">+</span>
              </summary>
              <p className="mt-3 text-sm text-text-secondary">{item.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------------- Final CTA ---------------- */
function FinalCTA() {
  return (
    <section className="py-24">
      <div className="max-w-4xl mx-auto px-4">
        <div className="relative overflow-hidden rounded-3xl border border-secondary/30 bg-gradient-to-br from-secondary/20 via-surface to-accent/10 p-10 sm:p-14 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
            Stop highlighting. <span className="text-accent">Start remembering.</span>
          </h2>
          <p className="mt-4 text-text-secondary max-w-xl mx-auto">
            Upload your first PDF and get your first set of structured notes and flashcards in minutes.
          </p>
          <Link
            href="/practice"
            className="mt-8 inline-block px-7 py-3.5 rounded-xl bg-secondary hover:bg-secondary-light text-white font-semibold shadow-lg shadow-secondary/30 transition"
          >
            Upload your first PDF →
          </Link>
        </div>
      </div>
    </section>
  );
}

/* ---------------- Footer ---------------- */
function SiteFooter() {
  return (
    <footer className="border-t border-surface-light/30 py-8 text-xs text-text-muted">
      <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <span>Examinator © {new Date().getFullYear()} · Apache 2.0</span>
        <span>Made for learners who want to remember.</span>
      </div>
    </footer>
  );
}

/* ---------------- Helpers ---------------- */
function SectionHeading({
  eyebrow,
  title,
  center = false,
}: {
  eyebrow: string;
  title: string;
  center?: boolean;
}) {
  return (
    <div className={center ? "text-center" : ""}>
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
        {eyebrow}
      </p>
      <h2 className="mt-3 text-3xl sm:text-4xl font-bold tracking-tight">{title}</h2>
    </div>
  );
}

