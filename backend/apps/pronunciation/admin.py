from django.contrib import admin

from .models import (
    MinimalPair,
    MinimalPairSet,
    Phoneme,
    PhonemeLesson,
    PronunciationStage,
    UserPhonemeProgress,
)


@admin.register(PronunciationStage)
class PronunciationStageAdmin(admin.ModelAdmin):
    list_display = ["title", "stage_type", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(PhonemeLesson)
class PhonemeLessonAdmin(admin.ModelAdmin):
    list_display = ["title", "stage", "cefr_level", "order", "is_published"]
    list_filter = ["stage", "cefr_level"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["title"]}


@admin.register(Phoneme)
class PhonemeAdmin(admin.ModelAdmin):
    list_display = ["symbol", "phoneme_type", "description", "lesson", "order"]
    list_filter = ["phoneme_type"]


@admin.register(MinimalPairSet)
class MinimalPairSetAdmin(admin.ModelAdmin):
    list_display = ["title", "focus_phoneme_1", "focus_phoneme_2", "cefr_level", "is_published"]
    list_filter = ["cefr_level"]


admin.site.register(MinimalPair)
admin.site.register(UserPhonemeProgress)

