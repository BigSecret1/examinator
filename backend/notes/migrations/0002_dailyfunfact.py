# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyFunFact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('fact', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='fun_facts',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'examinator_daily_fun_fact',
                'ordering': ['-date'],
                'unique_together': {('user', 'date')},
            },
        ),
    ]
