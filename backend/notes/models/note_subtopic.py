# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import models

from .note_section import NoteSection


class NoteSubtopic(models.Model):
    '''A granular concept within a section (e.g. a single principle / rule).'''

    section = models.ForeignKey(
        NoteSection,
        on_delete=models.CASCADE,
        related_name='subtopics',
    )
    heading = models.CharField(max_length=300)
    content_md = models.TextField(
        help_text='Markdown-formatted explanation of this concept.',
    )
    examples = models.JSONField(
        default=list,
        blank=True,
        help_text='List of short example strings illustrating the concept.',
    )
    key_takeaways = models.JSONField(
        default=list,
        blank=True,
        help_text='List of short takeaway bullets a student should memorize.',
    )
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.section_id}#{self.position} – {self.heading}'

    class Meta:
        app_label = 'notes'
        db_table = 'examinator_note_subtopic'
        ordering = ['section', 'position']
        indexes = [
            models.Index(fields=['section', 'position']),
        ]

