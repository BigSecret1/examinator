# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import sys
from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from django.conf import settings
from django.db import transaction

from apps.subjects.models import Subject, Topic, SubTopic

BASE_DIR = Path(settings.BASE_DIR)
SEEDS_DIR = BASE_DIR / 'seeds' / 'data'


def read_file(path):
    """Read and validate a YAML seed file. Returns parsed data."""
    if not path.exists():
        raise FileNotFoundError(f'YAML file not found at {path}')

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not data or not isinstance(data, list):
        raise ValueError(f'{path.name}: YAML root must be a list.')

    return data


class SeedLoader(ABC):
    """Abstract base for all seed-data loaders."""

    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.created = 0
        self.updated = 0
        self.errors = []

    def load(self):
        """Read → persist → report."""
        items = read_file(self.yaml_path)
        with transaction.atomic():
            self.persist(items)
        self.report()

    @abstractmethod
    def validate(self, i, entry):
        """validate the given entry."""
        ...

    @abstractmethod
    def persist(self, items):
        """upsert items into the database."""
        ...

    def report(self):
        label = self.yaml_path.stem
        print(f'\n{label} sync complete:')
        print(f'  Created : {self.created}')
        print(f'  Updated : {self.updated}')
        if self.errors:
            print(f'  Errors  : {len(self.errors)}')
            for e in self.errors:
                print(f'    - {e}')
        else:
            print(f'  Errors  : 0')
        print()


class SubjectLoader(SeedLoader):

    def validate(self, i, entry):
        """Validate a single entry. Returns (name, description) or None."""
        name = (entry.get('name') or '').strip()
        description = (entry.get('description') or '').strip()

        if not name:
            self.errors.append(f'Row {i}: missing "name"')
            return None

        return name, description

    def persist(self, items):
        for i, entry in enumerate(items, start=1):
            result = self.validate(i, entry)
            if result is None:
                continue

            name, description = result
            _, was_created = Subject.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )
            if was_created:
                self.created += 1
            else:
                self.updated += 1


class TopicLoader(SeedLoader):

    def find_subject(self, name):
        return Subject.objects.filter(name__iexact=name).first()

    def validate(self, i, entry):
        """Validate a single entry. Returns (name, description, subject_ref) or None."""
        name = (entry.get('name') or '').strip()
        description = (entry.get('description') or '').strip()
        subject_ref = (entry.get('subject') or '').strip().lower()

        if not name:
            self.errors.append(f'Row {i}: missing "name"')
            return None
        if not subject_ref:
            self.errors.append(f'Row {i} ({name}): missing "subject"')
            return None

        return name, description, subject_ref

    def persist(self, items):
        for i, entry in enumerate(items, start=1):
            result = self.validate(i, entry)
            if result is None:
                continue

            name, description, subject_ref = result

            subject = self.find_subject(subject_ref)
            if subject is None:
                self.errors.append(
                    f'Row {i} ({name}): subject "{subject_ref}" not found in DB'
                )
                continue

            _, was_created = Topic.objects.update_or_create(
                subject=subject,
                name=name,
                defaults={'description': description},
            )
            if was_created:
                self.created += 1
            else:
                self.updated += 1


class SubtopicLoader(SeedLoader):

    def find_subject(self, name):
        return Subject.objects.filter(name__iexact=name).first()

    def find_topic(self, subject, topic_name):
        return Topic.objects.filter(subject=subject, name__iexact=topic_name).first()

    def validate(self, i, entry):
        """Validate a single entry. Returns (name, description, topic_ref, subject_ref) or None."""
        name = (entry.get('name') or '').strip()
        description = (entry.get('description') or '').strip()
        topic_ref = (entry.get('topic') or '').strip().lower()
        subject_ref = (entry.get('subject') or '').strip().lower()

        if not name:
            self.errors.append(f'Row {i}: missing "name"')
            return None
        if not topic_ref:
            self.errors.append(f'Row {i} ({name}): missing "topic"')
            return None
        if not subject_ref:
            self.errors.append(f'Row {i} ({name}): missing "subject"')
            return None

        return name, description, topic_ref, subject_ref

    def persist(self, items):
        for i, entry in enumerate(items, start=1):
            result = self.validate(i, entry)
            if result is None:
                continue

            name, description, topic_ref, subject_ref = result

            subject = self.find_subject(subject_ref)
            if subject is None:
                self.errors.append(
                    f'Row {i} ({name}): subject "{subject_ref}" not found in DB'
                )
                continue

            topic = self.find_topic(subject, topic_ref)
            if topic is None:
                self.errors.append(
                    f'Row {i} ({name}): topic "{topic_ref}" under subject "{subject_ref}" not found in DB'
                )
                continue

            _, was_created = SubTopic.objects.update_or_create(
                topic=topic,
                name=name,
                defaults={'description': description},
            )
            if was_created:
                self.created += 1
            else:
                self.updated += 1


def load_all():
    SubjectLoader(SEEDS_DIR / 'subjects.yaml').load()
    TopicLoader(SEEDS_DIR / 'topics.yaml').load()
    SubtopicLoader(SEEDS_DIR / 'subtopics.yaml').load()
