"""apps/grammar/admin.py"""
from django.contrib import admin
from .models import GrammarExample, GrammarRule, GrammarTopic


class GrammarRuleInline(admin.TabularInline):
    model = GrammarRule
    extra = 0
    fields = ("order", "title", "formula", "is_exception", "memory_hook")
    ordering = ("order",)


class GrammarExampleInline(admin.TabularInline):
    model = GrammarExample
    extra = 0
    fields = ("sentence", "translation", "context", "highlight")


@admin.register(GrammarTopic)
class GrammarTopicAdmin(admin.ModelAdmin):
    list_display  = ("level", "order", "title", "is_published", "rule_count", "updated_at")
    list_filter   = ("level", "is_published")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("level", "title")}
    ordering = ("level", "order")
    inlines = [GrammarRuleInline]

    @admin.display(description="# Rules")
    def rule_count(self, obj):
        return obj.rules.count()


@admin.register(GrammarRule)
class GrammarRuleAdmin(admin.ModelAdmin):
    list_display  = ("topic", "order", "title", "formula", "is_exception")
    list_filter   = ("topic__level", "is_exception")
    search_fields = ("title", "formula", "explanation")
    ordering      = ("topic__level", "topic__order", "order")
    inlines       = [GrammarExampleInline]


@admin.register(GrammarExample)
class GrammarExampleAdmin(admin.ModelAdmin):
    list_display  = ("sentence", "translation", "highlight", "rule")
    list_filter   = ("rule__topic__level",)
    search_fields = ("sentence", "translation")
