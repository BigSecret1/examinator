import json
import logging
import time
from decimal import Decimal

import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Cost per 1M tokens in USD — verify at https://ai.google.dev/pricing
MODEL_PRICING = {
    'gemini-2.5-flash': {'input': Decimal('0.075'),  'output': Decimal('0.30')},
    # 'gemini-2.5-pro':   {'input': Decimal('1.25'),   'output': Decimal('10.00')},
}
MILLION = Decimal('1000000')


class GeminiClientAction:
    DEFAULT_MODELS = [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
    ]
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]

    def __init__(
            self,
            system_instruction,
            response_schema,
            temperature=0.5,
            models=None,
            max_retries=None,
            caller='',
            max_output_tokens=None,
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
        self._caller = caller
        self._max_output_tokens = max_output_tokens

    def _build_model(self, model_name):
        config_kwargs = {
            'response_mime_type': 'application/json',
            'response_schema': self._response_schema,
            'temperature': self._temperature,
        }
        if self._max_output_tokens:
            config_kwargs['max_output_tokens'] = self._max_output_tokens

        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self._system_instruction,
            generation_config=genai.GenerationConfig(**config_kwargs),
        )

    def generate(self, prompt, inline_files=None):
        '''Generate a structured response from Gemini.

        Args:
            prompt: The text prompt (string).
            inline_files: Optional list of (mime_type, bytes) tuples to send
                alongside the prompt. Used for multimodal inputs such as PDFs
                (mime_type='application/pdf') or images.
        '''
        parts = []
        if inline_files:
            for mime_type, data in inline_files:
                parts.append({'mime_type': mime_type, 'data': data})
        parts.append(prompt)

        last_error = None

        for model_name in self._models:
            model = self._build_model(model_name)

            for attempt in range(self._max_retries):
                try:
                    logger.info(
                        'GeminiClient: model=%s attempt=%d',
                        model_name,
                        attempt + 1, )
                    response = model.generate_content(
                        parts,
                        request_options={'timeout': 300},
                    )
                    self._log_cost(model_name, response.usage_metadata)
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

    def _log_cost(self, model_name, usage):
        try:
            from geminiclient.models import GeminiAPICall
            input_tokens = usage.prompt_token_count or 0
            output_tokens = usage.candidates_token_count or 0
            prices = MODEL_PRICING.get(model_name, {'input': Decimal('0'), 'output': Decimal('0')})
            input_cost = (Decimal(input_tokens) / MILLION) * prices['input']
            output_cost = (Decimal(output_tokens) / MILLION) * prices['output']
            GeminiAPICall.objects.create(
                model_name=model_name,
                caller=self._caller,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost_usd=input_cost,
                output_cost_usd=output_cost,
                total_cost_usd=input_cost + output_cost,
            )
            logger.info(
                'GeminiClient: cost logged | model=%s input=%d output=%d total=$%s',
                model_name, input_tokens, output_tokens, input_cost + output_cost,
            )
        except Exception as e:
            logger.warning('GeminiClient: failed to log cost: %s', e)
