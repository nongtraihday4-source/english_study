"""
App: curriculum
Models: CEFRLevel, Course, Chapter, Lesson, Exercise (polymorphic ref), UnlockRule
"""
from django.conf import settings
from django.db import models


class CEFRLevel(models.Model):
    code = models.CharField(max_length=3, unique=True)          # A1, A2, B1…
    name = models.CharField(max_length=50)                      # "Elementary"
    name_vi = models.CharField(max_length=50)                   # "Sơ cấp"
    order = models.SmallIntegerField(db_index=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "curriculum_cefrlevel"
        ordering = ["order"]

    def __str__(self):
        return self.code


class Course(models.Model):
    level = models.ForeignKey(CEFRLevel, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    order = models.SmallIntegerField(db_index=True)
    is_premium = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "curriculum_course"
        ordering = ["level__order", "order"]
        indexes = [
            models.Index(fields=["level", "order"]),
        ]

    def __str__(self):
        return f"{self.level.code} — {self.title}"


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=200)
    order = models.SmallIntegerField(db_index=True)
    description = models.TextField(null=True, blank=True)
    passing_score = models.SmallIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "curriculum_chapter"
        ordering = ["order"]
        indexes = [models.Index(fields=["course", "order"])]

    def __str__(self):
        return f"{self.course.slug} — Ch{self.order}: {self.title}"


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ("listening", "Nghe"),
        ("speaking", "Nói"),
        ("reading", "Đọc"),
        ("writing", "Viết"),
        ("grammar", "Ngữ pháp"),
        ("vocabulary", "Từ vựng"),
        ("pronunciation", "Phát âm"),
        ("assessment", "Kiểm tra"),
    ]

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    order = models.SmallIntegerField(db_index=True)
    lesson_type = models.CharField(max_length=15, choices=LESSON_TYPE_CHOICES, db_index=True)
    estimated_minutes = models.SmallIntegerField(default=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "curriculum_lesson"
        ordering = ["order"]
        indexes = [
            models.Index(fields=["chapter", "order"]),
            models.Index(fields=["lesson_type"]),
        ]

    def __str__(self):
        return f"Lesson({self.id}): {self.title} [{self.lesson_type}]"


class LessonExercise(models.Model):
    """
    Polymorphic join: links a Lesson to a concrete exercise in another app.
    exercise_type + exercise_id → e.g. ('listening', 7) → exercises_listeningexercise(id=7)
    """
    EXERCISE_TYPES = [
        ("listening", "Listening"),
        ("speaking", "Speaking"),
        ("reading", "Reading"),
        ("writing", "Writing"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="exercises")
    exercise_type = models.CharField(max_length=15, choices=EXERCISE_TYPES)
    exercise_id = models.BigIntegerField()
    order = models.SmallIntegerField(default=1)
    passing_score = models.SmallIntegerField(default=60)

    class Meta:
        db_table = "curriculum_lessonexercise"
        ordering = ["order"]
        indexes = [models.Index(fields=["exercise_type", "exercise_id"])]


class UnlockRule(models.Model):
    """Prerequisite rules: lesson is locked until required_lesson is completed with min_score."""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="unlock_rules")
    required_lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="unlocks"
    )
    min_score = models.SmallIntegerField(default=60)

    class Meta:
        db_table = "curriculum_unlockrule"

    def __str__(self):
        return f"Lesson {self.lesson_id} requires Lesson {self.required_lesson_id} ≥ {self.min_score}"
