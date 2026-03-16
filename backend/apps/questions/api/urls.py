# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import QuestionViewSet, daily_questions

router = DefaultRouter()
router.register("", QuestionViewSet, basename="question")

urlpatterns = [
    path("daily/", daily_questions, name="daily-questions"),
] + router.urls
