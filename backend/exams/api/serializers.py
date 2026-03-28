from rest_framework import serializers

from apps.subjects.api.serializers import SubjectSerializer
from ..models import Exam, ExamSubject


class ExamSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)

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
