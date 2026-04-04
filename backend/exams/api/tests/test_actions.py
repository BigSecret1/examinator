from unittest.mock import patch

from django.core.cache import cache
from django.http import Http404
from django.test import TestCase

from apps.subjects.models import Subject
from exams.api.actions import ExamAPIAction, UpstreamError
from exams.models import Exam, ExamQuestion, ExamQuestionAnswer, ExamSubject


def _gemini_success_response():
    """A valid Gemini response with 1 question (4 answers, 1 correct)."""
    return {
        'status': 'success',
        'questions': [
            {
                'text': 'What is 2+2?',
                'explanation': '2+2 equals 4.',
                'answers': [
                    {'text': '3', 'is_correct': False},
                    {'text': '4', 'is_correct': True},
                    {'text': '5', 'is_correct': False},
                    {'text': '6', 'is_correct': False},
                ],
            },
        ],
    }


class ValidateExamSubjectTests(TestCase):
    """Tests for ExamAPIAction.validate_exam_subject."""

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Physics')
        self.exam = Exam.objects.create(name='JEE Main', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject)

    def test_returns_exam_and_subject_when_valid(self):
        exam, subject = ExamAPIAction.validate_exam_subject(
            self.exam.pk, self.subject.pk
        )
        assert exam == self.exam
        assert subject == self.subject

    def test_raises_when_exam_not_found(self):
        with self.assertRaises(Http404):
            ExamAPIAction.validate_exam_subject(99999, self.subject.pk)

    def test_raises_when_exam_inactive(self):
        self.exam.is_active = False
        self.exam.save()
        with self.assertRaises(Http404):
            ExamAPIAction.validate_exam_subject(self.exam.pk, self.subject.pk)

    def test_raises_when_subject_not_found(self):
        with self.assertRaises(Http404):
            ExamAPIAction.validate_exam_subject(self.exam.pk, 99999)

    def test_raises_when_subject_not_linked_to_exam(self):
        other_subject, _ = Subject.objects.get_or_create(name='Chemistry')
        with self.assertRaises(Http404):
            ExamAPIAction.validate_exam_subject(self.exam.pk, other_subject.pk)


class GetDailyQuestionsFromCacheTests(TestCase):
    """Tests for cache hit path."""

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Physics')
        self.exam = Exam.objects.create(name='JEE Cache Test', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject)

    def tearDown(self):
        cache.clear()

    @patch('exams.api.actions.cache')
    def test_returns_cached_data(self, mock_cache):
        cached_data = [{'id': 1, 'text': 'cached question'}]
        mock_cache.get.return_value = cached_data

        result = ExamAPIAction.get_daily_questions(
            self.exam.pk, self.subject.pk
        )

        assert result['source'] == 'cache'
        assert result['data'] == cached_data


class GetDailyQuestionsFromDBTests(TestCase):
    """Tests for DB hit path (questions already exist for today)."""

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Physics')
        self.exam = Exam.objects.create(name='JEE DB Test', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject)

    def tearDown(self):
        cache.clear()

    def test_returns_from_db_when_enough_questions_exist(self):
        for i in range(10):
            q = ExamQuestion.objects.create(
                exam=self.exam,
                subject=self.subject,
                text=f'DB question {i}',
                difficulty='medium',
            )
            for j in range(4):
                ExamQuestionAnswer.objects.create(
                    question=q,
                    text=f'Answer {j}',
                    is_correct=(j == 0),
                )

        result = ExamAPIAction.get_daily_questions(
            self.exam.pk, self.subject.pk, difficulty='medium', count=10
        )

        assert result['source'] == 'db'
        assert len(result['data']) == 10


class GetDailyQuestionsFromGeminiTests(TestCase):
    """Tests for Gemini generation path."""

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Physics')
        self.exam = Exam.objects.create(name='JEE Gemini Test', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject)

    def tearDown(self):
        cache.clear()

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_generates_and_persists_questions(self, mock_generate):
        mock_generate.return_value = _gemini_success_response()

        result = ExamAPIAction.get_daily_questions(
            self.exam.pk, self.subject.pk, difficulty='medium', count=1
        )

        assert result['source'] == 'generated'
        assert len(result['data']) == 1
        assert ExamQuestion.objects.count() >= 1
        assert ExamQuestionAnswer.objects.count() >= 4

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_persisted_question_has_correct_fields(self, mock_generate):
        mock_generate.return_value = _gemini_success_response()

        ExamAPIAction.get_daily_questions(
            self.exam.pk, self.subject.pk, difficulty='hard', count=1
        )

        q = ExamQuestion.objects.last()
        assert q.text == 'What is 2+2?'
        assert q.explanation == '2+2 equals 4.'
        assert q.difficulty == 'hard'
        assert q.answers.count() == 4
        assert q.answers.filter(is_correct=True).count() == 1

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_caches_generated_data(self, mock_generate):
        mock_generate.return_value = _gemini_success_response()

        result1 = ExamAPIAction.get_daily_questions(
            self.exam.pk, self.subject.pk, difficulty='medium', count=1
        )
        assert result1['source'] == 'generated'

        # Second call should hit cache
        result2 = ExamAPIAction.get_daily_questions(
            self.exam.pk, self.subject.pk, difficulty='medium', count=1
        )
        assert result2['source'] == 'cache'
        mock_generate.assert_called_once()

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_raises_on_invalid_topic_response(self, mock_generate):
        mock_generate.return_value = {
            'status': 'invalid_topic',
            'message': 'Physics does not belong to this exam.',
            'questions': [],
        }

        with self.assertRaises(UpstreamError) as ctx:
            ExamAPIAction.get_daily_questions(
                self.exam.pk, self.subject.pk
            )

        assert 'Physics does not belong' in str(ctx.exception.detail)

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_raises_when_answer_count_not_4(self, mock_generate):
        bad_response = _gemini_success_response()
        bad_response['questions'][0]['answers'] = bad_response['questions'][0]['answers'][:3]
        mock_generate.return_value = bad_response

        with self.assertRaises(UpstreamError) as ctx:
            ExamAPIAction.get_daily_questions(
                self.exam.pk, self.subject.pk, count=1
            )

        assert '4 options' in str(ctx.exception.detail)

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_raises_when_no_correct_answer(self, mock_generate):
        bad_response = _gemini_success_response()
        for a in bad_response['questions'][0]['answers']:
            a['is_correct'] = False
        mock_generate.return_value = bad_response

        with self.assertRaises(UpstreamError) as ctx:
            ExamAPIAction.get_daily_questions(
                self.exam.pk, self.subject.pk, count=1
            )

        assert '1 correct answer' in str(ctx.exception.detail)

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_raises_when_multiple_correct_answers(self, mock_generate):
        bad_response = _gemini_success_response()
        for a in bad_response['questions'][0]['answers']:
            a['is_correct'] = True
        mock_generate.return_value = bad_response

        with self.assertRaises(UpstreamError) as ctx:
            ExamAPIAction.get_daily_questions(
                self.exam.pk, self.subject.pk, count=1
            )

        assert '1 correct answer' in str(ctx.exception.detail)

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_does_not_persist_on_validation_failure(self, mock_generate):
        bad_response = _gemini_success_response()
        bad_response['questions'][0]['answers'] = bad_response['questions'][0]['answers'][:2]
        mock_generate.return_value = bad_response

        initial_count = ExamQuestion.objects.count()
        with self.assertRaises(UpstreamError):
            ExamAPIAction.get_daily_questions(
                self.exam.pk, self.subject.pk, count=1
            )

        assert ExamQuestion.objects.count() == initial_count
