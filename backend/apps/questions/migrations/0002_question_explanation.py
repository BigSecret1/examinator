# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True, default=''),
        ),
    ]
