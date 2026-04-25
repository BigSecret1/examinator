# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.conf import settings
from django.db import models

from .note import Note


class FileUploadActivity(models.Model):
    '''Logs every file upload attempt — both accepted and rejected.

    Platform-wide: not specific to notes. Today only PDFs (for notes
    generation) flow through it; future file types will reuse it.

    Rejected attempts have no associated Note. Accepted attempts that
    produce a Note link to it via FK.
    '''

    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    REASON_OK = ''
    REASON_NOT_PDF = 'not_pdf'
    REASON_OVER_SIZE = 'over_size_limit'
    REASON_OVER_PAGES = 'over_page_limit'
    REASON_TOO_LITTLE_TEXT = 'too_little_text'
    REASON_DAILY_LIMIT = 'daily_limit_exceeded'
    REASON_OTHER = 'other'
    REASON_CHOICES = [
        (REASON_OK, 'OK'),
        (REASON_NOT_PDF, 'Not a PDF'),
        (REASON_OVER_SIZE, 'Over file-size limit'),
        (REASON_OVER_PAGES, 'Over page-count limit'),
        (REASON_TOO_LITTLE_TEXT, 'Too little extractable text'),
        (REASON_DAILY_LIMIT, 'Daily upload limit exceeded'),
        (REASON_OTHER, 'Other'),
    ]

    PURPOSE_NOTES = 'notes'
    PURPOSE_CHOICES = [
        (PURPOSE_NOTES, 'Notes generation'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_upload_activities',
    )
    purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
        default=PURPOSE_NOTES,
        help_text='What the upload was intended for.',
    )
    file_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    file_size = models.PositiveBigIntegerField(
        default=0,
        help_text='File size in bytes.',
    )
    page_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Null if the upload was rejected before parsing.',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    rejection_reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        blank=True,
        default=REASON_OK,
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='upload_activities',
        help_text='The note created from this upload (only when accepted).',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user_id} {self.file_name} {self.status}'

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_file_upload_activity'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['purpose']),
        ]

