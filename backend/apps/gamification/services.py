"""
apps/gamification/services.py
─────────────────────────────────────────────────────────────────────────────
XP awarding, badge checking, streak maintenance, live leaderboard fallback.
─────────────────────────────────────────────────────────────────────────────
Called from:
  • AutoGrader (after every exercise result)
  • Celery tasks (after AI grading completes)
  • Celery beat (daily streak check, leaderboard snapshot)
"""
import logging
import secrets
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from utils.formatters import fmt_vn

logger = logging.getLogger("es.progress")


# ─── XP ───────────────────────────────────────────────────────────────────────

XP_TABLE = {
    "exercise_complete": 10,
    "perfect_score": 25,
    "streak_7": 50,
    "streak_30": 150,
    "chapter_complete": 100,
    "daily_challenge": 20,
}


@transaction.atomic
def award_xp(user, source: str, xp_amount: int = None, reference_id=None, reference_type: str = None, note: str = None):
    """
    Award XP to a user, log it, and trigger achievement checks.
    xp_amount defaults to XP_TABLE[source] if not provided.
    """
    from .models import XPLog

    if xp_amount is None:
        xp_amount = XP_TABLE.get(source, 0)
    if xp_amount <= 0:
        return None

    log = XPLog.objects.create(
        user=user,
        source=source,
        xp_amount=xp_amount,
        reference_id=reference_id,
        reference_type=reference_type,
        note=note,
    )

    logger.debug(
        "XP awarded | user=%s source=%s amount=%s total_logged=%s",
        user.pk, source, fmt_vn(xp_amount),
        fmt_vn(XPLog.objects.filter(user=user).count()),
    )

    # Async badge check (avoid slowing down the main request)
    check_achievements_task.delay(user.pk)

    return log


# ─── Streak ───────────────────────────────────────────────────────────────────

@transaction.atomic
def record_daily_activity(user) -> dict:
    """
    Called once per day when user completes any exercise.
    Returns updated streak data.
    """
    from apps.progress.models import DailyStreak

    today = date.today()
    streak, _ = DailyStreak.objects.select_for_update().get_or_create(user=user)

    previous = streak.last_activity_date

    if previous == today:
        return {"current_streak": streak.current_streak, "extended": False}

    if previous == today - timedelta(days=1):
        # Consecutive day
        streak.current_streak += 1
    elif streak.streak_protected_until and today <= streak.streak_protected_until:
        # Streak shield active — maintain streak
        pass
    else:
        # Streak broken
        streak.current_streak = 1

    streak.last_activity_date = today
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    streak.save()

    # Award XP for milestone streaks
    cs = streak.current_streak
    if cs == 7:
        award_xp(user, "streak_7", note=f"🔥 Streak {cs} ngày!")
    elif cs == 30:
        award_xp(user, "streak_30", note=f"🔥 Streak {cs} ngày!")

    logger.debug("Streak | user=%s streak=%d longest=%d", user.pk, cs, streak.longest_streak)
    return {"current_streak": cs, "extended": True}


# ─── Achievement checking ─────────────────────────────────────────────────────

def check_achievements_for_user(user_id: int):
    """
    Check all active achievements for a user and award any not yet earned.
    Called asynchronously via Celery to avoid blocking requests.
    """
    from django.contrib.auth import get_user_model
    from .models import Achievement, UserAchievement, XPLog
    from apps.progress.models import DailyStreak, LessonProgress
    from apps.vocabulary.models import UserFlashcardProgress

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    earned_ids = set(UserAchievement.objects.filter(user=user).values_list("achievement_id", flat=True))
    achievements = Achievement.objects.filter(is_active=True).exclude(pk__in=earned_ids)

    for ach in achievements:
        earned = _evaluate_achievement(user, ach)
        if earned:
            UserAchievement.objects.create(user=user, achievement=ach)
            award_xp(
                user,
                source="badge_earned",
                xp_amount=ach.xp_reward,
                reference_id=ach.pk,
                reference_type="achievement",
                note=f"Badge: {ach.name_vi}",
            )
            # Notify user
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=user,
                notification_type="achievement",
                title=f"Bạn nhận được huy hiệu: {ach.name_vi}!",
                message=ach.description,
                reference_id=ach.pk,
                reference_type="achievement",
            )
            logger.info("Badge earned | user=%s badge=%s xp=%s", user.pk, ach.name_vi, ach.xp_reward)


def _evaluate_achievement(user, achievement) -> bool:
    """Returns True if user has met the achievement's condition."""
    from apps.progress.models import DailyStreak, LessonProgress
    ct = achievement.condition_type
    t = achievement.threshold_value

    if ct == "streak_days":
        streak = DailyStreak.objects.filter(user=user).first()
        return streak and streak.longest_streak >= t

    if ct == "lessons_done":
        return LessonProgress.objects.filter(user=user, status="completed").count() >= t

    if ct == "words_learned":
        from apps.vocabulary.models import UserFlashcardProgress
        return UserFlashcardProgress.objects.filter(user=user, is_mastered=True).count() >= t

    if ct == "skill_score_gte":
        from apps.progress.models import CumulativeScore
        return CumulativeScore.objects.filter(user=user, overall_avg__gte=t).exists()

    return False


# ─── Live leaderboard fallback ────────────────────────────────────────────────

def build_live_leaderboard(period: str):
    """
    Returns a list of (rank, user, xp_total) dicts when no snapshot exists.
    Used as fallback before the first Celery beat run.
    """
    from django.contrib.auth import get_user_model
    from django.db.models import Sum
    from .models import XPLog

    User = get_user_model()
    now = timezone.now()

    if period == "weekly":
        since = now - timedelta(days=7)
    elif period == "monthly":
        since = now - timedelta(days=30)
    else:
        since = None

    qs = XPLog.objects.all()
    if since:
        qs = qs.filter(created_at__gte=since)

    top = (
        qs.values("user")
        .annotate(xp_total=Sum("xp_amount"))
        .order_by("-xp_total")[:100]
    )

    # Build mock LeaderboardSnapshot objects (not persisted)
    from .models import LeaderboardSnapshot
    results = []
    for i, row in enumerate(top, start=1):
        snap = LeaderboardSnapshot.__new__(LeaderboardSnapshot)
        snap.rank = i
        snap.user_id = row["user"]
        snap.xp_total = row["xp_total"] or 0
        snap.period = period
        try:
            snap.user = User.objects.get(pk=row["user"])
        except User.DoesNotExist:
            continue
        results.append(snap)
    return results


# ─── Certificate generation ───────────────────────────────────────────────────

@transaction.atomic
def issue_certificate(user, course=None, level=None) -> "Certificate":
    from .models import Certificate

    cert = Certificate.objects.create(
        user=user,
        course=course,
        level=level,
        verification_code=secrets.token_hex(16),
    )
    # TODO: generate PDF via reportlab/wkhtmltopdf, upload to S3
    logger.info("Certificate issued | user=%s cert=%s", user.pk, cert.verification_code)
    return cert


# ─── Celery tasks (defined here to avoid circular imports) ────────────────────

from english_study.celery import app as celery_app  # noqa: E402


@celery_app.task(name="gamification.check_achievements", ignore_result=True)
def check_achievements_task(user_id: int):
    check_achievements_for_user(user_id)
