import hashlib
import logging
from datetime import date

from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status as http_status
from rest_framework.exceptions import APIException

from apps.subjects.models import Subject
from exams.models import Exam, ExamQuestion, ExamQuestionAnswer, ExamSubject
from geminiclient.api.interfaces import GeminiClientInterface

from .utils import MCQ_SCHEMA, SYSTEM_INSTRUCTION, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class UpstreamError(APIException):
    status_code = http_status.HTTP_502_BAD_GATEWAY
    default_detail = 'Upstream service error.'
    default_code = 'upstream_error'

    def get_full_details(self):
        return {'error': str(self.detail)}


class ExamAPIAction:
    """Business logic layer for exam-related API operations."""

    @staticmethod
    def get_exam_subjects(exam_id):
        exam = get_object_or_404(Exam, pk=exam_id, is_active=True)
        qs = ExamSubject.objects.filter(exam=exam).select_related('subject')
        from .serializers import ExamSubjectListSerializer
        return ExamSubjectListSerializer(qs, many=True).data

    @staticmethod
    def validate_exam_subject(exam_id, subject_id):
        exam = get_object_or_404(Exam, pk=exam_id, is_active=True)
        subject = get_object_or_404(Subject, pk=subject_id)
        get_object_or_404(ExamSubject, exam=exam, subject=subject)
        return exam, subject

    @staticmethod
    def get_daily_questions(exam_id, subject_id, difficulty='medium', count=10):
        exam, subject = ExamAPIAction.validate_exam_subject(exam_id, subject_id)

        today = date.today().isoformat()
        key_raw = f"exam_daily:{exam.id}:{subject.id}:{difficulty}:{today}"
        cache_key = "edq_" + hashlib.md5(key_raw.encode()).hexdigest()

        cached = cache.get(cache_key)
        if cached is not None:
            return {'source': 'cache', 'data': cached}

        qs = ExamQuestion.objects.filter(
            exam=exam,
            subject=subject,
            difficulty=difficulty,
            created_at__date=today,
        ).select_related(
            'exam', 'subject',
        ).prefetch_related('answers')

        if qs.count() >= count:
            from .serializers import ExamQuestionSerializer
            data = ExamQuestionSerializer(qs[:count], many=True).data
            cache.set(cache_key, data, timeout=3600)
            return {'source': 'db', 'data': data}

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
            raise UpstreamError(
                result.get('message') or 'Gemini rejected the requested topic.'
            )

        raw_questions = result.get('questions', [])
        if len(raw_questions) < count:
            raise UpstreamError(
                f'Gemini returned {len(raw_questions)} questions but '
                f'{count} were requested. Aborting to avoid partial data.'
            )

        created_questions = []

        with transaction.atomic():
            for q_data in raw_questions:
                answers = q_data.get('answers', [])
                if len(answers) != 4:
                    raise UpstreamError('Each question must have exactly 4 options.')
                if sum(1 for a in answers if a.get('is_correct')) != 1:
                    raise UpstreamError(
                        'Each question must have exactly 1 correct answer.'
                    )

                q_obj = ExamQuestion.objects.create(
                    exam=exam,
                    subject=subject,
                    text=q_data['text'],
                    explanation=q_data.get('explanation', ''),
                    difficulty=difficulty,
                )
                for a_data in answers:
                    ExamQuestionAnswer.objects.create(
                        question=q_obj,
                        text=a_data['text'],
                        is_correct=a_data['is_correct'],
                    )
                created_questions.append(q_obj)

        from .serializers import ExamQuestionSerializer
        data = ExamQuestionSerializer(created_questions, many=True).data
        cache.set(cache_key, data, timeout=3600)
        return {'source': 'generated', 'data': data}
