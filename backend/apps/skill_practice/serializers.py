"""
Serializers for skill_practice app.
"""
from rest_framework import serializers

from .models import DictationAttempt, PracticePassage, UserPassageProgress


class PracticePassageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for passage lists (no full text)."""
    dictation_progress = serializers.SerializerMethodField()
    shadowing_progress = serializers.SerializerMethodField()

    class Meta:
        model = PracticePassage
        fields = [
            "id", "title", "topic", "topic_slug", "cefr_level",
            "difficulty_tag", "word_count", "is_published",
            "dictation_progress", "shadowing_progress",
        ]

    def _progress_for_mode(self, obj, mode):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        progress = getattr(obj, "_user_progresses", None)
        if progress is None:
            return None
        for p in progress:
            if p.mode == mode:
                return {
                    "status": p.status,
                    "best_score": p.best_score,
                    "attempts": p.attempts,
                    "sentences_completed": p.completed_sentence_count(),
                }
        return {"status": "not_started", "best_score": 0, "attempts": 0, "sentences_completed": 0}

    def get_dictation_progress(self, obj):
        return self._progress_for_mode(obj, "dictation")

    def get_shadowing_progress(self, obj):
        return self._progress_for_mode(obj, "shadowing")


class PracticePassageDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer including sentences and vocab highlights."""
    dictation_progress = serializers.SerializerMethodField()
    shadowing_progress = serializers.SerializerMethodField()

    class Meta:
        model = PracticePassage
        fields = [
            "id", "title", "full_text", "translation_vi", "sentences_json",
            "full_audio_url", "topic", "topic_slug", "cefr_level",
            "difficulty_tag", "word_count", "vocab_highlights_json",
            "grammar_notes", "tts_voice",
            "dictation_progress", "shadowing_progress",
        ]

    def _progress_for_mode(self, obj, mode):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        try:
            p = obj.user_progresses.get(user=request.user, mode=mode)
            return {
                "status": p.status,
                "best_score": p.best_score,
                "attempts": p.attempts,
                "sentences_completed_json": p.sentences_completed_json,
                "time_spent_seconds": p.time_spent_seconds,
                "last_practiced_at": p.last_practiced_at,
            }
        except UserPassageProgress.DoesNotExist:
            return {
                "status": "not_started",
                "best_score": 0,
                "attempts": 0,
                "sentences_completed_json": {},
                "time_spent_seconds": 0,
                "last_practiced_at": None,
            }

    def get_dictation_progress(self, obj):
        return self._progress_for_mode(obj, "dictation")

    def get_shadowing_progress(self, obj):
        return self._progress_for_mode(obj, "shadowing")


class TopicSummarySerializer(serializers.Serializer):
    """Summary of a topic for the topic browser."""
    topic = serializers.CharField()
    topic_slug = serializers.CharField()
    cefr_level = serializers.CharField()
    passage_count = serializers.IntegerField()
    easy_count = serializers.IntegerField()
    medium_count = serializers.IntegerField()
    hard_count = serializers.IntegerField()
    # User progress: how many passages in this topic have been completed
    dictation_completed = serializers.IntegerField()
    shadowing_completed = serializers.IntegerField()


class DictationCheckSerializer(serializers.Serializer):
    """Input for POST /passages/{id}/dictation/check/"""
    sentence_index = serializers.IntegerField(
        required=False, allow_null=True,
        help_text="null for full-passage mode",
    )
    user_input = serializers.CharField(allow_blank=False, max_length=2000)
    time_spent_seconds = serializers.IntegerField(required=False, default=0)


class DictationCheckResultSerializer(serializers.Serializer):
    """Output of dictation check."""
    accuracy_percent = serializers.IntegerField()
    diff = serializers.ListField(child=serializers.DictField())
    correct_text = serializers.CharField()
    is_correct = serializers.BooleanField()
    hint = serializers.CharField(allow_null=True)
    progress_status = serializers.CharField()


class ShadowingCompleteSerializer(serializers.Serializer):
    """Input for POST /passages/{id}/shadowing/complete/"""
    sentence_index = serializers.IntegerField(
        required=False, allow_null=True,
    )
    self_rating = serializers.IntegerField(
        min_value=1, max_value=5,
        help_text="1=Cần cải thiện, 2=Tạm được, 3=Khá tốt, 4=Tốt, 5=Xuất sắc",
    )
    time_spent_seconds = serializers.IntegerField(required=False, default=0)


class ProgressSummarySerializer(serializers.Serializer):
    """Output for GET /progress/summary/"""
    total_passages_started = serializers.IntegerField()
    dictation_completed = serializers.IntegerField()
    shadowing_completed = serializers.IntegerField()
    total_time_seconds = serializers.IntegerField()
    recent_passages = PracticePassageListSerializer(many=True)
