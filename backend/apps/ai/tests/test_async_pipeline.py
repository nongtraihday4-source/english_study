from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock

from apps.ai.tasks import grade_submission_task
from apps.ai.models import AIGradingLog


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class AsyncPipelineTest(TestCase):
    @patch("apps.ai.tasks.GradingService.grade_writing")
    def test_task_success_flow(self, mock_grade):
        mock_grade.return_value = {
            "score": 85,
            "feedback": "Good job",
            "status": "success",
            "latency_ms": 1200,
            "prompt_hash": "abc123",
        }

        result = grade_submission_task(1, "writing", "I go to school.", "Present Simple")

        self.assertEqual(result["score"], 85)
        self.assertEqual(result["status"], "success")
        self.assertTrue(AIGradingLog.objects.filter(submission_id=1).exists())
        log = AIGradingLog.objects.get(submission_id=1)
        self.assertEqual(log.score, 85)
        self.assertEqual(log.status, "success")

    @patch("apps.ai.tasks.GradingService.grade_writing")
    def test_task_fallback_flow(self, mock_grade):
        mock_grade.return_value = {
            "score": 40,
            "feedback": "Fallback due to error",
            "status": "fallback",
            "latency_ms": 50,
            "prompt_hash": "err123",
        }

        result = grade_submission_task(2, "writing", "Test text", "")

        self.assertEqual(result["status"], "fallback")
        self.assertTrue(
            AIGradingLog.objects.filter(submission_id=2, status="fallback").exists()
        )

    @patch("apps.ai.tasks.GradingService.grade_writing")
    def test_task_retry_on_exception(self, mock_grade):
        mock_grade.side_effect = ConnectionError("LLM unreachable")

        with self.assertRaises(Exception):
            grade_submission_task(3, "writing", "Test", "")

    @patch("apps.ai.tasks.GradingService.grade_writing")
    def test_task_logs_audit_trail(self, mock_grade):
        mock_grade.return_value = {
            "score": 72,
            "feedback": "Nice work",
            "status": "success",
            "latency_ms": 890,
            "prompt_hash": "def456",
        }

        grade_submission_task(10, "speaking", "Hello world text.", "")

        self.assertEqual(AIGradingLog.objects.filter(submission_id=10).count(), 1)
        log = AIGradingLog.objects.get(submission_id=10)
        self.assertEqual(log.submission_type, "speaking")
        self.assertEqual(log.latency_ms, 890)
        self.assertEqual(log.prompt_hash, "def456")
