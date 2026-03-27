"""
App: progress
Models: UserEnrollment, LessonProgress, ExerciseResult,
        SpeakingSubmission, WritingSubmission, AIGradingJob,
        DailyStreak, CumulativeScore
"""
from django.conf import settings
from django.db import models


class UserEnrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Đang học"),
        ("paused", "Tạm dừng"),
        ("completed", "Hoàn thành"),
        ("dropped", "Bỏ dở"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey("curriculum.Course", on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="active", db_index=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    current_lesson = models.ForeignKey(
        "curriculum.Lesson", on_delete=models.SET_NULL, null=True, blank=True
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "progress_userenrollment"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["course", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                condition=models.Q(is_deleted=False),
                name="unique_active_enrollment",
            )
        ]

    def __str__(self):
        return f"Enrollment({self.user_id} → {self.course_id} [{self.status}])"


class LessonProgress(models.Model):
    STATUS_CHOICES = [
        ("locked", "Khoá"),
        ("available", "Sẵn sàng"),
        ("in_progress", "Đang học"),
        ("completed", "Hoàn thành"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey("curriculum.Lesson", on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="locked", db_index=True)
    best_score = models.SmallIntegerField(null=True, blank=True)
    attempts_count = models.SmallIntegerField(default=0)
    time_spent_seconds = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "progress_lessonprogress"
        constraints = [
            models.UniqueConstraint(fields=["user", "lesson"], name="unique_lesson_progress")
        ]
        indexes = [models.Index(fields=["user", "status"])]


class ExerciseResult(models.Model):
    """Stores every graded exercise attempt."""
    EXERCISE_TYPES = [
        ("listening", "Listening"),
        ("speaking", "Speaking"),
        ("reading", "Reading"),
        ("writing", "Writing"),
        ("grammar", "Grammar"),
        ("exam", "Exam"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        "curriculum.Lesson", on_delete=models.SET_NULL, null=True, blank=True
    )
    exercise_type = models.CharField(max_length=15, choices=EXERCISE_TYPES, db_index=True)
    exercise_id = models.BigIntegerField(db_index=True)
    score = models.SmallIntegerField()           # 0–100
    passed = models.BooleanField()               # score >= passing_score
    time_spent_seconds = models.IntegerField(default=0)
    # Per-question detail: [{q_id, user_ans, correct, points}]
    detail_json = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "progress_exerciseresult"
        indexes = [
            models.Index(fields=["user", "exercise_type", "exercise_id"]),
            models.Index(fields=["user", "created_at"]),
        ]


class SpeakingSubmission(models.Model):
    """Audio submission from a student for a Speaking exercise."""
    STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),
        ("processing", "Đang chấm"),
        ("completed", "Hoàn thành"),
        ("failed", "Thất bại"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise_id = models.BigIntegerField(db_index=True)
    lesson = models.ForeignKey(
        "curriculum.Lesson", on_delete=models.SET_NULL, null=True, blank=True
    )
    audio_s3_key = models.CharField(max_length=500)
    audio_duration_seconds = models.FloatField(null=True, blank=True)
    audio_size_bytes = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending", db_index=True)

    # Whisper output
    transcript = models.TextField(null=True, blank=True)

    target_sentence = models.CharField(max_length=500, null=True, blank=True)
    # GPT-4o rubric scores (35/25/20/20)
    ai_score = models.SmallIntegerField(null=True, blank=True)                # 0–100 final
    score_pronunciation = models.SmallIntegerField(null=True, blank=True)     # 35%
    score_fluency = models.SmallIntegerField(null=True, blank=True)           # 25%
    score_intonation = models.SmallIntegerField(null=True, blank=True)        # 20%
    score_vocabulary = models.SmallIntegerField(null=True, blank=True)        # 20%
    feedback_vi = models.TextField(null=True, blank=True)
    # [{type, word, suggestion}]
    error_list_json = models.JSONField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "progress_speakingsubmission"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "exercise_id"]),
        ]

    def __str__(self):
        return f"Speaking({self.id}) user={self.user_id} status={self.status}"


class WritingSubmission(models.Model):
    STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),
        ("processing", "Đang chấm"),
        ("completed", "Hoàn thành"),
        ("failed", "Thất bại"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise_id = models.BigIntegerField(db_index=True)
    lesson = models.ForeignKey(
        "curriculum.Lesson", on_delete=models.SET_NULL, null=True, blank=True
    )
    content_text = models.TextField()
    word_count = models.SmallIntegerField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending", db_index=True)

    # GPT-4o rubric scores (25/25/25/25)
    ai_score = models.SmallIntegerField(null=True, blank=True)
    score_task_achievement = models.SmallIntegerField(null=True, blank=True)  # 25%
    score_grammar = models.SmallIntegerField(null=True, blank=True)           # 25%
    score_vocabulary = models.SmallIntegerField(null=True, blank=True)        # 25%
    score_coherence = models.SmallIntegerField(null=True, blank=True)         # 25%

    feedback_text = models.TextField(null=True, blank=True)
    # [{type, original, suggestion, explanation}]
    error_list_json = models.JSONField(null=True, blank=True)
    # [{word, cefr_level}]
    vocab_cefr_json = models.JSONField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    teacher_comment = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "progress_writingsubmission"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "exercise_id"]),
        ]

    def __str__(self):
        return f"Writing({self.id}) user={self.user_id} words={self.word_count} status={self.status}"


class AIGradingJob(models.Model):
    """Celery job tracker for Speaking and Writing AI grading."""
    JOB_TYPES = [("speaking", "Speaking"), ("writing", "Writing")]
    STATUS_CHOICES = [
        ("queued", "Xếp hàng"),
        ("processing", "Đang xử lý"),
        ("completed", "Hoàn thành"),
        ("failed", "Thất bại"),
        ("retrying", "Thử lại"),
    ]

    job_type = models.CharField(max_length=15, choices=JOB_TYPES, db_index=True)
    submission_id = models.BigIntegerField(db_index=True)
    celery_task_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="queued", db_index=True)
    retry_count = models.SmallIntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    ai_model_used = models.CharField(max_length=50, null=True, blank=True)
    tokens_used = models.IntegerField(null=True, blank=True)
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "progress_aigradingjob"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["job_type", "status"]),
        ]

    def __str__(self):
        return f"AIJob({self.id}) {self.job_type} sub={self.submission_id} [{self.status}]"


class DailyStreak(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streak"
    )
    current_streak = models.SmallIntegerField(default=0)
    longest_streak = models.SmallIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    streak_protected_until = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "progress_dailystreak"


class CumulativeScore(models.Model):
    """Running average scores per user per CEFR level — updated after each graded exercise."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    level = models.ForeignKey("curriculum.CEFRLevel", on_delete=models.CASCADE)
    listening_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    speaking_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reading_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    writing_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_exercises_done = models.IntegerField(default=0)
    cefr_equivalent = models.CharField(max_length=3, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "progress_cumulativescore"
        constraints = [
            models.UniqueConstraint(fields=["user", "level"], name="unique_user_level_score")
        ]
