# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import models

from .note import Note


class NoteSection(models.Model):
    '''A top-level section of a note (typically a chapter).'''

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='sections',
    )
    heading = models.CharField(max_length=300)
    overview = models.TextField(blank=True, default='')
    position = models.PositiveIntegerField(
        default=0,
        help_text='Sort order within the note (0 = first).',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.note_id}#{self.position} – {self.heading}'

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_note_section'
        ordering = ['note', 'position']
        indexes = [
            models.Index(fields=['note', 'position']),
        ]

