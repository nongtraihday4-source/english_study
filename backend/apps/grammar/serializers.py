"""apps/grammar/serializers.py"""
from rest_framework import serializers

from .models import GrammarExample, GrammarRule, GrammarTopic


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
            "id", "title", "slug", "level", "order", "icon",
            "description", "analogy", "is_published", "rule_count",
        ]

    def get_rule_count(self, obj) -> int:
        return obj.rules.count()


class GrammarTopicDetailSerializer(serializers.ModelSerializer):
    """Full serializer including rules and examples."""
    rules = GrammarRuleSerializer(many=True, read_only=True)

    class Meta:
        model = GrammarTopic
        fields = [
            "id", "title", "slug", "level", "order", "icon",
            "description", "analogy", "real_world_use", "memory_hook",
            "is_published", "lesson", "rules",
            "created_at", "updated_at",
        ]
