"""
Generate structured study notes from a PDF file using GeminiClientInterface.

Usage:
    python scripts/generate_notes.py /path/to/file.pdf

Output:
    Writes a Markdown notes file next to the PDF (same name, .md extension).
    Also logs the API cost via the GeminiAPICall model (requires migrate).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examinator.settings.development')

import django
django.setup()

try:
    from pypdf import PdfReader
except ImportError:
    print('ERROR: pypdf is not installed. Run: pip install pypdf')
    sys.exit(1)

from geminiclient.api.interfaces import GeminiClientInterface

SYSTEM_INSTRUCTION_FILE = Path(__file__).resolve().parent / 'notes_system_instruction.md'

NOTES_SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'title': {'type': 'STRING'},
        'summary': {'type': 'STRING'},
        'key_points': {
            'type': 'ARRAY',
            'items': {'type': 'STRING'},
        },
        'sections': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'heading': {'type': 'STRING'},
                    'content': {'type': 'STRING'},
                },
                'required': ['heading', 'content'],
            },
        },
    },
    'required': ['title', 'summary', 'key_points', 'sections'],
}

USER_PROMPT_TEMPLATE = '''\
Below is text extracted from a PDF document. Generate structured study notes from it.

Note: The text may end abruptly mid-sentence if the document was too large and had to be truncated. Generate notes for all content that is present — do not let the abrupt ending stop you.

--- BEGIN DOCUMENT TEXT ---
{text}
--- END DOCUMENT TEXT ---
'''

MAX_CHARS = 400_000  # ~100K tokens — safe limit for gemini-2.5-flash


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return '\n'.join(pages)


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/generate_notes.py /path/to/file.pdf')
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f'ERROR: File not found: {pdf_path}')
        sys.exit(1)

    print(f'Reading PDF: {pdf_path.name}', file=sys.stderr)
    text = extract_text(pdf_path)

    if not text.strip():
        print('ERROR: No text extracted. PDF may be scanned/image-based.')
        sys.exit(1)

    if len(text) > MAX_CHARS:
        print(
            f'WARNING: Document truncated from {len(text):,} to {MAX_CHARS:,} characters.',
            file=sys.stderr,
        )
        text = text[:MAX_CHARS]

    system_instruction = SYSTEM_INSTRUCTION_FILE.read_text(encoding='utf-8')
    prompt = USER_PROMPT_TEMPLATE.format(text=text)

    print('Calling Gemini...', file=sys.stderr)
    result = GeminiClientInterface.generate(
        system_instruction=system_instruction,
        response_schema=NOTES_SCHEMA,
        prompt=prompt,
        caller='pdf_notes_script',
    )

    output_path = pdf_path.with_suffix('.md')
    output_path.write_text(to_markdown(result), encoding='utf-8')
    print(f'Notes written to: {output_path}', file=sys.stderr)


def to_markdown(result):
    lines = []

    lines.append(f"# {result.get('title', 'Notes')}")
    lines.append('')

    summary = result.get('summary', '')
    if summary:
        lines.append('## Summary')
        lines.append('')
        lines.append(summary)
        lines.append('')

    key_points = result.get('key_points', [])
    if key_points:
        lines.append('## Key Points')
        lines.append('')
        for point in key_points:
            lines.append(f'- {point}')
        lines.append('')

    for section in result.get('sections', []):
        heading = section.get('heading', '')
        content = section.get('content', '')
        if heading:
            lines.append(f'## {heading}')
            lines.append('')
        if content:
            lines.append(content)
            lines.append('')

    return '\n'.join(lines)


if __name__ == '__main__':
    main()
