from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.curriculum.models import CEFRLevel, Course, Chapter, Lesson, LessonContent
from apps.curriculum.serializers import LessonContentSerializer

User = get_user_model()


class MockRequest:
    def __init__(self, user):
        self.user = user
        self.data = {}


class PedagogyFeaturesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="pass", is_staff=True)
        level = CEFRLevel.objects.create(code="A1", name="Beginner", order=1)
        course = Course.objects.create(level=level, title="C1", slug="c1", order=1)
        chapter = Chapter.objects.create(course=course, title="Ch1", order=1)
        self.lesson = Lesson.objects.create(
            chapter=chapter, title="L1", order=1, lesson_type="reading"
        )
        self.content = LessonContent.objects.create(lesson=self.lesson)

    def test_learning_objectives_field_exists(self):
        self.content.learning_objectives = ["Hello world", "Basic grammar"]
        self.content.save()
        self.content.refresh_from_db()
        self.assertEqual(self.content.learning_objectives, ["Hello world", "Basic grammar"])

    def test_serializer_includes_objectives(self):
        self.content.learning_objectives = ["Objective 1"]
        self.content.save()
        serializer = LessonContentSerializer(self.content, context={"request": MockRequest(self.user)})
        self.assertIn("learning_objectives", serializer.data)
        self.assertEqual(serializer.data["learning_objectives"], ["Objective 1"])

    def test_schema_validates_objectives_list(self):
        payload = {"learning_objectives": ["Obj 1", "Obj 2"]}
        serializer = LessonContentSerializer(
            data=payload, context={"request": MockRequest(self.user)}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_schema_rejects_non_list_objectives(self):
        payload = {"learning_objectives": "Not a list"}
        serializer = LessonContentSerializer(
            data=payload, context={"request": MockRequest(self.user)}
        )
        self.assertFalse(serializer.is_valid())

    def test_objectives_empty_by_default(self):
        serializer = LessonContentSerializer(self.content, context={"request": MockRequest(self.user)})
        self.assertEqual(serializer.data["learning_objectives"], [])

    def test_objectives_can_hold_multiple_items(self):
        objectives = [f"Objective {i}" for i in range(5)]
        self.content.learning_objectives = objectives
        self.content.save()
        self.content.refresh_from_db()
        self.assertEqual(len(self.content.learning_objectives), 5)