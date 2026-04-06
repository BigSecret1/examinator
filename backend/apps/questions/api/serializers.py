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
    topic_name = serializers.CharField(
        source="topic.name", read_only=True, allow_null=True,
    )
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


class DailyQuestionsParamsSerializer(serializers.Serializer):
    subject = serializers.IntegerField(min_value=1)
    topic = serializers.IntegerField(min_value=1, required=False, default=None, allow_null=True)
    subtopic = serializers.IntegerField(min_value=1, required=False, default=None, allow_null=True)
    difficulty = serializers.ChoiceField(
        choices=["easy", "medium", "hard"],
        default="medium",
    )

    def validate(self, data):
        if data["topic"] is None:
            data["subtopic"] = None
        return data
