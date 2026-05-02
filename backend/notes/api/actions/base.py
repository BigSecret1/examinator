# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import logging

import fitz  # PyMuPDF
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from geminiclient.api.interfaces import GeminiClientInterface
from notes.models import (
    FileUploadActivity,
    FileUploadDailyUsage,
    Note,
    NoteFlashcard,
    NoteKeyTerm,
    NoteSection,
    NoteSubtopic,
    UserUploadQuota,
)

from ..utils import (
    MAX_FILE_SIZE_BYTES,
    MAX_OUTPUT_TOKENS,
    MAX_PAGES,
    MIN_DENSITY_CHARS_PER_PAGE,
    NOTES_SCHEMA,
    SYSTEM_INSTRUCTION,
    USER_PROMPT_TEMPLATE_TEXT,
    USER_PROMPT_TEMPLATE_VISION,
)

logger = logging.getLogger(__name__)


class NotesAPIAction:
    '''Business logic for notes upload, generation and persistence.'''

    @staticmethod
    def log_file_upload_event(
            *,
            user,
            file_name,
            file_size,
            page_count,
            status,
            rejection_reason,
            note=None,
            purpose=FileUploadActivity.PURPOSE_NOTES,
    ):
        return FileUploadActivity.objects.create(
            user=user,
            purpose=purpose,
            file_name=file_name or '',
            file_size=file_size or 0,
            page_count=page_count,
            status=status,
            rejection_reason=rejection_reason,
            note=note,
        )

    @staticmethod
    def get_user_daily_limit(user):
        quota = getattr(user, 'upload_quota', None)
        if quota and isinstance(quota, UserUploadQuota):
            return quota.daily_limit
        return settings.FILE_UPLOAD_DAILY_LIMIT

    @staticmethod
    def is_daily_quota_exceeded(user, date=None):
        target_date = date or timezone.localdate()
        limit = NotesAPIAction.get_user_daily_limit(user)
        usage = FileUploadDailyUsage.objects.filter(
            user=user,
            date=target_date,
        ).first()
        if not usage:
            return False
        return usage.count >= limit

    @staticmethod
    def increment_daily_usage(user, date=None):
        target_date = date or timezone.localdate()
        usage, _ = FileUploadDailyUsage.objects.get_or_create(
            user=user,
            date=target_date,
            defaults={'count': 0},
        )
        usage.count += 1
        usage.save(update_fields=['count', 'updated_at'])
        return usage

    @staticmethod
    def is_file_eligible(*, file_name, file_size, page_count):
        if file_name and not file_name.lower().endswith('.pdf'):
            return False, FileUploadActivity.REASON_NOT_PDF

        if file_size is not None and file_size > MAX_FILE_SIZE_BYTES:
            return False, FileUploadActivity.REASON_OVER_SIZE

        if page_count is not None and page_count > MAX_PAGES:
            return False, FileUploadActivity.REASON_OVER_PAGES

        return True, FileUploadActivity.REASON_OK

    @staticmethod
    def extract_text(pdf_bytes):
        doc = fitz.open(stream=pdf_bytes, filetype='pdf')
        page_count = doc.page_count

        pages_text = []
        for page in doc:
            pages_text.append(page.get_text('text'))

        toc = doc.get_toc()
        outline_lines = []
        if toc:
            for level, title, _page in toc:
                indent = '  ' * max(0, level - 1)
                outline_lines.append(f'{indent}- {title.strip()}')
        else:
            outline_lines = NotesAPIAction._detect_headings_by_font_size(doc)

        doc.close()
        return '\n'.join(pages_text), outline_lines, page_count

    @staticmethod
    def _detect_headings_by_font_size(doc):
        sizes = []
        spans = []
        for page in doc:
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
                        spans.append((line_size, text))

        if not sizes:
            return []

        sizes_sorted = sorted(sizes)
        median = sizes_sorted[len(sizes_sorted) // 2]
        threshold = median * 1.25

        headings = []
        seen = set()
        for size, text in spans:
            if size >= threshold and len(text) <= 120 and text not in seen:
                seen.add(text)
                headings.append(f'- {text}')
            if len(headings) >= 60:
                break
        return headings

    @staticmethod
    def resolve_processing_mode(*, pdf_bytes, text, page_count, force_vision=False):
        if force_vision:
            return 'vision'

        if not page_count:
            return 'vision'

        # Count image objects across the first 10 pages as a sample.
        try:
            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
            sample_pages = min(page_count, 10)
            image_pages = sum(
                1 for i in range(sample_pages) if doc[i].get_images()
            )
            doc.close()
        except Exception:
            image_pages = 0

        # If more than 30% of sampled pages contain images/figures, use vision
        # so diagrams and equations rendered as graphics are not lost.
        if image_pages / max(sample_pages, 1) > 0.30:
            return 'vision'

        # Fall back to text mode only for pure prose PDFs with sufficient density.
        density = len(text.strip()) / page_count
        return 'vision' if density < MIN_DENSITY_CHARS_PER_PAGE else 'text'

    @staticmethod
    def generate_notes(*, pdf_bytes, outline_lines, text, page_count, force_vision=True):
        mode = NotesAPIAction.resolve_processing_mode(
            pdf_bytes=pdf_bytes,
            text=text,
            page_count=page_count,
            force_vision=force_vision,
        )
        outline = '\n'.join(outline_lines) if outline_lines else '(no outline detected)'

        if mode == 'vision':
            prompt = USER_PROMPT_TEMPLATE_VISION.format(outline=outline)
            inline_files = [('application/pdf', pdf_bytes)]
            caller = 'notes_api_vision'
        else:
            prompt = USER_PROMPT_TEMPLATE_TEXT.format(outline=outline, text=text)
            inline_files = None
            caller = 'notes_api_text'

        result = GeminiClientInterface.generate(
            system_instruction=SYSTEM_INSTRUCTION,
            response_schema=NOTES_SCHEMA,
            prompt=prompt,
            caller=caller,
            inline_files=inline_files,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )

        return result, mode

    @staticmethod
    def create_note(*, user, source_filename, page_count, mode, result):
        return Note.objects.create(
            user=user,
            title=result.get('title', 'Notes'),
            summary=result.get('summary', ''),
            learning_objectives=result.get('learning_objectives', []),
            source_filename=source_filename or '',
            page_count=page_count or 0,
            generation_mode=mode,
            status=Note.STATUS_COMPLETED,
            error_message='',
        )

    @staticmethod
    def save_key_terms(*, note, key_terms):
        for idx, term in enumerate(key_terms):
            NoteKeyTerm.objects.create(
                note=note,
                term=term.get('term', ''),
                definition=term.get('definition', ''),
                position=idx,
            )

    @staticmethod
    def save_flashcards(*, note, flashcards):
        for idx, card in enumerate(flashcards):
            NoteFlashcard.objects.create(
                note=note,
                question=card.get('question', ''),
                answer=card.get('answer', ''),
                position=idx,
            )

    @staticmethod
    def save_sections(*, note, sections):
        for sec_idx, section in enumerate(sections):
            sec_obj = NoteSection.objects.create(
                note=note,
                heading=section.get('heading', ''),
                overview=section.get('overview', ''),
                position=sec_idx,
            )

            for sub_idx, subtopic in enumerate(section.get('subtopics', [])):
                NoteSubtopic.objects.create(
                    section=sec_obj,
                    heading=subtopic.get('heading', ''),
                    content_md=subtopic.get('content_md', ''),
                    examples=subtopic.get('examples', []),
                    key_takeaways=subtopic.get('key_takeaways', []),
                    position=sub_idx,
                )

    @staticmethod
    def persist_note_bundle(*, user, source_filename, page_count, mode, result):
        with transaction.atomic():
            note = NotesAPIAction.create_note(
                user=user,
                source_filename=source_filename,
                page_count=page_count,
                mode=mode,
                result=result,
            )
            NotesAPIAction.save_key_terms(
                note=note,
                key_terms=result.get('key_terms', []),
            )
            NotesAPIAction.save_flashcards(
                note=note,
                flashcards=result.get('flashcards', []),
            )
            NotesAPIAction.save_sections(
                note=note,
                sections=result.get('sections', []),
            )

        return note
