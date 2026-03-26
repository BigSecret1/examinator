# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

"""
Archive seed data files.

For each YAML file in seeds/data/, copies its contents into the
matching archive sub-folder with a timestamp, then empties the
original file.

Usage:
    python scripts/archive_seeds.py
"""

import shutil
from datetime import date
from pathlib import Path

SEEDS_DIR = Path(__file__).resolve().parent.parent / 'seeds' / 'data'
ARCHIVE_DIR = SEEDS_DIR / 'archive'


def archive_seeds():
    """Archive every YAML file in the data directory."""
    today = date.today().strftime('%Y-%m-%d')
    archived = []

    for src in sorted(SEEDS_DIR.glob('*.yaml')):
        dest_dir = ARCHIVE_DIR / src.stem
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest = dest_dir / f'{src.stem}_{today}.yaml'
        if dest.exists():
            print(f'  Skipped {src.name} — archive already exists for {today}')
            continue

        shutil.copy2(src, dest)

        # Empty the original file
        src.write_text('')

        archived.append(src.name)
        print(f'  Archived {src.name} → {dest.relative_to(SEEDS_DIR)}')

    if not archived:
        print('Nothing to archive.')
    else:
        print(f'\nDone — {len(archived)} file(s) archived.')


if __name__ == '__main__':
    archive_seeds()
