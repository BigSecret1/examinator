from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.http import Http404
from django.test import TestCase
from django.utils import timezone

from apps.questions.api.actions import QuestionAPIAction, UpstreamError
from apps.questions.models import Answer, Question
from apps.subjects.models import Subject, SubTopic, Topic


def _gemini_success_response(count=1):
    """A valid Gemini response with `count` questions."""
    questions = []
    for i in range(count):
        questions.append({
            'text': f'What is {i}+{i}?',
            'explanation': f'{i}+{i} equals {i * 2}.',
            'answers': [
                {'text': f'{i * 2}', 'is_correct': True},
                {'text': f'{i * 2 + 1}', 'is_correct': False},
                {'text': f'{i * 2 + 2}', 'is_correct': False},
                {'text': f'{i * 2 + 3}', 'is_correct': False},
            ],
        })
    return {'status': 'success', 'questions': questions}


def _create_question_for_date(topic, difficulty, date, subtopic=None, count=1):
    """Create questions backdated to a specific date."""
    questions = []
    for i in range(count):
        q = Question.objects.create(
            topic=topic, subtopic=subtopic,
            text=f'Q{i}', difficulty=difficulty,
        )
        for j in range(4):
            Answer.objects.create(
                question=q, text=f'A{j}', is_correct=(j == 0),
            )
        questions.append(q)
    Question.objects.filter(
        pk__in=[q.pk for q in questions],
    ).update(created_at=timezone.make_aware(
        timezone.datetime.combine(date, timezone.datetime.min.time()),
    ))
    return questions


# ── _persist_answers ──


class PersistAnswersTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Physics')
        self.topic = Topic.objects.create(subject=self.subject, name='Mechanics')
        self.question = Question.objects.create(
            topic=self.topic, text='Test?', difficulty='easy',
        )

    def test_creates_answers_for_question(self):
        answers_data = [
            {'text': 'A', 'is_correct': True},
            {'text': 'B', 'is_correct': False},
            {'text': 'C', 'is_correct': False},
            {'text': 'D', 'is_correct': False},
        ]
        QuestionAPIAction._persist_answers(self.question, answers_data)

        self.assertEqual(self.question.answers.count(), 4)
        self.assertEqual(self.question.answers.filter(is_correct=True).count(), 1)
        self.assertEqual(
            self.question.answers.filter(is_correct=True).first().text, 'A',
        )

    def test_creates_no_answers_when_empty(self):
        QuestionAPIAction._persist_answers(self.question, [])
        self.assertEqual(self.question.answers.count(), 0)


# ── _persist_questions ──


class PersistQuestionsTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Physics')
        self.topic = Topic.objects.create(subject=self.subject, name='Mechanics')

    def test_creates_questions_with_answers(self):
        raw = _gemini_success_response(count=2)['questions']

        created = QuestionAPIAction._persist_questions(
            raw, self.topic, None, 'medium',
        )

        self.assertEqual(len(created), 2)
        self.assertEqual(Question.objects.count(), 2)
        for q in created:
            self.assertEqual(q.answers.count(), 4)
            self.assertEqual(q.difficulty, 'medium')
            self.assertEqual(q.topic, self.topic)
            self.assertIsNone(q.subtopic)

    def test_sets_subtopic_when_provided(self):
        subtopic = SubTopic.objects.create(topic=self.topic, name='Kinematics')
        raw = _gemini_success_response(count=1)['questions']

        created = QuestionAPIAction._persist_questions(
            raw, self.topic, subtopic, 'hard',
        )

        self.assertEqual(created[0].subtopic, subtopic)
        self.assertEqual(created[0].difficulty, 'hard')

    def test_stores_explanation(self):
        raw = _gemini_success_response(count=1)['questions']

        created = QuestionAPIAction._persist_questions(
            raw, self.topic, None, 'easy',
        )

        self.assertEqual(created[0].explanation, '0+0 equals 0.')

    def test_empty_raw_questions_returns_empty_list(self):
        created = QuestionAPIAction._persist_questions(
            [], self.topic, None, 'easy',
        )
        self.assertEqual(created, [])
        self.assertEqual(Question.objects.count(), 0)


# ── get_daily_questions: resolution errors ──


class GetDailyQuestionsResolutionTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Physics')
        self.topic = Topic.objects.create(subject=self.subject, name='Mechanics')

    def test_raises_404_for_invalid_subject(self):
        with self.assertRaises(Http404):
            QuestionAPIAction.get_daily_questions(subject_id=99999)

    def test_raises_404_for_invalid_topic(self):
        with self.assertRaises(Http404):
            QuestionAPIAction.get_daily_questions(
                subject_id=self.subject.pk, topic_id=99999,
            )

    def test_raises_404_for_topic_wrong_subject(self):
        other_subject = Subject.objects.create(name='Chemistry')
        with self.assertRaises(Http404):
            QuestionAPIAction.get_daily_questions(
                subject_id=other_subject.pk, topic_id=self.topic.pk,
            )

    def test_raises_404_for_invalid_subtopic(self):
        with self.assertRaises(Http404):
            QuestionAPIAction.get_daily_questions(
                subject_id=self.subject.pk,
                topic_id=self.topic.pk,
                subtopic_id=99999,
            )


# ── get_daily_questions: cache ──


class GetDailyQuestionsCacheTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Physics')

    def tearDown(self):
        cache.clear()

    @patch('apps.questions.api.actions.cache')
    def test_returns_cached_data(self, mock_cache):
        cached_data = [{'id': 1, 'text': 'cached question'}]
        mock_cache.get.return_value = cached_data

        result = QuestionAPIAction.get_daily_questions(
            subject_id=self.subject.pk,
        )

        self.assertEqual(result['source'], 'cache')
        self.assertEqual(result['data'], cached_data)


# ── get_daily_questions: DB path (yesterday's questions) ──


class GetDailyQuestionsDBTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Physics')
        self.topic = Topic.objects.create(subject=self.subject, name='Mechanics')
        self.yesterday = timezone.localdate() - timedelta(days=1)

    def tearDown(self):
        cache.clear()

    def test_returns_yesterday_questions_from_db(self):
        _create_question_for_date(
            self.topic, 'medium', self.yesterday, count=10,
        )

        result = QuestionAPIAction.get_daily_questions(
            subject_id=self.subject.pk, difficulty='medium', count=10,
        )

        self.assertEqual(result['source'], 'db')
        self.assertEqual(len(result['data']), 10)

    def test_returns_empty_when_no_yesterday_questions(self):
        result = QuestionAPIAction.get_daily_questions(
            subject_id=self.subject.pk, difficulty='medium', count=10,
        )

        self.assertEqual(result['source'], 'db')
        self.assertEqual(result['data'], [])

    def test_ignores_today_questions(self):
        # Create questions dated today — should NOT be returned
        for i in range(10):
            q = Question.objects.create(
                topic=self.topic, text=f'Q{i}', difficulty='medium',
            )
            for j in range(4):
                Answer.objects.create(
                    question=q, text=f'A{j}', is_correct=(j == 0),
                )

        result = QuestionAPIAction.get_daily_questions(
            subject_id=self.subject.pk, difficulty='medium', count=10,
        )

        self.assertEqual(result['source'], 'db')
        self.assertEqual(result['data'], [])

    def test_returns_filtered_by_topic(self):
        other_topic = Topic.objects.create(
            subject=self.subject, name='Thermodynamics',
        )
        _create_question_for_date(
            self.topic, 'easy', self.yesterday, count=10,
        )
        _create_question_for_date(
            other_topic, 'easy', self.yesterday, count=10,
        )

        result = QuestionAPIAction.get_daily_questions(
            subject_id=self.subject.pk,
            topic_id=self.topic.pk,
            difficulty='easy',
            count=10,
        )

        self.assertEqual(result['source'], 'db')
        self.assertEqual(len(result['data']), 10)
        for item in result['data']:
            self.assertEqual(item['topic_name'], 'Mechanics')


# ── generate_daily_questions ──


class GenerateDailyQuestionsTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Physics')
        self.topic = Topic.objects.create(subject=self.subject, name='Mechanics')

    def tearDown(self):
        cache.clear()

    def test_raises_404_for_invalid_subject(self):
        with self.assertRaises(Http404):
            QuestionAPIAction.generate_daily_questions(subject_id=99999)

    def test_raises_404_for_invalid_topic(self):
        with self.assertRaises(Http404):
            QuestionAPIAction.generate_daily_questions(
                subject_id=self.subject.pk, topic_id=99999,
            )

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_generates_and_persists_questions(self, mock_generate):
        mock_generate.return_value = _gemini_success_response(count=10)

        result = QuestionAPIAction.generate_daily_questions(
            subject_id=self.subject.pk, difficulty='medium', count=10,
        )

        self.assertEqual(result['status'], 'generated')
        self.assertEqual(result['count'], 10)
        self.assertEqual(Question.objects.count(), 10)
        self.assertEqual(Answer.objects.count(), 40)

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_creates_general_topic_when_no_topic_id(self, mock_generate):
        mock_generate.return_value = _gemini_success_response(count=1)

        QuestionAPIAction.generate_daily_questions(
            subject_id=self.subject.pk, count=1,
        )

        general = Topic.objects.filter(subject=self.subject, name='General')
        self.assertTrue(general.exists())
        self.assertEqual(Question.objects.first().topic.name, 'General')

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_uses_specified_topic_for_storage(self, mock_generate):
        mock_generate.return_value = _gemini_success_response(count=1)

        QuestionAPIAction.generate_daily_questions(
            subject_id=self.subject.pk,
            topic_id=self.topic.pk,
            count=1,
        )

        self.assertEqual(Question.objects.first().topic, self.topic)

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_raises_upstream_error_on_invalid_topic(self, mock_generate):
        mock_generate.return_value = {
            'status': 'invalid_topic',
            'message': 'Topic does not belong to subject.',
            'questions': [],
        }

        with self.assertRaises(UpstreamError):
            QuestionAPIAction.generate_daily_questions(
                subject_id=self.subject.pk, count=1,
            )

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_persisted_question_has_correct_fields(self, mock_generate):
        mock_generate.return_value = _gemini_success_response(count=1)

        QuestionAPIAction.generate_daily_questions(
            subject_id=self.subject.pk, difficulty='hard', count=1,
        )

        q = Question.objects.last()
        self.assertEqual(q.text, 'What is 0+0?')
        self.assertEqual(q.explanation, '0+0 equals 0.')
        self.assertEqual(q.difficulty, 'hard')
        self.assertEqual(q.answers.count(), 4)
        self.assertEqual(q.answers.filter(is_correct=True).count(), 1)

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_skips_when_already_generated_today(self, mock_generate):
        # Create enough questions for today
        for i in range(10):
            q = Question.objects.create(
                topic=self.topic, text=f'Q{i}', difficulty='medium',
            )
            Answer.objects.create(question=q, text='A', is_correct=True)

        result = QuestionAPIAction.generate_daily_questions(
            subject_id=self.subject.pk,
            topic_id=self.topic.pk,
            difficulty='medium',
            count=10,
        )

        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'already_generated')
        mock_generate.assert_not_called()

    @patch('apps.questions.api.actions.cache')
    def test_skips_when_lock_held(self, mock_cache):
        mock_cache.get.return_value = None
        mock_cache.add.return_value = False  # lock already held

        result = QuestionAPIAction.generate_daily_questions(
            subject_id=self.subject.pk, count=10,
        )

        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'generation_in_progress')

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_releases_lock_after_generation(self, mock_generate):
        mock_generate.return_value = _gemini_success_response(count=1)

        QuestionAPIAction.generate_daily_questions(
            subject_id=self.subject.pk, count=1,
        )

        # Lock should be released — cache.add should succeed
        today = timezone.localdate()
        lock_key = f"gen_lock:q:{self.subject.id}:all:all:medium:{today}"
        self.assertTrue(cache.add(lock_key, 'test', timeout=5))

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_raises_upstream_error_on_insufficient_questions(self, mock_generate):
        mock_generate.return_value = _gemini_success_response(count=3)

        with self.assertRaises(UpstreamError):
            QuestionAPIAction.generate_daily_questions(
                subject_id=self.subject.pk, count=10,
            )

    @patch('apps.questions.api.actions.GeminiClientInterface.generate')
    def test_raises_upstream_error_on_bad_answer_count(self, mock_generate):
        response = _gemini_success_response(count=1)
        response['questions'][0]['answers'] = [
            {'text': 'A', 'is_correct': True},
            {'text': 'B', 'is_correct': False},
        ]
        mock_generate.return_value = response

        with self.assertRaises(UpstreamError):
            QuestionAPIAction.generate_daily_questions(
                subject_id=self.subject.pk, count=1,
            )
