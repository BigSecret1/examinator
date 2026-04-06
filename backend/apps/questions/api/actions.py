# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import hashlib
import logging
from dataclasses import dataclass
from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status as http_status
from rest_framework.exceptions import APIException

from apps.subjects.models import Subject, SubTopic, Topic
from geminiclient.api.interfaces import GeminiClientInterface

from ..models import Answer, Question
from .utils import MCQ_SCHEMA, SYSTEM_INSTRUCTION, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class UpstreamError(APIException):
    status_code = http_status.HTTP_502_BAD_GATEWAY
    default_detail = 'Upstream service error.'
    default_code = 'upstream_error'

    def get_full_details(self):
        return {'error': str(self.detail)}


@dataclass(frozen=True)
class QuestionScope:
    """Immutable container for a resolved subject/topic/subtopic request."""

    subject: Subject
    topic: Topic | None = None
    subtopic: SubTopic | None = None

    # ── display names (for Gemini prompt) ──

    @property
    def topic_name(self) -> str:
        return self.topic.name if self.topic else 'All Topics'

    @property
    def subtopic_name(self) -> str:
        return self.subtopic.name if self.subtopic else 'All Subtopics'

    # ── tokens (for cache/lock keys) ──

    @property
    def topic_token(self) -> str:
        return str(self.topic.pk) if self.topic else 'all'

    @property
    def subtopic_token(self) -> str:
        return str(self.subtopic.pk) if self.subtopic else 'all'

    # ── keys ──

    def cache_key(self, difficulty: str, date) -> str:
        key_raw = (
            f"daily:{self.subject.id}:{self.topic_token}:{self.subtopic_token}"
            f":{difficulty}:{date.isoformat()}"
        )
        return 'dq_' + hashlib.md5(key_raw.encode()).hexdigest()

    def lock_key(self, difficulty: str, date) -> str:
        return (
            f"gen_lock:q:{self.subject.id}:{self.topic_token}:"
            f"{self.subtopic_token}:{difficulty}:{date}"
        )

    # ── queryset filtering ──

    def apply_filters(self, qs: QuerySet) -> QuerySet:
        """Apply topic/subtopic filters.

        None means 'all' — filter for NULL (questions generated without
        a specific topic/subtopic).
        """
        if self.topic is not None:
            qs = qs.filter(topic=self.topic)
        else:
            qs = qs.filter(topic__isnull=True)
        if self.subtopic is not None:
            qs = qs.filter(subtopic=self.subtopic)
        else:
            qs = qs.filter(subtopic__isnull=True)
        return qs

    # ── factory ──

    @classmethod
    def resolve(cls, subject_id, topic_id=None, subtopic_id=None):
        subject = get_object_or_404(Subject, pk=subject_id)
        topic_obj = None
        subtopic_obj = None
        if topic_id is not None:
            topic_obj = get_object_or_404(Topic, pk=topic_id, subject=subject)
            if subtopic_id is not None:
                subtopic_obj = get_object_or_404(
                    SubTopic, pk=subtopic_id, topic_id=topic_id,
                )
        return cls(subject=subject, topic=topic_obj, subtopic=subtopic_obj)


class QuestionAPIAction:

    @staticmethod
    def _persist_answers(question, answers_data):
        for a_data in answers_data:
            Answer.objects.create(
                question=question,
                text=a_data['text'],
                is_correct=a_data['is_correct'],
            )

    @staticmethod
    def _persist_questions(raw_questions, scope, difficulty):
        created = []
        for q_data in raw_questions:
            q_obj = Question.objects.create(
                subject=scope.subject,
                topic=scope.topic,
                subtopic=scope.subtopic,
                text=q_data['text'],
                explanation=q_data.get('explanation', ''),
                difficulty=difficulty,
            )
            QuestionAPIAction._persist_answers(q_obj, q_data['answers'])
            created.append(q_obj)
        return created

    @staticmethod
    def get_daily_questions(
            subject_id,
            topic_id=None,
            subtopic_id=None,
            difficulty='medium',
            count=10
    ):
        scope = QuestionScope.resolve(subject_id, topic_id, subtopic_id)
        yesterday = timezone.localdate() - timedelta(days=1)

        cache_key = scope.cache_key(difficulty, yesterday)
        cached = cache.get(cache_key)
        if cached is not None:
            return {'source': 'cache', 'data': cached}

        qs = Question.objects.filter(
            subject=scope.subject,
            difficulty=difficulty,
            created_at__date=yesterday,
        ).select_related('subject', 'topic', 'subtopic').prefetch_related('answers')
        qs = scope.apply_filters(qs)

        if not qs.exists():
            return {'source': 'db', 'data': []}

        from .serializers import QuestionSerializer
        data = QuestionSerializer(qs[:count], many=True).data
        cache.set(cache_key, data, timeout=86400)
        return {'source': 'db', 'data': data}

    @staticmethod
    def generate_daily_questions(
            subject_id,
            topic_id=None,
            subtopic_id=None,
            difficulty='medium',
            count=10
    ):
        scope = QuestionScope.resolve(subject_id, topic_id, subtopic_id)
        today = timezone.localdate()

        existing_qs = Question.objects.filter(
            subject=scope.subject,
            difficulty=difficulty,
            created_at__date=today,
        )
        if scope.apply_filters(existing_qs).count() >= count:
            return {'status': 'skipped', 'reason': 'already_generated'}

        lock_key = scope.lock_key(difficulty, today)
        if not cache.add(lock_key, 'locked', timeout=300):
            return {'status': 'skipped', 'reason': 'generation_in_progress'}

        try:
            prompt = USER_PROMPT_TEMPLATE.format(
                count=count,
                subject=scope.subject.name,
                topic=scope.topic_name,
                subtopic=scope.subtopic_name,
                difficulty=difficulty,
            )
            result = GeminiClientInterface.generate(
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=MCQ_SCHEMA,
                prompt=prompt,
            )

            if result.get('status') == 'invalid_topic':
                raise UpstreamError(
                    result.get('message', 'The topic does not match the subject.')
                )

            raw_questions = result.get('questions', [])
            if len(raw_questions) < count:
                raise UpstreamError(
                    f'Gemini returned {len(raw_questions)} questions but '
                    f'{count} were requested. Aborting to avoid partial data.'
                )

            with transaction.atomic():
                for q_data in raw_questions:
                    answers = q_data.get('answers', [])
                    if len(answers) != 4:
                        raise UpstreamError(
                            'Each question must have exactly 4 options.'
                        )
                    if sum(1 for a in answers if a.get('is_correct')) != 1:
                        raise UpstreamError(
                            'Each question must have exactly 1 correct answer.'
                        )

                created_questions = QuestionAPIAction._persist_questions(
                    raw_questions, scope, difficulty,
                )

            return {'status': 'generated', 'count': len(created_questions)}
        finally:
            cache.delete(lock_key)
