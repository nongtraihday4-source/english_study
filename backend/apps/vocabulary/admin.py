from django.contrib import admin

from .models import Flashcard, FlashcardDeck, Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ["word", "part_of_speech", "cefr_level", "domain", "is_oxford_3000", "is_oxford_5000", "frequency_rank"]
    list_filter = ["cefr_level", "domain", "part_of_speech", "is_oxford_3000", "is_oxford_5000"]
    search_fields = ["word", "meaning_vi", "domain"]
    ordering = ["word"]


class FlashcardInline(admin.TabularInline):
    model = Flashcard
    extra = 0


@admin.register(FlashcardDeck)
class FlashcardDeckAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "cefr_level", "is_public"]
    list_filter = ["cefr_level", "is_public"]
    search_fields = ["name"]
    inlines = [FlashcardInline]
