# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_question_explanation'),
        ('subjects', '0003_subtopic'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='subtopic',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='questions',
                to='subjects.subtopic',
            ),
        ),
    ]
