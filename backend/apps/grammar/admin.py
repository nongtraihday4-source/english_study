"""apps/grammar/admin.py"""
from django.contrib import admin
from .models import GrammarChapter, GrammarExample, GrammarRule, GrammarTopic


class GrammarTopicInline(admin.TabularInline):
    model = GrammarTopic
    extra = 0
    fields = ("order", "level", "title", "is_published")
    ordering = ("order",)
    show_change_link = True


@admin.register(GrammarChapter)
class GrammarChapterAdmin(admin.ModelAdmin):
    list_display  = ("level", "order", "name", "icon", "topic_count")
    list_filter   = ("level",)
    search_fields = ("name",)
    ordering      = ("level", "order")
    inlines       = [GrammarTopicInline]

    @admin.display(description="# Topics")
    def topic_count(self, obj):
        return obj.topics.count()


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
    list_display  = ("level", "order", "chapter", "title", "is_published", "rule_count", "updated_at")
    list_filter   = ("level", "is_published", "chapter")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("level", "title")}
    ordering = ("level", "chapter__order", "order")
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
