# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import logging

from .actions import NotesAPIAction

logger = logging.getLogger(__name__)


class NotesInterface:

    @staticmethod
    def generate_notes_from_pdf(
            *,
            user,
            file_name,
            file_size,
            pdf_bytes,
            force_vision=False,
    ):
        try:
            text, outline_lines, page_count = NotesAPIAction.extract_text(
                pdf_bytes
            )
            eligible, reason = NotesAPIAction.is_file_eligible(
                file_name=file_name,
                file_size=file_size,
                page_count=page_count,
            )
            if not eligible:
                return {
                    'status': 'rejected',
                    'reason': reason,
                    'page_count': page_count,
                }

            if NotesAPIAction.is_daily_quota_exceeded(user):
                return {
                    'status': 'rejected',
                    'reason': 'daily_limit_exceeded',
                    'page_count': page_count,
                }

            result, mode = NotesAPIAction.generate_notes(
                pdf_bytes=pdf_bytes,
                outline_lines=outline_lines,
                text=text,
                page_count=page_count,
                force_vision=force_vision,
            )
            note = NotesAPIAction.write_note_to_db(
                user=user,
                source_filename=file_name,
                page_count=page_count,
                mode=mode,
                result=result,
            )
            NotesAPIAction.increment_daily_usage(user)
            return {
                'status': 'success',
                'note_id': note.id,
                'page_count': page_count,
                'generation_mode': mode,
            }
        except Exception as exc:
            logger.exception('generate_notes_from_pdf failed')
            return {'status': 'error', 'error': str(exc)}

