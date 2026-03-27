"""
App: exercises
Models: ListeningExercise, SpeakingExercise, ReadingExercise, WritingExercise,
        Question, QuestionOption, ExamSet
"""
from django.db import models

CEFR_CHOICES = [("A1", "A1"), ("A2", "A2"), ("B1", "B1"), ("B2", "B2"), ("C1", "C1")]


class ListeningExercise(models.Model):
    title = models.CharField(max_length=200)
    audio_file = models.CharField(max_length=500, help_text="S3 key của file MP3")
    audio_duration_seconds = models.IntegerField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    context_hint = models.TextField(null=True, blank=True)
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, db_index=True)
    max_plays = models.SmallIntegerField(default=0, help_text="0 = unlimited")
    time_limit_seconds = models.SmallIntegerField(default=0, help_text="0 = no limit")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises_listeningexercise"

    def __str__(self):
        return f"Listening({self.id}): {self.title} [{self.cefr_level}]"


class SpeakingExercise(models.Model):
    title = models.CharField(max_length=200)
    scenario = models.TextField(help_text="Mô tả tình huống nhập vai")
    dialogue_json = models.JSONField(
        default=list, help_text='[{"role": "AI", "text": "...", "audio_key": "..."}]'
    )
    target_sentence = models.TextField(help_text="Câu học viên cần nói")
    target_audio_key = models.CharField(max_length=500, help_text="S3 key audio mẫu")
    karaoke_words_json = models.JSONField(
        default=list, help_text='[{"word": "hello", "start_ms": 0, "end_ms": 400}]'
    )
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, db_index=True)
    time_limit_seconds = models.SmallIntegerField(default=60, help_text="Max recording seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises_speakingexercise"

    def __str__(self):
        return f"Speaking({self.id}): {self.title} [{self.cefr_level}]"


class ReadingExercise(models.Model):
    title = models.CharField(max_length=200)
    article_text = models.TextField(help_text="Nội dung bài đọc (HTML/Markdown)")
    vocab_tooltip_json = models.JSONField(
        default=list, help_text='[{"word": "...", "ipa": "...", "meaning_vi": "..."}]'
    )
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, db_index=True)
    time_limit_seconds = models.SmallIntegerField(default=0, help_text="0 = no limit")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises_readingexercise"

    def __str__(self):
        return f"Reading({self.id}): {self.title} [{self.cefr_level}]"


class WritingExercise(models.Model):
    title = models.CharField(max_length=200)
    prompt_text = models.TextField(help_text="Đề bài")
    prompt_description = models.TextField(help_text="Hướng dẫn chi tiết")
    min_words = models.SmallIntegerField(default=150)
    max_words = models.SmallIntegerField(default=300)
    time_limit_minutes = models.SmallIntegerField(default=30)
    structure_tips_json = models.JSONField(
        default=list, help_text='["Paragraph 1: Introduction...", "Paragraph 2: ..."]'
    )
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises_writingexercise"

    def __str__(self):
        return f"Writing({self.id}): {self.title} [{self.cefr_level}]"


class Question(models.Model):
    """Questions for Listening and Reading exercises."""
    EXERCISE_TYPES = [("listening", "Listening"), ("reading", "Reading"), ("grammar", "Grammar"), ("exam", "Exam")]
    QUESTION_TYPES = [
        ("mc", "Multiple Choice"),
        ("gap_fill", "Gap Fill"),
        ("drag_drop", "Drag & Drop"),
    ]

    exercise_type = models.CharField(max_length=15, choices=EXERCISE_TYPES, db_index=True)
    exercise_id = models.BigIntegerField(db_index=True)
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES)
    question_text = models.TextField()
    order = models.SmallIntegerField(default=1)
    correct_answers_json = models.JSONField(help_text='["A", "B"] — supports multiple correct answers')
    explanation = models.TextField(null=True, blank=True)
    points = models.SmallIntegerField(default=1)
    is_locked_initially = models.BooleanField(default=False)
    passage_ref_start = models.IntegerField(null=True, blank=True, help_text="Char offset start in passage")
    passage_ref_end = models.IntegerField(null=True, blank=True, help_text="Char offset end in passage")

    class Meta:
        db_table = "exercises_question"
        ordering = ["order"]
        indexes = [
            models.Index(fields=["exercise_type", "exercise_id"]),
        ]

    def __str__(self):
        return f"Q({self.id}) [{self.exercise_type}:{self.exercise_id}] {self.question_text[:50]}"


class QuestionOption(models.Model):
    """Multiple-choice options for a Question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=500)
    order = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "exercises_questionoption"
        ordering = ["order"]


class ExamSet(models.Model):
    """A timed exam combining multiple exercise types."""
    SKILL_CHOICES = [
        ("listening", "Listening"),
        ("reading", "Reading"),
        ("mixed", "Mixed"),
    ]
    EXAM_TYPE_CHOICES = [
        ("progress_check", "Progress Check"),
        ("mock_test", "Mock Test"),
        ("placement", "Placement Test"),
    ]
    title = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default="mock_test", db_index=True)
    skill = models.CharField(max_length=10, choices=SKILL_CHOICES)
    cefr_level = models.CharField(max_length=3, choices=CEFR_CHOICES, db_index=True)
    time_limit_minutes = models.SmallIntegerField()
    passing_score = models.SmallIntegerField(default=60)
    total_questions = models.SmallIntegerField()
    structure_json = models.JSONField(
        default=dict, help_text='{"mc": 10, "gap_fill": 5, "drag_drop": 5}'
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises_examset"
