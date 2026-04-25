# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import models

from .note import Note


class NoteKeyTerm(models.Model):
    '''A glossary entry belonging to a note.'''

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='key_terms',
    )
    term = models.CharField(max_length=200)
    definition = models.TextField()
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.term

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_note_key_term'
        ordering = ['note', 'position']
        indexes = [
            models.Index(fields=['note', 'position']),
        ]

