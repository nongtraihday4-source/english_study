from django.test import TestCase
from django.contrib.auth import get_user_model
# pyrefly: ignore [missing-import]
from apps.curriculum.models import Lesson, Chapter, Course, CEFRLevel, UnlockRule
from apps.curriculum.services import UnlockService, ProgressService
from apps.progress.models import LessonProgress

User = get_user_model()

class ServiceLayerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pass")
        level = CEFRLevel.objects.create(code="A1", name="Beginner", order=1)
        course = Course.objects.create(level=level, title="Test Course", slug="test", order=1)  
        chapter = Chapter.objects.create(course=course, title="Ch1", order=1)
        self.l1 = Lesson.objects.create(chapter=chapter, title="L1", order=1, lesson_type="vocabulary")
        self.l2 = Lesson.objects.create(chapter=chapter, title="L2", order=2, lesson_type="grammar")
        UnlockRule.objects.create(lesson=self.l2, required_lesson=self.l1, min_score=60)

    def test_batch_unlock_zero_queries(self):
        LessonProgress.objects.create(user=self.user, lesson=self.l1, status="completed", best_score=80)
        lessons = list(Lesson.objects.filter(id__in=[self.l1.id, self.l2.id]))
        
        # 2 queries: 1 cho UnlockRule batch, 1 cho LessonProgress batch
        with self.assertNumQueries(2):
            result = UnlockService.batch_check_unlocked(self.user, lessons)
        
        self.assertTrue(result[self.l1.id])
        self.assertTrue(result[self.l2.id])

    def test_batch_progress_status(self):
        LessonProgress.objects.create(user=self.user, lesson=self.l1, status="completed", best_score=70)
        lessons = [self.l1, self.l2]
        result = ProgressService.batch_get_status(self.user, lessons)
        self.assertEqual(result[self.l1.id], "completed")
        self.assertEqual(result[self.l2.id], "locked")