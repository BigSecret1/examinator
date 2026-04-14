# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/subjects/", include("apps.subjects.api.urls")),
    path("api/questions/", include("apps.questions.api.urls")),
    path("api/exams/", include("exams.api.urls")),
    path("api/auth/", include("users.api.urls")),
]
