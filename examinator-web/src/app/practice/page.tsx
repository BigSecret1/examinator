// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import AuthGuard from "@/components/AuthGuard";
import UserAvatar from "@/components/UserAvatar";
import FilterPanel from "@/components/FilterPanel";
import QuizView from "@/components/QuizView";
import { getSubjects, getDailyQuestions } from "@/lib/api";
import type { Subject, Question, Difficulty } from "@/types";

export default function Page() {
  return (
    <AuthGuard>
      <Home />
    </AuthGuard>
  );
}

function Home() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [subjectsLoading, setSubjectsLoading] = useState(true);

  useEffect(() => {
    getSubjects()
      .then(setSubjects)
      .catch((e) => setError(e.message))
      .finally(() => setSubjectsLoading(false));
  }, []);

  async function handleStart(subjectId: number, topicId: number | null, difficulty: Difficulty, subtopicId: number | null = null) {
    setLoading(true);
    setError(null);
    try {
      const data = await getDailyQuestions(subjectId, topicId, difficulty, subtopicId);
      setQuestions(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-surface-light/30 bg-primary/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/app" className="flex items-center gap-3">
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
            </Link>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-secondary/20 text-secondary border border-secondary/30">
              Beta
            </span>
          </div>
          <UserAvatar />
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-10">
        {/* Hero section */}
        {!questions && (
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-3">
              Practice by Subject<span className="text-secondary">.</span>
            </h2>
            <p className="text-text-secondary max-w-md mx-auto">
              Build strong fundamentals by focusing on one subject at a time with targeted question sets.
            </p>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="max-w-2xl mx-auto mb-6 bg-error/10 border border-error/20 text-error text-sm rounded-xl px-5 py-4">
            {error}
          </div>
        )}

        {/* Loading subjects */}
        {subjectsLoading && (
          <div className="text-center py-20">
            <svg className="animate-spin h-8 w-8 mx-auto text-secondary" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p className="mt-4 text-text-muted text-sm">Loading subjects...</p>
          </div>
        )}

        {/* Filter panel or Quiz view */}
        {!subjectsLoading && !questions && (
          <FilterPanel subjects={subjects} onStart={handleStart} loading={loading} />
        )}

        {questions && (
          <QuizView
            questions={questions}
            onBack={() => {
              setQuestions(null);
              setError(null);
            }}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-light/30 py-6 text-center text-xs text-text-muted">
        Examinator &copy; {new Date().getFullYear()} &middot; Powered by AI
      </footer>
    </div>
  );
}
