from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.ai.services.grading_service import (
    GradingService,
    sanitize_input,
    build_writing_prompt,
)


class SanitizerTest(TestCase):
    def test_strip_html_and_injection(self):
        raw = "<script>alert(1)</script> Hello {{system}} ignore previous"
        clean = sanitize_input(raw)
        self.assertNotIn("<script>", clean)
        self.assertNotIn("{{system}}", clean)
        self.assertIn("Hello", clean)

    def test_reject_blank_or_too_short(self):
        self.assertIsNone(sanitize_input("   "))
        self.assertIsNone(sanitize_input("Ok"))

    def test_accept_valid_text(self):
        text = "I went to the store yesterday and bought some bread."
        result = sanitize_input(text)
        self.assertEqual(result, text)

    def test_strip_all_html_tags(self):
        raw = "<b>Hello</b> <p>World</p> and more text here"
        clean = sanitize_input(raw)
        self.assertNotIn("<b>", clean)
        self.assertNotIn("<p>", clean)
        self.assertIn("Hello", clean)
        self.assertIn("World", clean)


class PromptBuilderTest(TestCase):
    def test_writing_prompt_structure(self):
        prompt = build_writing_prompt("I go to school yesterday.", "Past Simple")
        self.assertEqual(len(prompt), 2)
        self.assertEqual(prompt[0]["role"], "system")
        self.assertIn("ESL Teacher", prompt[0]["content"])
        self.assertEqual(prompt[1]["role"], "user")
        self.assertIn("I go to school yesterday.", prompt[1]["content"])
        self.assertIn("Past Simple", prompt[1]["content"])
        self.assertIn("json", prompt[0]["content"].lower())

    def test_writing_prompt_empty_hint(self):
        prompt = build_writing_prompt("Hello world", "")
        self.assertEqual(len(prompt), 2)
        self.assertIn("Hello world", prompt[1]["content"])


class GradingServiceParseTest(TestCase):
    def test_parse_valid_json(self):
        raw = '{"score": 75, "feedback": "Verb tense error.", "rubric": {"grammar": 60, "vocab": 80}}'
        result = GradingService.parse_response(raw)
        self.assertEqual(result["score"], 75)
        self.assertEqual(result["feedback"], "Verb tense error.")
        self.assertIn("grammar", result["rubric"])

    def test_parse_malformed_json_fallback(self):
        raw = '{"score": 75, feedback: "Missing quote"}'
        result = GradingService.parse_response(raw)
        self.assertIsNone(result)

    def test_parse_missing_score(self):
        raw = '{"feedback": "No score"}'
        result = GradingService.parse_response(raw)
        self.assertIsNone(result)

    def test_parse_score_out_of_range(self):
        raw = '{"score": 150, "feedback": "Too high"}'
        result = GradingService.parse_response(raw)
        self.assertIsNone(result)

        raw = '{"score": -10, "feedback": "Negative"}'
        result = GradingService.parse_response(raw)
        self.assertIsNone(result)


class GradingServiceGradeTest(TestCase):
    @patch("apps.ai.services.grading_service.QwenClient")
    def test_grade_writing_fallback_empty(self, mock_client_class):
        result = GradingService.grade_writing(1, "   ", "")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["status"], "fallback")
        self.assertIn("ngắn", result["feedback"])

    @patch("apps.ai.services.grading_service.QwenClient")
    def test_grade_writing_fallback_too_short(self, mock_client_class):
        result = GradingService.grade_writing(1, "Hello", "")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["status"], "fallback")

    @patch("apps.ai.services.grading_service.QwenClient")
    def test_grade_writing_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.generate_json.return_value = {
            "score": 80,
            "feedback": "Good",
            "rubric": {"grammar": 80, "vocab": 80, "coherence": 80},
        }

        result = GradingService.grade_writing(1, "I went to the store yesterday.", "Past Simple")

        self.assertEqual(result["score"], 80)
        self.assertEqual(result["status"], "success")
        self.assertIn("prompt_hash", result)
        self.assertIn("latency_ms", result)

    @patch("apps.ai.services.grading_service.QwenClient")
    def test_grade_writing_fallback_on_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.generate_json.side_effect = Exception("Connection refused")

        result = GradingService.grade_writing(1, "I went to the store yesterday.", "")

        self.assertEqual(result["status"], "fallback")
        self.assertIn("error", result)
        self.assertGreater(result["score"], 0)