# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import models

from apps.subjects.models import SubTopic, Topic


class Question(models.Model):
    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, "Easy"),
        (DIFFICULTY_MEDIUM, "Medium"),
        (DIFFICULTY_HARD, "Hard"),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    subtopic = models.ForeignKey(
        SubTopic, on_delete=models.SET_NULL, related_name="questions",
        null=True, blank=True,
    )
    text = models.TextField()
    explanation = models.TextField(blank=True, default='')
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default=DIFFICULTY_MEDIUM
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:80]

    class Meta:
        ordering = ["-created_at"]


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'correct' if self.is_correct else 'wrong'})"

    class Meta:
        ordering = ["id"]
