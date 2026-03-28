from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Exam
from .actions import ExamAPIAction
from .serializers import (
    ExamDailyQuestionsParamsSerializer,
    ExamListSerializer,
    ExamSerializer,
)


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exam.objects.prefetch_related(
        'exam_subjects__subject',
    ).filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ExamListSerializer
        return ExamSerializer


class ExamSubjectsAPIView(APIView):

    def get(self, request, exam_id):
        data = ExamAPIAction.get_exam_subjects(exam_id)
        return Response(data)


class ExamDailyQuestionsAPIView(APIView):

    def get(self, request, exam_id):
        params = ExamDailyQuestionsParamsSerializer(data=request.query_params)
        if not params.is_valid():
            return Response(params.errors, status=status.HTTP_400_BAD_REQUEST)

        result = ExamAPIAction.get_daily_questions(
            exam_id=exam_id,
            subject_id=params.validated_data['subject'],
            difficulty=params.validated_data['difficulty'],
        )

        return Response(result['data'])
