from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ExamSubjectQuestionAPIView, ExamViewSet

router = DefaultRouter()
router.register('', ExamViewSet, basename='exam')

urlpatterns = [
    path(
        '<int:exam_id>/daily-questions/',
        ExamSubjectQuestionAPIView.as_view(),
        name='exam-daily-questions',
    ),
] + router.urls
