# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from rest_framework import serializers

from ..models import Answer, Question


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    topic_name = serializers.CharField(source="topic.name", read_only=True)
    subject_name = serializers.CharField(source="topic.subject.name", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id", "topic", "topic_name", "subject_name",
            "text", "explanation", "difficulty", "answers", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
