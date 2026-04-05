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
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    subtopic_id = serializers.IntegerField(
        source="subtopic.id",
        read_only=True,
        allow_null=True
    )
    subtopic_name = serializers.CharField(
        source="subtopic.name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Question
        fields = [
            "id",
            "subject",
            "subject_name",
            "topic",
            "topic_name",
            "subtopic_id",
            "subtopic_name",
            "text",
            "explanation",
            "difficulty",
            "answers", "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class _AllOrIntegerField(serializers.Field):
    """Accepts 'all' (as None) or a positive integer."""

    def to_internal_value(self, data):
        if str(data).lower() == "all":
            return None
        try:
            value = int(data)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Must be a positive integer or 'all'.")
        if value <= 0:
            raise serializers.ValidationError("Must be a positive integer or 'all'.")
        return value


class DailyQuestionsParamsSerializer(serializers.Serializer):
    subject = serializers.IntegerField(min_value=1)
    topic = _AllOrIntegerField(default=None)
    subtopic = _AllOrIntegerField(default=None)
    difficulty = serializers.ChoiceField(
        choices=["easy", "medium", "hard"],
        default="medium",
    )

    def validate(self, data):
        # topic=all forces subtopic=all
        if data["topic"] is None:
            data["subtopic"] = None
        return data
