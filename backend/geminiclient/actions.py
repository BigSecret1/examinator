import json
import logging
import time

import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    DEFAULT_MODELS = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
    ]
    MAX_RETRIES = 5
    RETRY_DELAYS = [1, 2, 4, 8, 16]

    def __init__(
            self,
            system_instruction,
            response_schema,
            temperature=0.7,
            models=None,
            max_retries=None,
    ):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError('GEMINI_API_KEY is not configured in settings.')

        genai.configure(api_key=api_key)

        self._system_instruction = system_instruction
        self._response_schema = response_schema
        self._temperature = temperature
        self._models = models or self.DEFAULT_MODELS
        self._max_retries = max_retries or self.MAX_RETRIES

    def _build_model(self, model_name):
        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self._system_instruction,
            generation_config=genai.GenerationConfig(
                response_mime_type='application/json',
                response_schema=self._response_schema,
                temperature=self._temperature,
            ),
        )

    def generate(self, prompt):
        last_error = None

        for model_name in self._models:
            model = self._build_model(model_name)

            for attempt in range(self._max_retries):
                try:
                    logger.info(
                        'GeminiClient: model=%s attempt=%d',
                        model_name,
                        attempt + 1, )
                    response = model.generate_content(prompt)
                    return json.loads(response.text)

                except Exception as e:
                    logger.warning(
                        'GeminiClient: model=%s attempt=%d failed: %s',
                        model_name, attempt + 1, e,
                    )
                    last_error = e
                    if attempt < self._max_retries - 1:
                        time.sleep(self.RETRY_DELAYS[attempt])

        raise last_error or ValueError('All Gemini models failed after retries.')
