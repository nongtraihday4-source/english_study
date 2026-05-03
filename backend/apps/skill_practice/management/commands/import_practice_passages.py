"""
Management command: import_practice_passages
Bulk import practice passages from a JSON file.

JSON format:
[
  {
    "title": "A Morning Routine",
    "full_text": "Sarah wakes up at 6 AM every day...",
    "translation_vi": "Sarah thức dậy lúc 6 giờ sáng mỗi ngày...",
    "topic": "Daily Life - Daily Routines & Habits",
    "cefr_level": "A2",
    "difficulty_tag": "easy",
    "vocab_highlights": [
      {"word": "routine", "ipa": "/ruːˈtiːn/", "meaning_vi": "thói quen"}
    ],
    "grammar_notes": "Uses Present Simple for habitual actions.",
    "tts_voice": "en-US-AriaNeural",
    "is_published": true
  }
]

Usage:
  python manage.py import_practice_passages --file passages.json
  python manage.py import_practice_passages --file passages.json --dry-run
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from apps.skill_practice.models import PracticePassage
from utils.sentence_splitter import split_to_sentence_dicts


class Command(BaseCommand):
    help = "Import practice passages from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to JSON file")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Validate and preview without saving",
        )
        parser.add_argument(
            "--split-sentences", action="store_true", default=True,
            help="Auto-split full_text into sentences_json (default: True)",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise CommandError("JSON must be a list of passage objects.")

        self.stdout.write(f"Found {len(data)} passage(s) to import.")

        created = 0
        skipped = 0

        for i, item in enumerate(data, start=1):
            title = item.get("title", "").strip()
            full_text = item.get("full_text", "").strip()
            cefr_level = item.get("cefr_level", "").upper()
            topic = item.get("topic", "").strip()

            if not title or not full_text or not cefr_level or not topic:
                self.stderr.write(
                    f"  [{i}] SKIP — missing required fields (title/full_text/cefr_level/topic)"
                )
                skipped += 1
                continue

            if cefr_level not in ("A1", "A2", "B1", "B2", "C1", "C2"):
                self.stderr.write(f"  [{i}] SKIP — invalid cefr_level: {cefr_level}")
                skipped += 1
                continue

            topic_slug = slugify(topic)
            difficulty_tag = item.get("difficulty_tag", "medium")
            if difficulty_tag not in ("easy", "medium", "hard"):
                difficulty_tag = "medium"

            sentences = split_to_sentence_dicts(full_text) if options["split_sentences"] else []

            self.stdout.write(
                f"  [{i}] {cefr_level} | {difficulty_tag} | {topic} | '{title}'"
                f" ({len(sentences)} sentences)"
            )

            if not options["dry_run"]:
                passage = PracticePassage(
                    title=title,
                    full_text=full_text,
                    translation_vi=item.get("translation_vi") or "",
                    sentences_json=sentences,
                    topic=topic,
                    topic_slug=topic_slug,
                    cefr_level=cefr_level,
                    difficulty_tag=difficulty_tag,
                    vocab_highlights_json=item.get("vocab_highlights") or None,
                    grammar_notes=item.get("grammar_notes") or "",
                    tts_voice=item.get("tts_voice") or "en-US-AriaNeural",
                    is_published=item.get("is_published", False),
                )
                # word_count is set in save()
                passage.save()
                created += 1

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN — {len(data)} parsed, {skipped} would be skipped"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\nImported {created} passage(s), skipped {skipped}.")
            )
