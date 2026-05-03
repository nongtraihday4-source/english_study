"""
Management command: load_oxford_dict

Loads the curated Oxford 3000/5000 dictionary fixtures from:
    tu_vung/dictionary-3000-5000(A1-C1)/*.json

Each file uses the Django fixture format:
    [{"model": "vocabulary.word", "pk": <old_pk>, "fields": {...}}, ...]

PK renumbering: new_pk = old_pk - 100
    i.e. old_pk 101 → new_pk 1, old_pk 5417 → new_pk 5317

Usage:
    python manage.py load_oxford_dict
    python manage.py load_oxford_dict --dry-run
    python manage.py load_oxford_dict --clear     # delete all Oxford words first
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.vocabulary.models import Word

PROJECT_ROOT = Path(__file__).resolve().parents[5]
DICT_DIR = PROJECT_ROOT / "tu_vung" / "dictionary-3000-5000(A1-C1)"

PK_OFFSET = 100  # new_pk = old_pk - PK_OFFSET

# All writable fields on the Word model (exclude auto fields)
WORD_FIELDS = frozenset({
    "word", "topic", "part_of_speech", "cefr_level", "domain",
    "ipa_uk", "ipa_us", "audio_uk_s3_key", "audio_us_s3_key",
    "meaning_vi", "definition_en", "example_en", "example_vi",
    "collocations_json", "synonyms_json", "antonyms_json",
    "mnemonic", "frequency_rank", "register", "image_key",
    "is_oxford_3000", "is_oxford_5000",
    # NB: created_at is auto_now_add — intentionally excluded
})


def _first_pk(fpath: Path) -> int:
    """Return the first pk value found in a JSON file, for sorting."""
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
        if isinstance(data, list) and data:
            return data[0].get("pk", 0)
    except Exception:
        pass
    return 0


class Command(BaseCommand):
    help = "Load Oxford 3000/5000 dictionary fixtures from tu_vung/dictionary-3000-5000(A1-C1)/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Delete all existing Oxford words (is_oxford_3000 OR is_oxford_5000) before loading",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Parse and count without writing to the database",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        do_clear = options["clear"]

        if not DICT_DIR.exists():
            self.stdout.write(self.style.ERROR(f"Directory not found: {DICT_DIR}"))
            return

        json_files = sorted(DICT_DIR.glob("*.json"), key=_first_pk)
        if not json_files:
            self.stdout.write(self.style.WARNING("No *.json files found in directory"))
            return

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"\nload_oxford_dict — {len(json_files)} files from {DICT_DIR.name}"
            )
        )

        if do_clear and not dry:
            from django.db.models import Q
            deleted, _ = Word.objects.filter(
                Q(is_oxford_3000=True) | Q(is_oxford_5000=True)
            ).delete()
            self.stdout.write(f"  Cleared {deleted} existing Oxford words")

        total_created = total_updated = total_skipped = 0

        for fpath in json_files:
            c, u, s = self._load_file(fpath, dry)
            total_created += c
            total_updated += u
            total_skipped += s

        prefix = "[DRY RUN] " if dry else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{prefix}Done — created: {total_created}, "
                f"updated: {total_updated}, skipped: {total_skipped}"
            )
        )

    @transaction.atomic
    def _load_file(self, fpath: Path, dry: bool) -> tuple[int, int, int]:
        try:
            raw = json.loads(fpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            self.stdout.write(self.style.ERROR(f"  ERROR reading {fpath.name}: {exc}"))
            return 0, 0, 0

        if not isinstance(raw, list):
            self.stdout.write(self.style.WARNING(f"  {fpath.name}: unexpected format, skipping"))
            return 0, 0, 0

        records = [r for r in raw if isinstance(r, dict) and r.get("model") == "vocabulary.word"]
        if not records:
            self.stdout.write(f"  {fpath.name}: 0 word records — skipped")
            return 0, 0, 0

        created = updated = skipped = 0

        if dry:
            # Count valid records without writing
            for rec in records:
                old_pk = rec.get("pk")
                if old_pk is None:
                    skipped += 1
                else:
                    created += 1
            self.stdout.write(f"  {fpath.name}: {created} words (dry)")
            return created, 0, skipped

        for rec in records:
            old_pk = rec.get("pk")
            if old_pk is None:
                skipped += 1
                continue

            new_pk = old_pk - PK_OFFSET
            if new_pk < 1:
                self.stdout.write(
                    self.style.WARNING(f"  {fpath.name}: pk {old_pk} → {new_pk} (< 1) — skipped")
                )
                skipped += 1
                continue

            fields = rec.get("fields", {})
            cleaned = {k: v for k, v in fields.items() if k in WORD_FIELDS}

            obj, is_new = Word.objects.update_or_create(
                pk=new_pk,
                defaults=cleaned,
            )
            if is_new:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            f"  {fpath.name}: +{created} new, ~{updated} updated, -{skipped} skipped"
        )
        return created, updated, skipped
