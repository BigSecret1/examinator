# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Question
from .actions import QuestionAPIAction
from .serializers import QuestionSerializer, DailyQuestionsParamsSerializer

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
    """Return 10 daily questions for the given subject/topic/difficulty."""
    params = DailyQuestionsParamsSerializer(data=request.query_params)
    if not params.is_valid():
        return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

    data = params.validated_data
    result = QuestionAPIAction.get_daily_questions(
        subject_id=data['subject'],
        topic_id=data.get('topic'),
        subtopic_id=data.get('subtopic'),
        difficulty=data['difficulty'],
    )
    return Response(result['data'])
