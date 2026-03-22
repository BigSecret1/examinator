# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import hashlib
import logging
from datetime import date

from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.subjects.models import Subject, SubTopic, Topic

from ..models import Answer, Question
from .serializers import QuestionSerializer, DailyQuestionsParamsSerializer
from .actions import generate_questions

logger = logging.getLogger(__name__)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.select_related(
            "topic__subject",
            "subtopic"
        ).prefetch_related("answers")
        topic_id = self.request.query_params.get("topic")
        difficulty = self.request.query_params.get("difficulty")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        return queryset


@api_view(["GET"])
def daily_questions(request):
    """Return 10 daily questions for the given subject/topic/difficulty.

    Query params:
        subject  – subject ID (required)
        topic    – topic ID, or 'all' (default: all)
        subtopic    – subtopic ID, or 'all' (default: all)
        difficulty – easy | medium | hard (default: medium)
    """
    params = DailyQuestionsParamsSerializer(data=request.query_params)
    if not params.is_valid():
        return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

    subject_id = request.query_params.get("subject")
    topic_id = request.query_params.get("topic", "all")
    subtopic_id = request.query_params.get("subtopic", "all")
    difficulty = request.query_params.get("difficulty", "medium")

    # topic=all forces subtopic=all
    if topic_id == "all":
        subtopic_id = "all"

    if not subject_id:
        return Response(
            {"error": "subject is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if difficulty not in ("easy", "medium", "hard"):
        return Response(
            {"error": "difficulty must be easy, medium, or hard."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Resolve subject
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        return Response(
            {"error": "Subject not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Resolve topic
    topic_name = "All Topics"
    if topic_id and topic_id != "all":
        try:
            topic = Topic.objects.get(pk=topic_id, subject=subject)
            topic_name = topic.name
        except Topic.DoesNotExist:
            return Response(
                {"error": "Topic not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    # Resolve subtopic
    resolved_subtopic = None
    subtopic_name = "None"
    if subtopic_id and subtopic_id != "all":
        try:
            resolved_subtopic = SubTopic.objects.get(pk=subtopic_id, topic_id=topic_id)
            subtopic_name = resolved_subtopic.name
        except SubTopic.DoesNotExist:
            return Response(
                {"error": "Subtopic not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    # Build a cache key unique to this combination + today's date
    today = date.today().isoformat()
    subtopic_token = str(resolved_subtopic.pk) if resolved_subtopic else "all"
    key_raw = f"daily:{subject.id}:{topic_id}:{subtopic_token}:{difficulty}:{today}"
    cache_key = "dq_" + hashlib.md5(key_raw.encode()).hexdigest()

    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)

    # Check DB for questions generated today for this combo
    qs = Question.objects.filter(
        topic__subject=subject,
        difficulty=difficulty,
        created_at__date=today,
    ).select_related("topic__subject", "subtopic").prefetch_related("answers")

    if topic_id and topic_id != "all":
        qs = qs.filter(topic_id=topic_id)

    if resolved_subtopic:
        qs = qs.filter(subtopic=resolved_subtopic)

    if qs.count() >= 10:
        serializer = QuestionSerializer(qs[:10], many=True)
        cache.set(cache_key, serializer.data, timeout=3600)
        return Response(serializer.data)

    # Generate via Gemini
    try:
        result = generate_questions(
            subject_name=subject.name,
            topic_name=topic_name,
            difficulty=difficulty,
            subtopic_name=subtopic_name,
            count=10,
        )
    except Exception as e:
        logger.exception("Gemini generation failed")
        return Response(
            {"error": f"Failed to generate questions: {e}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if result.get("status") == "invalid_topic":
        return Response(
            {"error": result.get("message", "The topic does not match the subject.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    raw_questions = result.get("questions", [])

    # Resolve or create topic for storage
    if topic_id == "all" or not topic_id:
        storage_topic, _ = Topic.objects.get_or_create(
            subject=subject, name="General",
            defaults={"description": "General questions"}
        )
    else:
        storage_topic = Topic.objects.get(pk=topic_id)

    # Persist to DB
    created_questions = []
    for q_data in raw_questions:
        q_obj = Question.objects.create(
            topic=storage_topic,
            subtopic=resolved_subtopic,
            text=q_data["text"],
            explanation=q_data.get("explanation", ""),
            difficulty=difficulty,
        )
        for a_data in q_data["answers"]:
            Answer.objects.create(
                question=q_obj,
                text=a_data["text"],
                is_correct=a_data["is_correct"],
            )
        created_questions.append(q_obj)

    serializer = QuestionSerializer(created_questions, many=True)
    cache.set(cache_key, serializer.data, timeout=3600)
    return Response(serializer.data)
