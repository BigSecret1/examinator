from rest_framework import viewsets

from ..models import Exam
from .serializers import ExamListSerializer, ExamSerializer


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.prefetch_related(
        'exam_subjects__subject',
    ).filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ExamListSerializer
        return ExamSerializer
