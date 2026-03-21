# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import sys
from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from django.conf import settings
from django.db import transaction

from apps.subjects.models import Topic, SubTopic

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


# ── Base loader (SRP: one reason to change per method, OCP: extend via subclass) ──

class SeedLoader(ABC):
    """Abstract base for all seed-data loaders."""

    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.created = 0
        self.updated = 0
        self.errors = []

    def load(self):
        """Template method — read → parse → persist → report."""
        data = read_file(self.yaml_path)
        items = self.parse(data)
        if not items:
            raise ValueError(f'No entries found in {self.yaml_path.name}.')
        with transaction.atomic():
            self.persist(items)
        self.report()

    @abstractmethod
    def parse(self, data):
        """Extract flat list of items from raw YAML structure."""
        ...

    @abstractmethod
    def persist(self, items):
        """Validate and upsert items into the database."""
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


# ── Concrete loader (LSP: substitutable for SeedLoader anywhere) ──

class SubtopicLoader(SeedLoader):

    def parse(self, data):
        items = []
        for block in data:
            if isinstance(block, dict) and 'subtopics' in block:
                items.extend(block['subtopics'])
            elif isinstance(block, dict) and 'name' in block:
                items.append(block)
            else:
                print(f'WARNING: Skipping unrecognised block: {block}')
        return items

    def persist(self, items):
        topics_by_key = {
            (t.subject.name.lower(), t.name.lower()): t
            for t in Topic.objects.select_related('subject').all()
        }

        for i, entry in enumerate(items, start=1):
            name = (entry.get('name') or '').strip()
            description = (entry.get('description') or '').strip()
            topic_ref = (entry.get('topic') or '').strip().lower()
            subject_ref = (entry.get('subject') or '').strip().lower()

            if not name:
                self.errors.append(f'Row {i}: missing "name"')
                continue
            if not topic_ref:
                self.errors.append(f'Row {i} ({name}): missing "topic"')
                continue
            if not subject_ref:
                self.errors.append(f'Row {i} ({name}): missing "subject"')
                continue

            topic = topics_by_key.get((subject_ref, topic_ref))
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


def load_subtopics():
    loader = SubtopicLoader(SEEDS_DIR / 'subtopics.yaml')
    loader.load()
    print()