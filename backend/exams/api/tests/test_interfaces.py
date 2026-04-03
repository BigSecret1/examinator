from unittest.mock import patch

from django.test import TestCase

from apps.subjects.models import Subject
from exams.api.interfaces import ExamInterface
from exams.models import Exam, ExamSubject


class ExamInterfaceTests(TestCase):

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Physics')
        self.exam = Exam.objects.create(name='JEE Main', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject)

    @patch('exams.api.interfaces.ExamAPIAction.get_daily_questions')
    def test_returns_action_result_on_success(self, mock_action):
        mock_action.return_value = {'source': 'generated', 'data': [{'id': 1}]}
        result = ExamInterface.generate_daily_questions(
            self.exam.pk, self.subject.pk, difficulty='easy',
        )
        self.assertEqual(result['source'], 'generated')
        self.assertEqual(len(result['data']), 1)
        mock_action.assert_called_once_with(
            self.exam.pk, self.subject.pk, difficulty='easy', count=10,
        )

    @patch('exams.api.interfaces.ExamAPIAction.get_daily_questions')
    def test_returns_error_dict_on_exception(self, mock_action):
        mock_action.side_effect = RuntimeError('upstream down')
        result = ExamInterface.generate_daily_questions(
            self.exam.pk, self.subject.pk,
        )
        self.assertIn('error', result)
        self.assertIn('upstream down', result['error'])
