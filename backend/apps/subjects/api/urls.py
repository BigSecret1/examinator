# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from rest_framework.routers import DefaultRouter

from .views import SubjectViewSet, TopicViewSet

router = DefaultRouter()
router.register("topics", TopicViewSet, basename="topic")
router.register("", SubjectViewSet, basename="subject")

urlpatterns = router.urls
