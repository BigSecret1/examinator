"use client";

import { useState } from "react";
import type { Question } from "@/types";

interface Props {
  question: Question;
  index: number;
  total: number;
}

export default function QuestionCard({ question, index, total }: Props) {
  const [selected, setSelected] = useState<number | null>(null);
  const revealed = selected !== null;

  return (
    <div className="bg-surface rounded-2xl p-6 md:p-8 shadow-xl border border-surface-light/30">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-medium text-secondary bg-secondary/10 px-3 py-1 rounded-full">
          Question {index + 1} of {total}
        </span>
        <span
          className={`text-xs font-medium px-3 py-1 rounded-full capitalize ${
            question.difficulty === "easy"
              ? "bg-success/10 text-success"
              : question.difficulty === "medium"
              ? "bg-warning/10 text-warning"
              : "bg-error/10 text-error"
          }`}
        >
          {question.difficulty}
        </span>
      </div>

      {/* Question text */}
      <p className="text-lg font-medium text-text-primary leading-relaxed mb-6">
        {question.text}
      </p>

      {/* Answer options */}
      <div className="space-y-3">
        {question.answers.map((answer, i) => {
          const letter = String.fromCharCode(65 + i);
          let style = "bg-surface-light border-surface-lighter hover:border-secondary/40 hover:bg-secondary/5 cursor-pointer";
          if (revealed) {
            if (answer.is_correct) {
              style = "bg-success/10 border-success/40 ring-1 ring-success/20";
            } else if (selected === answer.id) {
              style = "bg-error/10 border-error/40 ring-1 ring-error/20";
            } else {
              style = "bg-surface-light border-surface-lighter opacity-50";
            }
          }

          return (
            <button
              key={answer.id}
              type="button"
              onClick={() => {
                if (!revealed) setSelected(answer.id);
              }}
              disabled={revealed}
              className={`w-full flex items-start gap-4 p-4 rounded-xl border text-left transition-all ${style}`}
            >
              <span
                className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold ${
                  revealed && answer.is_correct
                    ? "bg-success text-white"
                    : revealed && selected === answer.id
                    ? "bg-error text-white"
                    : "bg-surface-lighter text-text-secondary"
                }`}
              >
                {letter}
              </span>
              <span className="text-text-primary pt-1">{answer.text}</span>
              {revealed && answer.is_correct && (
                <svg className="ml-auto shrink-0 w-5 h-5 text-success mt-1.5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
              {revealed && selected === answer.id && !answer.is_correct && (
                <svg className="ml-auto shrink-0 w-5 h-5 text-error mt-1.5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          );
        })}
      </div>

      {/* Result feedback */}
      {revealed && (
        <div
          className={`mt-5 p-4 rounded-xl text-sm font-medium ${
            question.answers.find((a) => a.id === selected)?.is_correct
              ? "bg-success/10 text-success border border-success/20"
              : "bg-error/10 text-error border border-error/20"
          }`}
        >
          {question.answers.find((a) => a.id === selected)?.is_correct
            ? "✓ Correct! Well done."
            : `✗ Incorrect. The correct answer is: ${question.answers.find((a) => a.is_correct)?.text}`}
        </div>
      )}
    </div>
  );
}
