# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from rest_framework import viewsets

from .models import Subject, Topic
from .serializers import SubjectSerializer, TopicSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.prefetch_related("topics").all()
    serializer_class = SubjectSerializer


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.select_related("subject").all()
    serializer_class = TopicSerializer
