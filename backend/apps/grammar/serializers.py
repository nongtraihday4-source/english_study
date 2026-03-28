"""apps/grammar/serializers.py"""
from rest_framework import serializers

from .models import GrammarExample, GrammarQuizResult, GrammarRule, GrammarTopic


class GrammarExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarExample
        fields = ["id", "sentence", "translation", "context", "highlight", "audio_url"]


class GrammarRuleSerializer(serializers.ModelSerializer):
    examples = GrammarExampleSerializer(many=True, read_only=True)

    class Meta:
        model = GrammarRule
        fields = [
            "id", "title", "formula", "explanation",
            "memory_hook", "is_exception", "order", "examples",
        ]


class GrammarTopicListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view (no rules)."""
    rule_count = serializers.SerializerMethodField()

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
    prev_topic = serializers.SerializerMethodField()
    next_topic = serializers.SerializerMethodField()

    class Meta:
        model = GrammarTopic
        fields = [
            "id", "title", "slug", "level", "chapter", "order", "icon",
            "description", "analogy", "real_world_use", "memory_hook",
            "is_published", "lesson", "rules",
            "prev_topic", "next_topic",
            "created_at", "updated_at",
        ]

    def _sibling(self, obj, direction):
        """Return slug+title of the prev/next topic in the same level, ordered by order."""
        filt = {"level": obj.level, "is_published": True}
        if direction == "prev":
            qs = GrammarTopic.objects.filter(**filt, order__lt=obj.order).order_by("-order")
        else:
            qs = GrammarTopic.objects.filter(**filt, order__gt=obj.order).order_by("order")
        sibling = qs.values("slug", "title").first()
        return sibling

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
