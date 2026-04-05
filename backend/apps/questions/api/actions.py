# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import json
import logging
import time

import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
]

SYSTEM_INSTRUCTION = '''\
You are an expert assessment item writer.
Validation Rule: If the requested Topic does not logically belong to the Subject,
set status to 'invalid_topic' and return an empty questions array.
Rules: 4 options per question, exactly 1 correct, random correct answer placement,
no 'All of the above', distinct and plausible distractors. Include detailed explanations.
'''

USER_PROMPT_TEMPLATE = '''\
Generate exactly {count} unique multiple-choice questions:
- Subject: {subject}
- Topic: {topic}
- Subtopic: {subtopic}
- Difficulty: {difficulty}

Difficulty Policy:
- easy: recall/basic concepts
- medium: applied understanding
- hard: analysis, synthesis, multi-step reasoning
'''

MCQ_SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'status': {
            'type': 'STRING',
            'enum': ['success', 'invalid_topic'],
            'description': "Returns 'success' if the topic matches the subject, 'invalid_topic' if the input is nonsensical.",
        },
        'message': {
            'type': 'STRING',
            'description': 'Optional message explaining why a topic was invalid.',
        },
        'questions': {
            'type': 'ARRAY',
            'description': 'Array of multiple choice questions.',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'text': {
                        'type': 'STRING',
                        'description': 'The actual question text ending with a question mark.',
                    },
                    'answers': {
                        'type': 'ARRAY',
                        'items': {
                            'type': 'OBJECT',
                            'properties': {
                                'text': {'type': 'STRING'},
                                'is_correct': {'type': 'BOOLEAN'},
                            },
                            'required': ['text', 'is_correct'],
                        },
                    },
                    'explanation': {
                        'type': 'STRING',
                        'description': 'Explanation of the correct answer.',
                    },
                },
                'required': ['text', 'answers', 'explanation'],
            },
        },
    },
    'required': ['status', 'questions'],
}


def generate_questions(
        subject_name: str,
        topic_name: str,
        difficulty: str,
        subtopic_name: str,
        count: int = 10,
) -> dict:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured in settings.')

    genai.configure(api_key=api_key)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        count=count,
        subject=subject_name,
        topic=topic_name,
        subtopic=subtopic_name,
        difficulty=difficulty,
    )

    max_retries = 5
    delays = [1, 2, 4, 8, 16]
    last_error = None

    for model_name in GEMINI_MODELS:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=genai.GenerationConfig(
                response_mime_type='application/json',
                response_schema=MCQ_SCHEMA,
                temperature=0.5,
            ),
        )

        for attempt in range(max_retries):
            try:
                logger.info('Trying model %s (attempt %d)', model_name, attempt + 1)
                response = model.generate_content(user_prompt)
                data = json.loads(response.text)

                if data.get('status') == 'invalid_topic':
                    return data

                questions = data.get('questions', [])
                for q in questions:
                    if len(q.get('answers', [])) != 4:
                        raise ValueError('Each question must have exactly 4 options.')
                    correct_count = sum(1 for a in q['answers'] if a.get('is_correct'))
                    if correct_count != 1:
                        raise ValueError(
                            'Each question must have exactly 1 correct answer.')

                return data

            except Exception as e:
                logger.warning('Model %s attempt %d failed: %s', model_name,
                               attempt + 1, e)
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(delays[attempt])

    raise last_error or ValueError('All Gemini models failed after retries.')
