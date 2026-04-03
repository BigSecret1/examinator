#!/usr/bin/env python3
"""Standalone entry point for the exam question generator cron job.

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

from scripts.question_generator import ExamQuestionGenerator  # noqa: E402


def main():
    generator = ExamQuestionGenerator()
    report = generator.run()
    print(json.dumps(report, indent=2))
    if report['total_failed']:
        print(f"FAILED: {report['total_failed']} generation(s) failed.", file=sys.stderr)
        sys.exit(1)
    print(f"SUCCESS: {report['total_success']} generation(s) succeeded.")


if __name__ == '__main__':
    main()
