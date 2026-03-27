from django.db import models


class Exam(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    conducting_body = models.CharField(
        max_length=200, blank=True,
        help_text='Organisation that conducts the exam (e.g. UPSC, NTA).',
    )
    frequency = models.CharField(
        max_length=50, blank=True,
        help_text='How often the exam is held (e.g. Annual, Biannual).',
    )
    official_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    subjects = models.ManyToManyField(
        'subjects.Subject',
        through='ExamSubject',
        blank=True,
        related_name='exams',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'examinator_exam'
        ordering = ['name']


class ExamSubject(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE,
        related_name='exam_subjects',
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='exam_subjects',
    )
    is_optional = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.exam.name} – {self.subject.name}'

    class Meta:
        db_table = 'examinator_exam_subject'
        unique_together = [['exam', 'subject']]
        ordering = ['exam', 'subject']
