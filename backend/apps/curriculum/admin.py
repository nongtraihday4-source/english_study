from django.contrib import admin

from .models import CEFRLevel, Chapter, Course, Lesson, LessonExercise, UnlockRule


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
