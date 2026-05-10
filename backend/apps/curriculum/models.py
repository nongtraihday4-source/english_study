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


class LessonContent(models.Model):
    """
    Rich integrated content for a lesson.
    Each lesson has ONE content record containing all materials:
    reading passage, vocab highlights, grammar notes, exercises, SRS config.
    """
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="content")

    # ── Reading passage ──────────────────────────────────────────────────
    reading_passage = models.TextField(
        blank=True, default="",
        help_text="HTML/Markdown reading passage for the lesson.",
    )
    reading_image_url = models.CharField(
        max_length=500, blank=True, default="",
        help_text="Optional hero image for the reading passage.",
    )
    reading_questions = models.JSONField(
        default=list, blank=True,
        help_text='[{"question":"…","options":["a","b","c","d"],"correct":0,"explanation":"…"}]',
    )
    learning_objectives = models.JSONField(
        default=list, blank=True,
        help_text='["Understand present simple", "Learn 10 vocab words"]',
    )

    # ── Vocabulary items ─────────────────────────────────────────────────
    vocab_items = models.JSONField(
        default=list, blank=True,
        help_text=(
            '[{"word":"headache","pos":"noun","ipa":"/ˈhed.eɪk/","meaning_vi":"đau đầu",'
            '"definition_en":"A pain inside your head.","example_en":"I have a headache.",'
            '"example_vi":"Tôi bị đau đầu.","collocations":["have a ~","splitting ~"],'
            '"highlight_in_passage":true}]'
        ),
    )
    vocab_word_ids = models.JSONField(
        default=list, blank=True,
        help_text="List of vocabulary.Word PKs linked to this lesson (for SRS tracking).",
    )

    # ── Grammar spotlight ────────────────────────────────────────────────
    grammar_topic_id = models.IntegerField(
        null=True, blank=True,
        help_text="FK to grammar.GrammarTopic (for deep-link).",
    )
    grammar_title = models.CharField(max_length=200, blank=True, default="")
    grammar_note = models.TextField(
        blank=True, default="",
        help_text="Short grammar explanation in context of the lesson theme.",
    )
    grammar_examples = models.JSONField(
        default=list, blank=True,
        help_text='[{"en":"She is tall.","vi":"Cô ấy cao.","highlight":"is"}]',
    )

    # ── Grammar sections (new: multiple topics per lesson) ───────────────
    grammar_sections = models.JSONField(
        default=list, blank=True,
        help_text=(
            '[{"title":"...","grammar_topic_id":null,"note":"...","examples":[...],'
            '"exercises":[{"type":"gap-fill","prompt":"...","options":[...],'
            '"correct":0,"explanation":"..."}]}]'
        ),
    )

    # ── Skill practice sections (structured: dictation/shadowing/writing) ─
    skill_sections = models.JSONField(
        default=dict, blank=True,
        help_text='{"dictation":[...],"shadowing":[...],"guided_writing":[...]}',
    )

    # ── Dedicated skill lesson content ───────────────────────────────────
    listening_content = models.JSONField(
        default=dict, blank=True,
        help_text=(
            '{"audio_text":"...","translation_vi":"...",'
            '"sentences":[{"text":"...","translation_vi":"...","audio_url":""}],'
            '"speed":0.9,"comprehension_questions":[{"question":"...","options":[...],'
            '"correct":0,"explanation":"..."}],'
            '"dictation_sentences":[{"text":"...","hint":"...","translation_vi":"..."}]}'
        ),
    )
    speaking_content = models.JSONField(
        default=dict, blank=True,
        help_text=(
            '{"mode":"repeat|shadow|dialogue",'
            '"sentences":[{"text":"...","translation_vi":"...","speed":0.85,'
            '"focus_words":["key","words"]}],'
            '"dialogue":[{"speaker":"A","text":"...","translation_vi":"..."}]}'
        ),
    )
    writing_content = models.JSONField(
        default=dict, blank=True,
        help_text=(
            '{"exercises":[{"type":"word_order|gap_fill|sentence_completion|guided|free",'
            '"prompt":"...","prompt_vi":"...","grammar_hint":"...",'
            '"items":[["word","order","items"]],'
            '"correct_answer":"...","min_words":8,"max_words":25,'
            '"sample_answer":"..."}]}'
        ),
    )

    # ── Exercises ────────────────────────────────────────────────────────
    exercises = models.JSONField(
        default=list, blank=True,
        help_text=(
            '[{"type":"gap-fill|mc|rewrite|error|cloze",'
            '"prompt":"…","options":["a","b"],"correct":0,"explanation":"…"}]'
        ),
    )

    # ── SRS review config ────────────────────────────────────────────────
    srs_review_count = models.SmallIntegerField(
        default=5,
        help_text="Number of SRS review items to pull from previous chapters.",
    )

    # ── Rewards ──────────────────────────────────────────────────────────
    completion_xp = models.SmallIntegerField(default=10)
    bonus_xp = models.SmallIntegerField(
        default=50,
        help_text="Extra XP if score >= 80%.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "curriculum_lessoncontent"

    def __str__(self):
        return f"Content for: {self.lesson.title}"


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


class SourceFile(models.Model):
    """Files attached to a lesson (audio, PDF, image, video)."""
    FILE_TYPES = [
        ("audio", "Audio"),
        ("pdf", "PDF"),
        ("image", "Image"),
        ("video", "Video"),
        ("other", "Other"),
    ]
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="source_files")
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default="other")
    s3_key = models.CharField(max_length=500, blank=True, default="")
    original_name = models.CharField(max_length=255)
    file_size_bytes = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_source_files",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "curriculum_sourcefile"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.original_name} ({self.lesson_id})"
