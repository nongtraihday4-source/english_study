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
    _generate_certificate_pdf(cert)
    logger.info("Certificate issued | user=%s cert=%s", user.pk, cert.verification_code)
    return cert


def _generate_certificate_pdf(cert: "Certificate") -> None:
    """
    Generate a certificate PDF using reportlab and upload to S3 (or local MEDIA_ROOT).
    Sets cert.pdf_s3_key on success.
    """
    import io
    from django.conf import settings as django_settings

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        logger.warning("reportlab not installed — certificate PDF skipped for cert=%s", cert.pk)
        return

    width, height = landscape(A4)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    center = ParagraphStyle(
        "center", parent=styles["Normal"],
        alignment=TA_CENTER, fontName="Helvetica",
    )
    title_style = ParagraphStyle(
        "cert_title", parent=center,
        fontSize=32, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "cert_sub", parent=center,
        fontSize=14, fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
    )
    name_style = ParagraphStyle(
        "cert_name", parent=center,
        fontSize=28, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "cert_body", parent=center,
        fontSize=13, fontName="Helvetica",
        textColor=colors.HexColor("#444444"),
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "cert_meta", parent=center,
        fontSize=10, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#888888"),
    )

    full_name = (
        f"{cert.user.first_name} {cert.user.last_name}".strip()
        or cert.user.email
    )
    course_name = cert.course.title if cert.course else ""
    level_name = cert.level.name if cert.level else ""
    achievement = course_name or level_name or "English Study Programme"
    issued_date = cert.issued_at.strftime("%d/%m/%Y")

    story = [
        Spacer(1, 10 * mm),
        Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style),
        Spacer(1, 4 * mm),
        Paragraph("This is to certify that", subtitle_style),
        Spacer(1, 3 * mm),
        Paragraph(full_name, name_style),
        Spacer(1, 3 * mm),
        Paragraph(
            f"has successfully completed the <b>{achievement}</b>",
            body_style,
        ),
        Spacer(1, 2 * mm),
        Paragraph(
            "demonstrating proficiency in English language skills.",
            body_style,
        ),
        Spacer(1, 8 * mm),
        Paragraph(f"Issued on: {issued_date}", meta_style),
        Spacer(1, 2 * mm),
        Paragraph(
            f"Verification code: {cert.verification_code}",
            meta_style,
        ),
    ]

    doc.build(story)
    pdf_bytes = buf.getvalue()

    # ── Upload to S3 or save locally ─────────────────────────────────────────
    s3_prefix = getattr(django_settings, "CERTIFICATE_PDF_S3_PREFIX", "certificates/")
    s3_key = f"{s3_prefix}{cert.verification_code}.pdf"

    aws_key = getattr(django_settings, "AWS_ACCESS_KEY_ID", "")
    if aws_key:
        try:
            import boto3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_key,
                aws_secret_access_key=django_settings.AWS_SECRET_ACCESS_KEY,
                region_name=django_settings.AWS_S3_REGION_NAME,
            )
            s3.put_object(
                Bucket=django_settings.AWS_STORAGE_BUCKET_NAME,
                Key=s3_key,
                Body=pdf_bytes,
                ContentType="application/pdf",
            )
            cert.pdf_s3_key = s3_key
            cert.save(update_fields=["pdf_s3_key"])
            logger.info("Certificate PDF uploaded to S3 | key=%s", s3_key)
            return
        except Exception as exc:
            logger.warning("S3 upload failed for cert PDF — falling back to local: %s", exc)

    # Fallback: save to MEDIA_ROOT/certificates/
    from pathlib import Path
    media_root = getattr(django_settings, "MEDIA_ROOT", "/tmp")
    cert_dir = Path(media_root) / "certificates"
    cert_dir.mkdir(parents=True, exist_ok=True)
    local_path = cert_dir / f"{cert.verification_code}.pdf"
    local_path.write_bytes(pdf_bytes)
    cert.pdf_s3_key = str(local_path)
    cert.save(update_fields=["pdf_s3_key"])
    logger.info("Certificate PDF saved locally | path=%s", local_path)


# ─── Celery tasks (defined here to avoid circular imports) ────────────────────

from english_study.celery import app as celery_app  # noqa: E402


@celery_app.task(name="gamification.check_achievements", ignore_result=True)
def check_achievements_task(user_id: int):
    check_achievements_for_user(user_id)
