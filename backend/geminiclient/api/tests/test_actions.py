import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from geminiclient.api.actions import GeminiClientAction

FAKE_SCHEMA = {'type': 'OBJECT', 'properties': {'answer': {'type': 'STRING'}}}
FAKE_INSTRUCTION = 'You are a test assistant.'


@override_settings(GEMINI_API_KEY='test-key')
class GeminiClientActionInitTests(TestCase):
    """Tests for __init__ validation and defaults."""

    def test_raises_when_api_key_missing(self):
        with override_settings(GEMINI_API_KEY=''):
            with self.assertRaises(ValueError) as ctx:
                GeminiClientAction(
                    system_instruction=FAKE_INSTRUCTION,
                    response_schema=FAKE_SCHEMA,
                )
            assert 'GEMINI_API_KEY' in str(ctx.exception)

    @patch('geminiclient.api.actions.genai.configure')
    def test_configures_genai_with_api_key(self, mock_configure):
        GeminiClientAction(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
        )
        mock_configure.assert_called_once_with(api_key='test-key')

    @patch('geminiclient.api.actions.genai.configure')
    def test_uses_default_models(self, _):
        client = GeminiClientAction(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
        )
        assert client._models == GeminiClientAction.DEFAULT_MODELS

    @patch('geminiclient.api.actions.genai.configure')
    def test_accepts_custom_models(self, _):
        custom = ['gemini-custom-1']
        client = GeminiClientAction(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            models=custom,
        )
        assert client._models == custom

    @patch('geminiclient.api.actions.genai.configure')
    def test_accepts_custom_temperature(self, _):
        client = GeminiClientAction(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            temperature=0.9,
        )
        assert client._temperature == 0.9

    @patch('geminiclient.api.actions.genai.configure')
    def test_accepts_custom_max_retries(self, _):
        client = GeminiClientAction(
            system_instruction=FAKE_INSTRUCTION,
            response_schema=FAKE_SCHEMA,
            max_retries=2,
        )
        assert client._max_retries == 2


@override_settings(GEMINI_API_KEY='test-key')
class GeminiClientActionGenerateTests(TestCase):
    """Tests for the generate method — model fallback, retries, parsing."""

    def _make_client(self, **kwargs):
        with patch('geminiclient.api.actions.genai.configure'):
            return GeminiClientAction(
                system_instruction=FAKE_INSTRUCTION,
                response_schema=FAKE_SCHEMA,
                models=['model-a'],
                max_retries=2,
                **kwargs,
            )

    @patch('geminiclient.api.actions.genai.GenerativeModel')
    def test_returns_parsed_json_on_success(self, mock_model_cls):
        expected = {'answer': 'hello'}
        mock_response = MagicMock()
        mock_response.text = json.dumps(expected)
        mock_model_cls.return_value.generate_content.return_value = mock_response

        client = self._make_client()
        result = client.generate('test prompt')

        assert result == expected
        mock_model_cls.return_value.generate_content.assert_called_once_with(
            'test prompt',
            request_options={'timeout': 60},
        )

    @patch('geminiclient.api.actions.time.sleep')
    @patch('geminiclient.api.actions.genai.GenerativeModel')
    def test_retries_on_failure_then_succeeds(self, mock_model_cls, mock_sleep):
        expected = {'answer': 'recovered'}
        mock_response = MagicMock()
        mock_response.text = json.dumps(expected)
        mock_model_cls.return_value.generate_content.side_effect = [
            RuntimeError('transient error'),
            mock_response,
        ]

        client = self._make_client()
        result = client.generate('test prompt')

        assert result == expected
        assert mock_model_cls.return_value.generate_content.call_count == 2
        mock_sleep.assert_called_once()

    @patch('geminiclient.api.actions.time.sleep')
    @patch('geminiclient.api.actions.genai.GenerativeModel')
    def test_raises_after_all_retries_exhausted(self, mock_model_cls, mock_sleep):
        mock_model_cls.return_value.generate_content.side_effect = RuntimeError(
            'persistent failure'
        )

        client = self._make_client()
        with self.assertRaises(RuntimeError) as ctx:
            client.generate('test prompt')

        assert 'persistent failure' in str(ctx.exception)
        assert mock_model_cls.return_value.generate_content.call_count == 2

    @patch('geminiclient.api.actions.time.sleep')
    @patch('geminiclient.api.actions.genai.GenerativeModel')
    def test_falls_back_to_next_model(self, mock_model_cls, mock_sleep):
        expected = {'answer': 'from model-b'}
        mock_response = MagicMock()
        mock_response.text = json.dumps(expected)

        # model-a always fails, model-b succeeds
        call_count = {'n': 0}
        def side_effect(prompt, **kwargs):
            call_count['n'] += 1
            if call_count['n'] <= 2:  # max_retries for model-a
                raise RuntimeError('model-a down')
            return mock_response

        mock_model_cls.return_value.generate_content.side_effect = side_effect

        with patch('geminiclient.api.actions.genai.configure'):
            client = GeminiClientAction(
                system_instruction=FAKE_INSTRUCTION,
                response_schema=FAKE_SCHEMA,
                models=['model-a', 'model-b'],
                max_retries=2,
            )
        result = client.generate('test prompt')

        assert result == expected

    @patch('geminiclient.api.actions.time.sleep')
    @patch('geminiclient.api.actions.genai.GenerativeModel')
    def test_raises_after_all_models_exhausted(self, mock_model_cls, mock_sleep):
        mock_model_cls.return_value.generate_content.side_effect = RuntimeError(
            'all down'
        )

        with patch('geminiclient.api.actions.genai.configure'):
            client = GeminiClientAction(
                system_instruction=FAKE_INSTRUCTION,
                response_schema=FAKE_SCHEMA,
                models=['model-a', 'model-b'],
                max_retries=2,
            )
        with self.assertRaises(RuntimeError):
            client.generate('test prompt')

        # 2 models × 2 retries = 4 calls
        assert mock_model_cls.return_value.generate_content.call_count == 4

    @patch('geminiclient.api.actions.genai.GenerativeModel')
    def test_raises_on_invalid_json_response(self, mock_model_cls):
        mock_response = MagicMock()
        mock_response.text = 'not valid json{{'
        mock_model_cls.return_value.generate_content.return_value = mock_response

        client = self._make_client()
        with self.assertRaises(json.JSONDecodeError):
            client.generate('test prompt')

    @patch('geminiclient.api.actions.time.sleep')
    @patch('geminiclient.api.actions.genai.GenerativeModel')
    def test_no_sleep_after_last_retry(self, mock_model_cls, mock_sleep):
        mock_model_cls.return_value.generate_content.side_effect = RuntimeError(
            'fail'
        )

        client = self._make_client()  # max_retries=2
        with self.assertRaises(RuntimeError):
            client.generate('test prompt')

        # With 2 retries, sleep should be called once (after attempt 1, not after attempt 2)
        assert mock_sleep.call_count == 1
