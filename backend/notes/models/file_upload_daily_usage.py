# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.conf import settings
from django.db import models


class FileUploadDailyUsage(models.Model):
    '''Per-user daily counter used to enforce upload quotas.

    Platform-wide (covers all file uploads, not just notes). The effective
    daily limit for a user is determined by:

        UserUploadQuota.daily_limit  (if a row exists for the user)
        else  settings.FILE_UPLOAD_DAILY_LIMIT  (platform default)
    '''

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_upload_daily_usage',
    )
    date = models.DateField(help_text='Calendar date in UTC.')
    count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} {self.date} ({self.count})'

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_file_upload_daily_usage'
        unique_together = [['user', 'date']]
        ordering = ['-date', 'user']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]

