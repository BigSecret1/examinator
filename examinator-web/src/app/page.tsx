// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-surface-light/30 bg-primary/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-secondary flex items-center justify-center shadow-lg shadow-secondary/25">
              <Image
                src="/examinator-icon.png"
                alt="Examinator logo"
                width={38}
                height={50}
                className="w-6 h-6 object-contain"
                priority
              />
            </div>
            <h1 className="text-xl font-bold text-text-primary tracking-tight">
              Examinator
            </h1>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-secondary/20 text-secondary border border-secondary/30">
              Beta
            </span>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-3">
            Train Your Brain<span className="text-secondary">.</span>
          </h2>
          <p className="text-text-secondary max-w-md mx-auto">
            A playground to test your knowledge and keep improving every day.
          </p>
        </div>

        <div className="grid gap-6 max-w-2xl mx-auto md:grid-cols-2">
          {/* Practice by Subject */}
          <Link
            href="/practice"
            className="group bg-surface rounded-2xl p-6 border border-surface-light/30 shadow-xl hover:border-secondary/40 transition-all"
          >
            <div className="w-12 h-12 rounded-xl bg-accent/15 flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-text-primary mb-2 group-hover:text-secondary transition-colors">
              Practice by Subject
            </h3>
            <p className="text-sm text-text-secondary">
              Build strong fundamentals by focusing on one subject at a time with targeted question sets.
            </p>
          </Link>

          {/* Practice by Exam */}
          <Link
            href="/practice/exams"
            className="group bg-surface rounded-2xl p-6 border border-surface-light/30 shadow-xl hover:border-secondary/40 transition-all"
          >
            <div className="w-12 h-12 rounded-xl bg-secondary/15 flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-text-primary mb-2 group-hover:text-secondary transition-colors">
              Practice by Exam
            </h3>
            <p className="text-sm text-text-secondary">
              Prepare in exam context with subject-wise questions aligned to your selected exam pattern.
            </p>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-light/30 py-6 text-center text-xs text-text-muted">
        Examinator &copy; {new Date().getFullYear()} &middot; Powered by AI
      </footer>
    </div>
  );
}
