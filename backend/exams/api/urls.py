from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ExamDailyQuestionsAPIView, ExamSubjectsAPIView, ExamViewSet

router = DefaultRouter()
router.register('', ExamViewSet, basename='exam')

urlpatterns = [
    path(
        '<int:exam_id>/subjects/',
        ExamSubjectsAPIView.as_view(),
        name='exam-subjects',
    ),
    path(
        '<int:exam_id>/daily-questions/',
        ExamDailyQuestionsAPIView.as_view(),
        name='exam-daily-questions',
    ),
] + router.urls
