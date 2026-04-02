"use client";

import Image from "next/image";
import { useState } from "react";
import ExamFilterPanel from "@/components/ExamFilterPanel";
import QuizView from "@/components/QuizView";
import { getExamDailyQuestions } from "@/lib/api";
import type { Question, Difficulty } from "@/types";

export default function ExamsPage() {
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleStart(examId: number, subjectId: number, difficulty: Difficulty) {
    setLoading(true);
    setError(null);
    try {
      const data = await getExamDailyQuestions(examId, subjectId, difficulty);
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
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-10">
        {/* Hero section */}
        {!questions && (
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-3">
              Practice by Exam<span className="text-secondary">.</span>
            </h2>
            <p className="text-text-secondary max-w-md mx-auto">
              Prepare in exam context with subject-wise questions aligned to your selected exam pattern.
            </p>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="max-w-2xl mx-auto mb-6 bg-error/10 border border-error/20 text-error text-sm rounded-xl px-5 py-4">
            {error}
          </div>
        )}

        {/* Filter panel or Quiz view */}
        {!questions && (
          <ExamFilterPanel onStart={handleStart} loading={loading} />
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
