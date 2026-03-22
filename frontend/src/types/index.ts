export interface Answer {
  id: number;
  text: string;
  is_correct: boolean;
}

export interface Question {
  id: number;
  topic: number;
  topic_name: string;
  subject_name: string;
  subtopic_id: number | null;
  subtopic_name: string | null;
  text: string;
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
