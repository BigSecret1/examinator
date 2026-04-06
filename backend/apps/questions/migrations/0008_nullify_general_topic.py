from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0007_make_topic_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE questions_question SET topic_id = NULL WHERE topic_id IN (SELECT id FROM subjects_topic WHERE name = 'General');",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
