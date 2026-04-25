# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.conf import settings
from django.db import models


class UserUploadQuota(models.Model):
    '''Per-user override of the platform-wide daily upload limit.

    A row here represents an explicit quota for one user (e.g. paid
    subscriber, admin, beta tester). When no row exists, the platform
    default settings.FILE_UPLOAD_DAILY_LIMIT applies.

    `tier` is informational and forward-compatible with subscription tiers.
    '''

    TIER_FREE = 'free'
    TIER_PRO = 'pro'
    TIER_UNLIMITED = 'unlimited'
    TIER_CHOICES = [
        (TIER_FREE, 'Free'),
        (TIER_PRO, 'Pro'),
        (TIER_UNLIMITED, 'Unlimited'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='upload_quota',
    )
    daily_limit = models.PositiveIntegerField(
        help_text='Maximum file uploads allowed per UTC day.',
    )
    tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default=TIER_FREE,
    )
    note = models.TextField(
        blank=True,
        default='',
        help_text='Admin note about why this override exists.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id} {self.tier} ({self.daily_limit}/day)'

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_user_upload_quota'
        ordering = ['user']

