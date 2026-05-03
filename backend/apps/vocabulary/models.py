"""
App: vocabulary
Models: Word, FlashcardDeck, Flashcard, UserFlashcardProgress
"""
from django.conf import settings
from django.db import models

CEFR_CHOICES = [("A1", "A1"), ("A2", "A2"), ("B1", "B1"), ("B2", "B2"), ("C1", "C1")]


class Word(models.Model):
    POS_CHOICES = [
        ("noun", "Danh từ"), ("verb", "Động từ"),
        ("adjective", "Tính từ"), ("adverb", "Trạng từ"),
        ("phrase", "Cụm từ"), ("other", "Khác"),
    ]
    REGISTER_CHOICES = [
        ("formal", "Trang trọng"), ("informal", "Thân mật"),
        ("slang", "Tiếng lóng"), ("academic", "Học thuật"),
    ]

    word = models.CharField(max_length=100, db_index=True)
    topic = models.CharField(
        max_length=200, null=True, blank=True, db_index=True,
        help_text="Vocabulary topic this word belongs to, e.g. 'Health - Symptoms & Illnesses'",
    )
    part_of_speech = models.CharField(max_length=20, choices=POS_CHOICES, null=True, blank=True)
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, db_index=True)
    domain = models.CharField(
        max_length=30, null=True, blank=True, db_index=True,
        help_text="general|everyday|business|technology|academic|medical|health|travel|food|vegetables|animals|nature|art",
    )
    ipa_uk = models.CharField(max_length=100, null=True, blank=True)
    ipa_us = models.CharField(max_length=100, null=True, blank=True)
    audio_uk_s3_key = models.CharField(max_length=500, null=True, blank=True)
    audio_us_s3_key = models.CharField(max_length=500, null=True, blank=True)
    meaning_vi = models.TextField()
    definition_en = models.TextField(null=True, blank=True)
    example_en = models.TextField(null=True, blank=True)
    example_vi = models.TextField(null=True, blank=True)
    collocations_json = models.JSONField(null=True, blank=True)
    synonyms_json = models.JSONField(null=True, blank=True)
    antonyms_json = models.JSONField(null=True, blank=True)
    mnemonic = models.TextField(null=True, blank=True)
    frequency_rank = models.IntegerField(null=True, blank=True)
    register = models.CharField(max_length=15, choices=REGISTER_CHOICES, null=True, blank=True)
    image_key = models.CharField(max_length=500, null=True, blank=True)
    is_oxford_3000 = models.BooleanField(default=False, db_index=True)
    is_oxford_5000 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vocabulary_word"
        indexes = [
            models.Index(fields=["word"]),
            models.Index(fields=["cefr_level", "domain"]),
        ]

    def __str__(self):
        return f"{self.word} [{self.cefr_level}]"


class FlashcardDeck(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        help_text="null = system deck",
    )
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, null=True, blank=True)
    domain = models.CharField(max_length=30, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vocabulary_flashcarddeck"

    def __str__(self):
        owner = self.owner.email if self.owner else "System"
        return f"Deck({self.id}): {self.name} [{owner}]"


class Flashcard(models.Model):
    TYPE_CHOICES = [
        ("word_to_def", "Từ → Định nghĩa"),
        ("def_to_word", "Định nghĩa → Từ"),
        ("audio_to_word", "Âm thanh → Từ"),
    ]

    deck = models.ForeignKey(FlashcardDeck, on_delete=models.CASCADE, related_name="cards")
    word = models.ForeignKey(Word, on_delete=models.CASCADE, null=True, blank=True)
    front_text = models.CharField(max_length=300)
    back_text = models.TextField()
    card_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="word_to_def")
    order = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "vocabulary_flashcard"
        ordering = ["order"]


class UserFlashcardProgress(models.Model):
    """SM-2 algorithm state per user per flashcard."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    # SM-2 fields
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.SmallIntegerField(default=1)
    repetitions = models.SmallIntegerField(default=0)
    next_review_date = models.DateField(null=True, blank=True)
    last_rating = models.SmallIntegerField(null=True, blank=True)   # 0-5
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    is_mastered = models.BooleanField(default=False)

    class Meta:
        db_table = "vocabulary_userflashcardprogress"
        constraints = [
            models.UniqueConstraint(fields=["user", "flashcard"], name="unique_user_card")
        ]

    def apply_sm2(self, rating: int) -> None:
        """
        Apply the SM-2 algorithm in-place and save.
        rating: 0 = complete blackout, 5 = perfect recall.
        """
        from datetime import date, timedelta
        from django.utils import timezone

        self.last_rating = rating
        self.last_reviewed_at = timezone.now()

        if rating >= 3:
            # Correct response
            if self.repetitions == 0:
                self.interval_days = 1
            elif self.repetitions == 1:
                self.interval_days = 6
            else:
                self.interval_days = round(self.interval_days * self.ease_factor)

            self.repetitions += 1
            # Update ease factor: EF' = EF + (0.1 - (5-q)*(0.08+(5-q)*0.02))
            delta = 0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)
            self.ease_factor = max(1.3, self.ease_factor + delta)
        else:
            # Incorrect — reset
            self.repetitions = 0
            self.interval_days = 1

        self.next_review_date = date.today() + timedelta(days=self.interval_days)
        self.is_mastered = self.interval_days >= 21  # ~3 weeks interval = mastered
        self.save()


class StudySession(models.Model):
    """
    PRD 5.8 Session Tracking — records one deck study session.
    Stores new_cards, review_cards, time, accuracy % per session.
    DeckStudyHistory is derived by aggregating sessions per day.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="study_sessions"
    )
    deck = models.ForeignKey(
        FlashcardDeck, on_delete=models.CASCADE, related_name="study_sessions"
    )
    new_cards = models.SmallIntegerField(default=0)
    review_cards = models.SmallIntegerField(default=0)
    total_reviewed = models.SmallIntegerField(default=0)
    correct_count = models.SmallIntegerField(default=0)   # rated >= 4
    accuracy_pct = models.FloatField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "vocabulary_studysession"
        indexes = [models.Index(fields=["user", "deck", "started_at"])]

    def __str__(self):
        return f"Session({self.id}): {self.user} / {self.deck.name} — {self.accuracy_pct}%"
