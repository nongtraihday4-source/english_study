from django.contrib import admin

from .models import ListeningExercise, Question, QuestionOption, ReadingExercise, SpeakingExercise, WritingExercise


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "exercise_type", "exercise_id", "question_type", "points"]
    list_filter = ["exercise_type", "question_type"]
    search_fields = ["question_text"]
    inlines = [QuestionOptionInline]


@admin.register(ListeningExercise)
class ListeningAdmin(admin.ModelAdmin):
    list_display = ["title", "cefr_level", "audio_duration_seconds"]
    list_filter = ["cefr_level"]
    search_fields = ["title"]


@admin.register(ReadingExercise)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ["title", "cefr_level"]
    list_filter = ["cefr_level"]
    search_fields = ["title"]


@admin.register(SpeakingExercise)
class SpeakingAdmin(admin.ModelAdmin):
    list_display = ["title", "cefr_level"]
    search_fields = ["title"]


@admin.register(WritingExercise)
class WritingAdmin(admin.ModelAdmin):
    list_display = ["title", "cefr_level", "min_words", "max_words", "time_limit_minutes"]
    list_filter = ["cefr_level"]
