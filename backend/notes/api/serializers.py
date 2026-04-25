# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from rest_framework import serializers

from notes.models import (
    Feedback,
    FileUploadActivity,
    FileUploadDailyUsage,
    Note,
    NoteFlashcard,
    NoteKeyTerm,
    NoteSection,
    NoteSubtopic,
    UserUploadQuota,
)


class NoteKeyTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteKeyTerm
        fields = [
            'id',
            'term',
            'definition',
            'position',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class NoteFlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteFlashcard
        fields = [
            'id',
            'question',
            'answer',
            'position',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class NoteSubtopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSubtopic
        fields = [
            'id',
            'heading',
            'content_md',
            'examples',
            'key_takeaways',
            'position',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class NoteSectionSerializer(serializers.ModelSerializer):
    subtopics = NoteSubtopicSerializer(many=True, read_only=True)

    class Meta:
        model = NoteSection
        fields = [
            'id',
            'heading',
            'overview',
            'position',
            'subtopics',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class NoteSerializer(serializers.ModelSerializer):
    sections = NoteSectionSerializer(many=True, read_only=True)
    flashcards = NoteFlashcardSerializer(many=True, read_only=True)
    key_terms = NoteKeyTermSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            'id',
            'user',
            'title',
            'summary',
            'learning_objectives',
            'source_filename',
            'page_count',
            'generation_mode',
            'status',
            'error_message',
            'sections',
            'flashcards',
            'key_terms',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NoteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id',
            'title',
            'summary',
            'source_filename',
            'page_count',
            'generation_mode',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FileUploadActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadActivity
        fields = [
            'id',
            'user',
            'purpose',
            'file_name',
            'file_size',
            'page_count',
            'status',
            'rejection_reason',
            'note',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class FileUploadDailyUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadDailyUsage
        fields = ['id', 'user', 'date', 'count', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class UserUploadQuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUploadQuota
        fields = [
            'id',
            'user',
            'daily_limit',
            'tier',
            'note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id',
            'user',
            'note',
            'rating',
            'message',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

