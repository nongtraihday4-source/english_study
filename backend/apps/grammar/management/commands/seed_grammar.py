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

from apps.grammar.models import GrammarExample, GrammarRule, GrammarTopic

LEVELS = ["A1", "A2", "B1", "B2", "C1"]
FIXTURES_DIR = Path(__file__).resolve().parents[5] / "scripts" / "grammar_fixtures"


class Command(BaseCommand):
    help = "Seed grammar topics/rules/examples from JSON fixtures"

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
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        topic_count = rule_count = example_count = 0

        for topic_data in data:
            topic, created = GrammarTopic.objects.update_or_create(
                slug=topic_data["slug"],
                defaults={
                    "level":          topic_data.get("level", level),
                    "title":          topic_data["title"],
                    "order":          topic_data.get("order", 0),
                    "description":    topic_data.get("description", ""),
                    "analogy":        topic_data.get("analogy", ""),
                    "real_world_use": topic_data.get("real_world_use", ""),
                    "memory_hook":    topic_data.get("memory_hook", ""),
                    "icon":           topic_data.get("icon", "📖"),
                    "is_published":   True,
                },
            )
            topic_count += 1

            for rule_data in topic_data.get("rules", []):
                rule, _ = GrammarRule.objects.update_or_create(
                    topic=topic,
                    order=rule_data.get("order", 0),
                    defaults={
                        "title":        rule_data["title"],
                        "formula":      rule_data.get("formula", ""),
                        "explanation":  rule_data.get("explanation", ""),
                        "memory_hook":  rule_data.get("memory_hook", ""),
                        "is_exception": rule_data.get("is_exception", False),
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
                        },
                    )
                    example_count += 1

        action = "created/updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"  [{level}] {topic_count} topics, {rule_count} rules, "
                f"{example_count} examples {action}"
            )
        )
