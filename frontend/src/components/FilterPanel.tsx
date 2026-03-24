"use client";

import { useState, useRef, useEffect } from "react";
import type { Subject, Topic, SubTopic, Difficulty } from "@/types";

interface Props {
  subjects: Subject[];
  onStart: (subjectId: number, topicId: string | number, difficulty: Difficulty, subtopicId: string | number) => void;
  loading: boolean;
}

export default function FilterPanel({ subjects, onStart, loading }: Props) {
  const [search, setSearch] = useState("");
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string | number>("all");
  const [selectedSubtopic, setSelectedSubtopic] = useState<string | number>("all");
  const [difficulty, setDifficulty] = useState<Difficulty>("medium");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filtered = subjects.filter((s) =>
    s.name.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const topics: Topic[] = selectedSubject?.topics ?? [];
  const subtopics: SubTopic[] =
    selectedTopic !== "all"
      ? topics.find((t) => String(t.id) === String(selectedTopic))?.subtopics ?? []
      : [];

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-surface rounded-2xl p-6 md:p-8 shadow-2xl border border-surface-light/30">
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Choose Your Practice
        </h2>

        {/* Subject dropdown with search */}
        <div className="mb-5" ref={dropdownRef}>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Subject
          </label>
          <div className="relative">
            <button
              type="button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="w-full bg-surface-light border border-surface-lighter rounded-xl px-4 py-3 text-left text-text-primary hover:border-secondary/50 focus:outline-none focus:ring-2 focus:ring-secondary/40 transition-all"
            >
              {selectedSubject ? selectedSubject.name : "Select a subject..."}
              <svg
                className={`absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted transition-transform ${
                  dropdownOpen ? "rotate-180" : ""
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {dropdownOpen && (
              <div className="absolute z-50 mt-2 w-full bg-surface-light border border-surface-lighter rounded-xl shadow-2xl overflow-hidden">
                <div className="p-3 border-b border-surface-lighter">
                  <input
                    type="text"
                    placeholder="Search subjects..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full bg-surface border border-surface-lighter rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-secondary/40"
                    autoFocus
                  />
                </div>
                <ul className="max-h-56 overflow-y-auto">
                  {filtered.length === 0 ? (
                    <li className="px-4 py-3 text-sm text-text-muted">No subjects found</li>
                  ) : (
                    filtered.map((s) => (
                      <li key={s.id}>
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedSubject(s);
                            setSelectedTopic("all");
                            setSelectedSubtopic("all");
                            setDropdownOpen(false);
                            setSearch("");
                          }}
                          className={`w-full text-left px-4 py-3 text-sm hover:bg-secondary/10 transition-colors ${
                            selectedSubject?.id === s.id
                              ? "bg-secondary/15 text-secondary-light"
                              : "text-text-primary"
                          }`}
                        >
                          {s.name}
                          <span className="block text-xs text-text-muted mt-0.5">
                            {s.topics.length} topic{s.topics.length !== 1 ? "s" : ""}
                          </span>
                        </button>
                      </li>
                    ))
                  )}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Topic selector */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Topic
          </label>
          <div className="relative">
            <select
              value={selectedTopic}
              onChange={(e) => {
                setSelectedTopic(e.target.value);
                setSelectedSubtopic("all");
              }}
              disabled={!selectedSubject}
              className="w-full bg-surface-light border border-surface-lighter rounded-xl px-4 pr-10 py-3 text-text-primary hover:border-secondary/50 focus:outline-none focus:ring-2 focus:ring-secondary/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed appearance-none"
            >
              <option value="all">All Topics</option>
              {topics.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
            <svg
              className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Subtopic selector */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Subtopic
          </label>
          <div className="relative">
            <select
              value={selectedSubtopic}
              onChange={(e) => setSelectedSubtopic(e.target.value)}
              disabled={selectedTopic === "all"}
              className="w-full bg-surface-light border border-surface-lighter rounded-xl px-4 pr-10 py-3 text-text-primary hover:border-secondary/50 focus:outline-none focus:ring-2 focus:ring-secondary/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed appearance-none"
            >
              <option value="all">All Subtopics</option>
              {subtopics.map((st) => (
                <option key={st.id} value={st.id}>
                  {st.name}
                </option>
              ))}
            </select>
            <svg
              className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Difficulty */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-text-secondary mb-3">
            Difficulty
          </label>
          <div className="flex gap-3">
            {(["easy", "medium", "hard"] as Difficulty[]).map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDifficulty(d)}
                className={`flex-1 py-2.5 rounded-xl text-sm font-medium capitalize transition-all ${
                  difficulty === d
                    ? "bg-accent/20 text-accent-light border border-accent/30"
                    : "bg-surface-light border border-surface-lighter text-text-secondary hover:border-surface-lighter hover:text-text-primary"
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        {/* Start button */}
        <button
          type="button"
          onClick={() => {
            if (selectedSubject) {
              onStart(selectedSubject.id, selectedTopic, difficulty, selectedSubtopic);
            }
          }}
          disabled={!selectedSubject || loading}
          className="w-full bg-secondary hover:bg-secondary-dark text-white font-semibold py-3.5 rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-secondary/25 hover:shadow-secondary/40 active:scale-[0.98]"
        >
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Preparing Question Set...
            </span>
          ) : (
            "Start Practice"
          )}
        </button>
      </div>
    </div>
  );
}
