"use client";

import { useState, useEffect } from "react";
import { getExams, getExamSubjects } from "@/lib/api";
import type { Exam, ExamSubject, Difficulty } from "@/types";

interface Props {
  onStart: (examId: number, subjectId: number, difficulty: Difficulty) => void;
  loading: boolean;
}

export default function ExamFilterPanel({ onStart, loading }: Props) {
  const [exams, setExams] = useState<Exam[]>([]);
  const [subjects, setSubjects] = useState<ExamSubject[]>([]);
  const [selectedExamId, setSelectedExamId] = useState<number | "">("");
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | "">("");
  const [difficulty, setDifficulty] = useState<Difficulty>("medium");
  const [examsLoading, setExamsLoading] = useState(true);
  const [subjectsLoading, setSubjectsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch exams on mount
  useEffect(() => {
    getExams()
      .then(setExams)
      .catch((e) => setError(e.message))
      .finally(() => setExamsLoading(false));
  }, []);

  // Fetch subjects when exam changes
  useEffect(() => {
    if (!selectedExamId) {
      setSubjects([]);
      setSelectedSubjectId("");
      return;
    }
    setSubjectsLoading(true);
    setSelectedSubjectId("");
    setError(null);
    getExamSubjects(selectedExamId)
      .then(setSubjects)
      .catch((e) => setError(e.message))
      .finally(() => setSubjectsLoading(false));
  }, [selectedExamId]);

  const canStart = selectedExamId && selectedSubjectId && !loading;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (canStart) {
      onStart(selectedExamId as number, selectedSubjectId as number, difficulty);
    }
  }

  const difficulties: Difficulty[] = ["easy", "medium", "hard"];

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form
        onSubmit={handleSubmit}
        className="bg-surface rounded-2xl p-6 md:p-8 shadow-2xl border border-surface-light/30"
      >
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Exam Practice
        </h2>

        {error && (
          <div className="mb-5 bg-error/10 border border-error/20 text-error text-sm rounded-xl px-4 py-3">
            {error}
          </div>
        )}

        {/* Exam selector */}
        <div className="mb-5">
          <label htmlFor="exam" className="block text-sm font-medium text-text-secondary mb-2">
            Exam
          </label>
          <select
            id="exam"
            value={selectedExamId}
            onChange={(e) => setSelectedExamId(e.target.value ? Number(e.target.value) : "")}
            disabled={examsLoading}
            className="w-full bg-surface-light border border-surface-lighter rounded-xl px-4 py-3 text-text-primary hover:border-secondary/50 focus:outline-none focus:ring-2 focus:ring-secondary/40 transition-all disabled:opacity-50"
          >
            <option value="">
              {examsLoading ? "Loading exams..." : "Select an exam..."}
            </option>
            {exams.map((exam) => (
              <option key={exam.id} value={exam.id}>
                {exam.name}
              </option>
            ))}
          </select>
        </div>

        {/* Subject selector */}
        <div className="mb-5">
          <label htmlFor="subject" className="block text-sm font-medium text-text-secondary mb-2">
            Subject
          </label>
          <select
            id="subject"
            value={selectedSubjectId}
            onChange={(e) => setSelectedSubjectId(e.target.value ? Number(e.target.value) : "")}
            disabled={!selectedExamId || subjectsLoading}
            className="w-full bg-surface-light border border-surface-lighter rounded-xl px-4 py-3 text-text-primary hover:border-secondary/50 focus:outline-none focus:ring-2 focus:ring-secondary/40 transition-all disabled:opacity-50"
          >
            <option value="">
              {subjectsLoading
                ? "Loading subjects..."
                : !selectedExamId
                ? "Select an exam first..."
                : "Select a subject..."}
            </option>
            {subjects.map((s) => (
              <option key={s.subject_id} value={s.subject_id}>
                {s.subject_name}
                {s.is_optional ? " (Optional)" : ""}
              </option>
            ))}
          </select>
        </div>

        {/* Difficulty selector */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-text-secondary mb-3">
            Difficulty
          </label>
          <div className="flex gap-3">
            {difficulties.map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDifficulty(d)}
                className={`flex-1 py-2.5 rounded-xl text-sm font-medium capitalize transition-all ${
                  difficulty === d
                    ? d === "easy"
                      ? "bg-success/20 text-success border border-success/30"
                      : d === "medium"
                      ? "bg-warning/20 text-warning border border-warning/30"
                      : "bg-error/20 text-error border border-error/30"
                    : "bg-surface-light text-text-muted border border-surface-lighter hover:border-surface-lighter/80"
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        {/* Generate button */}
        <button
          type="submit"
          disabled={!canStart}
          className="w-full bg-secondary hover:bg-secondary-dark text-white font-semibold py-3.5 rounded-xl transition-all shadow-lg shadow-secondary/25 hover:shadow-secondary/40 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-secondary disabled:active:scale-100 disabled:shadow-none"
        >
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Generating Questions...
            </span>
          ) : (
            "Generate Questions"
          )}
        </button>
      </form>
    </div>
  );
}
