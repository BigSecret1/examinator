// Copyright 2026 BigSecret1
//
// Licensed under the Apache License, Version 2.0

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

/* ---------------- Token helpers ---------------- */

const ACCESS_KEY = "access";
const REFRESH_KEY = "refresh";
const USER_KEY = "user";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens(access: string, refresh?: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearAuthStorage() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

/* ---------------- Refresh-token flow ---------------- */

let refreshInflight: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshInflight) return refreshInflight;
  const refresh = getRefreshToken();
  if (!refresh) return null;

  refreshInflight = (async () => {
    try {
      const res = await fetch(`${API_URL}/auth/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });
      if (!res.ok) return null;
      const data = (await res.json()) as { access: string; refresh?: string };
      setTokens(data.access, data.refresh);
      return data.access;
    } catch {
      return null;
    } finally {
      refreshInflight = null;
    }
  })();

  return refreshInflight;
}

/* ---------------- Core fetch wrapper ---------------- */

interface FetchOptions extends RequestInit {
  /** Skip attaching the Authorization header (e.g. for the login call). */
  anonymous?: boolean;
}

async function authedFetch(url: string, opts: FetchOptions = {}): Promise<Response> {
  const { anonymous, headers, ...rest } = opts;
  const finalHeaders = new Headers(headers ?? {});
  if (
    !finalHeaders.has("Content-Type") &&
    rest.body &&
    typeof rest.body === "string"
  ) {
    finalHeaders.set("Content-Type", "application/json");
  }
  if (!anonymous) {
    const token = getAccessToken();
    if (token) finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  let res = await fetch(url, { ...rest, headers: finalHeaders });

  // One refresh-and-retry cycle on 401.
  if (!anonymous && res.status === 401) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      finalHeaders.set("Authorization", `Bearer ${newAccess}`);
      res = await fetch(url, { ...rest, headers: finalHeaders });
    } else {
      clearAuthStorage();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("auth:logout"));
      }
    }
  }
  return res;
}

async function fetchJSON<T>(url: string, opts: FetchOptions = {}): Promise<T> {
  const res = await authedFetch(url, opts);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

/* ---------------- Subjects / Questions / Exams ---------------- */

export async function getSubjects() {
  const data = await fetchJSON<{ results: import("@/types").Subject[] }>(
    `${API_URL}/subjects/`,
  );
  return data.results;
}

export async function getDailyQuestions(
  subjectId: number,
  topicId: number | null,
  difficulty: string,
  subtopicId: number | null = null,
) {
  const params = new URLSearchParams({
    subject: String(subjectId),
    difficulty,
  });
  if (topicId !== null) params.set("topic", String(topicId));
  if (subtopicId !== null) params.set("subtopic", String(subtopicId));

  return fetchJSON<import("@/types").Question[]>(
    `${API_URL}/questions/daily/?${params}`,
  );
}

export async function getExams() {
  const data = await fetchJSON<{ results: import("@/types").Exam[] }>(
    `${API_URL}/exams/`,
  );
  return data.results;
}

export async function getExamSubjects(examId: number) {
  return fetchJSON<import("@/types").ExamSubject[]>(
    `${API_URL}/exams/${examId}/subjects/`,
  );
}

export async function getExamDailyQuestions(
  examId: number,
  subjectId: number,
  difficulty: string,
) {
  const params = new URLSearchParams({
    subject: String(subjectId),
    difficulty,
  });
  return fetchJSON<import("@/types").Question[]>(
    `${API_URL}/exams/${examId}/daily-questions/?${params}`,
  );
}

/* ---------------- Auth ---------------- */

export async function googleLogin(credential: string) {
  return fetchJSON<import("@/types").AuthResponse>(
    `${API_URL}/auth/google/login/`,
    {
      method: "POST",
      body: JSON.stringify({ credential }),
      anonymous: true,
    },
  );
}

export async function getCurrentUser() {
  return fetchJSON<import("@/types").User>(`${API_URL}/auth/me/`);
}

