"use client";

import type { Question } from "@/types";
import QuestionCard from "./QuestionCard";

interface Props {
  questions: Question[];
  onBack: () => void;
}

export default function QuizView({ questions, onBack }: Props) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Header bar */}
      <div className="flex items-center justify-between mb-8">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors text-sm"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          New Practice
        </button>
        <div className="text-sm text-text-muted">
          {questions[0]?.subject_name} &middot; {questions[0]?.topic_name} &middot;{" "}
          <span className="capitalize">{questions[0]?.difficulty}</span>
        </div>
      </div>

      {/* Questions */}
      <div className="space-y-6">
        {questions.map((q, i) => (
          <QuestionCard key={q.id} question={q} index={i} total={questions.length} />
        ))}
      </div>

      {/* Bottom action */}
      <div className="mt-10 text-center">
        <button
          type="button"
          onClick={onBack}
          className="bg-secondary hover:bg-secondary-dark text-white font-semibold px-8 py-3 rounded-xl transition-all shadow-lg shadow-secondary/25 hover:shadow-secondary/40 active:scale-[0.98]"
        >
          Practice Another Set
        </button>
      </div>
    </div>
  );
}
