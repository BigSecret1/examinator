# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from rest_framework import serializers

from ..models import Subject, SubTopic, Topic


class SubTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTopic
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class TopicSerializer(serializers.ModelSerializer):
    subtopics = SubTopicSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'subtopics', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'topics', 'created_at']
        read_only_fields = ['id', 'created_at']

