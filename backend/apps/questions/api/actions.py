# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import hashlib
import logging
from datetime import date

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.subjects.models import Subject, SubTopic, Topic
from geminiclient.api.interfaces import GeminiClientInterface

from ..models import Answer, Question
from .utils import MCQ_SCHEMA, SYSTEM_INSTRUCTION, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


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
    def _persist_questions(raw_questions, topic, subtopic, difficulty):
        created = []
        for q_data in raw_questions:
            q_obj = Question.objects.create(
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

        # Resolve topic
        topic_name = 'All Topics'
        if topic_id is not None:
            topic_obj = get_object_or_404(Topic, pk=topic_id, subject=subject)
            topic_name = topic_obj.name

        # Resolve subtopic
        resolved_subtopic = None
        subtopic_name = 'None'
        if subtopic_id is not None:
            resolved_subtopic = get_object_or_404(
                SubTopic, pk=subtopic_id, topic_id=topic_id,
            )
            subtopic_name = resolved_subtopic.name

        # Cache
        today = date.today().isoformat()
        subtopic_token = str(resolved_subtopic.pk) if resolved_subtopic else 'all'
        topic_token = str(topic_id) if topic_id else 'all'
        key_raw = (
            f"daily:{subject.id}:{topic_token}:{subtopic_token}"
            f":{difficulty}:{today}"
        )
        cache_key = 'dq_' + hashlib.md5(key_raw.encode()).hexdigest()

        cached = cache.get(cache_key)
        if cached is not None:
            return {'source': 'cache', 'data': cached}

        # DB lookup
        qs = Question.objects.filter(
            topic__subject=subject,
            difficulty=difficulty,
            created_at__date=today,
        ).select_related('topic__subject', 'subtopic').prefetch_related('answers')

        if topic_id is not None:
            qs = qs.filter(topic_id=topic_id)
        if resolved_subtopic:
            qs = qs.filter(subtopic=resolved_subtopic)

        if qs.count() >= count:
            from .serializers import QuestionSerializer
            data = QuestionSerializer(qs[:count], many=True).data
            cache.set(cache_key, data, timeout=3600)
            return {'source': 'db', 'data': data}

        # Generate via Gemini
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
            raise ValidationError(
                result.get('message', 'The topic does not match the subject.')
            )

        raw_questions = result.get('questions', [])

        # Resolve or create storage topic
        if topic_id is None:
            storage_topic, _ = Topic.objects.get_or_create(
                subject=subject, name='General',
                defaults={'description': 'General questions'},
            )
        else:
            storage_topic = Topic.objects.get(pk=topic_id)

        # Persist
        created_questions = QuestionAPIAction._persist_questions(
            raw_questions, storage_topic, resolved_subtopic, difficulty,
        )

        from .serializers import QuestionSerializer
        data = QuestionSerializer(created_questions, many=True).data
        cache.set(cache_key, data, timeout=3600)
        return {'source': 'generated', 'data': data}
