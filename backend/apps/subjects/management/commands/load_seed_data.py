# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.core.management.base import BaseCommand

from scripts.seed_loader import load_all


class Command(BaseCommand):
    help = 'Load seed data (subtopics, etc.) from YAML files into the database.'

    def handle(self, *args, **options):
        load_all()
