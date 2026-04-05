from unittest.mock import patch

from django.test import TestCase

from apps.questions.api.interfaces import QuestionInterface
from apps.subjects.models import Subject


class QuestionInterfaceTests(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(name='Physics')

    @patch('apps.questions.api.interfaces.QuestionAPIAction.get_daily_questions')
    def test_returns_action_result_on_success(self, mock_action):
        mock_action.return_value = {
            'source': 'generated',
            'data': [{'id': 1}],
        }

        result = QuestionInterface.get_daily_questions(
            subject_id=self.subject.pk, difficulty='easy',
        )

        self.assertEqual(result['source'], 'generated')
        self.assertEqual(len(result['data']), 1)
        mock_action.assert_called_once_with(
            subject_id=self.subject.pk,
            topic_id=None,
            subtopic_id=None,
            difficulty='easy',
            count=10,
        )

    @patch('apps.questions.api.interfaces.QuestionAPIAction.get_daily_questions')
    def test_passes_all_parameters(self, mock_action):
        mock_action.return_value = {'source': 'db', 'data': []}

        QuestionInterface.get_daily_questions(
            subject_id=self.subject.pk,
            topic_id=5,
            subtopic_id=7,
            difficulty='hard',
            count=20,
        )

        mock_action.assert_called_once_with(
            subject_id=self.subject.pk,
            topic_id=5,
            subtopic_id=7,
            difficulty='hard',
            count=20,
        )

    @patch('apps.questions.api.interfaces.QuestionAPIAction.get_daily_questions')
    def test_returns_error_dict_on_exception(self, mock_action):
        mock_action.side_effect = RuntimeError('Gemini exploded')

        result = QuestionInterface.get_daily_questions(
            subject_id=self.subject.pk,
        )

        self.assertIn('error', result)
        self.assertIn('Gemini exploded', result['error'])
