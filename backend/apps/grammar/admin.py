"""apps/grammar/admin.py"""
from django.contrib import admin, messages
from .models import GrammarChapter, GrammarExample, GrammarRule, GrammarTopic,GrammarQuizQuestion 

class GrammarTopicInline(admin.TabularInline):
    model = GrammarTopic
    extra = 0
    fields = ("order", "level", "title", "is_published")
    ordering = ("order",)
    show_change_link = True


@admin.register(GrammarChapter)
class GrammarChapterAdmin(admin.ModelAdmin):
    list_display  = ("level", "order", "name", "icon", "topic_count")
    list_filter   = ("level",)
    search_fields = ("name",)
    ordering      = ("level", "order")
    inlines       = [GrammarTopicInline]

    @admin.display(description="# Topics")
    def topic_count(self, obj):
        return obj.topics.count()


class GrammarRuleInline(admin.TabularInline):
    model = GrammarRule
    extra = 0
    fields = ("order", "title", "formula", "is_exception", "memory_hook")
    ordering = ("order",)


class GrammarExampleInline(admin.TabularInline):
    model = GrammarExample
    extra = 0
    fields = ("sentence", "translation", "context", "highlight")


@admin.register(GrammarTopic)
class GrammarTopicAdmin(admin.ModelAdmin):
    list_display  = ("level", "order", "chapter", "title", "is_published", "rule_count", "updated_at")
    list_filter   = ("level", "is_published", "chapter")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("level", "title")}
    ordering = ("level", "chapter__order", "order")
    inlines = [GrammarRuleInline]

    @admin.display(description="# Rules")
    def rule_count(self, obj):
        return obj.rules.count()


@admin.register(GrammarRule)
class GrammarRuleAdmin(admin.ModelAdmin):
    list_display  = ("topic", "order", "title", "formula", "is_exception")
    list_filter   = ("topic__level", "is_exception")
    search_fields = ("title", "formula", "explanation")
    ordering      = ("topic__level", "topic__order", "order")
    inlines       = [GrammarExampleInline]


@admin.register(GrammarExample)
class GrammarExampleAdmin(admin.ModelAdmin):
    list_display = ("sentence", "translation", "highlight", "difficulty", "rule")
    list_filter = ("difficulty", "rule__topic__level")
    list_editable = ("difficulty",)
    search_fields = ("sentence", "translation")


@admin.action(description="✅ Đánh dấu đã kiểm định (Verify)")
def bulk_verify(modeladmin, request, queryset):
    updated = queryset.update(is_verified=True, needs_review=False)
    modeladmin.message_user(request, f"Đã kiểm định {updated} câu hỏi.", messages.SUCCESS)

@admin.action(description="🔍 Đánh dấu cần xem lại")
def bulk_mark_needs_review(modeladmin, request, queryset):
    updated = queryset.update(is_verified=False, needs_review=True)
    modeladmin.message_user(request, f"Đã đánh dấu {updated} câu hỏi cần xem lại.", messages.WARNING)

@admin.register(GrammarQuizQuestion)
class GrammarQuizQuestionAdmin(admin.ModelAdmin):
    actions = [bulk_verify, bulk_mark_needs_review]
    
    list_display = ("id", "topic", "type", "difficulty", "is_verified", "needs_review", "updated_at")
    list_filter = ("difficulty", "is_verified", "needs_review", "type", "topic__level")
    list_editable = ("difficulty", "is_verified", "needs_review")
    search_fields = ("prompt", "topic__title", "rule__title")
    list_per_page = 50  # Hiển thị nhiều hơn mỗi trang
    ordering = ("-needs_review", "-updated_at")
    readonly_fields = ("is_auto_generated", "created_at", "updated_at")

    fieldsets = (
        ("Thông tin cơ bản", {"fields": ("topic", "rule", "source_example", "type")}),
        ("Nội dung câu hỏi", {"fields": ("prompt", "options", "correct_index", "explanation")}),
        ("Trạng thái", {"fields": ("is_verified", "needs_review", "is_auto_generated")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    @admin.display(description="Options Preview", ordering="options")
    def options_preview(self, obj):
        opts = obj.options if isinstance(obj.options, list) else []
        correct = opts[obj.correct_index] if obj.correct_index < len(opts) else "?"
        return f"<b>✓ {correct}</b><br>" + "<br>".join(f"• {o}" for o in opts if o != correct)
    options_preview.short_description = "Options & Answer"
    options_preview.allow_tags = True  # Django 3.x (Django 4+ dùng @admin.display(boolean=False))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("topic", "rule")