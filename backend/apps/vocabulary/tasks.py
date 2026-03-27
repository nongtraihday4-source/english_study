"""
apps/vocabulary/tasks.py
─────────────────────────────────────────────────────────────────────────────
Celery tasks for the Vocabulary / Flashcard module.

Scheduled task:
  check_due_cards_and_notify  — runs every hour (top of hour).
  For each user, fires only when the current ICT hour matches their
  preferred `flashcard_notify_hour` setting (default: 8 = 08:00 ICT).
  Deduplication: skips users already notified today.
─────────────────────────────────────────────────────────────────────────────
"""
import logging

from celery import shared_task

logger = logging.getLogger("es.vocabulary")


@shared_task(
    bind=True,
    name="vocabulary.check_due_cards_and_notify",
    max_retries=3,
    default_retry_delay=300,
)
def check_due_cards_and_notify(self):
    """
    PRD 5.8 — Smart Notification: personalised daily flashcard due reminder.

    Runs every hour. For each user, checks if the current ICT hour matches
    their `flashcard_notify_hour` setting before sending a notification.
    Idempotent: only one notification per user per calendar day.

    Returns a summary string for Celery result inspection.
    """
    try:
        from django.db.models import Count
        from django.utils import timezone

        from apps.notifications.models import Notification
        from apps.users.models import UserSettings

        from .models import UserFlashcardProgress

        now_ict = timezone.localtime(timezone.now())  # CELERY_TIMEZONE = Asia/Ho_Chi_Minh → already ICT
        current_hour = now_ict.hour
        today = now_ict.date()

        # Only process users whose preferred notify hour matches NOW
        matching_user_ids = list(
            UserSettings.objects
            .filter(notify_flashcard_due=True, flashcard_notify_hour=current_hour)
            .values_list("user_id", flat=True)
        )

        if not matching_user_ids:
            return f"Hour {current_hour}:00 ICT — no users scheduled for this hour."

        due_rows = (
            UserFlashcardProgress.objects
            .filter(next_review_date__lte=today, is_mastered=False, user_id__in=matching_user_ids)
            .values("user_id")
            .annotate(due_count=Count("id"))
        )

        created = 0
        skipped = 0

        for row in due_rows:
            user_id = row["user_id"]
            due_count = row["due_count"]

            # Idempotency — skip if already notified today
            already_sent = Notification.objects.filter(
                user_id=user_id,
                notification_type="flashcard_due",
                created_at__date=today,
            ).exists()

            if already_sent:
                skipped += 1
                continue

            Notification.objects.create(
                user_id=user_id,
                notification_type="flashcard_due",
                title=f"Bạn có {due_count} thẻ cần ôn hôm nay!",
                message=(
                    f"Đừng để mất streak! Hãy ôn {due_count} flashcard "
                    "để củng cố từ vựng của bạn."
                ),
                action_url="/flashcards",
                reference_type="flashcard_due_reminder",
            )
            created += 1

        summary = (
            f"Hour {current_hour}:00 ICT — {created} notifications created, "
            f"{skipped} skipped (already sent today)."
        )
        logger.info(summary)
        return summary

    except Exception as exc:
        logger.exception("check_due_cards_and_notify failed: %s", exc)
        raise self.retry(exc=exc)



@shared_task(
    bind=True,
    name="vocabulary.check_due_cards_and_notify",
    max_retries=3,
    default_retry_delay=300,
)
def check_due_cards_and_notify(self):
    """
    PRD 5.8 — Smart Notification: daily flashcard due reminder.

    Algorithm:
      1. Group UserFlashcardProgress by user where next_review_date <= today
         and card is not yet mastered.
      2. For each user, skip if a 'flashcard_due' notification was already
         sent today (idempotent).
      3. Otherwise create a Notification record.

    Returns a summary string for Celery result inspection.
    """
    try:
        from django.db.models import Count
        from django.utils import timezone

        from apps.notifications.models import Notification

        from .models import UserFlashcardProgress

        today = timezone.localdate()

        due_rows = (
            UserFlashcardProgress.objects
            .filter(next_review_date__lte=today, is_mastered=False)
            .values("user_id")
            .annotate(due_count=Count("id"))
        )

        created = 0
        skipped = 0

        for row in due_rows:
            user_id = row["user_id"]
            due_count = row["due_count"]

            # Idempotency — skip if already notified today
            already_sent = Notification.objects.filter(
                user_id=user_id,
                notification_type="flashcard_due",
                created_at__date=today,
            ).exists()

            if already_sent:
                skipped += 1
                continue

            Notification.objects.create(
                user_id=user_id,
                notification_type="flashcard_due",
                title=f"Bạn có {due_count} thẻ cần ôn hôm nay!",
                message=(
                    f"Đừng để mất streak! Hãy ôn {due_count} flashcard "
                    "để củng cố từ vựng của bạn."
                ),
                action_url="/flashcards",
                reference_type="flashcard_due_reminder",
            )
            created += 1

        summary = (
            f"Flashcard due-reminder: {created} notifications created, "
            f"{skipped} skipped (already sent today)."
        )
        logger.info(summary)
        return summary

    except Exception as exc:
        logger.exception("check_due_cards_and_notify failed: %s", exc)
        raise self.retry(exc=exc)
