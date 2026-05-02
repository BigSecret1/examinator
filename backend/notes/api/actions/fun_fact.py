# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

import logging

import google.generativeai as genai
from django.conf import settings
from django.utils import timezone

from notes.models import DailyFunFact

logger = logging.getLogger(__name__)

_FUN_FACT_MODEL = 'gemini-2.5-flash'
_FUN_FACT_PROMPT = (
    'Generate a single fascinating, surprising, or delightful fun fact '
    'about science, history, mathematics, nature, technology, or the '
    'universe. The fact should spark curiosity and bring a smile. '
    'Write it as one or two punchy sentences. No intro, no label, '
    'no bullet — just the fact itself.'
)


class FunFactAction:
    '''Generates and caches a daily fun fact per user.'''

    @staticmethod
    def get_fun_fact(user):
        '''Return today\'s fun fact for the user, generating it if needed.'''
        today = timezone.localdate()

        cached = DailyFunFact.objects.filter(user=user, date=today).first()
        if cached:
            return cached.fact

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return None

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(_FUN_FACT_MODEL)
            response = model.generate_content(
                _FUN_FACT_PROMPT,
                request_options={'timeout': 15},
            )
            fact = response.text.strip()
        except Exception:
            logger.exception('Fun fact generation failed')
            return None

        DailyFunFact.objects.get_or_create(
            user=user,
            date=today,
            defaults={'fact': fact},
        )
        return fact
