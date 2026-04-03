import logging
from abc import ABC, abstractmethod

from exams.api.interfaces import ExamInterface, DIFFICULTIES
from exams.models import ExamSubject

logger = logging.getLogger(__name__)


class QuestionGeneratorReport:

    def __init__(self):
        self.successes = []
        self.failures = []

    def add_success(self, exam_name, subject_name, difficulty, source, count):
        self.successes.append({
            'exam': exam_name,
            'subject': subject_name,
            'difficulty': difficulty,
            'source': source,
            'questions_count': count,
        })

    def add_failure(self, exam_name, subject_name, difficulty, error):
        self.failures.append({
            'exam': exam_name,
            'subject': subject_name,
            'difficulty': difficulty,
            'error': error,
        })

    def summary(self):
        return {
            'total_success': len(self.successes),
            'total_failed': len(self.failures),
            'successes': self.successes,
            'failures': self.failures,
        }


class BaseQuestionGenerator(ABC):

    def __init__(self, difficulties=DIFFICULTIES, count=10):
        self.difficulties = difficulties
        self.count = count
        self.report = QuestionGeneratorReport()

    @abstractmethod
    def get_combinations(self):
        """Return an iterable of dicts with keys: exam_id, exam_name,
        subject_id, subject_name."""

    def _generate(self, combo, difficulty):
        result = ExamInterface.generate_daily_questions(
            exam_id=combo['exam_id'],
            subject_id=combo['subject_id'],
            difficulty=difficulty,
            count=self.count,
        )
        if 'error' in result:
            self.report.add_failure(
                combo['exam_name'], combo['subject_name'],
                difficulty, result['error'],
            )
        else:
            self.report.add_success(
                combo['exam_name'],
                combo['subject_name'],
                difficulty, result.get('source', 'unknown'),
                len(result.get('data', [])),
            )

    def run(self):
        combinations = self.get_combinations()
        for combo in combinations:
            for difficulty in self.difficulties:
                self._generate(combo, difficulty)
        return self.report.summary()


class ExamQuestionGenerator(BaseQuestionGenerator):

    def get_combinations(self):
        rows = (
            ExamSubject.objects
            .filter(exam__is_active=True)
            .select_related('exam', 'subject')
        )
        return [
            {
                'exam_id': row.exam_id,
                'exam_name': row.exam.name,
                'subject_id': row.subject_id,
                'subject_name': row.subject.name,
            }
            for row in rows
        ]
