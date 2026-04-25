# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import models

from .note import Note


class NoteFlashcard(models.Model):
    '''An active-recall question/answer pair belonging to a note.'''

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='flashcards',
    )
    question = models.TextField()
    answer = models.TextField()
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:80]

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_note_flashcard'
        ordering = ['note', 'position']
        indexes = [
            models.Index(fields=['note', 'position']),
        ]

