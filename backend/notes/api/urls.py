# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.urls import path

from .views import (
    FeedbackAPIView,
    FunFactAPIView,
    NoteDetailAPIView,
    NotesListAPIView,
    NotesQuotaAPIView,
    NotesUploadAPIView,
)

urlpatterns = [
    path('', NotesListAPIView.as_view(), name='notes-list'),
    path('upload/', NotesUploadAPIView.as_view(), name='notes-upload'),
    path('quota/', NotesQuotaAPIView.as_view(), name='notes-quota'),
    path('fun-fact/', FunFactAPIView.as_view(), name='notes-fun-fact'),
    path('<int:pk>/', NoteDetailAPIView.as_view(), name='notes-detail'),
    path('feedback/', FeedbackAPIView.as_view(), name='notes-feedback'),
]

