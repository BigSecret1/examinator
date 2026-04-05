# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import hashlib
import logging
from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
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
    def _persist_questions(raw_questions, subject, topic, subtopic, difficulty):
        created = []
        for q_data in raw_questions:
            q_obj = Question.objects.create(
                subject=subject,
                topic=topic,
                subtopic=subtopic,
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
        subject = get_object_or_404(Subject, pk=subject_id)

        if topic_id is not None:
            get_object_or_404(Topic, pk=topic_id, subject=subject)

        resolved_subtopic = None
        if subtopic_id is not None:
            resolved_subtopic = get_object_or_404(
                SubTopic, pk=subtopic_id, topic_id=topic_id,
            )

        yesterday = timezone.localdate() - timedelta(days=1)
        subtopic_token = str(resolved_subtopic.pk) if resolved_subtopic else 'all'
        topic_token = str(topic_id) if topic_id else 'all'
        key_raw = (
            f"daily:{subject.id}:{topic_token}:{subtopic_token}"
            f":{difficulty}:{yesterday.isoformat()}"
        )
        cache_key = 'dq_' + hashlib.md5(key_raw.encode()).hexdigest()

        cached = cache.get(cache_key)
        if cached is not None:
            return {'source': 'cache', 'data': cached}

        qs = Question.objects.filter(
            subject=subject,
            difficulty=difficulty,
            created_at__date=yesterday,
        ).select_related('subject', 'topic', 'subtopic').prefetch_related('answers')

        if topic_id is not None:
            qs = qs.filter(topic_id=topic_id)
        if resolved_subtopic:
            qs = qs.filter(subtopic=resolved_subtopic)

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
        subject = get_object_or_404(Subject, pk=subject_id)

        topic_name = 'All Topics'
        if topic_id is not None:
            topic_obj = get_object_or_404(Topic, pk=topic_id, subject=subject)
            topic_name = topic_obj.name

        resolved_subtopic = None
        subtopic_name = 'None'
        if subtopic_id is not None:
            resolved_subtopic = get_object_or_404(
                SubTopic, pk=subtopic_id, topic_id=topic_id,
            )
            subtopic_name = resolved_subtopic.name

        today = timezone.localdate()

        qs_filter = {
            'subject': subject,
            'difficulty': difficulty,
            'created_at__date': today,
        }
        if topic_id is not None:
            qs_filter['topic_id'] = topic_id
        if resolved_subtopic:
            qs_filter['subtopic'] = resolved_subtopic

        existing = Question.objects.filter(**qs_filter).count()
        if existing >= count:
            return {'status': 'skipped', 'reason': 'already_generated'}

        topic_token = str(topic_id) if topic_id else 'all'
        subtopic_token = str(resolved_subtopic.pk) if resolved_subtopic else 'all'
        lock_key = (
            f"gen_lock:q:{subject.id}:{topic_token}:"
            f"{subtopic_token}:{difficulty}:{today}"
        )
        if not cache.add(lock_key, 'locked', timeout=300):
            return {'status': 'skipped', 'reason': 'generation_in_progress'}

        try:
            prompt = USER_PROMPT_TEMPLATE.format(
                count=count,
                subject=subject.name,
                topic=topic_name,
                subtopic=subtopic_name,
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

            if topic_id is None:
                storage_topic, _ = Topic.objects.get_or_create(
                    subject=subject, name='General',
                    defaults={'description': 'General questions'},
                )
            else:
                storage_topic = topic_obj

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
                    raw_questions, subject, storage_topic, resolved_subtopic, difficulty,
                )

            return {'status': 'generated', 'count': len(created_questions)}
        finally:
            cache.delete(lock_key)
