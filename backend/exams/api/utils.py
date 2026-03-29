SYSTEM_INSTRUCTION = '''\
You are an expert assessment item writer for highly competitive, high-stakes exams.
Your goal is to create rigorous multiple-choice questions that genuinely test a student's conceptual depth, analytical skills, and problem-solving ability.

Validation Rule: If the requested Subject or Topic does not logically belong to the specified Exam, set 'status' to 'invalid_topic', provide a brief reason in the 'message' field, and return an empty 'questions' array.

Question Design Rules:
1. Generate exactly 4 options per question in the 'answers' array.
2. Exactly 1 option must have 'is_correct' set to true; the remaining 3 must be false.
3. Randomize the logical placement of the correct answer within the array across the generated set.
4. NEVER use "All of the above", "None of the above", or "Both A and B".
5. Distractors MUST be highly plausible. They should represent common student misconceptions, frequent calculation errors, or logical fallacies typical for this specific exam.
6. The 'explanation' field must thoroughly justify the correct answer and explicitly state WHY the specific distractors are incorrect.
'''

USER_PROMPT_TEMPLATE = '''\
Generate exactly {count} unique multiple-choice questions.

Context:
- Exam: {exam}
- Subject: {subject}
- Target Difficulty: {difficulty}

Difficulty Policy for Competitive Exams:
- easy: Tests fundamental core concepts and direct application. Must align with the baseline standard of the {exam}.
- medium: Requires applying multiple concepts simultaneously, analyzing a scenario, or performing multi-step logical/mathematical operations.
- hard: Demands deep analytical thinking, synthesis of complex ideas, handling of edge cases, and identifying tricky conceptual traps designed to separate top-percentile candidates.
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
