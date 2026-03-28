SYSTEM_INSTRUCTION = '''\
You are an expert assessment item writer.
Validation Rule: If the requested Topic does not logically belong to the Subject,
set status to 'invalid_topic' and return an empty questions array.
Rules: 4 options per question, exactly 1 correct, random correct answer placement,
no 'All of the above', distinct and plausible distractors. Include detailed explanations.
'''

USER_PROMPT_TEMPLATE = '''\
Generate exactly {count} unique multiple-choice questions:
- Exam: {exam}
- Subject: {subject}
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
        },
        'message': {
            'type': 'STRING',
        },
        'questions': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'text': {'type': 'STRING'},
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
                    'explanation': {'type': 'STRING'},
                },
                'required': ['text', 'answers', 'explanation'],
            },
        },
    },
    'required': ['status', 'questions'],
}
