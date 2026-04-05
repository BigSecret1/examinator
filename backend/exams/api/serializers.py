from rest_framework import serializers

from ..models import (
    Exam, ExamQuestion, ExamQuestionAnswer, ExamSubject, ExamSubjectCatalog,
)


class ExamSubjectCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubjectCatalog
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExamSubjectSerializer(serializers.ModelSerializer):
    subject = ExamSubjectCatalogSerializer(read_only=True)

    class Meta:
        model = ExamSubject
        fields = ['id', 'subject', 'is_optional', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExamSerializer(serializers.ModelSerializer):
    exam_subjects = ExamSubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id',
            'name',
            'description',
            'country',
            'conducting_body',
            'frequency',
            'official_url',
            'is_active',
            'exam_subjects',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no nested subjects)."""

    class Meta:
        model = Exam
        fields = [
            'id',
            'name',
            'description',
            'country',
            'conducting_body',
            'frequency',
            'official_url',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamSubjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for subject picker — no topics/subtopics."""
    subject_name = serializers.CharField(source='subject.name')

    class Meta:
        model = ExamSubject
        fields = ['id', 'subject_id', 'subject_name', 'is_optional']


class ExamQuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamQuestionAnswer
        fields = ['id', 'text', 'is_correct']


class ExamQuestionSerializer(serializers.ModelSerializer):
    answers = ExamQuestionAnswerSerializer(many=True, read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = ExamQuestion
        fields = [
            'id',
            'exam',
            'subject',
            'subject_name',
            'text',
            'explanation',
            'difficulty',
            'answers',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamDailyQuestionsParamsSerializer(serializers.Serializer):
    subject = serializers.IntegerField(min_value=1)
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        default='medium',
    )
