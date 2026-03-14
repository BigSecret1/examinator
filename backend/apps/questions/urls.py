# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from rest_framework.routers import DefaultRouter

from .views import QuestionViewSet

router = DefaultRouter()
router.register("", QuestionViewSet, basename="question")

urlpatterns = router.urls
