# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from pathlib import Path


MAX_PAGES = 65
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MIN_DENSITY_CHARS_PER_PAGE = 100
MAX_OUTPUT_TOKENS = 32768

NOTES_PROMPT_DIR = Path(__file__).resolve().parent.parent / 'prompts'
SYSTEM_INSTRUCTION_PATHS = [
    NOTES_PROMPT_DIR / 'notes_system_instruction.md',
    Path(__file__).resolve().parent.parent.parent / 'scripts' /
    'notes_system_instruction.md',
]
USER_PROMPT_TEXT_PATHS = [
    NOTES_PROMPT_DIR / 'user_prompt_text.md',
]
USER_PROMPT_VISION_PATHS = [
    NOTES_PROMPT_DIR / 'user_prompt_vision.md',
]

SYSTEM_INSTRUCTION = None
for path in SYSTEM_INSTRUCTION_PATHS:
    if path.exists():
        SYSTEM_INSTRUCTION = path.read_text(encoding='utf-8')
        break

if SYSTEM_INSTRUCTION is None:
    SYSTEM_INSTRUCTION = (
        'You are an expert study-notes writer for students. '
        'Generate structured notes using the provided schema.'
    )

USER_PROMPT_TEMPLATE_TEXT = None
for path in USER_PROMPT_TEXT_PATHS:
    if path.exists():
        USER_PROMPT_TEMPLATE_TEXT = path.read_text(encoding='utf-8')
        break

if USER_PROMPT_TEMPLATE_TEXT is None:
    USER_PROMPT_TEMPLATE_TEXT = (
        'Generate structured study notes from the document below.\n\n'
        'Detected outline (use these as your section headings if non-empty):\n'
        '{outline}\n\n'
        '--- BEGIN DOCUMENT TEXT ---\n'
        '{text}\n'
        '--- END DOCUMENT TEXT ---\n'
    )

USER_PROMPT_TEMPLATE_VISION = None
for path in USER_PROMPT_VISION_PATHS:
    if path.exists():
        USER_PROMPT_TEMPLATE_VISION = path.read_text(encoding='utf-8')
        break

if USER_PROMPT_TEMPLATE_VISION is None:
    USER_PROMPT_TEMPLATE_VISION = (
        'Generate structured study notes from the attached PDF document.\n\n'
        'The PDF is scanned or image-based. Read the page images directly: '
        'perform\n'
        'OCR, interpret diagrams and equations, and produce the structured '
        'notes\n'
        'defined by the schema. Use surrounding context to correct likely OCR '
        'errors.\n\n'
        'Detected outline (use these as your section headings if non-empty):\n'
        '{outline}\n'
    )

NOTES_SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'title': {'type': 'STRING'},
        'summary': {'type': 'STRING'},
        'learning_objectives': {
            'type': 'ARRAY',
            'items': {'type': 'STRING'},
        },
        'key_terms': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'term': {'type': 'STRING'},
                    'definition': {'type': 'STRING'},
                },
                'required': ['term', 'definition'],
            },
        },
        'flashcards': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'question': {'type': 'STRING'},
                    'answer': {'type': 'STRING'},
                },
                'required': ['question', 'answer'],
            },
        },
        'sections': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'heading': {'type': 'STRING'},
                    'overview': {'type': 'STRING'},
                    'subtopics': {
                        'type': 'ARRAY',
                        'items': {
                            'type': 'OBJECT',
                            'properties': {
                                'heading': {'type': 'STRING'},
                                'content_md': {'type': 'STRING'},
                                'examples': {
                                    'type': 'ARRAY',
                                    'items': {'type': 'STRING'},
                                },
                                'key_takeaways': {
                                    'type': 'ARRAY',
                                    'items': {'type': 'STRING'},
                                },
                            },
                            'required': ['heading', 'content_md'],
                        },
                    },
                },
                'required': ['heading', 'overview', 'subtopics'],
            },
        },
    },
    'required': [
        'title',
        'summary',
        'learning_objectives',
        'key_terms',
        'flashcards',
        'sections',
    ],
}
