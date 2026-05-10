from datetime import date

from django.utils import timezone

from apps.vocabulary.models import Flashcard, UserFlashcardProgress


class SRSService:
    @staticmethod
    def get_due_queue(user, limit=10):
        now = date.today() if hasattr(timezone, "now") else timezone.now().date()
        due_progress = UserFlashcardProgress.objects.filter(
            user=user,
            next_review_date__lte=now,
        ).select_related("flashcard__word", "flashcard__deck").order_by("next_review_date")[:limit]

        return [p.flashcard for p in due_progress]

    @staticmethod
    def get_new_cards(user, deck, limit=10):
        return (
            Flashcard.objects.filter(deck=deck)
            .exclude(
                id__in=UserFlashcardProgress.objects.filter(user=user).values_list(
                    "flashcard_id", flat=True
                )
            )
            .select_related("word")[:limit]
        )