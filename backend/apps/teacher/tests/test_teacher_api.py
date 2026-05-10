from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from apps.curriculum.models import CEFRLevel, Course, Chapter, Lesson
from apps.progress.models import LessonProgress
from apps.teacher.services import TeacherService

User = get_user_model()


class TeacherServiceTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", email="teacher@test.com", password="pass", role="teacher")
        self.student = User.objects.create_user(username="student", email="student@test.com", password="pass")
        level = CEFRLevel.objects.create(code="A1", name="Beginner", order=1)
        course = Course.objects.create(level=level, title="C1", slug="c1", order=1)
        chapter = Chapter.objects.create(course=course, title="Ch1", order=1)
        self.lesson = Lesson.objects.create(chapter=chapter, title="L1", order=1, lesson_type="reading")

    def test_override_create_new_progress(self):
        lp = TeacherService.override_lesson_progress(
            self.teacher, self.student.id, self.lesson.id, "completed", 80
        )
        self.assertEqual(lp.status, "completed")
        self.assertEqual(lp.best_score, 80)
        self.assertEqual(lp.user, self.student)

    def test_override_update_existing_progress(self):
        LessonProgress.objects.create(user=self.student, lesson=self.lesson, status="locked", best_score=0)
        lp = TeacherService.override_lesson_progress(
            self.teacher, self.student.id, self.lesson.id, "completed", 90
        )
        lp.refresh_from_db()
        self.assertEqual(lp.status, "completed")
        self.assertEqual(lp.best_score, 90)

    def test_stuck_points_aggregation(self):
        # Create 3 different students with low scores for the same lesson
        for i in range(3):
            student = User.objects.create_user(
                username=f"student{i}", 
                email=f"student{i}@test.com", 
                password="pass"
            )
            LessonProgress.objects.create(
                user=student, lesson=self.lesson, status="completed", best_score=40 + i
            )

        stuck_data = list(
            TeacherService.get_stuck_points(self.lesson.chapter.course.id, threshold_score=60)
        )

        self.assertEqual(len(stuck_data), 1)
        self.assertEqual(stuck_data[0]["lesson_id"], self.lesson.id)
        self.assertLess(stuck_data[0]["avg_score"], 60)
        self.assertEqual(stuck_data[0]["attempts"], 3)

    def test_stuck_points_empty_when_all_pass(self):
        LessonProgress.objects.create(
            user=self.student, lesson=self.lesson, status="completed", best_score=80
        )
        stuck_data = list(
            TeacherService.get_stuck_points(self.lesson.chapter.course.id, threshold_score=60)
        )
        self.assertEqual(len(stuck_data), 0)

    def test_stuck_points_includes_min_score(self):
        LessonProgress.objects.create(
            user=self.student, lesson=self.lesson, status="completed", best_score=30
        )
        stuck_data = list(
            TeacherService.get_stuck_points(self.lesson.chapter.course.id, threshold_score=60)
        )
        self.assertEqual(stuck_data[0]["min_score"], 30)


class TeacherAPITest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", email="teacher@test.com", password="pass", role="teacher")
        self.student = User.objects.create_user(username="student", email="student@test.com", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.teacher)

        level = CEFRLevel.objects.create(code="A1", name="Beginner", order=1)
        course = Course.objects.create(level=level, title="C1", slug="c1", order=1)
        chapter = Chapter.objects.create(course=course, title="Ch1", order=1)
        self.lesson = Lesson.objects.create(chapter=chapter, title="L1", order=1, lesson_type="reading")

    def test_override_api_success(self):
        url = reverse("teacher-override")
        payload = {
            "student_id": self.student.id,
            "lesson_id": self.lesson.id,
            "status": "completed",
            "score": 85,
            "note": "Teacher override",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["lesson_progress"]["status"], "completed")
        self.assertEqual(response.data["lesson_progress"]["best_score"], 85)

    def test_override_api_missing_fields(self):
        url = reverse("teacher-override")
        payload = {"student_id": self.student.id}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    def test_stuck_points_api(self):
        LessonProgress.objects.create(
            user=self.student, lesson=self.lesson, status="completed", best_score=30
        )

        url = reverse("teacher-stuck-points")
        response = self.client.get(url, {"course_id": self.lesson.chapter.course.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["avg_score"], 30.0)

    def test_stuck_points_api_missing_course_id(self):
        url = reverse("teacher-stuck-points")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("course_id", response.data["detail"])

    def test_override_requires_authentication(self):
        self.client.logout()
        url = reverse("teacher-override")
        payload = {
            "student_id": self.student.id,
            "lesson_id": self.lesson.id,
            "status": "completed",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 403)
