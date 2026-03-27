"""
Management command: seed_default_decks

Creates 5 public system flashcard decks (owner=None), one per CEFR level,
seeded with Word objects at that level (all 3 card types per word).

Usage:
  python manage.py seed_default_decks
  python manage.py seed_default_decks --dry-run
  python manage.py seed_default_decks --clear    # drop & re-create system decks
"""
from django.core.management.base import BaseCommand

from apps.vocabulary.models import Flashcard, FlashcardDeck, Word

DECK_CONFIG = [
    {
        "name": "A1 Core Vocabulary",
        "description": "300 từ tiếng Anh cơ bản nhất trình độ A1 theo chuẩn Oxford.",
        "cefr_level": "A1",
        "domain": "general",
        "limit": 300,
    },
    {
        "name": "A2 Expansion",
        "description": "Mở rộng vốn từ A2 với 600 từ hữu dụng trong đời sống và giao tiếp.",
        "cefr_level": "A2",
        "domain": "everyday",
        "limit": 600,
    },
    {
        "name": "B1 Everyday English",
        "description": "Từ vựng B1 cho giao tiếp hàng ngày và đọc hiểu thông dụng.",
        "cefr_level": "B1",
        "domain": "general",
        "limit": 500,
    },
    {
        "name": "B2 Business & Academic",
        "description": "Từ vựng B2 dành cho môi trường kinh doanh và học thuật.",
        "cefr_level": "B2",
        "domain": "business",
        "limit": 500,
    },
    {
        "name": "C1 Advanced",
        "description": "Từ vựng C1 nâng cao cho học thuật và văn viết chuyên nghiệp.",
        "cefr_level": "C1",
        "domain": "academic",
        "limit": 500,
    },
]


class Command(BaseCommand):
    help = "Seed system default flashcard decks (owner=None) for each CEFR level"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Preview what would be created, without writing to the DB.",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="Delete all existing system decks before re-creating them.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        clear = options["clear"]

        if clear and not dry_run:
            deleted, _ = FlashcardDeck.objects.filter(owner__isnull=True).delete()
            self.stdout.write(f"Cleared {deleted} existing system decks.\n")

        total_decks = 0
        total_cards = 0

        for cfg in DECK_CONFIG:
            cefr = cfg["cefr_level"]
            words = (
                Word.objects
                .filter(cefr_level=cefr)
                .order_by("frequency_rank", "word")[: cfg["limit"]]
            )
            word_count = words.count()

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] '{cfg['name']}' [{cefr}] — {word_count} words → {word_count * 3} cards"
                )
                total_decks += 1
                total_cards += word_count * 3
                continue

            deck, created = FlashcardDeck.objects.get_or_create(
                owner=None,
                name=cfg["name"],
                defaults={
                    "description": cfg["description"],
                    "cefr_level": cefr,
                    "domain": cfg["domain"],
                    "is_public": True,
                },
            )
            action = "Created" if created else "Updated"

            cards_made = 0
            for word in words:
                Flashcard.objects.get_or_create(
                    deck=deck, word=word, card_type="word_to_def",
                    defaults={"front_text": word.word, "back_text": word.meaning_vi, "order": 1},
                )
                Flashcard.objects.get_or_create(
                    deck=deck, word=word, card_type="def_to_word",
                    defaults={"front_text": word.meaning_vi or word.word, "back_text": word.word, "order": 2},
                )
                Flashcard.objects.get_or_create(
                    deck=deck, word=word, card_type="audio_to_word",
                    defaults={"front_text": word.word, "back_text": word.word, "order": 3},
                )
                cards_made += 1

            total_decks += 1
            total_cards += cards_made * 3
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} deck \"{cfg['name']}\" [{cefr}] — {word_count} words → {cards_made * 3} cards"
                )
            )

        suffix = " (DRY RUN)" if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone{suffix}! {total_decks} decks, {total_cards} flashcards total."
            )
        )
