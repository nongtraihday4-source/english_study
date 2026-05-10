"""apps/grammar/serializers.py"""
from rest_framework import serializers

from .models import GrammarChapter, GrammarExample, GrammarQuizResult, GrammarRule, GrammarTopic


class GrammarChapterSerializer(serializers.ModelSerializer):
    topic_count = serializers.SerializerMethodField()

    class Meta:
        model = GrammarChapter
        fields = ["id", "name", "slug", "level", "order", "description", "icon", "topic_count"]

    def get_topic_count(self, obj) -> int:
        return obj.topics.count()


class _ChapterMiniSerializer(serializers.ModelSerializer):
    """Compact chapter info embedded in topic responses."""
    class Meta:
        model = GrammarChapter
        fields = ["id", "name", "slug", "icon", "order"]


class GrammarExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarExample
        fields = ["id", "sentence", "translation", "context", "highlight", "audio_url", "is_correct"]


class GrammarRuleSerializer(serializers.ModelSerializer):
    examples = GrammarExampleSerializer(many=True, read_only=True)

    class Meta:
        model = GrammarRule
        fields = [
            "id", "title", "formula", "explanation",
            "memory_hook", "is_exception", "order", "grammar_table", "examples",
        ]


class GrammarTopicListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view (no rules)."""
    rule_count = serializers.SerializerMethodField()
    chapter = _ChapterMiniSerializer(read_only=True)

    class Meta:
        model = GrammarTopic
        fields = [
            "id", "title", "slug", "level", "chapter", "order", "icon",
            "description", "analogy", "is_published", "rule_count",
        ]

    def get_rule_count(self, obj) -> int:
        return obj.rules.count()


class GrammarTopicDetailSerializer(serializers.ModelSerializer):
    """Full serializer including rules and examples."""
    rules = GrammarRuleSerializer(many=True, read_only=True)
    chapter = _ChapterMiniSerializer(read_only=True)
    prev_topic = serializers.SerializerMethodField()
    next_topic = serializers.SerializerMethodField()

    class Meta:
        model = GrammarTopic
        fields = [
            "id", "title", "slug", "level", "chapter", "order", "icon",
            "description", "analogy", "real_world_use", "memory_hook",
            "signal_words", "common_mistakes", "notes",
            "is_published", "lesson", "rules",
            "prev_topic", "next_topic",
            "created_at", "updated_at",
        ]

    def _sibling(self, obj, direction):
        filt = {"level": obj.level, "is_published": True}
        if direction == "prev":
            qs = GrammarTopic.objects.filter(**filt, order__lt=obj.order).order_by("-order")
        else:
            qs = GrammarTopic.objects.filter(**filt, order__gt=obj.order).order_by("order")
        return qs.values("slug", "title").first()

    def get_prev_topic(self, obj):
        return self._sibling(obj, "prev")

    def get_next_topic(self, obj):
        return self._sibling(obj, "next")


class GrammarQuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarQuizResult
        fields = ["id", "topic", "score", "total_questions", "correct_answers", "attempted_at"]
        read_only_fields = ["id", "attempted_at"]


class GrammarQuizSubmitSerializer(serializers.Serializer):
    """Input serializer for quiz submission (POST)."""
    score = serializers.FloatField(min_value=0, max_value=100)
    total_questions = serializers.IntegerField(min_value=1)
    correct_answers = serializers.IntegerField(min_value=0)

class GrammarQuizQuestionSerializer(serializers.Serializer):
    """Read-only serializer for pre-generated quiz questions."""
    type = serializers.CharField()
    source_id = serializers.IntegerField()
    rule_id = serializers.IntegerField(allow_null=True)
    prompt = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField())
    correct_index = serializers.IntegerField()
    explanation = serializers.CharField(allow_blank=True)

class GrammarQuizAnswerInputSerializer(serializers.Serializer):
    """Payload cho từng câu trả lời user gửi lên."""
    question_source_id = serializers.IntegerField()
    selected_option = serializers.CharField(max_length=255)

class GrammarQuizSubmitInputSerializer(serializers.Serializer):
    """Payload tổng cho POST /quiz/submit/"""
    answers = GrammarQuizAnswerInputSerializer(many=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)