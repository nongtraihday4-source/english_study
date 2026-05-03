from django.contrib import admin
from django.utils.html import format_html

from .models import DictationAttempt, PracticePassage, UserPassageProgress


def _generate_audio_action(modeladmin, request, queryset):
    """Admin action: generate TTS audio for selected passages."""
    from utils.tts import TTSService, TTSVoice
    from utils.sentence_splitter import split_to_sentence_dicts

    tts = TTSService()
    updated = 0
    for passage in queryset:
        # Re-split sentences if sentences_json is empty
        if not passage.sentences_json and passage.full_text:
            passage.sentences_json = split_to_sentence_dicts(passage.full_text)

        # Generate audio for each sentence
        sentences = passage.sentences_json or []
        changed = False
        for s in sentences:
            if not s.get("audio_url"):
                url = tts.speak(s["text"], voice=passage.tts_voice or TTSVoice.US_FEMALE)
                if url:
                    s["audio_url"] = url
                    changed = True

        # Generate full-passage audio
        if not passage.full_audio_url and passage.full_text:
            url = tts.speak(passage.full_text, voice=passage.tts_voice or TTSVoice.US_FEMALE)
            if url:
                passage.full_audio_url = url
                changed = True

        if changed:
            passage.save(update_fields=["sentences_json", "full_audio_url"])
            updated += 1

    modeladmin.message_user(request, f"Generated audio for {updated} passage(s).")


_generate_audio_action.short_description = "Generate TTS audio"


def _split_sentences_action(modeladmin, request, queryset):
    """Admin action: (re)split sentences from full_text."""
    from utils.sentence_splitter import split_to_sentence_dicts

    updated = 0
    for passage in queryset:
        if passage.full_text:
            passage.sentences_json = split_to_sentence_dicts(passage.full_text)
            passage.save(update_fields=["sentences_json"])
            updated += 1
    modeladmin.message_user(request, f"Split sentences for {updated} passage(s).")


_split_sentences_action.short_description = "Split sentences from full_text"


def _publish_action(modeladmin, request, queryset):
    queryset.update(is_published=True)
    modeladmin.message_user(request, f"Published {queryset.count()} passage(s).")


_publish_action.short_description = "Publish selected passages"


def _unpublish_action(modeladmin, request, queryset):
    queryset.update(is_published=False)
    modeladmin.message_user(request, f"Unpublished {queryset.count()} passage(s).")


_unpublish_action.short_description = "Unpublish selected passages"


@admin.register(PracticePassage)
class PracticePassageAdmin(admin.ModelAdmin):
    list_display = [
        "id", "title", "cefr_level", "topic", "difficulty_tag",
        "word_count", "sentence_count", "has_audio", "is_published", "created_at",
    ]
    list_filter = ["cefr_level", "difficulty_tag", "is_published"]
    search_fields = ["title", "full_text", "topic"]
    list_editable = ["is_published"]
    readonly_fields = ["word_count", "topic_slug", "created_at", "updated_at", "sentence_preview"]
    actions = [_generate_audio_action, _split_sentences_action, _publish_action, _unpublish_action]

    fieldsets = (
        ("Content", {
            "fields": ("title", "full_text", "translation_vi", "grammar_notes"),
        }),
        ("Classification", {
            "fields": ("topic", "topic_slug", "cefr_level", "difficulty_tag"),
        }),
        ("Audio", {
            "fields": ("tts_voice", "full_audio_url"),
        }),
        ("Vocabulary", {
            "fields": ("vocab_highlights_json",),
            "classes": ("collapse",),
        }),
        ("Computed", {
            "fields": ("word_count", "sentence_preview"),
            "classes": ("collapse",),
        }),
        ("Status", {
            "fields": ("is_published", "created_at", "updated_at"),
        }),
    )

    def sentence_count(self, obj):
        return len(obj.sentences_json or [])
    sentence_count.short_description = "Sentences"

    def has_audio(self, obj):
        sentences = obj.sentences_json or []
        total = len(sentences)
        if total == 0:
            return format_html('<span style="color:gray">—</span>')
        with_audio = sum(1 for s in sentences if s.get("audio_url"))
        color = "green" if with_audio == total else "orange" if with_audio > 0 else "red"
        return format_html(
            '<span style="color:{}">{}/{}</span>', color, with_audio, total
        )
    has_audio.short_description = "Audio"

    def sentence_preview(self, obj):
        sentences = obj.sentences_json or []
        if not sentences:
            return "No sentences split yet."
        lines = [f"{s['index']+1}. {s['text']}" for s in sentences[:5]]
        if len(sentences) > 5:
            lines.append(f"... and {len(sentences) - 5} more")
        return format_html("<br>".join(lines))
    sentence_preview.short_description = "Sentence preview"


@admin.register(UserPassageProgress)
class UserPassageProgressAdmin(admin.ModelAdmin):
    list_display = [
        "user", "passage", "mode", "status", "best_score", "attempts",
        "time_spent_seconds", "last_practiced_at",
    ]
    list_filter = ["mode", "status"]
    search_fields = ["user__email", "passage__title"]
    readonly_fields = ["last_practiced_at"]


@admin.register(DictationAttempt)
class DictationAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "user", "passage", "sentence_index", "accuracy_percent", "created_at",
    ]
    list_filter = ["accuracy_percent"]
    search_fields = ["user__email", "passage__title"]
    readonly_fields = ["created_at"]
