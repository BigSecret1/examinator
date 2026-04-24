'''
Generate structured study notes from a PDF file using GeminiClientInterface.

Usage:
    python scripts/generate_notes.py /path/to/file.pdf [--force-vision]

Behaviour:
    - Digital PDFs (text density >= 100 chars/page) → text mode (cheap).
    - Scanned PDFs (text density <  100 chars/page) → vision mode: the raw
      PDF bytes are sent to Gemini, which performs OCR + structured note
      generation in a single call.
    - --force-vision: skip the density check and always use vision mode.

Output:
    Writes a Markdown notes file next to the PDF (same name, .md extension).
    Also logs the API cost via the GeminiAPICall model (requires migrate).

Limits (Phase 1, target audience: students):
    - Max pages:      65
    - Max file size:  15 MB
    - Min text:       ~500 chars (text mode); vision mode kicks in below this
'''

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examinator.settings.development')

import django
django.setup()

try:
    import fitz  # PyMuPDF
except ImportError:
    print('ERROR: PyMuPDF is not installed. Run: pip install pymupdf')
    sys.exit(1)

from geminiclient.api.interfaces import GeminiClientInterface

SYSTEM_INSTRUCTION_FILE = Path(__file__).resolve().parent / 'notes_system_instruction.md'

MAX_PAGES = 65
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MIN_DENSITY_CHARS_PER_PAGE = 100        # below this → assume scanned, use vision
MAX_OUTPUT_TOKENS = 32768

NOTES_SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'title': {'type': 'STRING'},
        'summary': {'type': 'STRING'},
        'learning_objectives': {
            'type': 'ARRAY',
            'items': {'type': 'STRING'},
        },
        'key_terms': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'term': {'type': 'STRING'},
                    'definition': {'type': 'STRING'},
                },
                'required': ['term', 'definition'],
            },
        },
        'flashcards': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'question': {'type': 'STRING'},
                    'answer': {'type': 'STRING'},
                },
                'required': ['question', 'answer'],
            },
        },
        'sections': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'heading': {'type': 'STRING'},
                    'overview': {'type': 'STRING'},
                    'subtopics': {
                        'type': 'ARRAY',
                        'items': {
                            'type': 'OBJECT',
                            'properties': {
                                'heading': {'type': 'STRING'},
                                'content_md': {'type': 'STRING'},
                                'examples': {
                                    'type': 'ARRAY',
                                    'items': {'type': 'STRING'},
                                },
                                'key_takeaways': {
                                    'type': 'ARRAY',
                                    'items': {'type': 'STRING'},
                                },
                            },
                            'required': ['heading', 'content_md'],
                        },
                    },
                },
                'required': ['heading', 'overview', 'subtopics'],
            },
        },
    },
    'required': [
        'title', 'summary', 'learning_objectives',
        'key_terms', 'flashcards', 'sections',
    ],
}

USER_PROMPT_TEMPLATE_TEXT = '''\
Generate structured study notes from the document below.

Detected outline (use these as your section headings if non-empty):
{outline}

--- BEGIN DOCUMENT TEXT ---
{text}
--- END DOCUMENT TEXT ---
'''

USER_PROMPT_TEMPLATE_VISION = '''\
Generate structured study notes from the attached PDF document.

The PDF is scanned or image-based. Read the page images directly: perform
OCR, interpret diagrams and equations, and produce the structured notes
defined by the schema. Use surrounding context to correct likely OCR errors.

Detected outline (use these as your section headings if non-empty):
{outline}
'''


def extract_pdf(pdf_path):
    '''Return (text, outline_lines, page_count) using PyMuPDF.

    `outline_lines` comes from the PDF's table of contents when available,
    otherwise from heading-like lines detected via font size.
    '''
    doc = fitz.open(pdf_path)

    page_count = doc.page_count
    if page_count > MAX_PAGES:
        doc.close()
        raise ValueError(
            f'PDF has {page_count} pages; limit is {MAX_PAGES}.'
        )

    pages_text = []
    for page in doc:
        pages_text.append(page.get_text('text'))

    toc = doc.get_toc()  # [[level, title, page], ...]
    outline_lines = []
    if toc:
        for level, title, _page in toc:
            indent = '  ' * max(0, level - 1)
            outline_lines.append(f'{indent}- {title.strip()}')
    else:
        outline_lines = _detect_headings_by_font_size(doc)

    doc.close()
    return '\n'.join(pages_text), outline_lines, page_count


def _detect_headings_by_font_size(doc):
    '''Fallback heading detection: lines whose font size is well above median.'''
    sizes = []
    spans = []  # (size, text, page_no)
    for page_no, page in enumerate(doc, start=1):
        for block in page.get_text('dict').get('blocks', []):
            for line in block.get('lines', []):
                text_parts = []
                line_size = 0
                for span in line.get('spans', []):
                    text_parts.append(span.get('text', ''))
                    line_size = max(line_size, span.get('size', 0))
                text = ''.join(text_parts).strip()
                if text and line_size > 0:
                    sizes.append(line_size)
                    spans.append((line_size, text, page_no))

    if not sizes:
        return []

    sizes_sorted = sorted(sizes)
    median = sizes_sorted[len(sizes_sorted) // 2]
    threshold = median * 1.25

    headings = []
    seen = set()
    for size, text, _page in spans:
        if size >= threshold and len(text) <= 120 and text not in seen:
            seen.add(text)
            headings.append(f'- {text}')
        if len(headings) >= 60:
            break
    return headings


def validate_pdf(pdf_path):
    if not pdf_path.exists():
        raise ValueError(f'File not found: {pdf_path}')
    if pdf_path.suffix.lower() != '.pdf':
        raise ValueError(f'Not a PDF file: {pdf_path}')
    size = pdf_path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f'File is {size / 1024 / 1024:.1f} MB; limit is '
            f'{MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f} MB.'
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate structured study notes from a PDF using Gemini.',
    )
    parser.add_argument('pdf_path', type=Path, help='Path to the PDF file.')
    parser.add_argument(
        '--force-vision',
        action='store_true',
        help='Skip text-density check and always use vision (PDF-as-image) mode.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    pdf_path = args.pdf_path

    try:
        validate_pdf(pdf_path)
    except ValueError as e:
        print(f'ERROR: {e}')
        sys.exit(1)

    print(f'Reading PDF: {pdf_path.name}', file=sys.stderr)
    try:
        text, outline_lines, page_count = extract_pdf(pdf_path)
    except ValueError as e:
        print(f'ERROR: {e}')
        sys.exit(1)

    density = len(text.strip()) / page_count if page_count else 0
    use_vision = args.force_vision or density < MIN_DENSITY_CHARS_PER_PAGE
    mode = 'vision' if use_vision else 'text'

    outline = '\n'.join(outline_lines) if outline_lines else '(no outline detected)'
    print(
        f'Pages: {page_count} | extracted: {len(text):,} chars '
        f'({density:.0f}/page) | outline entries: {len(outline_lines)} '
        f'| mode: {mode}',
        file=sys.stderr,
    )

    system_instruction = SYSTEM_INSTRUCTION_FILE.read_text(encoding='utf-8')

    if use_vision:
        prompt = USER_PROMPT_TEMPLATE_VISION.format(outline=outline)
        inline_files = [('application/pdf', pdf_path.read_bytes())]
        caller = 'pdf_notes_script_vision'
    else:
        prompt = USER_PROMPT_TEMPLATE_TEXT.format(outline=outline, text=text)
        inline_files = None
        caller = 'pdf_notes_script_text'

    print(f'Calling Gemini ({mode} mode)...', file=sys.stderr)
    result = GeminiClientInterface.generate(
        system_instruction=system_instruction,
        response_schema=NOTES_SCHEMA,
        prompt=prompt,
        caller=caller,
        inline_files=inline_files,
        max_output_tokens=MAX_OUTPUT_TOKENS,
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

    objectives = result.get('learning_objectives', [])
    if objectives:
        lines.append('## Learning Objectives')
        lines.append('')
        for obj in objectives:
            lines.append(f'- {obj}')
        lines.append('')

    key_terms = result.get('key_terms', [])
    if key_terms:
        lines.append('## Key Terms')
        lines.append('')
        for entry in key_terms:
            term = entry.get('term', '')
            definition = entry.get('definition', '')
            if term:
                lines.append(f'- **{term}** — {definition}')
        lines.append('')

    flashcards = result.get('flashcards', [])
    if flashcards:
        lines.append('## Flashcards')
        lines.append('')
        for i, card in enumerate(flashcards, start=1):
            question = card.get('question', '')
            answer = card.get('answer', '')
            lines.append(f'**Q{i}.** {question}')
            lines.append('')
            lines.append(f'**A.** {answer}')
            lines.append('')

    for section in result.get('sections', []):
        heading = section.get('heading', '')
        if heading:
            lines.append(f'## {heading}')
            lines.append('')

        overview = section.get('overview', '')
        if overview:
            lines.append(overview)
            lines.append('')

        for sub in section.get('subtopics', []):
            sub_heading = sub.get('heading', '')
            if sub_heading:
                lines.append(f'### {sub_heading}')
                lines.append('')

            content = sub.get('content_md', '')
            if content:
                lines.append(content)
                lines.append('')

            examples = sub.get('examples', [])
            if examples:
                lines.append('**Examples:**')
                lines.append('')
                for ex in examples:
                    lines.append(f'- {ex}')
                lines.append('')

            takeaways = sub.get('key_takeaways', [])
            if takeaways:
                lines.append('**Key takeaways:**')
                lines.append('')
                for t in takeaways:
                    lines.append(f'- {t}')
                lines.append('')

    return '\n'.join(lines)


if __name__ == '__main__':
    main()
