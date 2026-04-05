from django.db import migrations


populate_subject_sql = """
    UPDATE questions_question
    SET subject_id = subjects_topic.subject_id
    FROM subjects_topic
    WHERE questions_question.topic_id = subjects_topic.id
      AND questions_question.subject_id IS NULL;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_add_subject_to_question'),
    ]

    operations = [
        migrations.RunSQL(
            sql=populate_subject_sql,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
