# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.conf import settings
from django.db import models


class Note(models.Model):
    '''A study-notes document generated from a user-uploaded PDF.

    The top-level container. Sections, subtopics, flashcards and key terms
    hang off this via reverse FKs.
    '''

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    MODE_TEXT = 'text'
    MODE_VISION = 'vision'
    MODE_CHOICES = [
        (MODE_TEXT, 'Text'),
        (MODE_VISION, 'Vision'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
    )
    title = models.CharField(max_length=300)
    summary = models.TextField(blank=True, default='')
    learning_objectives = models.JSONField(
        default=list,
        blank=True,
        help_text='List of short objective strings.',
    )
    source_filename = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Original PDF filename, for the user library display.',
    )
    page_count = models.PositiveIntegerField(default=0)
    generation_mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default=MODE_TEXT,
        help_text='Text mode for digital PDFs, vision mode for scanned PDFs.',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} ({self.user_id})'

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_note'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

