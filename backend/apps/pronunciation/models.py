"""
App: pronunciation
Models: PronunciationStage, PhonemeLesson, Phoneme, MinimalPairSet, MinimalPair
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hierarchy:
  PronunciationStage (4 stages: Monophthongs, Consonants, Diphthongs, Advanced)
    └── PhonemeLesson  (individual phoneme or topic lesson)
          └── Phoneme  (individual IPA symbol with audio + examples)
  MinimalPairSet (e.g. ship/sheep)
    └── MinimalPair  (word + audio + IPA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from django.conf import settings
from django.db import models


CEFR_CHOICES = [
    ("A1", "A1"), ("A2", "A2"), ("B1", "B1"), ("B2", "B2"), ("C1", "C1"),
]

STAGE_TYPES = [
    ("monophthongs", "Stage 1: Monophthongs"),
    ("consonants", "Stage 2: Consonants"),
    ("diphthongs", "Stage 3: Diphthongs"),
    ("advanced", "Stage 4: Advanced (Connected Speech)"),
]

PHONEME_TYPES = [
    ("vowel", "Vowel"),
    ("consonant", "Consonant"),
    ("diphthong", "Diphthong"),
]


class PronunciationStage(models.Model):
    stage_type = models.CharField(max_length=30, choices=STAGE_TYPES, unique=True, db_index=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    icon = models.CharField(max_length=10, default="🔤")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Pronunciation Stage"
        verbose_name_plural = "Pronunciation Stages"

    def __str__(self):
        return self.title


class PhonemeLesson(models.Model):
    stage = models.ForeignKey(
        PronunciationStage, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, db_index=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    cefr_level = models.CharField(max_length=2, choices=CEFR_CHOICES, default="A1", db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["stage", "order"]
        verbose_name = "Phoneme Lesson"

    def __str__(self):
        return f"{self.stage} — {self.title}"


class Phoneme(models.Model):
    lesson = models.ForeignKey(
        PhonemeLesson, on_delete=models.CASCADE, related_name="phonemes", null=True, blank=True
    )
    symbol = models.CharField(max_length=10, unique=True, db_index=True, help_text="IPA symbol e.g. /æ/")
    phoneme_type = models.CharField(max_length=15, choices=PHONEME_TYPES, default="vowel")
    description = models.CharField(max_length=200, blank=True)
    audio_url = models.URLField(max_length=500, blank=True)
    audio_s3_key = models.CharField(max_length=500, blank=True)
    mouth_diagram_url = models.URLField(max_length=500, blank=True)
    example_words = models.JSONField(
        default=list,
        help_text='[{"word": "cat", "ipa": "/kæt/", "meaning": "con mèo"}]',
    )
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["phoneme_type", "order"]
        verbose_name = "Phoneme"

    def __str__(self):
        return self.symbol


class LessonSection(models.Model):
    SECTION_TYPES = [
        ("explanation", "Giải thích"),
        ("tip", "Mẹo phát âm"),
        ("examples", "Ví dụ"),
        ("common_mistakes", "Lỗi thường gặp"),
        ("practice", "Luyện tập"),
        ("quiz", "Kiểm tra"),
    ]

    lesson = models.ForeignKey(
        PhonemeLesson, on_delete=models.CASCADE, related_name="sections"
    )
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default="explanation")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, help_text="Main text content for this section")
    items = models.JSONField(
        default=list,
        help_text='Structured items: examples, quiz questions, practice phrases, etc.',
    )
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["lesson", "order"]
        verbose_name = "Lesson Section"

    def __str__(self):
        return f"{self.lesson.slug} — {self.section_type} #{self.order}"


class UserPhonemeProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="phoneme_progress"
    )
    lesson = models.ForeignKey(PhonemeLesson, on_delete=models.CASCADE, related_name="user_progress")
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)
    attempts = models.PositiveIntegerField(default=0)
    last_practiced_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("user", "lesson")]
        verbose_name = "User Phoneme Progress"

    def __str__(self):
        return f"{self.user} — {self.lesson}"


class MinimalPairSet(models.Model):
    title = models.CharField(max_length=120)
    focus_phoneme_1 = models.CharField(max_length=10)
    focus_phoneme_2 = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    cefr_level = models.CharField(max_length=2, choices=CEFR_CHOICES, default="A1", db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Minimal Pair Set"

    def __str__(self):
        return self.title


class MinimalPair(models.Model):
    pair_set = models.ForeignKey(MinimalPairSet, on_delete=models.CASCADE, related_name="pairs")
    word = models.CharField(max_length=60)
    ipa = models.CharField(max_length=30)
    audio_url = models.URLField(max_length=500, blank=True)
    audio_s3_key = models.CharField(max_length=500, blank=True)
    meaning = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["pair_set", "order"]
        verbose_name = "Minimal Pair"

    def __str__(self):
        return f"{self.pair_set} — {self.word} {self.ipa}"
