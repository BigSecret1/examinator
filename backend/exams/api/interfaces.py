import logging

from .actions import ExamAPIAction

logger = logging.getLogger(__name__)

DIFFICULTIES = ('easy', 'medium', 'hard')


class ExamInterface:

    @staticmethod
    def generate_daily_questions(exam_id, subject_id, difficulty='medium', count=10):
        try:
            return ExamAPIAction.generate_daily_questions(
                exam_id, subject_id, difficulty=difficulty, count=count,
            )
        except Exception as exc:
            logger.exception(
                'generate_daily_questions failed exam=%s subject=%s difficulty=%s',
                exam_id, subject_id, difficulty,
            )
            return {'error': str(exc)}
