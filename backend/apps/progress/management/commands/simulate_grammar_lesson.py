"""
management command: simulate_grammar_lesson
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mô phỏng đầy đủ luồng Học viên học 1 bài Ngữ pháp A1:

  1. KẾT NỐI DB — Truy xuất GrammarTopic A1 từ DB (đã seed)
  2. HIỂN THỊ NỘI DUNG — Render topic + rules + examples
  3. SEED QUIZ — Tạo câu hỏi trắc nghiệm ngữ pháp (Question model)
  4. KỊCH BẢN A — Học viên trả lời ĐÚNG HẾT → PASS (score ≥ 60)
     → Bài kế tiếp mở khoá (status = available)
  5. KỊCH BẢN B — Học viên trả lời SAI HẾT → FAIL (score < 60)
     → Bài kế tiếp vẫn LOCKED, best_score được giữ nguyên
  6. KỊCH BẢN C — Học viên retry → PASS, tiến độ khoá học cập nhật
  7. BẢNG TỔNG KẾT — Điểm, trạng thái khoá/mở, % tiến độ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cách chạy:
    python manage.py simulate_grammar_lesson
    python manage.py simulate_grammar_lesson --cleanup
"""
import textwrap

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

SEP  = "═" * 70
SEP2 = "─" * 70
PASS_COLOR  = "\033[92m"
FAIL_COLOR  = "\033[91m"
INFO_COLOR  = "\033[94m"
WARN_COLOR  = "\033[93m"
BOLD        = "\033[1m"
RESET       = "\033[0m"

def ok(msg):    print(f"  {PASS_COLOR}✔  {msg}{RESET}")
def err(msg):   print(f"  {FAIL_COLOR}✘  {msg}{RESET}")
def info(msg):  print(f"  {INFO_COLOR}ℹ  {msg}{RESET}")
def warn(msg):  print(f"  {WARN_COLOR}⚠  {msg}{RESET}")
def head(msg):  print(f"\n{SEP}\n  {BOLD}{msg}{RESET}\n{SEP2}")
def sub(msg):   print(f"  {BOLD}{msg}{RESET}")


User = get_user_model()

PASSING_SCORE = 60
TEST_EMAIL    = "grammar_student@test.local"
TOPIC_INDEX   = 0   # pick the 1st A1 grammar topic (Present Simple of be: Form)


class Command(BaseCommand):
    help = "Simulate a student completing a Grammar A1 lesson end-to-end"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cleanup", action="store_true",
            help="Xoá dữ liệu test cũ trước khi chạy lại"
        )
        parser.add_argument(
            "--topic-order", type=int, default=1,
            help="Order của GrammarTopic A1 cần mô phỏng (default=1)"
        )

    # ──────────────────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        if options["cleanup"]:
            self._cleanup()

        print(f"\n{SEP}")
        print(f"  {BOLD}ENGLISH STUDY — MÔ PHỎNG: Học viên học Ngữ pháp A1{RESET}")
        print(SEP)

        topic_order = options["topic_order"]

        # ── Bước 1: Kết nối DB, truy xuất nội dung bài học ───────────────────
        head("BƯỚC 1 — KẾT NỐI DATABASE & TRUY XUẤT NỘI DUNG BÀI HỌC")
        data = self._load_grammar_content(topic_order)

        # ── Bước 2: Seed dữ liệu khoá học + học viên ─────────────────────────
        head("BƯỚC 2 — SEED DỮ LIỆU KHOÁ HỌC & QUIZ")
        seed = self._seed_curriculum_and_quiz(data["topic"])

        # ── Bước 3: Đăng ký học viên ─────────────────────────────────────────
        head("BƯỚC 3 — TẠO HỌC VIÊN & ĐĂNG KÝ KHOÁ HỌC")
        student, enrollment = self._setup_student(seed["course"])

        # ── Bước 4: KỊCH BẢN A — Đúng hết → PASS ────────────────────────────
        head("BƯỚC 4A — KỊCH BẢN A: Trả lời ĐÚNG HẾT → Kỳ vọng: PASS")
        self._run_quiz(
            student=student,
            lesson=seed["lesson_grammar"],
            topic_id=data["topic"].pk,
            questions=seed["questions"],
            scenario="ALL_CORRECT",
        )
        self._check_unlock_status(student, seed)

        # ── Bước 5: KỊCH BẢN B — Sai hết → FAIL ─────────────────────────────
        head("BƯỚC 4B — KỊCH BẢN B: Trả lời SAI HẾT → Kỳ vọng: FAIL")
        self._run_quiz(
            student=student,
            lesson=seed["lesson_grammar"],
            topic_id=data["topic"].pk,
            questions=seed["questions"],
            scenario="ALL_WRONG",
        )
        self._check_unlock_status(student, seed)

        # ── Bước 6: KỊCH BẢN C — Bài 2 PASS → Tiến độ tăng, Lesson 3 mở ─────
        head("BƯỚC 4C — KỊCH BẢN C: Bài học 2 (Grammar) PASS → Lesson 3 mở khoá")
        # Use seed["topic_2"] (the topic that actually has MC questions seeded)
        topic_2_id = seed["topic_2"].pk if seed.get("topic_2") else data["topic"].pk
        self._run_quiz(
            student=student,
            lesson=seed["lesson_grammar_2"],
            topic_id=topic_2_id,
            questions=seed["questions_2"],
            scenario="ALL_CORRECT",
        )
        self._check_unlock_status(student, seed)

        # ── Bước 7: Bảng Tổng kết ────────────────────────────────────────────
        head("BẢNG TỔNG KẾT")
        self._print_summary(student, seed, enrollment)

        print(f"\n{SEP}")
        print(f"  {PASS_COLOR}{BOLD}✔  SIMULATION HOÀN THÀNH THÀNH CÔNG{RESET}")
        print(SEP)

    # ══════════════════════════════════════════════════════════════════════════
    # BƯỚC 1 — Load grammar content from DB (verify DB connection)
    # ══════════════════════════════════════════════════════════════════════════
    def _load_grammar_content(self, topic_order: int) -> dict:
        from apps.grammar.models import GrammarExample, GrammarRule, GrammarTopic

        # -- Verify DB connection by counting topics
        total_a1 = GrammarTopic.objects.filter(level="A1").count()
        total_all = GrammarTopic.objects.count()
        info(f"DB kết nối OK  ▸  grammar_topic: {total_all} topics tổng ({total_a1} topic A1)")

        # -- Fetch the specific topic
        try:
            topic = GrammarTopic.objects.prefetch_related(
                "rules__examples"
            ).get(level="A1", order=topic_order)
        except GrammarTopic.DoesNotExist:
            # Fallback to first available A1 topic
            topic = GrammarTopic.objects.filter(level="A1").prefetch_related(
                "rules__examples"
            ).first()
            if not topic:
                self.stderr.write("FATAL: Không có GrammarTopic A1 nào trong DB. Hãy chạy seed_grammar trước.")
                raise SystemExit(1)
            warn(f"Không tìm thấy order={topic_order}, dùng topic đầu tiên: '{topic.title}'")

        rules = list(topic.rules.all())
        all_examples = list(GrammarExample.objects.filter(rule__topic=topic))

        ok(f"Truy xuất thành công: [{topic.level}] {topic.slug}")
        print()
        sub(f"  📌 GRAMMAR TOPIC: {topic.icon} {topic.title}")
        print(f"     Level: {topic.level}  |  Order: {topic.order}  |  ID: {topic.pk}")
        if topic.description:
            desc = textwrap.shorten(topic.description, width=100, placeholder="…")
            print(f"     Description: {desc}")
        print()
        print(f"     {BOLD}Quy tắc ({len(rules)} rules, {len(all_examples)} examples):{RESET}")
        for i, rule in enumerate(rules[:5], 1):
            formula_str = f"  Formula: {rule.formula}" if rule.formula else ""
            exc_str = "  ⚠ NGOẠI LỆ" if rule.is_exception else ""
            print(f"       [{i}] {rule.title}{formula_str}{exc_str}")
            exs = [e for e in all_examples if e.rule_id == rule.pk][:2]
            for ex in exs:
                trans = f"  → {ex.translation}" if ex.translation else ""
                print(f"            EX: {ex.sentence[:80]}{trans}")
        if len(rules) > 5:
            print(f"       … và {len(rules) - 5} rules khác")

        # Also fetch a second topic for scenario C
        topic_2 = (
            GrammarTopic.objects.filter(level="A1", order__gt=topic.order)
            .prefetch_related("rules__examples")
            .first()
        )
        if topic_2:
            info(f"Topic 2 cho Kịch bản C: [{topic_2.order}] {topic_2.title}")

        return {"topic": topic, "rules": rules, "examples": all_examples, "topic_2": topic_2}

    # ══════════════════════════════════════════════════════════════════════════
    # BƯỚC 2 — Seed curriculum data + grammar quiz questions
    # ══════════════════════════════════════════════════════════════════════════
    @transaction.atomic
    def _seed_curriculum_and_quiz(self, topic) -> dict:
        from apps.curriculum.models import CEFRLevel, Chapter, Course, Lesson, UnlockRule
        from apps.exercises.models import Question
        from apps.grammar.models import GrammarRule, GrammarTopic as GT

        # -- CEFRLevel A1
        level, _ = CEFRLevel.objects.get_or_create(
            code="A1",
            defaults={"name": "Beginner", "name_vi": "Sơ cấp", "order": 1},
        )
        ok(f"CEFRLevel: {level.code} — {level.name_vi}")

        # -- Course
        course, created = Course.objects.get_or_create(
            slug="a1-grammar-course-sim",
            defaults={
                "level": level,
                "title": "[SIM] A1 Grammar Course",
                "description": "Simulation test course cho ngữ pháp A1",
                "order": 99,
                "is_premium": False,
            },
        )
        ok(f"Course: {course.title} {'(MỚI)' if created else '(đã có)'}")

        # -- Chapter
        chapter, _ = Chapter.objects.get_or_create(
            course=course, order=1,
            defaults={
                "title": "Chương 1 — Present Tenses",
                "description": "Thì hiện tại",
                "passing_score": PASSING_SCORE,
            },
        )
        ok(f"Chapter: {chapter.title}  (passing_score={chapter.passing_score})")

        # -- Lesson 1: grammar bài 1 (linked to topic)
        lesson_1, _ = Lesson.objects.get_or_create(
            chapter=chapter, order=1,
            defaults={
                "title": f"[SIM] {topic.title}",
                "lesson_type": "grammar",
                "estimated_minutes": 15,
            },
        )
        # Link GrammarTopic → Lesson (OneToOneField)
        if topic.lesson_id != lesson_1.pk:
            topic.lesson = lesson_1
            topic.save(update_fields=["lesson"])
        ok(f"Lesson 1 (grammar): '{lesson_1.title}'  id={lesson_1.pk}")

        # -- Find topic 2: the next A1 topic that actually has rules with examples
        gt2 = (
            GT.objects.filter(level="A1", order__gt=topic.order)
            .filter(rules__examples__isnull=False)
            .distinct()
            .prefetch_related("rules__examples")
            .first()
        )
        if not gt2:
            # fallback: any next topic
            gt2 = GT.objects.filter(level="A1", order__gt=topic.order).first()

        lesson_2, _ = Lesson.objects.get_or_create(
            chapter=chapter, order=2,
            defaults={
                "title": f"[SIM] {gt2.title}" if gt2 else "[SIM] Grammar Bài 2",
                "lesson_type": "grammar",
                "estimated_minutes": 15,
            },
        )
        if gt2 and gt2.lesson_id != lesson_2.pk:
            gt2.lesson = lesson_2
            gt2.save(update_fields=["lesson"])
        ok(f"Lesson 2 (grammar, locked): '{lesson_2.title}'  id={lesson_2.pk}")

        # -- Lesson 3: locked assessment
        lesson_3, _ = Lesson.objects.get_or_create(
            chapter=chapter, order=3,
            defaults={
                "title": "[SIM] Kiểm tra Chương 1",
                "lesson_type": "assessment",
                "estimated_minutes": 20,
            },
        )
        ok(f"Lesson 3 (assessment): '{lesson_3.title}'  id={lesson_3.pk}")

        # -- Create UnlockRules: L1→L2, L2→L3
        ur1, _ = UnlockRule.objects.get_or_create(
            lesson=lesson_2, required_lesson=lesson_1,
            defaults={"min_score": PASSING_SCORE},
        )
        ok(f"UnlockRule: Lesson 2 được mở khi Lesson 1 đạt ≥ {ur1.min_score}%")
        ur2, _ = UnlockRule.objects.get_or_create(
            lesson=lesson_3, required_lesson=lesson_2,
            defaults={"min_score": PASSING_SCORE},
        )
        ok(f"UnlockRule: Lesson 3 được mở khi Lesson 2 đạt ≥ {ur2.min_score}%")

        # ── grammar quiz questions cho Lesson 1 ──────────────────────────────
        print()
        info("Tạo câu hỏi trắc nghiệm ngữ pháp cho Lesson 1...")
        questions_1 = self._seed_grammar_questions(topic.pk, count=5)
        ok(f"Đã tạo {len(questions_1)} câu hỏi MC cho topic '{topic.title}'")

        # ── grammar quiz questions cho Lesson 2 ──────────────────────────────
        topic_for_l2 = gt2 or topic
        questions_2 = self._seed_grammar_questions(topic_for_l2.pk, count=5, offset=5)
        ok(f"Đã tạo {len(questions_2)} câu hỏi MC cho topic '{topic_for_l2.title}'")

        for q in questions_1[:3]:
            info(f"  Q{q.order}: [{q.question_type}] {q.question_text[:60]}")
            info(f"        Đáp án đúng: {q.correct_answers_json[0][:60]}")

        return {
            "course": course,
            "chapter": chapter,
            "lesson_grammar": lesson_1,
            "lesson_grammar_2": lesson_2,
            "lesson_locked": lesson_3,
            "questions": questions_1,
            "questions_2": questions_2,
            "topic_2": gt2,   # the topic actually used for Lesson 2 quiz
        }

    def _seed_grammar_questions(self, topic_id: int, count: int = 5, offset: int = 0):
        """
        Generate MC grammar questions from GrammarRule + GrammarExample data.
        exercise_type='grammar', exercise_id=topic_id.
        Each question: "Chọn câu đúng ngữ pháp theo quy tắc: [rule_title]"
        Correct answer: first example sentence from the rule.
        """
        from apps.exercises.models import Question
        from apps.grammar.models import GrammarExample, GrammarRule

        rules = list(
            GrammarRule.objects.filter(topic_id=topic_id)
            .prefetch_related("examples")
            .order_by("order")
        )
        questions = []
        order = offset + 1

        for rule in rules:
            if len(questions) >= count:
                break
            examples = list(rule.examples.all())
            if not examples:
                continue

            correct_example = examples[0].sentence[:200]
            # Build distractors from other examples (other rules)
            wrong_examples = list(
                GrammarExample.objects.filter(rule__topic_id=topic_id)
                .exclude(rule=rule)
                .values_list("sentence", flat=True)[:3]
            )
            # If not enough distractors, use modified wrong forms
            while len(wrong_examples) < 3:
                wrong_examples.append(f"[Dạng sai] {correct_example.lower()[:60]}...")

            q, created = Question.objects.get_or_create(
                exercise_type="grammar",
                exercise_id=topic_id,
                order=order,
                defaults={
                    "question_type": "mc",
                    "question_text": (
                        f"Chọn câu đúng ngữ pháp theo quy tắc:\n"
                        f"'{rule.title}'"
                        + (f"\n📐 {rule.formula}" if rule.formula else "")
                    ),
                    "correct_answers_json": [correct_example],
                    "explanation": rule.explanation[:300] if rule.explanation else "",
                    "points": 1,
                },
            )
            questions.append(q)
            order += 1

        return questions

    # ══════════════════════════════════════════════════════════════════════════
    # BƯỚC 3 — Setup student + enrollment
    # ══════════════════════════════════════════════════════════════════════════
    @transaction.atomic
    def _setup_student(self, course):
        from apps.progress.models import LessonProgress, UserEnrollment

        user, created = User.objects.get_or_create(
            email=TEST_EMAIL,
            defaults={
                "username": "grammar_student_sim",
                "first_name": "Học",
                "last_name": "Sinh Test",
                "is_active": True,
            },
        )
        if created:
            user.set_password("TestPass123!")
            user.save(update_fields=["password"])
            ok(f"Tạo học viên: {user.email} (MỚI)")
        else:
            ok(f"Tạo học viên: {user.email} (đã có)")

        enrollment, _ = UserEnrollment.objects.get_or_create(
            user=user, course=course,
            defaults={"status": "active", "progress_percent": 0},
        )
        info(f"Đăng ký khoá học: '{course.title}'  progress={enrollment.progress_percent}%")

        return user, enrollment

    # ══════════════════════════════════════════════════════════════════════════
    # BƯỚC 4 — Run quiz scenarios
    # ══════════════════════════════════════════════════════════════════════════
    def _run_quiz(self, student, lesson, topic_id, questions, scenario: str):
        from apps.progress.grading import AutoGrader

        if not questions:
            warn(f"[{scenario}] Không có câu hỏi để chấm. Bỏ qua kịch bản này.")
            return

        total = len(questions)
        user_answers = {}

        if scenario == "ALL_CORRECT":
            for q in questions:
                user_answers[str(q.pk)] = q.correct_answers_json[0]
            sub(f"[{scenario}] Học viên trả lời ĐÚNG HẾT {total}/{total} câu")

        elif scenario == "ALL_WRONG":
            for q in questions:
                user_answers[str(q.pk)] = "__SAI__"
            sub(f"[{scenario}] Học viên trả lời SAI HẾT {total}/{total} câu")

        elif scenario == "PARTIAL":
            for i, q in enumerate(questions):
                if i < total * 0.6:
                    user_answers[str(q.pk)] = q.correct_answers_json[0]
                else:
                    user_answers[str(q.pk)] = "__SAI__"
            correct = int(total * 0.6)
            sub(f"[{scenario}] Học viên trả lời ĐÚNG {correct}/{total} câu")

        result = AutoGrader.grade_grammar(
            user=student,
            lesson=lesson,
            topic_id=topic_id,
            user_answers=user_answers,
            time_spent_seconds=240,
        )

        score = float(result.score)
        passed = result.passed
        status_str = f"{PASS_COLOR}PASS ✔{RESET}" if passed else f"{FAIL_COLOR}FAIL ✘{RESET}"
        print(f"     ▶  Điểm: {score:.0f}/100  |  Kết quả: {status_str}")
        print(f"     ▶  passing_score = {PASSING_SCORE}  |  Thời gian: 240 giây")

        # Show per-question detail
        print()
        info("Chi tiết từng câu hỏi:")
        for row in result.detail_json:
            icon = f"{PASS_COLOR}✔{RESET}" if row["is_correct"] else f"{FAIL_COLOR}✘{RESET}"
            q_text = str(row.get("question_text", f"Q#{row['question_id']}"))[:55]
            print(
                f"     {icon} Q{row['question_id']}:  "
                f"điểm={row['points_awarded']}/{row['points_possible']}  "
            )

    # ══════════════════════════════════════════════════════════════════════════
    # Kiểm tra trạng thái khoá/mở bài học
    # ══════════════════════════════════════════════════════════════════════════
    def _check_unlock_status(self, student, seed: dict):
        from apps.progress.models import LessonProgress, UserEnrollment

        lessons = [
            ("Bài 1 Grammar", seed["lesson_grammar"]),
            ("Bài 2 Grammar", seed["lesson_grammar_2"]),
            ("Bài 3 Assessment", seed["lesson_locked"]),
        ]
        print()
        sub("  Trạng thái khoá/mở bài học:")
        for name, lesson in lessons:
            try:
                lp = LessonProgress.objects.get(user=student, lesson=lesson)
                status = lp.status
                score_str = f"best_score={lp.best_score}  attempts={lp.attempts_count}"
            except LessonProgress.DoesNotExist:
                status = "locked"
                score_str = "(chưa có record)"

            status_color = {
                "completed": PASS_COLOR,
                "available": INFO_COLOR,
                "in_progress": WARN_COLOR,
                "locked": FAIL_COLOR,
            }.get(status, RESET)
            icon = {"completed": "✔", "available": "🔓", "in_progress": "▶", "locked": "🔒"}.get(status, "?")
            print(f"     {status_color}{icon}  {name}: status={status}  {score_str}{RESET}")

        # Enrollment progress
        try:
            enrollment = UserEnrollment.objects.get(
                user=student, course=seed["course"], is_deleted=False
            )
            enrollment.refresh_from_db()
            print(f"\n     📊 Tiến độ khoá học: {enrollment.progress_percent}%")
        except UserEnrollment.DoesNotExist:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    # Bảng Tổng kết
    # ══════════════════════════════════════════════════════════════════════════
    def _print_summary(self, student, seed, enrollment):
        from apps.progress.models import CumulativeScore, ExerciseResult, LessonProgress
        from apps.curriculum.models import CEFRLevel

        print()
        sub("  ── KẾT QUẢ HỌC TẬP ──────────────────────────────────────────")

        # All exercise results for this student
        results = ExerciseResult.objects.filter(
            user=student, exercise_type="grammar"
        ).order_by("id")

        print(f"     Tổng số lần nộp bài ngữ pháp: {results.count()}")
        for r in results:
            passed_str = f"{PASS_COLOR}PASS{RESET}" if r.passed else f"{FAIL_COLOR}FAIL{RESET}"
            print(f"       #{r.pk}: score={r.score}  {passed_str}  exercise_id={r.exercise_id}")

        # LessonProgress summary
        print()
        sub("  ── TRẠNG THÁI BÀI HỌC ──────────────────────────────────────")
        for lp in LessonProgress.objects.filter(user=student).select_related("lesson"):
            icon = {"completed": "✔", "available": "🔓", "in_progress": "▶", "locked": "🔒"}.get(lp.status, "?")
            print(f"     {icon}  Lesson {lp.lesson.order}: '{lp.lesson.title[:45]}'  "
                  f"status={lp.status}  best_score={lp.best_score}  attempts={lp.attempts_count}")

        # CumulativeScore
        print()
        sub("  ── ĐIỂM TỔNG HỢP (CumulativeScore) ────────────────────────")
        try:
            level = CEFRLevel.objects.get(code="A1")
            cs = CumulativeScore.objects.get(user=student, level=level)
            print(f"     reading_avg (grammar → reading column): {cs.reading_avg}")
            print(f"     overall_avg: {cs.overall_avg}")
            print(f"     total_exercises_done: {cs.total_exercises_done}")
        except Exception:
            warn("Chưa có CumulativeScore cho học viên này.")

        # Enrollment
        enrollment.refresh_from_db()
        print()
        sub("  ── TIẾN ĐỘ KHOÁ HỌC ─────────────────────────────────────")
        print(f"     Khoá học: '{seed['course'].title}'")
        print(f"     progress_percent: {enrollment.progress_percent}%")
        print(f"     status: {enrollment.status}")

    # ══════════════════════════════════════════════════════════════════════════
    # Cleanup
    # ══════════════════════════════════════════════════════════════════════════
    @transaction.atomic
    def _cleanup(self):
        from apps.curriculum.models import Course
        from apps.progress.models import (CumulativeScore, ExerciseResult,
                                          LessonProgress, UserEnrollment)

        print(f"\n{WARN_COLOR}⚠  Đang xoá dữ liệu simulation cũ...{RESET}")
        try:
            student = User.objects.get(email=TEST_EMAIL)
            ExerciseResult.objects.filter(user=student).delete()
            LessonProgress.objects.filter(user=student).delete()
            CumulativeScore.objects.filter(user=student).delete()
            UserEnrollment.objects.filter(user=student).delete()
            student.delete()
            print(f"  {WARN_COLOR}Đã xoá user {TEST_EMAIL}{RESET}")
        except User.DoesNotExist:
            pass
        Course.objects.filter(slug="a1-grammar-course-sim").delete()
        print(f"  {WARN_COLOR}Đã xoá course a1-grammar-course-sim{RESET}")
