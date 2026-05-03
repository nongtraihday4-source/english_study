"""
Management command: seed_card_types

Creates def_to_word and audio_to_word flashcard variants for every
existing word_to_def card in all user/system decks.

Run once after upgrading the add-word flow to 3-card system, or any
time new cards are imported without the extra variants.

Usage:
  python manage.py seed_card_types
  python manage.py seed_card_types --deck-id 5    # only one deck
  python manage.py seed_card_types --dry-run       # preview only
"""
from django.core.management.base import BaseCommand

from apps.vocabulary.models import Flashcard


class Command(BaseCommand):
    help = "Seed def_to_word and audio_to_word variants for existing word_to_def cards"

    def add_arguments(self, parser):
        parser.add_argument(
            "--deck-id", type=int, default=None,
            help="Only process a specific deck by PK. Omit to process all decks.",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would be created without actually writing to the DB.",
        )

    def handle(self, *args, **options):
        deck_id = options["deck_id"]
        dry_run = options["dry_run"]

        base_qs = (
            Flashcard.objects
            .filter(card_type="word_to_def", word__isnull=False)
            .select_related("word", "deck")
        )
        if deck_id:
            base_qs = base_qs.filter(deck_id=deck_id)

        created_def = 0
        created_audio = 0
        already_existed = 0

        for fc in base_qs.iterator(chunk_size=500):
            word = fc.word
            deck = fc.deck

            # ── def_to_word ──────────────────────────────────────────────────
            if not Flashcard.objects.filter(deck=deck, word=word, card_type="def_to_word").exists():
                if not dry_run:
                    Flashcard.objects.create(
                        deck=deck,
                        word=word,
                        card_type="def_to_word",
                        front_text=word.meaning_vi or word.word,
                        back_text=word.word,
                        order=fc.order + 100,
                    )
                created_def += 1
            else:
                already_existed += 1

            # ── audio_to_word ─────────────────────────────────────────────────
            if not Flashcard.objects.filter(deck=deck, word=word, card_type="audio_to_word").exists():
                if not dry_run:
                    Flashcard.objects.create(
                        deck=deck,
                        word=word,
                        card_type="audio_to_word",
                        front_text=word.word,   # UI reads word_detail.audio_*_s3_key
                        back_text=word.word,
                        order=fc.order + 200,
                    )
                created_audio += 1

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}def_to_word created: {created_def} | "
                f"audio_to_word created: {created_audio} | "
                f"already existed (skipped): {already_existed}"
            )
        )
