import logging

from .actions import ExamAPIAction

logger = logging.getLogger(__name__)

DIFFICULTIES = ('easy', 'medium', 'hard')


class ExamInterface:
    """Public interface for generating exam-subject daily questions."""

    @staticmethod
    def generate_daily_questions(exam_id, subject_id, difficulty='medium', count=10):
        """Call the action layer and return the result dict.

        Returns:
            dict with keys 'source' and 'data' on success,
            or dict with 'error' on failure.
        """
        try:
            return ExamAPIAction.get_daily_questions(
                exam_id, subject_id, difficulty=difficulty, count=count,
            )
        except Exception as exc:
            logger.exception(
                'generate_daily_questions failed exam=%s subject=%s difficulty=%s',
                exam_id, subject_id, difficulty,
            )
            return {'error': str(exc)}
