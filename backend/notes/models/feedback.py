# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.conf import settings
from django.db import models

from .note import Note


class Feedback(models.Model):
    '''Platform-wide user feedback.

    Two common shapes today:
      1. General platform feedback — `note` and `rating` are null,
         `message` carries the user's comment.
      2. Post-note-generation rating — `note` set, `rating` set
         (1-5), `message` optional.

    Will evolve (categories, attachments, etc.) as the product grows.
    '''

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        help_text='Set when the feedback is about a specific generated note.',
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text='1-5 star rating of the note generation, if applicable.',
    )
    message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user_id} note={self.note_id} rating={self.rating}'

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_feedback'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['note']),
            models.Index(fields=['rating']),
        ]

