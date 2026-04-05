import logging

from .actions import QuestionAPIAction

logger = logging.getLogger(__name__)

DIFFICULTIES = ('easy', 'medium', 'hard')


class QuestionInterface:

    @staticmethod
    def generate_daily_questions(
            subject_id,
            topic_id=None,
            subtopic_id=None,
            difficulty='medium',
            count=10
    ):
        try:
            return QuestionAPIAction.generate_daily_questions(
                subject_id=subject_id,
                topic_id=topic_id,
                subtopic_id=subtopic_id,
                difficulty=difficulty,
                count=count,
            )
        except Exception as exc:
            logger.exception(
                'generate_daily_questions failed subject=%s topic=%s difficulty=%s',
                subject_id, topic_id, difficulty,
            )
            return {'error': str(exc)}
