#!/usr/bin/env python
"""
simulate_course_flow.py
─────────────────────────────────────────────────────────────────────────────
Simulates a complete learning journey for one user through Course A1:
  1. Enroll in course
  2. Check which lessons are available
  3. Complete each lesson (with a random score 60-100)
  4. Verify next lesson unlocks
  5. Continue until all lessons done
  6. Check enrollment completion + XP earned + streak + badge summary

Run from backend/:
  python manage.py shell < ../scripts/simulate_course_flow.py
OR:
  cd backend && python manage.py shell -c "exec(open('../scripts/simulate_course_flow.py').read())"
─────────────────────────────────────────────────────────────────────────────
"""
import os, sys, random, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings")

import django
django.setup()

from django.utils import timezone
from django.db import transaction

from apps.curriculum.models import Course, Chapter, Lesson
from apps.progress.models import UserEnrollment, LessonProgress
from apps.progress.views import (
    _initialize_lesson_progress,
    _unlock_next_lesson,
    _recalc_enrollment_progress,
)
from apps.users.models import User

# ─── ANSI Colors ──────────────────────────────────────────────────────────────
R  = "\033[91m"
G  = "\033[92m"
Y  = "\033[93m"
B  = "\033[94m"
M  = "\033[95m"
C  = "\033[96m"
W  = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RST = "\033[0m"

def hr(char="─", n=72):
    print(f"{DIM}{char * n}{RST}")

def section(title):
    print()
    hr("═")
    print(f"{BOLD}{C}  {title}{RST}")
    hr("═")

def ok(msg):  print(f"  {G}✓{RST}  {msg}")
def info(msg): print(f"  {B}ℹ{RST}  {msg}")
def warn(msg): print(f"  {Y}⚠{RST}  {msg}")
def err(msg):  print(f"  {R}✗{RST}  {msg}")
def step(n, msg): print(f"\n{BOLD}{Y}[Step {n}]{RST} {msg}")

# ─── Find test user ────────────────────────────────────────────────────────────
section("1. Setup — Finding Test User")

user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()
if not user:
    err("No users in database. Create one first.")
    sys.exit(1)

info(f"Using user: {BOLD}{user.username}{RST} (id={user.pk}, role={user.role})")

# Clean previous simulation data for this user
step("0", "Cleaning previous simulation data for clean run...")
UserEnrollment.objects.filter(user=user).delete()
LessonProgress.objects.filter(user=user).delete()
try:
    from apps.gamification.models import XPLog
    XPLog.objects.filter(user=user, reference_type="lesson").delete()
    ok("Removed previous XP log entries")
except Exception as e:
    warn(f"Could not clear XP logs: {e}")
try:
    from apps.progress.models import DailyStreak
    DailyStreak.objects.filter(user=user).delete()
    ok("Cleared streak data")
except Exception:
    pass
ok("Clean slate confirmed")

# ─── Find Course A1 ────────────────────────────────────────────────────────────
section("2. Course & Structure")

course = Course.objects.select_related("level").filter(
    level__code="A1", is_active=True
).first()
if not course:
    err("No A1 course found. Run seed_courses first.")
    sys.exit(1)

chapters = list(Chapter.objects.filter(course=course).order_by("order"))
all_lessons = list(
    Lesson.objects.filter(chapter__course=course, is_active=True).order_by(
        "chapter__order", "order"
    )
)

info(f"Course: {BOLD}{course.title}{RST} (id={course.pk})")
info(f"Level:  {course.level.code} — {course.level.name_vi}")
info(f"Chapters: {len(chapters)}")
info(f"Total lessons: {len(all_lessons)}")
print()
for ch in chapters:
    lessons_in = [l for l in all_lessons if l.chapter_id == ch.pk]
    lesson_names = ", ".join(f"{l.title} [{l.lesson_type}]" for l in lessons_in)
    print(f"  {DIM}Chapter {ch.order:2d}{RST} {BOLD}{ch.title}{RST}")
    for l in lessons_in:
        print(f"    {DIM}L{l.order}{RST} {l.title}  {DIM}[{l.lesson_type}, ~{l.estimated_minutes}min]{RST}")

# ─── Enroll ────────────────────────────────────────────────────────────────────
section("3. Enrollment")

step("1", "Enrolling user in course...")
with transaction.atomic():
    enrollment, created = UserEnrollment.objects.get_or_create(
        user=user, course=course, defaults={"is_deleted": False}
    )
    if not created and enrollment.is_deleted:
        enrollment.is_deleted = False
        enrollment.save(update_fields=["is_deleted"])
        created = True
    if created:
        _initialize_lesson_progress(user, course)
        ok(f"Enrolled! UserEnrollment id={enrollment.pk}")
    else:
        ok(f"Re-enrolled (already existed). id={enrollment.pk}")

# Show initial unlock state
unlocked = list(LessonProgress.objects.filter(
    user=user, lesson__chapter__course=course, status="available"
).select_related("lesson__chapter").order_by("lesson__chapter__order", "lesson__order"))

info(f"Lessons immediately unlocked after enrollment: {len(unlocked)}")
for lp in unlocked:
    ok(f"  Available: {lp.lesson.chapter.title} → {lp.lesson.title}")

# ─── Simulate Learning ─────────────────────────────────────────────────────────
section("4. Learning Simulation — Completing All Lessons")

total_xp_earned = 0
total_time_spent = 0
lessons_completed = 0
chapter_scores = {}  # chapter_id → [scores]

for lesson in all_lessons:
    # Poll current status
    lp = LessonProgress.objects.filter(user=user, lesson=lesson).first()
    current_status = lp.status if lp else "locked"

    if current_status == "locked":
        warn(f"LOCKED (should not happen): {lesson.title}")
        continue

    # Simulate study time (5-20 min per lesson)
    study_seconds = random.randint(300, 1200)
    score = random.randint(65, 100)  # Realistic: mostly pass, occasional high score
    total_time_spent += study_seconds

    # Mark complete
    if lp is None:
        lp, _ = LessonProgress.objects.get_or_create(
            user=user, lesson=lesson, defaults={"status": "available"}
        )
    lp.status = "completed"
    lp.attempts_count = (lp.attempts_count or 0) + 1
    lp.time_spent_seconds = (lp.time_spent_seconds or 0) + study_seconds
    lp.completed_at = timezone.now()
    if lp.best_score is None or score > lp.best_score:
        lp.best_score = score
    lp.save()

    lessons_completed += 1

    # Unlock next
    _unlock_next_lesson(user, lesson)

    # XP calculation
    xp = 10 + (50 if score >= 80 else 0)
    total_xp_earned += xp
    try:
        from apps.gamification.models import XPLog
        XPLog.objects.create(
            user=user,
            source="exercise_complete",
            xp_amount=xp,
            reference_id=lesson.pk,
            reference_type="lesson",
            note=f"Hoàn thành bài: {lesson.title}",
        )
    except Exception:
        pass

    # Track chapter scores
    chapter_scores.setdefault(lesson.chapter_id, []).append(score)

    score_color = G if score >= 80 else (Y if score >= 60 else R)
    print(
        f"  {G}✓{RST} {lesson.chapter.title[:25]:<25} "
        f"→ {lesson.title[:30]:<30} "
        f"score={score_color}{score:3d}%{RST}  "
        f"xp={BOLD}+{xp}{RST}  "
        f"time={study_seconds//60}m{study_seconds%60:02d}s"
    )

# Recalc enrollment progress
_recalc_enrollment_progress(user, course)
enrollment.refresh_from_db()

# ─── Chapter Completion Summary ────────────────────────────────────────────────
section("5. Chapter Completion Report")

for ch in chapters:
    scores = chapter_scores.get(ch.pk, [])
    if not scores:
        warn(f"Chapter '{ch.title}': no scores")
        continue
    avg = round(sum(scores) / len(scores))
    passed = avg >= ch.passing_score
    status_icon = f"{G}PASS{RST}" if passed else f"{R}FAIL{RST}"
    bar_filled = int(avg / 5)
    bar = f"{G}{'█' * bar_filled}{DIM}{'░' * (20 - bar_filled)}{RST}"
    print(
        f"  {status_icon}  {ch.title[:35]:<35} "
        f"avg={avg:3d}%  {bar}  "
        f"(passing={ch.passing_score}%)"
    )

# ─── Final Enrollment Stats ────────────────────────────────────────────────────
section("6. Course Completion Stats")

completed_count = LessonProgress.objects.filter(
    user=user, lesson__chapter__course=course, status="completed"
).count()
locked_count = len(all_lessons) - completed_count

ok(f"Lessons completed: {BOLD}{completed_count}/{len(all_lessons)}{RST}")
ok(f"Progress: {BOLD}{enrollment.progress_percent}%{RST}")
ok(f"Enrollment status: {BOLD}{enrollment.status}{RST}")
ok(f"Total study time: {BOLD}{total_time_spent//60} minutes {total_time_spent%60} seconds{RST}")
ok(f"Total XP earned: {BOLD}{total_xp_earned} XP{RST}")
if completed_count == len(all_lessons):
    print(f"\n  {BOLD}{G}🎉  COURSE COMPLETED!{RST}")
    if enrollment.completed_at:
        ok(f"Completed at: {enrollment.completed_at.strftime('%Y-%m-%d %H:%M')}")

# ─── Streak ───────────────────────────────────────────────────────────────────
section("7. Streak & Gamification")

try:
    from apps.progress.models import DailyStreak
    streak, _ = DailyStreak.objects.get_or_create(user=user)
    today = timezone.localdate()
    if streak.last_activity_date != today:
        streak.current_streak = (streak.current_streak or 0) + 1
        streak.longest_streak = max(streak.longest_streak or 0, streak.current_streak)
        streak.last_activity_date = today
        streak.save()
    ok(f"Current streak: {BOLD}🔥 {streak.current_streak} ngày{RST}")
    ok(f"Longest streak: {BOLD}{streak.longest_streak} ngày{RST}")
except Exception as e:
    warn(f"Could not update streak: {e}")

try:
    from apps.gamification.models import XPLog
    total_xp = sum(XPLog.objects.filter(user=user).values_list("xp_amount", flat=True))
    ok(f"Total XP (all time, from XPLog): {BOLD}{total_xp} XP{RST}")
except Exception as e:
    warn(f"Could not load XP: {e}")

# ─── What does learner receive on completion? ─────────────────────────────────
section("8. Course Completion Rewards")

print(f"""
  {BOLD}Khi hoàn thành khóa học, người học nhận được:{RST}

  {G}📊 Progress{RST}
     • enrollment.progress_percent = 100%
     • enrollment.status → "completed" (khi 100%)
     • enrollment.completed_at = timestamp

  {G}⚡ XP Points{RST}
     • +10 XP mỗi bài hoàn thành
     • +50 XP bonus nếu điểm ≥ 80%
     • Tổng khóa A1 (48 bài): {BOLD}~480-2880 XP{RST} tùy điểm số

  {G}🔥 Streak{RST}
     • +1 ngày streak cho mỗi ngày học
     • Badge đặc biệt khi đạt streak 7/30/100 ngày

  {G}🎖 Badges (gamification app){RST}
     • "Course Complete" badge cho A1
     • "Speed Learner" nếu hoàn thành trong 30 ngày
     • Level badge: "A1 Graduate"

  {G}🔓 Unlock{RST}
     • Mở khóa Course A2 (nếu có prerequisite)
     • Mở thêm nội dung flashcard cho level A2

  {G}📜 Certificate{RST} {DIM}(chưa triển khai — roadmap){RST}
     • PDF certificate với tên, ngày, cấp độ
     • Shareable link với QR code xác thực

  {Y}⚠ Lưu ý:{RST} Badges và Certificate hiện đang trong roadmap,
    chưa được tạo tự động. Cần implement badge_check signal
    sau khi enrollment.status = "completed".
""")

hr("═")
print(f"{BOLD}{G}  ✅  SIMULATION COMPLETE{RST}")
hr("═")
print()
