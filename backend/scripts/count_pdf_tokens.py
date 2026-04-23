"""
Quick utility to count Gemini input tokens for a PDF file.
Useful for cost estimation and enforcing upload size limits.

Usage:
    python scripts/count_pdf_tokens.py /path/to/file.pdf

Requires:
    pip install pypdf google-generativeai
    GEMINI_API_KEY must be set in your .env file
"""

import os
import sys
from pathlib import Path

# Allow running from the backend/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examinator.settings.development')

import django
django.setup()

import google.generativeai as genai
from django.conf import settings

from pypdf import PdfReader

# Gemini pricing (per 1M tokens) — verify at https://ai.google.dev/pricing
PRICING = {
    'gemini-2.5-flash': {'input': 0.075, 'output': 0.30},
    'gemini-2.5-pro':   {'input': 1.25,  'output': 10.00},
}


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return '\n'.join(pages)


def count_tokens(text, model_name):
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name)
    result = model.count_tokens(text)
    return result.total_tokens


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/count_pdf_tokens.py /path/to/file.pdf')
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f'ERROR: File not found: {pdf_path}')
        sys.exit(1)

    print(f'\nPDF: {pdf_path.name}')
    print(f'File size: {pdf_path.stat().st_size / (1024 * 1024):.1f} MB')

    print('\nExtracting text...')
    text = extract_text(pdf_path)
    char_count = len(text)
    print(f'Extracted characters: {char_count:,}')

    if not text.strip():
        print('WARNING: No text extracted. PDF may be scanned/image-based.')
        sys.exit(1)

    print('\nCounting tokens (no generation cost)...')
    print('-' * 50)

    for model_name, prices in PRICING.items():
        tokens = count_tokens(text, model_name)
        input_cost = (tokens / 1_000_000) * prices['input']
        print(f'\nModel: {model_name}')
        print(f'  Input tokens : {tokens:,}')
        print(f'  Input cost   : ${input_cost:.6f}')
        print(f'  (Output cost depends on notes length generated)')

    print('\n' + '-' * 50)
    print('NOTE: Gemini 2.5 Flash free tier includes 1M tokens/day.')
    print('Verify current pricing at: https://ai.google.dev/pricing')


if __name__ == '__main__':
    main()
