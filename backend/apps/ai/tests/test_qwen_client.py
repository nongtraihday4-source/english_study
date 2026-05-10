from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock

from apps.ai.services.qwen_client import QwenClient


@override_settings(AI_BASE_URL="http://localhost:11434/v1", AI_MODEL="qwen3.5-9b")
class QwenClientTest(TestCase):
    @patch("apps.ai.services.qwen_client.OpenAI")
    def test_client_initialization(self, mock_openai):
        client = QwenClient()
        mock_openai.assert_called_once_with(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            timeout=15.0,
        )

    @patch("apps.ai.services.qwen_client.OpenAI")
    def test_generate_json_response(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"score": 80, "feedback": "Good"}'))]
        )

        client = QwenClient()
        result = client.generate_json([{"role": "user", "content": "Test"}])

        self.assertEqual(result, {"score": 80, "feedback": "Good"})
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["response_format"]["type"], "json_object")

    @patch("apps.ai.services.qwen_client.OpenAI")
    def test_timeout_handling(self, mock_openai):
        from openai import APITimeoutError

        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = APITimeoutError("Timeout")

        client = QwenClient()
        with self.assertRaises(APITimeoutError):
            client.generate_json([{"role": "user", "content": "Test"}])