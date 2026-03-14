# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.urls import path

from .views import UserProfileView

urlpatterns = [
    path("me/", UserProfileView.as_view(), name="user-profile"),
]
