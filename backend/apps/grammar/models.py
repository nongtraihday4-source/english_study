"""
App: grammar
Models: GrammarChapter, GrammarTopic, GrammarRule, GrammarExample
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hierarchy:
  GrammarChapter  (e.g. "Present tenses")
    └── GrammarTopic (e.g. "Present Simple Tense")
          └── GrammarRule  (e.g. "Affirmative Form")
                └── GrammarExample (e.g. "She goes to school every day.")

Design: Ported from grammar-trichxuat-notebooklm.md with
        additional curriculum linking.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


CEFR_CHOICES = [
    ("A1", "A1 — Beginner"),
    ("A2", "A2 — Elementary"),
    ("B1", "B1 — Intermediate"),
    ("B2", "B2 — Upper Intermediate"),
    ("C1", "C1 — Advanced"),
    ("C2", "C2 — Proficiency"),
]


class GrammarChapter(models.Model):
    """
    A category grouping for GrammarTopics within a CEFR level.
    Derived from Heading 3 sections of the source DOCX.
    Examples: A1 → "Present tenses", "Past tenses", "Future"
    """
    name  = models.CharField(max_length=200, help_text="Tên chương (VD: Present tenses)")
    slug  = models.SlugField(max_length=220, db_index=True)
    level = models.CharField(max_length=2, choices=CEFR_CHOICES, default="A1", db_index=True)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    icon  = models.CharField(max_length=50, default="📚")

    class Meta:
        db_table = "grammar_chapter"
        unique_together = [("level", "slug")]
        ordering = ["level", "order"]
        indexes = [
            models.Index(fields=["level", "order"]),
        ]
        verbose_name = "Chương Ngữ pháp"
        verbose_name_plural = "Danh sách Chương Ngữ pháp"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:220]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.level}] {self.name}"


class GrammarTopic(models.Model):
    """
    Top-level grammar unit (1 Lesson = 1 Topic).
    Examples: Present Simple, Modal Verbs, Conditionals…
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    title = models.CharField(max_length=200, help_text="Tên chủ đề (VD: Present Simple Tense)")
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    level = models.CharField(max_length=2, choices=CEFR_CHOICES, default="A1", db_index=True)
    chapter = models.ForeignKey(
        "GrammarChapter",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="topics",
        help_text="Chương phân loại chủ đề (VD: Present tenses).",
    )
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)

    # ── Curriculum link (optional) ────────────────────────────────────────────
    lesson = models.OneToOneField(
        "curriculum.Lesson",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="grammar_topic",
        help_text="Bài học trong curriculum tương ứng với chủ đề này",
    )

    # ── Presentation ──────────────────────────────────────────────────────────
    icon = models.CharField(
        max_length=50, default="📚",
        help_text="Emoji hoặc mã class FontAwesome đại diện cho chủ đề",
    )
    description = models.TextField(
        blank=True,
        help_text="Mô tả ngắn gọn chủ đề (dùng làm meta description)",
    )

    # ── Pedagogical enrichment ────────────────────────────────────────────────
    metaphor_title = models.CharField(
        max_length=200, blank=True,
        verbose_name="Tiêu đề ẩn dụ",
        help_text="VD: Chiếc cầu nối giữa Quá khứ và Hiện tại",
    )
    narrative_intro = models.TextField(
        blank=True,
        verbose_name="Lời dẫn dắt",
        help_text="Lời mở đầu dẫn dắt, giải thích 'Tại sao' thì này tồn tại.",
    )
    quick_vibe = models.CharField(
        max_length=255, blank=True,
        verbose_name="Thần chú",
        help_text="Câu chốt 'thần chú' để nhớ thì (VD: Không cần biết khi nào, chỉ cần biết đã xong).",
    )
    concept_image_url = models.URLField(
        blank=True, null=True,
        verbose_name="Ảnh minh họa khái niệm",
        help_text="Link ảnh minh họa cho khái niệm ẩn dụ (Concept Art).",
    )
    analogy = models.TextField(
        blank=True,
        verbose_name="Phép ẩn dụ (Analogy)",
        help_text=(
            "So sánh cấu trúc ngữ pháp với khái niệm đời thường dễ hiểu. "
            "VD: 'Động từ to be giống như dấu bằng (=) trong toán học.'"
        ),
    )
    real_world_use = models.TextField(
        blank=True,
        verbose_name="Ứng dụng thực tế",
        help_text="Giải thích tại sao học viên cần học chủ đề này trong thực tế.",
    )
    memory_hook = models.TextField(
        blank=True,
        verbose_name="Mẹo nhớ tổng quát",
        help_text="Câu thần chú ngắn để nhớ toàn bộ chủ đề.",
    )

    # ── Extended pedagogical fields ───────────────────────────────────────────
    signal_words = models.JSONField(
        default=list, blank=True,
        verbose_name="Dấu hiệu nhận biết",
        help_text="Danh sách từ/cụm từ dấu hiệu nhận biết (VD: ['now', 'at the moment', 'these days']).",
    )
    common_mistakes = models.JSONField(
        default=list, blank=True,
        verbose_name="Lỗi thường gặp",
        help_text="Danh sách lỗi thường gặp. Mỗi item: {wrong, correct, explanation}.",
    )
    comparison_with = models.JSONField(
        default=list, blank=True,
        verbose_name="Phân biệt",
        help_text="So sánh với thì/cấu trúc dễ nhầm lẫn: {title, difference, examples}.",
    )
    notes = models.JSONField(
        default=list, blank=True,
        verbose_name="Ghi chú bổ sung",
        help_text="Danh sách ghi chú/tips bổ sung cho chủ đề. Mỗi item: {text, type} với type: 'tip'|'warning'|'info'.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grammar_topic"
        ordering = ["level", "order"]
        indexes = [
            models.Index(fields=["level", "order"]),
            models.Index(fields=["level", "is_published"]),
        ]
        verbose_name = "Chủ đề Ngữ pháp"
        verbose_name_plural = "Danh sách Chủ đề Ngữ pháp"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = f"{self.level.lower()}-{slugify(self.title)}"
            self.slug = base_slug[:220]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.level}] {self.title}"


class GrammarRule(models.Model):
    """
    A specific rule within a GrammarTopic.
    Examples: Affirmative, Negative, Question forms; spelling rules; exceptions.
    """
    topic = models.ForeignKey(
        GrammarTopic, on_delete=models.CASCADE, related_name="rules"
    )
    title = models.CharField(max_length=255, help_text="Tên quy tắc (VD: Câu khẳng định)")
    formula = models.CharField(
        max_length=500, blank=True,
        help_text="Công thức ngắn gọn. VD: S + V(s/es) + Object",
    )
    explanation = models.TextField(
        blank=True,
        help_text="Giải thích chi tiết cách dùng (hỗ trợ Markdown/HTML)."
    )
    memory_hook = models.TextField(
        blank=True,
        verbose_name="Mẹo nhớ quy tắc",
        help_text="Câu ngắn gọn/hài hước giúp học viên nhớ quy tắc này ngay lập tức.",
    )
    is_exception = models.BooleanField(
        default=False,
        help_text="Đánh dấu nếu đây là ngoại lệ (hiển thị cảnh báo đỏ trên UI).",
    )
    order = models.PositiveIntegerField(default=0)
    grammar_table = models.JSONField(
        default=dict, blank=True,
        verbose_name="Bảng ngữ pháp",
        help_text="Bảng chia động từ/so sánh dạng responsive. {headers: [...], rows: [[...]]}",
    )

    class Meta:
        db_table = "grammar_rule"
        ordering = ["order"]
        verbose_name = "Quy tắc Ngữ pháp"

    def __str__(self):
        return f"{self.topic.title} › {self.title}"


class GrammarExample(models.Model):
    """
    An example sentence illustrating a GrammarRule.
    Includes emotional context and highlighted keywords for interactive UI.
    """
    rule = models.ForeignKey(
        GrammarRule, on_delete=models.CASCADE, related_name="examples"
    )
    sentence = models.TextField(help_text="Câu ví dụ tiếng Anh")
    translation = models.TextField(blank=True, help_text="Dịch nghĩa tiếng Việt")
    context = models.CharField(
        max_length=255, blank=True,
        verbose_name="Ngữ cảnh cảm xúc",
        help_text=(
            "Tình huống cụ thể giúp học viên cảm nhận câu. "
            "VD: 'Khi đang ngạc nhiên', 'Nói khẽ để không đánh thức em bé'"
        ),
    )
    highlight = models.CharField(
        max_length=150, blank=True,
        help_text="Từ/cụm từ cần tô màu trong câu (VD: 'is sleeping', 'goes').",
    )
    audio_url = models.URLField(
        blank=True, null=True,
        help_text="Link file âm thanh (S3 key hoặc URL CDN).",
    )
    is_correct = models.BooleanField(
        default=True,
        help_text="True = câu đúng (✓), False = câu sai (✗) dùng để minh họa lỗi.",
    )
    DIFFICULTY_CHOICES = [(1, "Easy"), (2, "Medium"), (3, "Hard")]
    difficulty = models.PositiveIntegerField(
        default=2, choices=DIFFICULTY_CHOICES, db_index=True,
        help_text="Độ khó câu ví dụ (1=Dễ, 2=Trung bình, 3=Khó). Auto-generate heuristic, admin override được."
    )
    class Meta:
        db_table = "grammar_example"
        verbose_name = "Ví dụ Ngữ pháp"

    def __str__(self):
        return self.sentence[:80]


class GrammarQuizResult(models.Model):
    """
    Persists a learner's quiz score for a GrammarTopic.
    Upserted on each attempt (keeps latest score).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="grammar_quiz_results",
    )
    topic = models.ForeignKey(
        GrammarTopic, on_delete=models.CASCADE,
        related_name="quiz_results",
    )
    score = models.FloatField(help_text="Điểm phần trăm (0-100)")
    total_questions = models.PositiveIntegerField(default=5)
    correct_answers = models.PositiveIntegerField(default=0)
    attempted_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grammar_quiz_result"
        unique_together = ("user", "topic")
        verbose_name = "Kết quả Quiz Ngữ pháp"

    def __str__(self):
        return f"{self.user} — {self.topic.title}: {self.score}%"

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 1.1: Granular Quiz Tracking, SRS & Error Patterns
# ──────────────────────────────────────────────────────────────────────────────

class GrammarQuizAttempt(models.Model):
    """Mỗi lần làm quiz tạo 1 attempt. Không ghi đè lịch sử cũ."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grammar_quiz_attempts")
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name="quiz_attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0, help_text="Điểm % (0-100)")

    class Meta:
        db_table = "grammar_quiz_attempt"
        indexes = [models.Index(fields=["user", "topic", "-started_at"])]
        verbose_name = "Lần làm Quiz Ngữ pháp"

    def __str__(self):
        return f"{self.user} | {self.topic.slug} | {self.score}% | {self.started_at:%Y-%m-%d %H:%M}"


class GrammarQuizAnswer(models.Model):
    """Lưu đáp án từng câu, gắn với Rule để SRS & Error Tracking chính xác."""
    attempt = models.ForeignKey(GrammarQuizAttempt, on_delete=models.CASCADE, related_name="answers")
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE, null=True, blank=True, related_name="quiz_answers")
    question_source_id = models.PositiveIntegerField(help_text="ID của GrammarExample hoặc Question")
    selected_option = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    class Meta:
        db_table = "grammar_quiz_answer"
        indexes = [models.Index(fields=["attempt", "rule", "is_correct"])]
        verbose_name = "Đáp án Quiz Ngữ pháp"

    def __str__(self):
        return f"Q{self.question_source_id} | {'✓' if self.is_correct else '✗'}"


class GrammarReviewSchedule(models.Model):
    """SRS theo cấp độ Rule (không phải Topic). Áp dụng SM-2 biến thể."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grammar_reviews")
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE, related_name="review_schedules")
    next_review = models.DateField(db_index=True, help_text="Ngày cần ôn tiếp theo")
    interval_days = models.PositiveIntegerField(default=1)
    ease_factor = models.FloatField(default=2.5, help_text="Hệ số dễ (SM-2)")

    class Meta:
        db_table = "grammar_review_schedule"
        unique_together = ("user", "rule")
        verbose_name = "Lịch ôn Ngữ pháp (SRS)"

    def __str__(self):
        return f"{self.user} | {self.rule.title} | Next: {self.next_review}"


class ErrorPattern(models.Model):
    """Track lỗi sai lặp lại theo Rule để trigger Remedial Path."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grammar_errors")
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE, related_name="error_patterns")
    error_type = models.CharField(max_length=50, default="general", help_text="VD: chia_động_từ, sai_giới_từ, nhầm_thì")
    count = models.PositiveIntegerField(default=1)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grammar_error_pattern"
        unique_together = ("user", "rule", "error_type")
        verbose_name = "Mẫu lỗi Ngữ pháp"

    def __str__(self):
        return f"{self.user} | {self.rule.title} | {self.error_type} (x{self.count})"

class GrammarQuizQuestion(models.Model):
    """Lưu câu hỏi quiz để admin duyệt/chỉnh sửa. Ưu tiên is_verified=True."""
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name="quiz_questions")
    rule = models.ForeignKey(GrammarRule, on_delete=models.SET_NULL, null=True, blank=True)
    source_example = models.ForeignKey(GrammarExample, on_delete=models.SET_NULL, null=True, blank=True)
    
    type = models.CharField(max_length=20, choices=[("gap-fill", "Gap Fill"), ("mc", "Multiple Choice"), ("error", "Error Correction")])
    prompt = models.TextField()
    options = models.JSONField(help_text="Danh sách đáp án (list of strings)")
    correct_index = models.PositiveIntegerField()
    explanation = models.TextField(blank=True)
    
    is_auto_generated = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, db_index=True, help_text="Đã được admin kiểm định chất lượng")
    needs_review = models.BooleanField(default=True, db_index=True, help_text="Cần admin duyệt lại (nhiễu vô nghĩa, sai ngữ cảnh)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    DIFFICULTY_CHOICES = [(1, "Easy"), (2, "Medium"), (3, "Hard")]
    difficulty = models.PositiveIntegerField(
        default=2, choices=DIFFICULTY_CHOICES, db_index=True,
        help_text="Độ khó câu hỏi. Kế thừa từ source_example hoặc admin chỉnh."
    )
    class Meta:
        db_table = "grammar_quiz_question"
        unique_together = ("topic", "source_example", "type")
        indexes = [
            models.Index(fields=["topic", "is_verified", "needs_review"]),
        ]
        verbose_name = "Câu hỏi Quiz Ngữ pháp"
        verbose_name_plural = "Quản lý Câu hỏi Quiz"

    def __str__(self):
        return f"[{self.type}] {self.prompt[:50]}... ({'✓' if self.is_verified else '⏳'})"