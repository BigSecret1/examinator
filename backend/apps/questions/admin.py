# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.contrib import admin

from .models import Answer, Question


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "topic", "difficulty", "created_at"]
    list_filter = ["difficulty", "topic__subject"]
    inlines = [AnswerInline]
