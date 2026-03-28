from unittest.mock import MagicMock, patch

from django.test import TestCase

from geminiclient.api.interfaces import GeminiClientInterface

FAKE_SCHEMA = {'type': 'OBJECT', 'properties': {'answer': {'type': 'STRING'}}}
FAKE_INSTRUCTION = 'You are a test assistant.'
FAKE_PROMPT = 'Say hello.'


class GeminiClientInterfaceTests(TestCase):

    @patch('geminiclient.api.interfaces.GeminiClientAction')
    def test_generate_creates_action_with_required_args(self, mock_action_cls):
        mock_action_cls.return_value.generate.return_value = {'ok': True}

        GeminiClientInterface.generate(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            prompt=FAKE_PROMPT,
        )

        mock_action_cls.assert_called_once_with(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
        )

    @patch('geminiclient.api.interfaces.GeminiClientAction')
    def test_generate_passes_kwargs_to_action(self, mock_action_cls):
        mock_action_cls.return_value.generate.return_value = {}

        GeminiClientInterface.generate(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            prompt=FAKE_PROMPT,
            temperature=0.9,
            models=['custom-model'],
            max_retries=3,
        )

        mock_action_cls.assert_called_once_with(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            temperature=0.9,
            models=['custom-model'],
            max_retries=3,
        )

    @patch('geminiclient.api.interfaces.GeminiClientAction')
    def test_generate_calls_action_generate_with_prompt(self, mock_action_cls):
        mock_action_cls.return_value.generate.return_value = {}

        GeminiClientInterface.generate(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            prompt=FAKE_PROMPT,
        )

        mock_action_cls.return_value.generate.assert_called_once_with(FAKE_PROMPT)

    @patch('geminiclient.api.interfaces.GeminiClientAction')
    def test_generate_returns_action_result(self, mock_action_cls):
        expected = {'answer': 'hello world'}
        mock_action_cls.return_value.generate.return_value = expected

        result = GeminiClientInterface.generate(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            prompt=FAKE_PROMPT,
        )

        assert result == expected

    @patch('geminiclient.api.interfaces.GeminiClientAction')
    def test_generate_propagates_action_exception(self, mock_action_cls):
        mock_action_cls.return_value.generate.side_effect = ValueError('API failed')

        with self.assertRaises(ValueError) as ctx:
            GeminiClientInterface.generate(
                system_instruction=FAKE_INSTRUCTION,
                response_schema=FAKE_SCHEMA,
                prompt=FAKE_PROMPT,
            )

        assert 'API failed' in str(ctx.exception)

    @patch('geminiclient.api.interfaces.GeminiClientAction')
    def test_generate_propagates_init_exception(self, mock_action_cls):
        mock_action_cls.side_effect = ValueError('GEMINI_API_KEY is not configured')

        with self.assertRaises(ValueError) as ctx:
            GeminiClientInterface.generate(
                system_instruction=FAKE_INSTRUCTION,
                response_schema=FAKE_SCHEMA,
                prompt=FAKE_PROMPT,
            )

        assert 'GEMINI_API_KEY' in str(ctx.exception)
