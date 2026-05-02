// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getNoteQuota,
  uploadNotePdf,
  type NoteListItem,
  type NoteQuota,
  type NoteUploadResponse,
} from "@/lib/api";

type Phase = "idle" | "uploading" | "rejected" | "error" | "success";

interface Props {
  open: boolean;
  onClose: () => void;
  onUploaded?: (note: NoteListItem) => void;
}

const REJECTION_LABELS: Record<string, string> = {
  not_pdf: "That file isn't a PDF.",
  over_size: "That PDF is too large.",
  over_pages: "That PDF has too many pages.",
  daily_limit_exceeded: "You've hit your daily upload limit. Try again tomorrow.",
};

function formatBytes(n: number) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export default function UploadModal({ open, onClose, onUploaded }: Props) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reason, setReason] = useState<string | null>(null);
  const [response, setResponse] = useState<Extract<NoteUploadResponse, { status: "success" }> | null>(null);
  const [quota, setQuota] = useState<NoteQuota | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Reset on open + fetch quota.
  useEffect(() => {
    if (!open) return;
    setPhase("idle");
    setFile(null);
    setError(null);
    setReason(null);
    setResponse(null);

    let cancelled = false;
    getNoteQuota()
      .then((q) => !cancelled && setQuota(q))
      .catch(() => {
        /* non-fatal */
      });
    return () => {
      cancelled = true;
    };
  }, [open]);

  // Lock scroll + ESC to close.
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && phase !== "uploading") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose, phase]);

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    const f = files[0];
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file.");
      return;
    }
    setError(null);
    setFile(f);
  }, []);

  async function handleUpload() {
    if (!file) return;
    setPhase("uploading");
    setError(null);
    setReason(null);
    try {
      const result = await uploadNotePdf(file);
      if (result.status === "success") {
        setResponse(result);
        setPhase("success");
        onUploaded?.(result.note);
      } else if (result.status === "rejected") {
        setReason(result.reason);
        setPhase("rejected");
      } else {
        setError(result.error || "Generation failed.");
        setPhase("error");
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed.");
      setPhase("error");
    }
  }

  if (!open) return null;

  const busy = phase === "uploading";

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="upload-title"
    >
      <div
        className="absolute inset-0 bg-primary-dark/80 backdrop-blur-sm"
        onClick={() => !busy && onClose()}
      />

      <div className="relative w-full max-w-lg rounded-2xl bg-surface border border-surface-lighter shadow-2xl shadow-black/50 p-7">
        {/* Close */}
        <button
          onClick={onClose}
          disabled={busy}
          aria-label="Close"
          className="absolute top-4 right-4 w-8 h-8 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-light transition flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed"
        >
          ✕
        </button>

        <h2 id="upload-title" className="text-xl font-bold tracking-tight">
          Upload a PDF
        </h2>
        <p className="mt-1 text-sm text-text-secondary">
          We&apos;ll generate structured notes, key terms, and flashcards.
        </p>

        {/* Quota chip */}
        {quota && (
          <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-light/60 border border-surface-lighter text-xs text-text-secondary">
            <span className="w-1.5 h-1.5 rounded-full bg-accent" />
            {quota.used} / {quota.daily_limit} uploads today · max{" "}
            {formatBytes(quota.max_file_size_bytes)} · {quota.max_pages} pages
          </div>
        )}

        {/* SUCCESS */}
        {phase === "success" && response && (
          <div className="mt-6 space-y-4">
            <div className="rounded-xl bg-success/10 border border-success/30 p-4">
              <p className="text-sm font-semibold text-success">
                ✓ Notes generated
              </p>
              <p className="mt-1 text-sm text-text-secondary">
                <span className="font-medium text-text-primary">
                  {response.note.title}
                </span>{" "}
                · {response.page_count} pages · {response.generation_mode} mode
              </p>
            </div>
            <button
              onClick={onClose}
              className="w-full px-5 py-3 rounded-xl bg-secondary hover:bg-secondary-light text-white font-semibold shadow-lg shadow-secondary/25 transition"
            >
              Done
            </button>
          </div>
        )}

        {/* REJECTED */}
        {phase === "rejected" && (
          <div className="mt-6 space-y-4">
            <div className="rounded-xl bg-warning/10 border border-warning/30 p-4 text-sm text-warning">
              {(reason && REJECTION_LABELS[reason]) || `Upload rejected: ${reason}`}
            </div>
            <button
              onClick={() => setPhase("idle")}
              className="w-full px-5 py-3 rounded-xl bg-surface-light hover:bg-surface-lighter text-text-primary font-semibold border border-surface-lighter transition"
            >
              Try another file
            </button>
          </div>
        )}

        {/* ERROR */}
        {phase === "error" && (
          <div className="mt-6 space-y-4">
            <div className="rounded-xl bg-error/10 border border-error/30 p-4 text-sm text-error">
              {error || "Something went wrong."}
            </div>
            <button
              onClick={() => setPhase("idle")}
              className="w-full px-5 py-3 rounded-xl bg-surface-light hover:bg-surface-lighter text-text-primary font-semibold border border-surface-lighter transition"
            >
              Retry
            </button>
          </div>
        )}

        {/* IDLE / UPLOADING */}
        {(phase === "idle" || phase === "uploading") && (
          <div className="mt-6 space-y-4">
            {/* Drop zone */}
            <button
              type="button"
              disabled={busy}
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                if (busy) return;
                handleFiles(e.dataTransfer.files);
              }}
              className={`w-full text-left rounded-xl border-2 border-dashed transition p-6 ${
                dragOver
                  ? "border-secondary bg-secondary/5"
                  : "border-surface-lighter bg-surface/40 hover:border-secondary/50 hover:bg-surface-light/50"
              } disabled:opacity-60 disabled:cursor-not-allowed`}
            >
              {file ? (
                <div className="flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl bg-secondary/15 text-secondary flex items-center justify-center text-xl shrink-0">
                    📄
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{file.name}</p>
                    <p className="text-xs text-text-muted">{formatBytes(file.size)}</p>
                  </div>
                  {!busy && (
                    <span
                      className="text-xs text-text-secondary hover:text-text-primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                    >
                      Change
                    </span>
                  )}
                </div>
              ) : (
                <div className="text-center">
                  <span className="mx-auto block w-10 h-10 rounded-xl bg-secondary/15 text-secondary flex items-center justify-center text-xl">
                    ⬆
                  </span>
                  <p className="mt-3 text-sm font-medium">
                    Drop a PDF here, or click to choose
                  </p>
                  <p className="mt-1 text-xs text-text-muted">PDF only</p>
                </div>
              )}
              <input
                ref={inputRef}
                type="file"
                accept="application/pdf,.pdf"
                hidden
                onChange={(e) => handleFiles(e.target.files)}
              />
            </button>

            {error && (
              <p className="text-xs text-error">{error}</p>
            )}

            {/* Action */}
            <button
              type="button"
              onClick={handleUpload}
              disabled={!file || busy}
              className="w-full px-5 py-3 rounded-xl bg-secondary hover:bg-secondary-light text-white font-semibold shadow-lg shadow-secondary/25 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {busy && (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {busy ? "Generating notes…" : "Generate notes"}
            </button>

            {busy && (
              <div className="rounded-xl bg-surface-light/60 border border-surface-lighter px-4 py-3 text-center space-y-1">
                <p className="text-xs font-medium text-text-primary">
                  Hang tight — your notes are being crafted
                </p>
                <p className="text-xs text-text-muted">
                  We&apos;re reading the entire PDF and generating sections, flashcards, and key terms.
                  This usually takes <span className="text-text-secondary font-medium">1–3 minutes</span> for longer documents.
                  Please keep this window open.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

