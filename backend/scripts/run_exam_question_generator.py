#!/usr/bin/env python3
"""Standalone entry point for the question generator cron job.

Runs both exam and daily question generators sequentially.

Usage:
    python3 scripts/run_exam_question_generator.py
"""
import json
import os
import sys

# Ensure the backend root (parent of this script's directory) is on sys.path
# so Django can locate the 'examinator' settings package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examinator.settings.production')
django.setup()

from scripts.question_generator import (  # noqa: E402
    DailyQuestionGenerator,
    ExamQuestionGenerator,
)


def main():
    failed = False

    for name, gen_cls in [('Exam', ExamQuestionGenerator), ('Daily', DailyQuestionGenerator)]:
        print(f'\n── {name} Question Generator ──')
        generator = gen_cls()
        report = generator.run()
        print(json.dumps(report, indent=2))
        if report['total_failed']:
            print(
                f"{name} FAILED: {report['total_failed']} generation(s) failed.",
                file=sys.stderr,
            )
            failed = True
        else:
            print(f"{name} SUCCESS: {report['total_success']} generation(s) succeeded.")

    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
