# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Topic(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        related_name='topics'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.subject.name} – {self.name}'

    class Meta:
        unique_together = [['subject', 'name']]
        ordering = ['subject', 'name']


class SubTopic(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='subtopics',
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.topic.name} – {self.name}'

    class Meta:
        db_table = 'examinator_subtopic'
        unique_together = [['topic', 'name']]
        ordering = ['topic', 'name']
