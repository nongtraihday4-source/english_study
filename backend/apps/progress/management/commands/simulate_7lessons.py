"""
management command: simulate_7lessons
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mô phỏng toàn bộ luồng học viên đăng ký khoá học → hoàn thành
7 bài học liên tiếp (vocab → grammar → reading → listening →
speaking → writing → assessment), chấm điểm từng bài, xác nhận
unlock sequential, tổng hợp XP, % tiến độ và chapter_completed.

Usage:
    python manage.py simulate_7lessons [--chapter "Giới thiệu bản thân"]
    python manage.py simulate_7lessons --cleanup     # xoá dữ liệu test rồi chạy lại
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

# ── Console helpers ───────────────────────────────────────────────────────────
SEP  = "═" * 72
SEP2 = "─" * 72
GREEN  = "\033[92m"
RED    = "\033[91m"
BLUE   = "\033[94m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def ok(msg):     print(f"    {GREEN}✔  {msg}{RESET}")
def fail(msg):   print(f"    {RED}✘  {msg}{RESET}")
def info(msg):   print(f"    {BLUE}ℹ  {msg}{RESET}")
def warn(msg):   print(f"    {YELLOW}⚠  {msg}{RESET}")
def head(msg):   print(f"\n{SEP}\n  {BOLD}{msg}{RESET}\n{SEP2}")
def subhead(msg): print(f"\n  {CYAN}▶ {msg}{RESET}")
def dim(msg):    print(f"    {DIM}{msg}{RESET}")


# ── Lesson-type test scenarios ────────────────────────────────────────────────
# Each entry maps lesson_type → list of (attempt_label, score, time_s)
# Multiple entries = retry scenario (fail then pass).
SCENARIOS = {
    "vocabulary": [
        ("Lượt 1 — khám phá từ vựng (tự học, không chấm điểm)", None, 480),
    ],
    "grammar": [
        ("Lượt 1 — hoàn thành bài tập ngữ pháp (85%)", 85, 600),
    ],
    "reading": [
        ("Lượt 1 — trả lời đúng hết câu hỏi đọc hiểu (100%)", 100, 540),
    ],
    "listening": [
        ("Lượt 1 — nghe + chính tả, điểm thấp (40%) — FAIL", 40, 360),
        ("Lượt 2 — nghe lại, cải thiện (80%) — PASS", 80, 420),
    ],
    "speaking": [
        ("Lượt 1 — shadow + tự đánh giá (75%)", 75, 500),
    ],
    "writing": [
        ("Lượt 1 — sắp xếp từ + câu hoàn chỉnh (60%)", 60, 660),
    ],
    "assessment": [
        ("Lượt 1 — kiểm tra tổng hợp (92%)", 92, 900),
    ],
}

LESSON_EMOJIS = {
    "vocabulary": "📚",
    "grammar":    "📝",
    "reading":    "📖",
    "listening":  "🎧",
    "speaking":   "🗣️",
    "writing":    "✍️",
    "assessment": "🎯",
}


class Command(BaseCommand):
    help = "Mô phỏng luồng học 7 bài học: enroll → complete → score → unlock → summary"

    def add_arguments(self, parser):
        parser.add_argument("--chapter", default="Giới thiệu bản thân",
                            help="Tên chương cần mô phỏng (default: 'Giới thiệu bản thân')")
        parser.add_argument("--cleanup", action="store_true",
                            help="Xoá dữ liệu test của user mô phỏng trước khi chạy")
        parser.add_argument("--course", default="Nền tảng tiếng Anh",
                            help="Tên khoá học (default: 'Nền tảng tiếng Anh')")

    # ──────────────────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        chapter_name = options["chapter"]
        course_name  = options["course"]

        print(f"\n{SEP}")
        print(f"  {BOLD}ENGLISH STUDY — SIMULATE 7-LESSON FLOW{RESET}")
        print(f"  Khoá học : {course_name}")
        print(f"  Chương   : {chapter_name}")
        print(f"  Thời gian: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{SEP}")

        # ── Step 1: resolve course + chapter + lessons ────────────────────────
        head("BƯỚC 1 — Nạp dữ liệu khoá học")
        course, chapter, lessons = self._load_curriculum(course_name, chapter_name)
        if not lessons:
            return

        # ── Step 2: create/get test user ─────────────────────────────────────
        head("BƯỚC 2 — Chuẩn bị học viên test")
        student = self._get_or_create_student()

        if options["cleanup"]:
            self._cleanup(student, course)

        # ── Step 3: enroll student ────────────────────────────────────────────
        head("BƯỚC 3 — Đăng ký khoá học")
        enrollment = self._enroll(student, course, lessons)

        # ── Step 4: simulate each lesson ─────────────────────────────────────
        head("BƯỚC 4 — Mô phỏng hoàn thành 7 bài học")
        results = []
        total_xp = 0

        for lesson in lessons:
            r = self._simulate_lesson(student, lesson, course)
            results.append(r)
            total_xp += r["xp_earned"]

        # ── Step 5: final report ──────────────────────────────────────────────
        head("BƯỚC 5 — BÁO CÁO TỔNG HỢP")
        self._print_report(student, course, chapter, lessons, results, total_xp)

        print(f"\n{SEP}")
        print(f"  {GREEN}{BOLD}SIMULATION HOÀN TẤT{RESET}")
        print(f"{SEP}\n")

    # ──────────────────────────────────────────────────────────────────────────
    # Curriculum loading
    # ──────────────────────────────────────────────────────────────────────────
    def _load_curriculum(self, course_name, chapter_name):
        from apps.curriculum.models import Course, Chapter, Lesson, LessonContent

        try:
            course = Course.objects.get(title=course_name)
            ok(f"Khoá học: [{course.id}] {course.title}")
        except Course.DoesNotExist:
            fail(f"Khoá học '{course_name}' không tồn tại. Hãy chạy seed_courses trước.")
            return None, None, []
        except Course.MultipleObjectsReturned:
            course = Course.objects.filter(title=course_name).first()
            warn(f"Nhiều khoá học cùng tên — dùng id={course.id}")

        try:
            chapter = Chapter.objects.get(course=course, title__icontains=chapter_name)
            ok(f"Chương   : [{chapter.id}] {chapter.title}  (passing_score={chapter.passing_score})")
        except Chapter.DoesNotExist:
            fail(f"Chương '{chapter_name}' không tồn tại trong khoá học này.")
            return course, None, []
        except Chapter.MultipleObjectsReturned:
            chapter = Chapter.objects.filter(course=course, title__icontains=chapter_name).first()
            warn(f"Nhiều chương cùng tên — dùng id={chapter.id}")

        lessons = list(Lesson.objects.filter(chapter=chapter, is_active=True).order_by("order"))
        ok(f"Bài học  : {len(lessons)} bài học")

        if len(lessons) != 7:
            warn(f"Mong đợi 7 bài học, tìm thấy {len(lessons)}. Tiếp tục mô phỏng {len(lessons)} bài.")

        # Check LessonContent for each lesson
        subhead("Kiểm tra LessonContent")
        content_issues = []
        for l in lessons:
            try:
                lc = l.content  # related_name='content' on OneToOneField
                fields = {
                    "listening_content": bool(lc.listening_content),
                    "speaking_content":  bool(lc.speaking_content),
                    "writing_content":   bool(lc.writing_content),
                    "reading_passage":   bool(lc.reading_passage),
                    "grammar_sections":  bool(lc.grammar_sections),
                }
                emoji = LESSON_EMOJIS.get(l.lesson_type, "📄")
                relevant = {
                    "listening": "listening_content",
                    "speaking":  "speaking_content",
                    "writing":   "writing_content",
                    "reading":   "reading_passage",
                    "grammar":   "grammar_sections",
                }
                key = relevant.get(l.lesson_type)
                if key and not fields[key]:
                    warn(f"L{l.order} {emoji} {l.lesson_type:12s} — {key} rỗng (placeholder content)")
                    content_issues.append(l)
                else:
                    has_new = lc.listening_content or lc.speaking_content or lc.writing_content
                    ok(f"L{l.order} {emoji} {l.lesson_type:12s} — content OK  [new_fields={'✓' if has_new else '—'}]")
            except Exception:
                warn(f"L{l.order} ({l.lesson_type}) — LessonContent không tồn tại (placeholder)")
                content_issues.append(l)

        if content_issues:
            warn(f"{len(content_issues)} bài có content placeholder — mô phỏng vẫn tiếp tục")

        return course, chapter, lessons

    # ──────────────────────────────────────────────────────────────────────────
    # Student creation
    # ──────────────────────────────────────────────────────────────────────────
    def _get_or_create_student(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        email = "sim_7lessons@test.local"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": "sim_7lessons",
                "first_name": "Sim",
                "last_name": "Student",
                "is_active": True,
            },
        )
        if created:
            user.set_unusable_password()
            user.save()
            ok(f"Tạo học viên test: {user.email}  (id={user.id})")
        else:
            ok(f"Dùng học viên test: {user.email}  (id={user.id})")
        return user

    # ──────────────────────────────────────────────────────────────────────────
    # Enrollment
    # ──────────────────────────────────────────────────────────────────────────
    def _enroll(self, student, course, lessons):
        from apps.progress.models import UserEnrollment, LessonProgress

        enrollment, created = UserEnrollment.objects.get_or_create(
            user=student, course=course,
            defaults={"status": "active", "progress_percent": 0, "is_deleted": False},
        )
        if enrollment.is_deleted:
            enrollment.is_deleted = False
            enrollment.status = "active"
            enrollment.progress_percent = 0
            enrollment.save()

        if created:
            ok(f"Đăng ký mới: enrollment id={enrollment.id}")
        else:
            ok(f"Đăng ký hiện tại: enrollment id={enrollment.id}  progress={enrollment.progress_percent}%")

        # Unlock first lesson if not yet done
        first_lesson = lessons[0]
        lp, lp_created = LessonProgress.objects.get_or_create(
            user=student, lesson=first_lesson,
            defaults={"status": "available"},
        )
        if lp_created or lp.status == "locked":
            lp.status = "available"
            lp.save()
            ok(f"Mở khoá bài đầu tiên: L{first_lesson.order} '{first_lesson.title}'")
        else:
            ok(f"Bài đầu tiên đã mở: L{first_lesson.order} status={lp.status}")

        return enrollment

    # ──────────────────────────────────────────────────────────────────────────
    # Core lesson simulation
    # ──────────────────────────────────────────────────────────────────────────
    def _simulate_lesson(self, student, lesson, course):
        from apps.progress.models import LessonProgress
        from apps.progress.views import _unlock_next_lesson, _recalc_enrollment_progress
        from apps.progress.grading import _check_chapter_completion

        emoji = LESSON_EMOJIS.get(lesson.lesson_type, "📄")
        subhead(f"L{lesson.order} {emoji}  [{lesson.lesson_type.upper()}]  '{lesson.title}'  (id={lesson.id})")

        # ── Pre-check: status ─────────────────────────────────────────────────
        lp_pre = LessonProgress.objects.filter(user=student, lesson=lesson).first()
        pre_status = lp_pre.status if lp_pre else "locked"

        if pre_status == "locked":
            fail(f"TRẠNG THÁI TRƯỚC: {pre_status} — lỗi logic! Bài này phải được mở khoá trước.")
        else:
            ok(f"Trạng thái trước  : {pre_status}")

        xp_earned = 0
        best_score_before = lp_pre.best_score if lp_pre else None
        attempt_results = []

        # ── Run attempt(s) ────────────────────────────────────────────────────
        scenarios = SCENARIOS.get(lesson.lesson_type, [("Lượt 1", None, 300)])

        for label, score, time_s in scenarios:
            dim(f"  → {label}")
            result = self._do_complete(student, lesson, score, time_s, course)
            xp_earned += result["xp"]
            attempt_results.append(result)

            status_sym = f"{GREEN}PASS{RESET}" if (score is None or score >= 60) \
                else f"{RED}FAIL{RESET}" if score < 60 \
                else f"{YELLOW}?{RESET}"
            score_str = f"{score}%" if score is not None else "N/A (tự học)"
            info(f"  Điểm: {score_str}  |  XP: +{result['xp']}  |  "
                 f"best_score: {result['best']}  |  status: {status_sym}")

        # ── Post-check: status + unlock ───────────────────────────────────────
        lp_post = LessonProgress.objects.filter(user=student, lesson=lesson).first()
        post_status = lp_post.status if lp_post else "?"
        ok(f"Trạng thái sau    : {post_status}  (attempts={lp_post.attempts_count if lp_post else '?'})")

        # Check unlock of next lesson
        next_lp = LessonProgress.objects.filter(
            user=student, lesson__chapter=lesson.chapter,
            lesson__order=lesson.order + 1
        ).first()
        if next_lp:
            if next_lp.status in ("available", "completed"):
                ok(f"Mở khoá bài tiếp  : L{lesson.order + 1} → {next_lp.status}")
            else:
                fail(f"Bài tiếp (L{lesson.order + 1}) vẫn bị khoá — status={next_lp.status}")
        else:
            if lesson.order == len(list(lesson.chapter.lessons.filter(is_active=True))):
                ok(f"Không có bài tiếp — đây là bài cuối chương")
            else:
                warn(f"Bài L{lesson.order + 1} chưa có LessonProgress record")

        # Chapter completion check (only on last lesson)
        chapter_info = _check_chapter_completion(student, lesson)
        chapter_done = chapter_info.get("chapter_completed", False)

        # Enrollment progress
        from apps.progress.models import UserEnrollment
        enrollment = UserEnrollment.objects.filter(
            user=student, course=course, is_deleted=False
        ).first()
        progress_pct = float(enrollment.progress_percent) if enrollment else 0.0

        info(f"Tiến độ khoá học  : {progress_pct:.1f}%")
        if chapter_done:
            avg = chapter_info.get("chapter_avg_score", 0)
            ok(f"🏆 CHƯƠNG HOÀN TẤT sau bài {lesson.order}! (avg_score={avg})")

        return {
            "lesson_order": lesson.order,
            "lesson_type":  lesson.lesson_type,
            "lesson_title": lesson.title,
            "pre_status":   pre_status,
            "post_status":  post_status,
            "attempts":     len(scenarios),
            "best_score":   lp_post.best_score if lp_post else None,
            "xp_earned":    xp_earned,
            "progress_pct": progress_pct,
            "chapter_done": chapter_done,
            "unlock_ok":    next_lp is not None and next_lp.status in ("available", "completed")
                            if lesson.order < 7 else True,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Single attempt: calls same logic as MarkLessonCompleteView
    # ──────────────────────────────────────────────────────────────────────────
    @transaction.atomic
    def _do_complete(self, student, lesson, score, time_s, course):
        from apps.progress.models import LessonProgress, UserEnrollment
        from apps.progress.views import _unlock_next_lesson, _recalc_enrollment_progress
        from apps.progress.grading import _check_chapter_completion

        lp, _ = LessonProgress.objects.get_or_create(
            user=student, lesson=lesson,
            defaults={"status": "available"},
        )
        lp.status         = "completed"
        lp.attempts_count = (lp.attempts_count or 0) + 1
        lp.time_spent_seconds = (lp.time_spent_seconds or 0) + int(time_s)
        lp.completed_at   = timezone.now()

        if score is not None:
            sc = int(score)
            if lp.best_score is None or sc > lp.best_score:
                lp.best_score = sc
        lp.save()

        # Unlock next lesson
        _unlock_next_lesson(student, lesson)

        # Recalculate enrollment
        _recalc_enrollment_progress(student, course)

        # XP logic (mirrors MarkLessonCompleteView)
        xp = 0
        try:
            from apps.gamification.models import XPLog
            xp = 10
            if lp.best_score is not None and lp.best_score >= 80:
                xp += 50
            XPLog.objects.create(
                user=student,
                source="exercise_complete",
                xp_amount=xp,
                reference_id=lesson.pk,
                reference_type="lesson",
                note=f"[SIM] Hoàn thành bài: {lesson.title}",
            )
        except Exception as e:
            warn(f"XP award skipped: {e}")

        return {"xp": xp, "best": lp.best_score}

    # ──────────────────────────────────────────────────────────────────────────
    # Cleanup
    # ──────────────────────────────────────────────────────────────────────────
    def _cleanup(self, student, course):
        from apps.progress.models import LessonProgress, UserEnrollment
        from apps.gamification.models import XPLog

        deleted_lp, _ = LessonProgress.objects.filter(
            user=student, lesson__chapter__course=course
        ).delete()
        deleted_enr, _ = UserEnrollment.objects.filter(
            user=student, course=course
        ).delete()
        deleted_xp, _ = XPLog.objects.filter(
            user=student, reference_type="lesson", note__startswith="[SIM]"
        ).delete()
        warn(f"Cleanup: xoá {deleted_lp} LessonProgress, {deleted_enr} Enrollment, {deleted_xp} XPLog")

    # ──────────────────────────────────────────────────────────────────────────
    # Final report
    # ──────────────────────────────────────────────────────────────────────────
    def _print_report(self, student, course, chapter, lessons, results, total_xp):
        from apps.progress.models import LessonProgress, UserEnrollment

        # XP total from DB
        try:
            from apps.gamification.models import XPLog
            db_xp = XPLog.objects.filter(
                user=student, reference_type="lesson", note__startswith="[SIM]"
            ).aggregate(s=__import__("django.db.models", fromlist=["Sum"]).Sum("xp_amount"))["s"] or 0
        except Exception:
            db_xp = total_xp

        enrollment = UserEnrollment.objects.filter(
            user=student, course=course, is_deleted=False
        ).first()

        print()
        print(f"  {BOLD}{'Bài':>3}  {'Type':<12}  {'Trạng thái trước':>18}  {'best_score':>10}  {'XP':>5}  {'Tiến độ':>8}  {'Unlock':>6}{RESET}")
        print(f"  {SEP2}")

        all_pass = True
        for r in results:
            emoji    = LESSON_EMOJIS.get(r["lesson_type"], "📄")
            unlock   = f"{GREEN}OK{RESET}" if r.get("unlock_ok", True) else f"{RED}FAIL{RESET}"
            pre      = r["pre_status"]
            pre_col  = GREEN if pre == "available" else RED
            score_s  = f"{r['best_score']}%" if r['best_score'] is not None else "N/A"
            xp_s     = f"+{r['xp_earned']}"
            pct_s    = f"{r['progress_pct']:.1f}%"
            status_ok = r["pre_status"] == "available" and r["post_status"] == "completed"
            if not status_ok:
                all_pass = False

            print(
                f"  {emoji} L{r['lesson_order']}  {r['lesson_type']:<12}"
                f"  {pre_col}{pre:>18}{RESET}"
                f"  {score_s:>10}"
                f"  {CYAN}{xp_s:>5}{RESET}"
                f"  {pct_s:>8}"
                f"  {unlock}"
            )

        print(f"  {SEP2}")

        # Validation checks
        print(f"\n  {BOLD}Kiểm tra logic:{RESET}")

        checks = [
            ("7 bài học tồn tại", len(lessons) == 7),
            ("Bài 1 mở đầu (available)", results[0]["pre_status"] == "available"),
            ("Tất cả bài chuyển sang completed", all(r["post_status"] == "completed" for r in results)),
            ("Unlock tuần tự hoạt động", all(r.get("unlock_ok", True) for r in results[:-1])),
            ("best_score >= 60 cho bài có điểm",
                all(r["best_score"] >= 60 for r in results if r["best_score"] is not None)),
            ("XP được trao cho mỗi bài", all(r["xp_earned"] > 0 for r in results)),
            # 7 lessons / 84 total (12 chương × 7 bài) = 8.3%  → kiểm tra > 0 và tăng dần
            ("Tiến độ khoá học tăng sau mỗi bài (> 0)",
                all(results[i]["progress_pct"] > results[i-1]["progress_pct"] for i in range(1, len(results)))
                if len(results) > 1 else results[0]["progress_pct"] > 0 if results else False),
            ("Chương hoàn tất sau bài 7", results[-1].get("chapter_done", False) if results else False),
        ]

        for label, passed in checks:
            if passed:
                ok(label)
            else:
                fail(label)
                all_pass = False

        print()
        final_status = "completed" if enrollment and enrollment.status == "completed" else (
            enrollment.status if enrollment else "N/A"
        )
        print(f"  {BOLD}XP tổng kiếm được (mô phỏng) : {CYAN}{db_xp} XP{RESET}")
        print(f"  {BOLD}Tiến độ khoá học cuối         : {results[-1]['progress_pct']:.1f}%{RESET}")
        print(f"  {BOLD}Trạng thái enrollment         : {final_status}{RESET}")
        print()

        if all_pass:
            print(f"  {GREEN}{BOLD}✔ TẤT CẢ KIỂM TRA PASSED — Luồng 7 bài học hoạt động đúng!{RESET}")
        else:
            print(f"  {RED}{BOLD}✘ CÓ LỖI — Xem chi tiết ở trên.{RESET}")
