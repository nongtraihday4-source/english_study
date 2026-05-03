from django.contrib import admin

from .models import CEFRLevel, Chapter, Course, Lesson, LessonContent, LessonExercise, UnlockRule


@admin.register(CEFRLevel)
class CEFRLevelAdmin(admin.ModelAdmin):
    list_display = ["code", "name_vi", "order", "is_active"]
    ordering = ["order"]


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "level", "is_premium"]
    list_filter = ["level", "is_premium"]
    search_fields = ["title", "slug"]
    inlines = [ChapterInline]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ["title", "lesson_type", "order", "is_free_preview"]
    show_change_link = True


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order", "passing_score"]
    list_filter = ["course__level"]
    search_fields = ["title", "course__title"]
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "chapter", "lesson_type", "order", "estimated_minutes"]
    list_filter = ["lesson_type"]
    search_fields = ["title"]


@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ["lesson", "lesson_type_display", "has_reading", "vocab_count", "exercise_count", "completion_xp"]
    search_fields = ["lesson__title", "grammar_title"]
    list_filter = ["lesson__lesson_type", "lesson__chapter__course"]
    readonly_fields = ["created_at", "updated_at"]

    def lesson_type_display(self, obj):
        return obj.lesson.lesson_type
    lesson_type_display.short_description = "Type"

    def has_reading(self, obj):
        return bool(obj.reading_passage)
    has_reading.boolean = True
    has_reading.short_description = "Reading"

    def vocab_count(self, obj):
        return len(obj.vocab_items or [])
    vocab_count.short_description = "Vocab"

    def exercise_count(self, obj):
        return len(obj.exercises or [])
    exercise_count.short_description = "Exercises"
