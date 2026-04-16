export interface Answer {
  id: number;
  text: string;
  is_correct: boolean;
}

export interface Question {
  id: number;
  topic: number | null;
  topic_name: string | null;
  subject_name: string;
  subtopic_id: number | null;
  subtopic_name: string | null;
  text: string;
  explanation: string;
  difficulty: "easy" | "medium" | "hard";
  answers: Answer[];
  created_at: string;
  updated_at: string;
}

export interface SubTopic {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export interface Topic {
  id: number;
  name: string;
  description: string;
  subtopics: SubTopic[];
  created_at: string;
}

export interface Subject {
  id: number;
  name: string;
  description: string;
  topics: Topic[];
  created_at: string;
}

export type Difficulty = "easy" | "medium" | "hard";

export interface Exam {
  id: number;
  name: string;
  description: string;
  country: string;
  conducting_body: string;
  frequency: string;
  official_url: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExamSubject {
  id: number;
  subject_id: number;
  subject_name: string;
  is_optional: boolean;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  avatar_url: string;
  date_joined: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}
