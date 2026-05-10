"""
apps/curriculum/tests/test_schemas.py
TDD: Pydantic JSON Schema Validation cho LessonContent.
Test → Fail → Implement → Pass workflow.
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from apps.curriculum.models import CEFRLevel, Course, Chapter, Lesson, LessonContent
from apps.curriculum.serializers import LessonContentSerializer

User = get_user_model()


class MockRequest:
    def __init__(self, user):
        self.user = user
        self.data = {}


class LessonContentValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="pass", is_staff=True)
        level = CEFRLevel.objects.create(code="A1", name="Beginner", order=1)
        course = Course.objects.create(level=level, title="C1", slug="c1", order=1)
        chapter = Chapter.objects.create(course=course, title="Ch1", order=1)
        self.lesson = Lesson.objects.create(
            chapter=chapter, title="L1", order=1, lesson_type="reading"
        )
        LessonContent.objects.create(lesson=self.lesson)

    def _serializer(self, data):
        return LessonContentSerializer(
            data=data,
            context={"request": MockRequest(self.user)},
        )

    def test_reject_empty_question(self):
        payload = {
            "reading_questions": [
                {"question": "", "options": ["A", "B"], "correct": 0}
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_reject_correct_index_out_of_range(self):
        payload = {
            "reading_questions": [
                {"question": "Test?", "options": ["A", "B"], "correct": 5}
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_reject_prompt_injection(self):
        payload = {
            "reading_questions": [
                {
                    "question": "<script>alert(1)</script> {{system}}",
                    "options": ["A", "B"],
                    "correct": 0,
                }
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_reject_less_than_two_options(self):
        payload = {
            "reading_questions": [
                {"question": "Test?", "options": ["A"], "correct": 0}
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_reject_vocab_empty_word(self):
        payload = {
            "vocab_items": [
                {"word": "", "meaning_vi": "kiểm tra"}
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_reject_vocab_injection(self):
        payload = {
            "vocab_items": [
                {"word": "test {{ignore}}", "meaning_vi": "kiểm tra"}
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_reject_grammar_section_injection(self):
        payload = {
            "grammar_sections": [
                {
                    "title": "Test</script>",
                    "note": "Note {{system}}",
                    "examples": [{"en": "I am tall.", "vi": "Tôi cao."}],
                    "exercises": [],
                }
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_reject_grammar_exercise_wrong_correct_index(self):
        payload = {
            "grammar_sections": [
                {
                    "title": "Adjectives",
                    "exercises": [
                        {
                            "type": "gap-fill",
                            "prompt": "She is ___",
                            "options": ["tall", "run"],
                            "correct": 5,
                            "explanation": "Wrong",
                        }
                    ],
                }
            ]
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_accept_valid_reading_questions(self):
        payload = {
            "reading_questions": [
                {
                    "question": "What is the main topic?",
                    "options": ["A", "B", "C", "D"],
                    "correct": 1,
                    "explanation": "Correct answer is B",
                }
            ]
        }
        serializer = self._serializer(payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_accept_valid_vocab_items(self):
        payload = {
            "vocab_items": [
                {
                    "word": "hello",
                    "meaning_vi": "xin chào",
                    "pos": "noun",
                    "ipa": "/həˈloʊ/",
                    "definition_en": "A greeting",
                    "example_en": "Hello, world!",
                    "example_vi": "Xin chào, thế giới!",
                    "collocations": ["say ~"],
                    "highlight_in_passage": True,
                }
            ]
        }
        serializer = self._serializer(payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_accept_valid_grammar_section(self):
        payload = {
            "grammar_sections": [
                {
                    "title": "Present Simple",
                    "grammar_topic_id": 1,
                    "note": "Use present simple for habits",
                    "examples": [
                        {"en": "She works every day.", "vi": "Cô ấy làm việc mỗi ngày.", "highlight": "works"}
                    ],
                    "exercises": [
                        {
                            "type": "gap-fill",
                            "prompt": "He ___ English.",
                            "options": ["speak", "speaks"],
                            "correct": 1,
                            "explanation": "Third person singular",
                        }
                    ],
                }
            ]
        }
        serializer = self._serializer(payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_accept_valid_listening_content(self):
        payload = {
            "listening_content": {
                "audio_text": "Sample transcript",
                "translation_vi": "Bản dịch mẫu",
                "sentences": [{"text": "Hello world", "translation_vi": "Xin chào thế giới"}],
                "speed": 0.9,
                "comprehension_questions": [
                    {"question": "What is said?", "options": ["A", "B"], "correct": 0}
                ],
                "dictation_sentences": [
                    {"text": "Hello world", "hint": "H ___ w ___", "translation_vi": "Xin chào thế giới"}
                ],
            }
        }
        serializer = self._serializer(payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_reject_listening_comprehension_wrong_index(self):
        payload = {
            "listening_content": {
                "comprehension_questions": [
                    {"question": "What?", "options": ["A"], "correct": 3}
                ]
            }
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)

    def test_accept_empty_fields(self):
        payload = {
            "reading_questions": [],
            "vocab_items": [],
            "grammar_sections": [],
        }
        serializer = self._serializer(payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_reject_extra_forbidden_fields(self):
        payload = {
            "extra_field": "should be rejected",
            "reading_questions": [],
        }
        serializer = self._serializer(payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("json_schema", serializer.errors)