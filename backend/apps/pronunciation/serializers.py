from rest_framework import serializers

from .models import (
    LessonSection,
    MinimalPair,
    MinimalPairSet,
    Phoneme,
    PhonemeLesson,
    PronunciationStage,
    UserPhonemeProgress,
)


class LessonSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonSection
        fields = ["id", "section_type", "title", "body", "items", "order"]


class PhonemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phoneme
        fields = [
            "id", "symbol", "phoneme_type", "description",
            "audio_url", "mouth_diagram_url", "example_words", "order",
        ]


class PhonemeLessonSerializer(serializers.ModelSerializer):
    phonemes = PhonemeSerializer(many=True, read_only=True)
    sections = LessonSectionSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()
    progress_score = serializers.SerializerMethodField()

    class Meta:
        model = PhonemeLesson
        fields = [
            "id", "title", "slug", "description", "order",
            "cefr_level", "is_published", "phonemes", "sections",
            "is_completed", "progress_score",
        ]

    def _get_user_progress(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        return UserPhonemeProgress.objects.filter(user=request.user, lesson=obj).first()

    def get_is_completed(self, obj):
        prog = self._get_user_progress(obj)
        return prog.is_completed if prog else False

    def get_progress_score(self, obj):
        prog = self._get_user_progress(obj)
        return prog.score if prog else 0.0


class PhonemeLessonListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for stage lesson lists (no phoneme details)."""

    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = PhonemeLesson
        fields = ["id", "title", "slug", "description", "order", "cefr_level", "is_completed"]

    def get_is_completed(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return UserPhonemeProgress.objects.filter(
            user=request.user, lesson=obj, is_completed=True
        ).exists()


class PronunciationStageSerializer(serializers.ModelSerializer):
    lessons = PhonemeLessonListSerializer(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = PronunciationStage
        fields = [
            "id", "stage_type", "title", "description", "order", "icon",
            "total_lessons", "completed_lessons", "progress_percent", "lessons",
        ]

    def get_total_lessons(self, obj):
        return obj.lessons.filter(is_published=True).count()

    def get_completed_lessons(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        return UserPhonemeProgress.objects.filter(
            user=request.user,
            lesson__stage=obj,
            lesson__is_published=True,
            is_completed=True,
        ).count()

    def get_progress_percent(self, obj):
        total = self.get_total_lessons(obj)
        if not total:
            return 0
        completed = self.get_completed_lessons(obj)
        return round(completed / total * 100)


class MinimalPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinimalPair
        fields = ["id", "word", "ipa", "audio_url", "meaning", "order"]


class MinimalPairSetSerializer(serializers.ModelSerializer):
    pairs = MinimalPairSerializer(many=True, read_only=True)

    class Meta:
        model = MinimalPairSet
        fields = [
            "id", "title", "focus_phoneme_1", "focus_phoneme_2",
            "description", "cefr_level", "pairs",
        ]


class PhonemeChartSerializer(serializers.ModelSerializer):
    """Full IPA chart data by type."""

    class Meta:
        model = Phoneme
        fields = [
            "id", "symbol", "phoneme_type", "description",
            "audio_url", "mouth_diagram_url", "example_words",
        ]
