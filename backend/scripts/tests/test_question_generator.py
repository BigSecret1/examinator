from unittest.mock import patch

from django.test import TestCase

from exams.models import Exam, ExamSubject, ExamSubjectCatalog
from scripts.question_generator import (
    ExamQuestionGenerator,
    QuestionGeneratorReport,
)


class QuestionGeneratorReportTests(TestCase):

    def test_empty_report(self):
        report = QuestionGeneratorReport()
        summary = report.summary()
        self.assertEqual(summary['total_success'], 0)
        self.assertEqual(summary['total_failed'], 0)

    def test_add_success_and_failure(self):
        report = QuestionGeneratorReport()
        report.add_success('JEE', 'Physics', 'easy', 'generated', 10)
        report.add_failure('JEE', 'Chemistry', 'hard', 'timeout')
        summary = report.summary()
        self.assertEqual(summary['total_success'], 1)
        self.assertEqual(summary['total_failed'], 1)
        self.assertEqual(summary['successes'][0]['exam'], 'JEE')
        self.assertEqual(summary['failures'][0]['error'], 'timeout')


class ExamQuestionGeneratorTests(TestCase):

    def setUp(self):
        self.subject_physics, _ = ExamSubjectCatalog.objects.get_or_create(name='Physics')
        self.subject_chemistry, _ = ExamSubjectCatalog.objects.get_or_create(name='Chemistry')
        self.exam = Exam.objects.create(name='JEE Main', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject_physics)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject_chemistry)

    def test_get_combinations_returns_active_pairs(self):
        gen = ExamQuestionGenerator()
        combos = gen.get_combinations()
        self.assertEqual(len(combos), 2)
        names = {c['subject_name'] for c in combos}
        self.assertEqual(names, {'Physics', 'Chemistry'})

    def test_inactive_exam_excluded(self):
        self.exam.is_active = False
        self.exam.save()
        gen = ExamQuestionGenerator()
        self.assertEqual(len(gen.get_combinations()), 0)

    @patch('scripts.question_generator.ExamInterface.generate_daily_questions')
    def test_run_all_difficulties(self, mock_gen):
        mock_gen.return_value = {'source': 'generated', 'data': [{'id': 1}] * 10}
        gen = ExamQuestionGenerator()
        report = gen.run()
        # 2 subjects × 3 difficulties = 6 calls
        self.assertEqual(mock_gen.call_count, 6)
        self.assertEqual(report['total_success'], 6)
        self.assertEqual(report['total_failed'], 0)

    @patch('scripts.question_generator.ExamInterface.generate_daily_questions')
    def test_run_custom_difficulties(self, mock_gen):
        mock_gen.return_value = {'source': 'generated', 'data': [{'id': 1}]}
        gen = ExamQuestionGenerator(difficulties=('hard',), count=5)
        report = gen.run()
        # 2 subjects × 1 difficulty = 2 calls
        self.assertEqual(mock_gen.call_count, 2)
        self.assertEqual(report['total_success'], 2)

    @patch('scripts.question_generator.ExamInterface.generate_daily_questions')
    def test_run_records_failures(self, mock_gen):
        mock_gen.return_value = {'error': 'Gemini exploded'}
        gen = ExamQuestionGenerator(difficulties=('easy',))
        report = gen.run()
        self.assertEqual(report['total_success'], 0)
        self.assertEqual(report['total_failed'], 2)
        self.assertEqual(report['failures'][0]['error'], 'Gemini exploded')
