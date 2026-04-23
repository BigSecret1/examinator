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
                    response = model.generate_content(
                        prompt,
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
