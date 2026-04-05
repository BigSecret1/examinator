"""Data migration: copy subjects used by exams into ExamSubjectCatalog,
preserving the original IDs so that subject_id FK values need no remapping."""

from django.db import migrations


def copy_subjects_forward(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    ExamSubjectCatalog = apps.get_model('exams', 'ExamSubjectCatalog')
    ExamSubject = apps.get_model('exams', 'ExamSubject')
    ExamQuestion = apps.get_model('exams', 'ExamQuestion')

    # Only copy subjects that are actually used by the exams app.
    used_subject_ids = set(
        ExamSubject.objects.values_list('subject_id', flat=True).distinct()
    )
    used_subject_ids |= set(
        ExamQuestion.objects.values_list('subject_id', flat=True).distinct()
    )

    if not used_subject_ids:
        return

    # Copy with the SAME id — FK values in ExamSubject / ExamQuestion
    # remain valid, so no data remapping is needed at all.
    for subj in Subject.objects.filter(id__in=used_subject_ids):
        ExamSubjectCatalog.objects.create(
            id=subj.id,
            name=subj.name,
            description=subj.description,
        )


def copy_subjects_reverse(apps, schema_editor):
    """Reverse: just delete the catalog rows — the FK integer values
    already match subjects.Subject because we preserved IDs."""
    ExamSubjectCatalog = apps.get_model('exams', 'ExamSubjectCatalog')
    ExamSubjectCatalog.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0003_create_exam_subject_catalog'),
        ('subjects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            copy_subjects_forward,
            copy_subjects_reverse,
        ),
        # Reset the PK sequence so the next auto-generated id starts after
        # the highest explicitly-inserted id.  Without this, PostgreSQL's
        # sequence is still at 1 and the next INSERT will collide.
        migrations.RunSQL(
            sql="""
                SELECT setval(
                    pg_get_serial_sequence('examinator_exam_subject_catalog', 'id'),
                    COALESCE((SELECT MAX(id) FROM examinator_exam_subject_catalog), 1)
                );
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
