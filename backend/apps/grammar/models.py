"""
App: grammar
Models: GrammarTopic, GrammarRule, GrammarExample
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hierarchy:
  GrammarTopic (e.g. "Present Simple Tense")
    └── GrammarRule  (e.g. "Affirmative Form")
          └── GrammarExample (e.g. "She goes to school every day.")

Design: Ported from grammar-trichxuat-notebooklm.md with
        additional curriculum linking.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
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


class GrammarTopic(models.Model):
    """
    Top-level grammar unit (1 Lesson = 1 Topic).
    Examples: Present Simple, Modal Verbs, Conditionals…
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    title = models.CharField(max_length=200, help_text="Tên chủ đề (VD: Present Simple Tense)")
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    level = models.CharField(max_length=2, choices=CEFR_CHOICES, default="A1", db_index=True)
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

    class Meta:
        db_table = "grammar_example"
        verbose_name = "Ví dụ Ngữ pháp"

    def __str__(self):
        return self.sentence[:80]
