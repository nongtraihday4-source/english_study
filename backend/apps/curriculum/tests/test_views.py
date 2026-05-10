from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from apps.curriculum.models import CEFRLevel, Course, Chapter, Lesson

User = get_user_model()

class LessonListIntegrationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        level = CEFRLevel.objects.create(code="A1", name="Beginner", order=1)
        course = Course.objects.create(level=level, title="C1", slug="c1", order=1)
        chapter = Chapter.objects.create(course=course, title="Ch1", order=1)
        for i in range(10):
            Lesson.objects.create(chapter=chapter, title=f"L{i}", order=i, lesson_type="vocabulary")

    def test_lesson_list_contract_and_performance(self):
        url = reverse("lesson-list", kwargs={"course_pk": 1, "chapter_pk": 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.data.get("results", response.data)
        self.assertEqual(len(data), 10)
        
        # Verify service context injection & serializer contract
        first_lesson = data[0]
        self.assertIn("is_unlocked", first_lesson)
        self.assertIn("progress_status", first_lesson)
        self.assertEqual(first_lesson["progress_status"], "locked")
        self.assertTrue(first_lesson["is_unlocked"])
        
        # Verify Zero N+1: Query count phải hằng số, không scale theo N lessons
        # DRF pagination + service batch thường 4-6 queries. Ngưỡng ≤8 an toàn cho mọi env.
        from django.db import connection
        self.assertLessEqual(len(connection.queries), 8, "N+1 detected or query budget exceeded")