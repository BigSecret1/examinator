import hashlib
import logging
from datetime import date

from django.core.cache import cache

from apps.questions.api.serializers import QuestionSerializer
from apps.questions.models import Answer, Question
from apps.subjects.models import Subject, Topic
from exams.models import Exam, ExamSubject
from geminiclient.api.interfaces import GeminiClientInterface

from .utils import MCQ_SCHEMA, SYSTEM_INSTRUCTION, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class ExamAPIAction:
    """Business logic layer for exam-related API operations."""

    @staticmethod
    def validate_exam_subject(exam_id, subject_id):
        exam = Exam.objects.get(pk=exam_id, is_active=True)
        subject = Subject.objects.get(pk=subject_id)
        ExamSubject.objects.get(exam=exam, subject=subject)
        return exam, subject

    @staticmethod
    def get_daily_questions(exam_id, subject_id, difficulty='medium', count=10):
        exam, subject = ExamAPIAction.validate_exam_subject(exam_id, subject_id)

        today = date.today().isoformat()
        key_raw = f"exam_daily:{exam.id}:{subject.id}:{difficulty}:{today}"
        cache_key = "edq_" + hashlib.md5(key_raw.encode()).hexdigest()

        # 1. Check cache
        cached = cache.get(cache_key)
        if cached is not None:
            return {'source': 'cache', 'data': cached}

        # 2. Check DB for questions generated today
        storage_topic, _ = Topic.objects.get_or_create(
            subject=subject,
            name='General',
            defaults={'description': 'General questions'},
        )

        qs = Question.objects.filter(
            topic=storage_topic,
            difficulty=difficulty,
            created_at__date=today,
        ).select_related(
            'topic__subject', 'subtopic',
        ).prefetch_related('answers')

        if qs.count() >= count:
            data = QuestionSerializer(qs[:count], many=True).data
            cache.set(cache_key, data, timeout=3600)
            return {'source': 'db', 'data': data}

        # 3. Generate via Gemini
        prompt = USER_PROMPT_TEMPLATE.format(
            count=count,
            exam=exam.name,
            subject=subject.name,
            difficulty=difficulty,
        )

        result = GeminiClientInterface.generate(
            system_instruction=SYSTEM_INSTRUCTION,
            response_schema=MCQ_SCHEMA,
            prompt=prompt,
        )

        if result.get('status') == 'invalid_topic':
            raise ValueError(
                result.get('message', 'The subject does not match the exam.')
            )

        # 4. Validate and persist
        raw_questions = result.get('questions', [])
        created_questions = []

        for q_data in raw_questions:
            answers = q_data.get('answers', [])
            if len(answers) != 4:
                raise ValueError('Each question must have exactly 4 options.')
            if sum(1 for a in answers if a.get('is_correct')) != 1:
                raise ValueError('Each question must have exactly 1 correct answer.')

            q_obj = Question.objects.create(
                topic=storage_topic,
                text=q_data['text'],
                explanation=q_data.get('explanation', ''),
                difficulty=difficulty,
            )
            for a_data in answers:
                Answer.objects.create(
                    question=q_obj,
                    text=a_data['text'],
                    is_correct=a_data['is_correct'],
                )
            created_questions.append(q_obj)

        data = QuestionSerializer(created_questions, many=True).data
        cache.set(cache_key, data, timeout=3600)
        return {'source': 'generated', 'data': data}
