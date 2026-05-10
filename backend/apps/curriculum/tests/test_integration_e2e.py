"""
E2E Integration Test: Frontend Contract → Backend SSOT → AI Fallback → Teacher Override
Verify toàn bộ luồng liên kết module.
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch

from apps.curriculum.services.scoring_service import ScoringService
from apps.ai.tasks import grade_submission_task
from apps.ai.models import AIGradingLog
from apps.teacher.services import TeacherService
from apps.progress.models import LessonProgress
from apps.curriculum.models import CEFRLevel, Course, Chapter, Lesson

User = get_user_model()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class FullPipelineIntegrationTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", email="teacher@test.com", password="pass", role="teacher")
        self.student = User.objects.create_user(username="student", email="student@test.com", password="pass")

        level = CEFRLevel.objects.create(code="A1", name="Beginner", order=1)
        course = Course.objects.create(level=level, title="C1", slug="c1", order=1)
        chapter = Chapter.objects.create(course=course, title="Ch1", order=1)
        self.lesson = Lesson.objects.create(
            chapter=chapter, title="L1", order=1, lesson_type="writing"
        )

    def test_full_pipeline_flow(self):
        # Step 1 & 2: Backend SSOT Scoring
        content_data = {
            "reading_questions": [{"correct": 0}, {"correct": 1}],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [0, 1]}
        score_result = ScoringService.calculate_lesson_score(content_data, raw_answers)

        self.assertEqual(score_result["score"], 100)
        self.assertEqual(score_result["status"], "completed")
        self.assertEqual(score_result["xp_gained"], 60)

        # Step 3: AI Async Grading (Writing) — fallback safe on short text
        ai_result = grade_submission_task(1, "writing", "I like cat.", "")
        self.assertEqual(ai_result["status"], "fallback")
        self.assertTrue(AIGradingLog.objects.filter(submission_id=1).exists())
        log = AIGradingLog.objects.get(submission_id=1)
        self.assertGreater(log.latency_ms, 0)

        # Step 4: Teacher Override
        lp = TeacherService.override_lesson_progress(
            teacher=self.teacher,
            student_id=self.student.id,
            lesson_id=self.lesson.id,
            status="completed",
            score=85,
            note="AI fallback adjusted by teacher",
        )
        self.assertEqual(lp.status, "completed")
        self.assertEqual(lp.best_score, 85)

        # Step 5: Final State Verification
        lp.refresh_from_db()
        self.assertEqual(lp.best_score, 85)
        self.assertEqual(lp.status, "completed")

        # Audit trail integrity
        self.assertEqual(AIGradingLog.objects.count(), 1)
        log = AIGradingLog.objects.first()
        self.assertEqual(log.status, "fallback")
        self.assertGreater(log.latency_ms, 0)

    def test_scoring_then_ai_fallback_independent(self):
        # Verify scoring and AI grading are independent flows
        content_data = {
            "reading_questions": [{"correct": 0}],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [1]}  # Wrong answer
        score_result = ScoringService.calculate_lesson_score(content_data, raw_answers)

        self.assertEqual(score_result["score"], 0)
        self.assertEqual(score_result["status"], "failed")
        self.assertEqual(score_result["xp_gained"], 10)  # No bonus

        # AI task still works independently
        ai_result = grade_submission_task(2, "writing", "A long sentence for testing.", "")
        self.assertIn(ai_result["status"], ["success", "fallback"])
        self.assertTrue(AIGradingLog.objects.filter(submission_id=2).exists())

    def test_teacher_override_after_ai_grading(self):
        # Teacher can override after AI grading is complete
        ai_result = grade_submission_task(3, "writing", "The weather is nice today.", "")
        self.assertIn(ai_result["status"], ["success", "fallback"])

        # Teacher overrides AI score
        lp = TeacherService.override_lesson_progress(
            teacher=self.teacher,
            student_id=self.student.id,
            lesson_id=self.lesson.id,
            status="completed",
            score=90,
            note="Good writing despite short text",
        )

        self.assertEqual(lp.best_score, 90)
        self.assertEqual(lp.status, "completed")
