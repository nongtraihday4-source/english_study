"""
Management command: seed_topic_decks

Creates one public system FlashcardDeck per distinct topic stored on Word rows.
Each deck inherits the CEFR level of the majority of its words.
Flashcards are created as 3 card types per word (word_to_def, def_to_word, audio_to_word).

Usage:
    python manage.py seed_topic_decks
    python manage.py seed_topic_decks --dry-run
    python manage.py seed_topic_decks --clear   # drop & re-create topic decks
"""
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.vocabulary.models import Flashcard, FlashcardDeck, Word


def _majority_cefr(words) -> str:
    """Return the most common cefr_level among the given queryset of Words."""
    counter = Counter(w.cefr_level for w in words if w.cefr_level)
    if counter:
        return counter.most_common(1)[0][0]
    return "A2"


class Command(BaseCommand):
    help = "Seed system topic-based flashcard decks (one deck per distinct Word.topic)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be created without writing to the DB",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing system topic decks before re-creating",
        )

    def handle(self, *args, **options):
        dry = options["dry_run"]
        do_clear = options["clear"]

        # Fetch all distinct non-null topics
        topics = list(
            Word.objects.filter(topic__isnull=False)
            .exclude(topic="")
            .values_list("topic", flat=True)
            .distinct()
            .order_by("topic")
        )

        if not topics:
            self.stdout.write(self.style.WARNING("No words with topics found in DB. Aborting."))
            return

        self.stdout.write(
            self.style.MIGRATE_HEADING(f"\nseed_topic_decks — {len(topics)} topics found")
        )

        if do_clear and not dry:
            # Only delete system decks that are named exactly like a topic
            deleted, _ = FlashcardDeck.objects.filter(
                owner__isnull=True, name__in=topics
            ).delete()
            self.stdout.write(f"  Cleared {deleted} existing topic decks\n")

        total_decks = 0
        total_cards = 0

        for topic in topics:
            words = list(Word.objects.filter(topic=topic).order_by("frequency_rank", "word"))
            if not words:
                continue

            cefr = _majority_cefr(words)

            if dry:
                self.stdout.write(
                    f"  [DRY] '{topic}' [{cefr}] — {len(words)} words → {len(words) * 3} cards"
                )
                total_decks += 1
                total_cards += len(words) * 3
                continue

            deck, created = FlashcardDeck.objects.get_or_create(
                owner=None,
                name=topic,
                defaults={
                    "description": f"Từ vựng chương '{topic}' — {cefr}",
                    "cefr_level": cefr,
                    "domain": "general",
                    "is_public": True,
                },
            )

            # If deck already existed but cefr changed, update it
            if not created and deck.cefr_level != cefr:
                deck.cefr_level = cefr
                deck.save(update_fields=["cefr_level"])

            action = "Created" if created else "Updated"
            cards_made = 0

            with transaction.atomic():
                for word in words:
                    Flashcard.objects.get_or_create(
                        deck=deck, word=word, card_type="word_to_def",
                        defaults={
                            "front_text": word.word,
                            "back_text": word.meaning_vi or "",
                            "order": 1,
                        },
                    )
                    Flashcard.objects.get_or_create(
                        deck=deck, word=word, card_type="def_to_word",
                        defaults={
                            "front_text": word.meaning_vi or word.word,
                            "back_text": word.word,
                            "order": 2,
                        },
                    )
                    Flashcard.objects.get_or_create(
                        deck=deck, word=word, card_type="audio_to_word",
                        defaults={
                            "front_text": word.word,
                            "back_text": word.word,
                            "order": 3,
                        },
                    )
                    cards_made += 1

            total_decks += 1
            total_cards += cards_made * 3
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {action} '{topic}' [{cefr}] — {len(words)} words, {cards_made * 3} cards"
                )
            )

        suffix = " (DRY RUN)" if dry else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone{suffix}! {total_decks} decks, {total_cards} flashcards total."
            )
        )
