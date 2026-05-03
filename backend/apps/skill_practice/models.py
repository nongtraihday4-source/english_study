"""
App: skill_practice
Models: PracticePassage, UserPassageProgress, DictationAttempt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hierarchy:
  PracticePassage  (a passage classified by CEFR level + topic)
    └── sentences_json  [{index, text, translation_vi, audio_url}]
  UserPassageProgress  (per user/passage/mode: dictation | shadowing)
  DictationAttempt     (per sentence attempt log)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from django.conf import settings
from django.db import models

CEFR_CHOICES = [
    ("A1", "A1"), ("A2", "A2"), ("B1", "B1"), ("B2", "B2"), ("C1", "C1"), ("C2", "C2"),
]

DIFFICULTY_CHOICES = [
    ("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard"),
]

MODE_CHOICES = [
    ("dictation", "Chính tả"), ("shadowing", "Shadowing"),
]

PROGRESS_STATUS = [
    ("not_started", "Chưa bắt đầu"),
    ("in_progress", "Đang học"),
    ("completed", "Hoàn thành"),
]


class PracticePassage(models.Model):
    """
    Core content entity shared by Dictation and Shadowing practice.
    sentences_json stores pre-split sentences with per-sentence audio URLs.
    """
    title = models.CharField(max_length=200)
    full_text = models.TextField(help_text="Full passage content in English")
    translation_vi = models.TextField(
        null=True, blank=True,
        help_text="Vietnamese translation of the full passage",
    )
    # Pre-split: [{index, text, translation_vi, audio_url}]
    sentences_json = models.JSONField(
        default=list,
        help_text="List of sentences with individual TTS audio URLs",
    )
    full_audio_url = models.CharField(
        max_length=500, null=True, blank=True,
        help_text="TTS audio for the complete passage",
    )
    # Classification — uses same string format as vocabulary Word.topic
    topic = models.CharField(
        max_length=200, db_index=True,
        help_text="e.g. 'Health - Symptoms & Illnesses'",
    )
    topic_slug = models.SlugField(
        max_length=220, db_index=True,
        help_text="URL-safe slug derived from topic",
    )
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, db_index=True)
    difficulty_tag = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default="medium",
    )
    word_count = models.SmallIntegerField(default=0)
    # Optional enrichment
    vocab_highlights_json = models.JSONField(
        null=True, blank=True,
        help_text="[{word, ipa, meaning_vi, part_of_speech}]",
    )
    grammar_notes = models.TextField(
        null=True, blank=True,
        help_text="Key grammar patterns used in this passage",
    )
    # TTS voice used when generating audio
    tts_voice = models.CharField(
        max_length=50, default="en-US-AriaNeural",
        help_text="Edge-TTS voice name for generating audio",
    )
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "skill_practice_passage"
        ordering = ["cefr_level", "topic", "difficulty_tag"]
        indexes = [
            models.Index(fields=["cefr_level", "topic"]),
            models.Index(fields=["cefr_level", "is_published"]),
            models.Index(fields=["topic_slug"]),
        ]
        verbose_name = "Practice Passage"
        verbose_name_plural = "Practice Passages"

    def __str__(self):
        return f"[{self.cefr_level}] {self.title}"

    def save(self, *args, **kwargs):
        if self.full_text:
            self.word_count = len(self.full_text.split())
        if not self.topic_slug and self.topic:
            from django.utils.text import slugify
            self.topic_slug = slugify(self.topic)
        super().save(*args, **kwargs)


class UserPassageProgress(models.Model):
    """
    Per-user, per-passage, per-mode progress tracking.
    sentences_completed_json: {"0": true, "1": false, "2": true, ...}
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="passage_progresses",
    )
    passage = models.ForeignKey(
        PracticePassage,
        on_delete=models.CASCADE,
        related_name="user_progresses",
    )
    mode = models.CharField(max_length=15, choices=MODE_CHOICES)
    status = models.CharField(
        max_length=15, choices=PROGRESS_STATUS, default="not_started",
    )
    best_score = models.SmallIntegerField(
        default=0,
        help_text="Dictation: word accuracy %. Shadowing: avg self-assessment (1-5 scaled to 0-100)",
    )
    attempts = models.SmallIntegerField(default=0)
    sentences_completed_json = models.JSONField(
        default=dict,
        help_text='{"0": true, "1": false} — per-sentence completion',
    )
    last_practiced_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.IntegerField(default=0)

    class Meta:
        db_table = "skill_practice_user_progress"
        unique_together = [("user", "passage", "mode")]
        indexes = [
            models.Index(fields=["user", "mode"]),
            models.Index(fields=["user", "passage"]),
        ]
        verbose_name = "User Passage Progress"
        verbose_name_plural = "User Passage Progresses"

    def __str__(self):
        return f"{self.user} — {self.passage} [{self.mode}]"

    def completed_sentence_count(self):
        return sum(1 for v in self.sentences_completed_json.values() if v)


class DictationAttempt(models.Model):
    """Detailed log of each dictation attempt (sentence or full passage)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dictation_attempts",
    )
    passage = models.ForeignKey(
        PracticePassage,
        on_delete=models.CASCADE,
        related_name="dictation_attempts",
    )
    # null = full-passage attempt
    sentence_index = models.SmallIntegerField(
        null=True, blank=True,
        help_text="null means full-passage mode",
    )
    user_input = models.TextField()
    accuracy_percent = models.SmallIntegerField(default=0)
    diff_json = models.JSONField(
        default=list,
        help_text="[{word, match, correct_word}] word-level diff",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "skill_practice_dictation_attempt"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "passage"]),
        ]
        verbose_name = "Dictation Attempt"
        verbose_name_plural = "Dictation Attempts"

    def __str__(self):
        idx = self.sentence_index if self.sentence_index is not None else "full"
        return f"{self.user} — passage {self.passage_id} s{idx} ({self.accuracy_percent}%)"
