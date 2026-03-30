import time

from django.conf import settings
from django.test import TestCase, override_settings, tag

from geminiclient.api.actions import GeminiClientAction
from exams.api.utils import MCQ_SCHEMA, SYSTEM_INSTRUCTION, USER_PROMPT_TEMPLATE


def _skip_without_api_key():
    return not getattr(settings, 'GEMINI_API_KEY', '')


def _build_prompt(exam='JEE Main', subject='Physics', difficulty='medium', count=10):
    return USER_PROMPT_TEMPLATE.format(
        count=count,
        exam=exam,
        subject=subject,
        difficulty=difficulty,
    )


def _make_client():
    return GeminiClientAction(
        system_instruction=SYSTEM_INSTRUCTION,
        response_schema=MCQ_SCHEMA,
    )


@tag('integration')
class GeminiExamResponseStructureTests(TestCase):
    response = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if _skip_without_api_key():
            return
        client = _make_client()
        prompt = _build_prompt(count=10)
        cls.response = client.generate(prompt)

    def setUp(self):
        if _skip_without_api_key():
            self.skipTest('GEMINI_API_KEY not configured')

    def test_gemini_returns_valid_dict(self):
        """Response is a parsed dict, not None."""
        self.assertIsInstance(self.response, dict)

    def test_response_has_required_top_level_keys(self):
        """Must contain 'status' and 'questions' per MCQ_SCHEMA."""
        self.assertIn('status', self.response)
        self.assertIn('questions', self.response)

    def test_status_is_success_for_valid_subject(self):
        self.assertEqual(self.response['status'], 'success')

    def test_returns_exactly_10_questions(self):
        self.assertEqual(len(self.response['questions']), 10)

    def test_each_question_has_required_fields(self):
        for i, q in enumerate(self.response['questions']):
            with self.subTest(question=i):
                self.assertIn('text', q)
                self.assertIn('answers', q)
                self.assertIn('explanation', q)

    def test_each_question_has_exactly_4_answers(self):
        for i, q in enumerate(self.response['questions']):
            with self.subTest(question=i):
                self.assertEqual(len(q['answers']), 4)

    def test_each_answer_has_text_and_is_correct(self):
        for i, q in enumerate(self.response['questions']):
            for j, a in enumerate(q['answers']):
                with self.subTest(question=i, answer=j):
                    self.assertIn('text', a)
                    self.assertIn('is_correct', a)
                    self.assertIsInstance(a['text'], str)
                    self.assertIsInstance(a['is_correct'], bool)

    def test_each_question_has_exactly_one_correct_answer(self):
        for i, q in enumerate(self.response['questions']):
            correct_count = sum(1 for a in q['answers'] if a['is_correct'])
            with self.subTest(question=i):
                self.assertEqual(correct_count, 1)

    def test_question_text_is_non_empty(self):
        for i, q in enumerate(self.response['questions']):
            with self.subTest(question=i):
                self.assertIsInstance(q['text'], str)
                self.assertGreater(len(q['text'].strip()), 10)

    def test_explanation_is_non_empty(self):
        for i, q in enumerate(self.response['questions']):
            with self.subTest(question=i):
                self.assertIsInstance(q['explanation'], str)
                self.assertGreater(len(q['explanation'].strip()), 10)

    def test_answer_texts_are_distinct_per_question(self):
        for i, q in enumerate(self.response['questions']):
            texts = [a['text'].strip().lower() for a in q['answers']]
            with self.subTest(question=i):
                self.assertEqual(len(texts), len(set(texts)))

    def test_question_texts_are_unique_across_response(self):
        texts = [q['text'].strip() for q in self.response['questions']]
        self.assertEqual(len(texts), len(set(texts)))


@tag('integration')
class GeminiExamQuestionCountTests(TestCase):

    def setUp(self):
        if _skip_without_api_key():
            self.skipTest('GEMINI_API_KEY not configured')

    def test_returns_exact_count_for_small_request(self):
        client = _make_client()
        prompt = _build_prompt(count=3)
        response = client.generate(prompt)
        self.assertEqual(len(response['questions']), 3)

    def test_returns_exact_count_for_large_request(self):
        client = _make_client()
        prompt = _build_prompt(count=20)
        response = client.generate(prompt)
        self.assertEqual(len(response['questions']), 20)


@tag('integration')
class GeminiExamInvalidTopicTests(TestCase):
    response = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if _skip_without_api_key():
            return
        client = _make_client()
        prompt = _build_prompt(exam='JEE Main', subject='Culinary Arts')
        cls.response = client.generate(prompt)

    def setUp(self):
        if _skip_without_api_key():
            self.skipTest('GEMINI_API_KEY not configured')

    def test_status_is_invalid_topic(self):
        self.assertEqual(self.response['status'], 'invalid_topic')

    def test_questions_array_is_empty(self):
        self.assertEqual(len(self.response.get('questions', [])), 0)

    def test_message_is_non_empty(self):
        self.assertIn('message', self.response)
        self.assertIsInstance(self.response['message'], str)
        self.assertGreater(len(self.response['message'].strip()), 0)


@tag('integration')
class GeminiExamDifficultyTests(TestCase):

    def setUp(self):
        if _skip_without_api_key():
            self.skipTest('GEMINI_API_KEY not configured')

    def _assert_valid_response(self, response, expected_count):
        self.assertEqual(response['status'], 'success')
        self.assertEqual(len(response['questions']), expected_count)
        for q in response['questions']:
            self.assertEqual(len(q['answers']), 4)
            self.assertEqual(sum(1 for a in q['answers'] if a['is_correct']), 1)

    def test_easy_difficulty_generates_valid_response(self):
        client = _make_client()
        prompt = _build_prompt(difficulty='easy', count=5)
        response = client.generate(prompt)
        self._assert_valid_response(response, 5)

    def test_hard_difficulty_generates_valid_response(self):
        client = _make_client()
        prompt = _build_prompt(difficulty='hard', count=5)
        response = client.generate(prompt)
        self._assert_valid_response(response, 5)
