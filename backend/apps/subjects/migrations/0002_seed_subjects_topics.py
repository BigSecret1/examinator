# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.db import migrations


def seed_subjects_topics(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Topic = apps.get_model('subjects', 'Topic')

    seed = {
        'Mathematics': {
            'description': 'Mathematics practice',
            'topics': [
                ('Algebra', 'Algebra in Mathematics'),
                ('Geometry', 'Geometry in Mathematics'),
                ('Calculus', 'Calculus in Mathematics'),
                ('Probability', 'Probability in Mathematics'),
            ],
        },
        'Science': {
            'description': 'Science practice',
            'topics': [
                ('Physics', 'Physics in Science'),
                ('Chemistry', 'Chemistry in Science'),
                ('Biology', 'Biology in Science'),
                ('Astronomy', 'Astronomy in Science'),
            ],
        },
        'Computer Science': {
            'description': 'Computer Science practice',
            'topics': [
                ('Data Structures', 'Data Structures in Computer Science'),
                ('Algorithms', 'Algorithms in Computer Science'),
                ('Databases', 'Databases in Computer Science'),
                ('Networks', 'Networks in Computer Science'),
            ],
        },
        'History': {
            'description': 'History practice',
            'topics': [
                ('Ancient', 'Ancient in History'),
                ('Medieval', 'Medieval in History'),
                ('Modern', 'Modern in History'),
                ('World Wars', 'World Wars in History'),
            ],
        },
        'English': {
            'description': 'English practice',
            'topics': [
                ('Grammar', 'Grammar in English'),
                ('Vocabulary', 'Vocabulary in English'),
                ('Comprehension', 'Comprehension in English'),
                ('Writing', 'Writing in English'),
            ],
        },
        'Goods and Services Tax (GST)': {
            'description': 'Goods and Services Tax (GST) practice',
            'topics': [
                (
                    'Place of Supply Rules',
                    'Rules determining the location where a supply is deemed to take place under GST.',
                ),
                (
                    'Reverse Charge Mechanism (RCM)',
                    'Mechanism where the recipient of goods or services is liable to pay GST instead of the supplier.',
                ),
                (
                    'Blocked Input Tax Credit (ITC)',
                    'Restrictions under GST law where input tax credit cannot be claimed for certain goods and services.',
                ),
            ],
        },
        'Income Tax': {
            'description': 'Income Tax practice',
            'topics': [
                (
                    'Capital Gains Taxation',
                    'Taxation of gains arising from the transfer of capital assets under the Income Tax Act.',
                ),
                (
                    'Income Tax Litigation and Appeals',
                    'Procedures and provisions related to disputes, appeals, and litigation under the Income Tax Act.',
                ),
                (
                    'Tax Deducted at Source (TDS) and Tax Collected at Source (TCS)',
                    'Provisions governing deduction and collection of tax at source under the Income Tax Act.',
                ),
            ],
        },
    }

    for subject_name, data in seed.items():
        subject, _ = Subject.objects.get_or_create(
            name=subject_name,
            defaults={'description': data['description']},
        )
        for topic_name, topic_desc in data['topics']:
            Topic.objects.get_or_create(
                subject=subject,
                name=topic_name,
                defaults={'description': topic_desc},
            )


def unseed_subjects_topics(apps, schema_editor):
    Subject = apps.get_model('subjects', 'Subject')
    Subject.objects.filter(
        name__in=[
            'Mathematics', 'Science', 'Computer Science', 'History', 'English',
            'Goods and Services Tax (GST)', 'Income Tax',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_subjects_topics, unseed_subjects_topics),
    ]
