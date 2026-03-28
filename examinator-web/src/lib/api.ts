const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export async function getSubjects() {
  const data = await fetchJSON<{ results: import("@/types").Subject[] }>(
    `${API_URL}/subjects/`,
  );
  return data.results;
}

export async function getDailyQuestions(
  subjectId: number,
  topicId: string | number,
  difficulty: string,
  subtopicId: string | number = "all",
) {
  const params = new URLSearchParams({
    subject: String(subjectId),
    topic: String(topicId),
    difficulty,
    subtopic: String(subtopicId),
  });
  const data = await fetchJSON<import("@/types").Question[]>(
    `${API_URL}/questions/daily/?${params}`,
  );
  return data;
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
