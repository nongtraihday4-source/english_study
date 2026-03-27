"""
apps/vocabulary/serializers.py
"""
from rest_framework import serializers

from .models import Word, FlashcardDeck, Flashcard, UserFlashcardProgress


class WordSerializer(serializers.ModelSerializer):
    audio_uk_url = serializers.SerializerMethodField()
    audio_us_url = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = [
            "id", "word", "part_of_speech", "cefr_level", "domain",
            "ipa_uk", "ipa_us", "audio_uk_url", "audio_us_url",
            "meaning_vi", "definition_en", "example_en", "example_vi",
            "collocations_json", "synonyms_json", "antonyms_json",
            "is_oxford_3000", "is_oxford_5000", "frequency_rank",
        ]

    def _presigned(self, key):
        if not key:
            return None
        from django.conf import settings
        import boto3
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
                ExpiresIn=settings.AWS_PRESIGNED_URL_EXPIRY,
            )
        except Exception:
            return None

    def get_audio_uk_url(self, obj):
        return self._presigned(obj.audio_uk_s3_key)

    def get_audio_us_url(self, obj):
        return self._presigned(obj.audio_us_s3_key)


class FlashcardSerializer(serializers.ModelSerializer):
    word_detail = WordSerializer(source="word", read_only=True)

    class Meta:
        model = Flashcard
        fields = ["id", "front_text", "back_text", "card_type", "word_detail"]


class FlashcardDeckSerializer(serializers.ModelSerializer):
    card_count = serializers.IntegerField(source="cards.count", read_only=True)
    word_count = serializers.SerializerMethodField()
    due_count = serializers.SerializerMethodField()
    mastered_count = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardDeck
        fields = [
            "id", "name", "description", "cefr_level", "domain",
            "is_public", "card_count", "word_count", "due_count", "mastered_count",
        ]

    def _get_user(self):
        request = self.context.get("request")
        return request.user if request and request.user.is_authenticated else None

    def get_word_count(self, obj):
        """Number of distinct words in this deck (word_to_def cards only)."""
        return obj.cards.filter(card_type='word_to_def').values('word_id').distinct().count()

    def get_due_count(self, obj):
        from django.utils import timezone
        user = self._get_user()
        if not user:
            return 0
        today = timezone.localdate()
        # Overdue cards that are NOT mastered
        overdue = UserFlashcardProgress.objects.filter(
            user=user, flashcard__deck=obj, next_review_date__lte=today, is_mastered=False
        ).count()
        # Cards never reviewed (new)
        reviewed_ids = UserFlashcardProgress.objects.filter(
            user=user, flashcard__deck=obj
        ).values_list("flashcard_id", flat=True)
        new_count = obj.cards.exclude(id__in=reviewed_ids).count()
        return overdue + new_count

    def get_mastered_count(self, obj):
        """Number of WORDS (not cards) the user has mastered in this deck."""
        user = self._get_user()
        if not user:
            return 0
        # Count via word_to_def only to avoid triple-counting
        return UserFlashcardProgress.objects.filter(
            user=user, flashcard__deck=obj, flashcard__card_type='word_to_def', is_mastered=True
        ).count()


class FlashcardStudySerializer(serializers.ModelSerializer):
    """Deck header info only — cards returned separately in view."""

    class Meta(FlashcardDeckSerializer.Meta):
        fields = ["id", "name", "cefr_level"]


class SM2UpdateSerializer(serializers.Serializer):
    """POST body for SM-2 rating update after reviewing one flashcard."""
    flashcard_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=0, max_value=5, help_text="0=Again 1=Hard 2=Good 3=Easy 4=VeryEasy 5=Perfect")


class UserFlashcardProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFlashcardProgress
        fields = [
            "flashcard", "ease_factor", "interval_days", "repetitions",
            "next_review_date", "last_rating", "is_mastered",
        ]
