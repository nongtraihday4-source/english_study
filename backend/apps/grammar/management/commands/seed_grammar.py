"""
management command: seed_grammar
Loads JSON fixtures produced by scripts/extract_grammar_docx.py into the DB.

Usage:
    python manage.py seed_grammar                 # all levels
    python manage.py seed_grammar --level A1      # single level
    python manage.py seed_grammar --clear         # wipe before load
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.grammar.models import GrammarChapter, GrammarExample, GrammarRule, GrammarTopic

LEVELS = ["A1", "A2", "B1", "B2", "C1"]
FIXTURES_DIR = Path(__file__).resolve().parents[5] / "scripts" / "grammar_fixtures"


class Command(BaseCommand):
    help = "Seed grammar chapters/topics/rules/examples from JSON fixtures"

    def add_arguments(self, parser):
        parser.add_argument(
            "--level",
            choices=LEVELS,
            default=None,
            help="Only seed one CEFR level (default: all)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Delete existing grammar rows before seeding",
        )

    def handle(self, *args, **options):
        levels = [options["level"]] if options["level"] else LEVELS

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing grammar data…"))
            GrammarExample.objects.all().delete()
            GrammarRule.objects.all().delete()
            GrammarTopic.objects.filter(level__in=levels).delete()
            GrammarChapter.objects.filter(level__in=levels).delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        for level in levels:
            fixture_path = FIXTURES_DIR / f"grammar_{level}.json"
            if not fixture_path.exists():
                self.stdout.write(
                    self.style.WARNING(f"  [{level}] Fixture not found: {fixture_path} — skipping")
                )
                continue
            self._seed_level(fixture_path, level)

        self.stdout.write(self.style.SUCCESS("\nDone seeding grammar content."))

    @transaction.atomic
    def _seed_level(self, fixture_path: Path, level: str):
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))

        # Support both legacy list format and new {chapters, topics} dict format
        if isinstance(raw, list):
            chapters_data = []
            topics_data = raw
        else:
            chapters_data = raw.get("chapters", [])
            topics_data = raw.get("topics", [])

        # ── 1. Seed chapters ────────────────────────────────────────────────
        chapter_map: dict[str, GrammarChapter] = {}  # name → GrammarChapter
        chapter_count = 0
        for ch_data in chapters_data:
            name = ch_data["name"]
            slug = ch_data.get("slug") or slugify(name)[:220]
            chapter, _ = GrammarChapter.objects.update_or_create(
                level=level,
                slug=slug,
                defaults={
                    "name":        name,
                    "order":       ch_data.get("order", 0),
                    "icon":        ch_data.get("icon", "📚"),
                    "description": ch_data.get("description", ""),
                },
            )
            chapter_map[name] = chapter
            chapter_count += 1

        # ── 2. Seed topics ──────────────────────────────────────────────────
        topic_count = rule_count = example_count = 0

        for topic_data in topics_data:
            chapter_name = topic_data.get("chapter", "")
            chapter_obj = chapter_map.get(chapter_name)

            topic, _ = GrammarTopic.objects.update_or_create(
                slug=topic_data["slug"],
                defaults={
                    "level":           topic_data.get("level", level),
                    "title":           topic_data["title"],
                    "order":           topic_data.get("order", 0),
                    "chapter":         chapter_obj,
                    "description":     topic_data.get("description", ""),
                    "metaphor_title":  topic_data.get("metaphor_title", ""),
                    "narrative_intro": topic_data.get("narrative_intro", ""),
                    "quick_vibe":      topic_data.get("quick_vibe", ""),
                    "concept_image_url": topic_data.get("concept_image_url", ""),
                    "analogy":         topic_data.get("analogy", ""),
                    "real_world_use":  topic_data.get("real_world_use", ""),
                    "memory_hook":     topic_data.get("memory_hook", ""),
                    "signal_words":    topic_data.get("signal_words", []),
                    "common_mistakes": topic_data.get("common_mistakes", []),
                    "comparison_with": topic_data.get("comparison_with", []),
                    "notes":           topic_data.get("notes", []),
                    "icon":            topic_data.get("icon", "📖"),
                    "is_published":    True,
                },
            )
            topic_count += 1

            for rule_data in topic_data.get("rules", []):
                rule, _ = GrammarRule.objects.update_or_create(
                    topic=topic,
                    order=rule_data.get("order", 0),
                    defaults={
                        "title":         rule_data["title"],
                        "formula":       rule_data.get("formula", ""),
                        "explanation":   rule_data.get("explanation", ""),
                        "memory_hook":   rule_data.get("memory_hook", ""),
                        "is_exception":  rule_data.get("is_exception", False),
                        "grammar_table": rule_data.get("grammar_table", {}),
                    },
                )
                rule_count += 1

                for ex_data in rule_data.get("examples", []):
                    GrammarExample.objects.get_or_create(
                        rule=rule,
                        sentence=ex_data.get("sentence", ""),
                        defaults={
                            "translation": ex_data.get("translation", ""),
                            "context":     ex_data.get("context", ""),
                            "highlight":   ex_data.get("highlight", ""),
                            "audio_url":   ex_data.get("audio_url", ""),
                            "is_correct":  ex_data.get("is_correct", True),
                        },
                    )
                    example_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  [{level}] {chapter_count} chapters, {topic_count} topics, "
                f"{rule_count} rules, {example_count} examples"
            )
        )
