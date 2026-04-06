from unittest.mock import patch

from django.test import TestCase

from apps.subjects.models import Subject, SubTopic, Topic
from exams.models import Exam, ExamSubject, ExamSubjectCatalog
from scripts.question_generator import (
    DailyQuestionGenerator,
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


class DailyQuestionGeneratorTests(TestCase):

    def setUp(self):
        self.physics = Subject.objects.create(name='Physics')
        self.chemistry = Subject.objects.create(name='Chemistry')
        # Physics has 1 topic with 1 subtopic
        self.mechanics = Topic.objects.create(
            subject=self.physics, name='Mechanics',
        )
        self.kinematics = SubTopic.objects.create(
            topic=self.mechanics, name='Kinematics',
        )
        # Chemistry has no topics

    def test_get_combinations_builds_all_levels(self):
        gen = DailyQuestionGenerator()
        combos = gen.get_combinations()
        # Physics: subject-only + topic-only + topic+subtopic = 3
        # Chemistry: subject-only = 1
        # Total = 4
        self.assertEqual(len(combos), 4)

    def test_combinations_include_subject_only(self):
        gen = DailyQuestionGenerator()
        combos = gen.get_combinations()
        subject_only = [
            c for c in combos
            if c['topic_id'] is None and c['subtopic_id'] is None
        ]
        self.assertEqual(len(subject_only), 2)
        names = {c['subject_name'] for c in subject_only}
        self.assertEqual(names, {'Physics', 'Chemistry'})

    def test_combinations_include_topic_without_subtopic(self):
        gen = DailyQuestionGenerator()
        combos = gen.get_combinations()
        topic_only = [
            c for c in combos
            if c['topic_id'] is not None and c['subtopic_id'] is None
        ]
        self.assertEqual(len(topic_only), 1)
        self.assertEqual(topic_only[0]['topic_id'], self.mechanics.id)

    def test_combinations_include_full_scope(self):
        gen = DailyQuestionGenerator()
        combos = gen.get_combinations()
        full = [c for c in combos if c['subtopic_id'] is not None]
        self.assertEqual(len(full), 1)
        self.assertEqual(full[0]['subtopic_id'], self.kinematics.id)

    def test_get_combinations_empty_when_no_subjects(self):
        Subject.objects.all().delete()
        gen = DailyQuestionGenerator()
        self.assertEqual(len(gen.get_combinations()), 0)

    @patch('scripts.question_generator.QuestionInterface.generate_daily_questions')
    def test_run_all_difficulties(self, mock_gen):
        mock_gen.return_value = {'status': 'generated', 'count': 10}
        gen = DailyQuestionGenerator()
        report = gen.run()
        # 4 combos × 3 difficulties = 12 calls
        self.assertEqual(mock_gen.call_count, 12)
        self.assertEqual(report['total_success'], 12)
        self.assertEqual(report['total_failed'], 0)

    @patch('scripts.question_generator.QuestionInterface.generate_daily_questions')
    def test_run_passes_topic_and_subtopic_ids(self, mock_gen):
        mock_gen.return_value = {'status': 'generated', 'count': 10}
        gen = DailyQuestionGenerator(difficulties=('easy',))
        gen.run()
        # Find the call with subtopic
        calls = mock_gen.call_args_list
        subtopic_calls = [
            c for c in calls if c.kwargs.get('subtopic_id') is not None
        ]
        self.assertEqual(len(subtopic_calls), 1)
        self.assertEqual(
            subtopic_calls[0].kwargs['subtopic_id'], self.kinematics.id,
        )

    @patch('scripts.question_generator.QuestionInterface.generate_daily_questions')
    def test_run_records_failures(self, mock_gen):
        mock_gen.return_value = {'error': 'Gemini exploded'}
        gen = DailyQuestionGenerator(difficulties=('easy',))
        report = gen.run()
        self.assertEqual(report['total_success'], 0)
        self.assertEqual(report['total_failed'], 4)
        self.assertEqual(report['failures'][0]['error'], 'Gemini exploded')

    @patch('scripts.question_generator.QuestionInterface.generate_daily_questions')
    def test_run_skipped_counted_as_success(self, mock_gen):
        mock_gen.return_value = {'status': 'skipped', 'reason': 'already_generated'}
        gen = DailyQuestionGenerator(difficulties=('easy',))
        report = gen.run()
        self.assertEqual(report['total_success'], 4)
        self.assertEqual(report['total_failed'], 0)
        self.assertEqual(report['successes'][0]['source'], 'skipped')
