"""
Management command: load_topic_vocab
Loads vocabulary JSON fixtures from tu_vung/ directories into the DB.

Usage:
    python manage.py load_topic_vocab                          # all sets
    python manage.py load_topic_vocab --set a2_b1             # one set
    python manage.py load_topic_vocab --set b1_b2 --set c1_c2
    python manage.py load_topic_vocab --clear                  # wipe set(s) first

Fixture paths (relative to project root):
    tu_vung/topics_a2_b1/*_result.json
    tu_vung/topics_b1_b2/*_result.json
    tu_vung/topics_c1_c2/*_result.json
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.vocabulary.models import Word

PROJECT_ROOT = Path(__file__).resolve().parents[5]

VOCAB_SETS = {
    "a2_b1":  PROJECT_ROOT / "tu_vung" / "topics_a2_b1",
    "b1_b2":  PROJECT_ROOT / "tu_vung" / "topics_b1_b2",
    "c1_c2":  PROJECT_ROOT / "tu_vung" / "topics_c1-c2",
}

WORD_FIELDS = {
    "topic", "word", "part_of_speech", "cefr_level", "domain",
    "ipa_uk", "ipa_us", "meaning_vi", "definition_en",
    "example_en", "example_vi", "collocations_json", "synonyms_json",
    "antonyms_json", "mnemonic", "frequency_rank",
}


class Command(BaseCommand):
    help = "Load vocabulary topic fixtures from tu_vung/ into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--set",
            dest="sets",
            choices=list(VOCAB_SETS.keys()),
            action="append",
            default=None,
            help="Which vocabulary set to load (default: all)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Delete existing words whose topic matches files in the set before loading",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Parse and count without writing to DB",
        )

    def handle(self, *args, **options):
        sets = options["sets"] or list(VOCAB_SETS.keys())
        dry = options["dry_run"]

        total_created = 0
        total_updated = 0
        total_skipped = 0

        for set_name in sets:
            base_dir = VOCAB_SETS[set_name]
            if not base_dir.exists():
                self.stdout.write(self.style.WARNING(f"  [{set_name}] Directory not found: {base_dir} — skipping"))
                continue

            json_files = sorted(base_dir.glob("*_result.json"))
            if not json_files:
                self.stdout.write(self.style.WARNING(f"  [{set_name}] No *_result.json files found"))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"\n[{set_name}] {len(json_files)} files"))

            for fpath in json_files:
                c, u, s = self._load_file(fpath, dry, options["clear"])
                total_created += c
                total_updated += u
                total_skipped += s

        prefix = "[DRY RUN] " if dry else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{prefix}Done — created: {total_created}, updated: {total_updated}, skipped: {total_skipped}"
            )
        )

    @transaction.atomic
    def _load_file(self, fpath: Path, dry: bool, do_clear: bool) -> tuple[int, int, int]:
        try:
            raw = json.loads(fpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            self.stdout.write(self.style.ERROR(f"  ERROR reading {fpath.name}: {e}"))
            return 0, 0, 0

        # Fixtures may be {"topic": "...", "data": [...]} or a plain list
        if isinstance(raw, dict):
            records = raw.get("data", [])
        else:
            records = raw

        # Only handle vocabulary.word records
        word_records = [r for r in records if isinstance(r, dict) and r.get("model") == "vocabulary.word"]
        if not word_records:
            self.stdout.write(f"  {fpath.name}: 0 word records — skipped")
            return 0, 0, 0

        # Collect topic name from first record for reporting / clearing
        topic_name = word_records[0]["fields"].get("topic", "")

        if do_clear and not dry and topic_name:
            deleted, _ = Word.objects.filter(topic=topic_name).delete()
            if deleted:
                self.stdout.write(f"  Cleared {deleted} existing words for topic '{topic_name}'")

        created = updated = skipped = 0

        VALID_CEFR = {"A1", "A2", "B1", "B2", "C1", "C2"}

        if not dry:
            for rec in word_records:
                fields = rec["fields"]
                # Keep only known model fields to avoid crashes on schema drift
                cleaned = {k: v for k, v in fields.items() if k in WORD_FIELDS}
                word_text = cleaned.get("word", "").strip()
                topic = cleaned.get("topic", "")
                if not word_text:
                    skipped += 1
                    continue

                # Sanitise cefr_level — default to A2 if value is invalid/too long
                cefr = cleaned.get("cefr_level", "")
                if cefr not in VALID_CEFR:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    Bad cefr_level {cefr!r} for '{word_text}' — defaulting to A2"
                        )
                    )
                    cleaned["cefr_level"] = "A2"

                obj, is_new = Word.objects.update_or_create(
                    word=word_text,
                    topic=topic,
                    defaults=cleaned,
                )
                if is_new:
                    created += 1
                else:
                    updated += 1
        else:
            created = len(word_records)

        self.stdout.write(
            f"  {fpath.name}: +{created} new, ~{updated} updated, -{skipped} skipped"
        )
        return created, updated, skipped
