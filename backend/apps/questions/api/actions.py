# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import json
import logging

import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    'gemini-3-flash',
    'gemini-2.5-flash',
    'gemini-2.0-flash',
]

QUESTION_PROMPT = (
    'Generate exactly {count} multiple-choice questions about the subject "{subject}" '
    'on the topic "{topic}" with difficulty level "{difficulty}".\n\n'
    'Rules:\n'
    '- Each question must have exactly 4 answer options.\n'
    '- Exactly one answer must be correct.\n'
    '- Questions should be diverse and educational.\n'
    '- Difficulty guide: "easy" = basic recall, "medium" = applied understanding, '
    '"hard" = analysis/synthesis.\n\n'
    'Return ONLY a valid JSON array (no markdown fencing, no extra text) with this structure:\n'
    '[\n'
    '  {{\n'
    '    "text": "Question text here?",\n'
    '    "answers": [\n'
    '      {{"text": "Option A", "is_correct": false}},\n'
    '      {{"text": "Option B", "is_correct": true}},\n'
    '      {{"text": "Option C", "is_correct": false}},\n'
    '      {{"text": "Option D", "is_correct": false}}\n'
    '    ]\n'
    '  }}\n'
    ']'
)


def generate_questions(subject_name: str, topic_name: str, difficulty: str, count: int = 10) -> list[dict]:
    '''Call Google Gemini to generate MCQ questions and return parsed JSON.'''
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured in settings.')

    genai.configure(api_key=api_key)

    prompt = QUESTION_PROMPT.format(
        count=count,
        subject=subject_name,
        topic=topic_name,
        difficulty=difficulty,
    )

    # Try models in order until one succeeds
    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            logger.info('Trying model: %s', model_name)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            raw = response.text.strip()
            break
        except Exception as e:
            logger.warning('Model %s failed: %s', model_name, e)
            last_error = e
            continue
    else:
        raise last_error or ValueError('All Gemini models failed.')

    # Strip markdown code fences if present
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
    if raw.endswith('```'):
        raw = raw[: raw.rfind('```')]
    raw = raw.strip()

    questions = json.loads(raw)

    # Validate structure
    if not isinstance(questions, list):
        raise ValueError('Gemini returned non-list JSON.')
    for q in questions:
        if 'text' not in q or 'answers' not in q:
            raise ValueError('Invalid question structure from Gemini.')
        if len(q['answers']) != 4:
            raise ValueError('Each question must have exactly 4 answers.')
        correct_count = sum(1 for a in q['answers'] if a.get('is_correct'))
        if correct_count != 1:
            raise ValueError('Each question must have exactly 1 correct answer.')

    return questions
