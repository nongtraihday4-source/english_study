"""
management command: simulate_submission
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mô phỏng toàn bộ luồng học viên nộp bài Listening & Reading:
  1. Seed dữ liệu: CEFR A1, 1 khoá học, 1 chương, 3 bài học
     (Lesson 1 = Listening, Lesson 2 = Reading, Lesson 3 = Locked)
  2. Tạo học viên test + đăng ký khoá
  3. Kịch bản A — nộp Listening với đáp án ĐÚNG HẾT → PASS (>= 60)
     → Mở khoá Lesson 3
  4. Kịch bản B — nộp lại Listening với đáp án SAI HẾT → FAIL
  5. Kịch bản C — nộp Reading với đáp án hỗn hợp → PASS
  6. In bảng tổng kết: điểm, trạng thái mở khoá, % tiến độ khoá học
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import textwrap
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

SEP  = "═" * 70
SEP2 = "─" * 70
PASS_COLOR  = "\033[92m"   # green
FAIL_COLOR  = "\033[91m"   # red
INFO_COLOR  = "\033[94m"   # blue
WARN_COLOR  = "\033[93m"   # yellow
RESET       = "\033[0m"


def ok(msg):   print(f"  {PASS_COLOR}✔  {msg}{RESET}")
def err(msg):  print(f"  {FAIL_COLOR}✘  {msg}{RESET}")
def info(msg): print(f"  {INFO_COLOR}ℹ  {msg}{RESET}")
def warn(msg): print(f"  {WARN_COLOR}⚠  {msg}{RESET}")
def head(msg): print(f"\n{SEP}\n  {msg}\n{SEP2}")


class Command(BaseCommand):
    help = "Simulate a student submitting Listening & Reading exercises end-to-end"

    def add_arguments(self, parser):
        parser.add_argument("--cleanup", action="store_true",
                            help="Xoá toàn bộ dữ liệu test trước khi chạy")

    # ──────────────────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        if options["cleanup"]:
            self._cleanup()

        print(f"\n{SEP}")
        print("  ENGLISH STUDY — SIMULATION: Student Submission Flow  ")
        print(f"{SEP}")

        # Step 1: Seed
        head("BƯỚC 1 — Seed dữ liệu từ thư mục 'source' (mô phỏng)")
        data = self._seed_data()

        # Step 2: Enroll student
        head("BƯỚC 2 — Tạo học viên + đăng ký khoá học")
        student, enrollment = self._setup_student(data["course"])

        # Step 3: Scenario A — Listening ALL CORRECT
        head("BƯỚC 3A — Nộp bài LISTENING (đáp án ĐÚNG HẾT)")
        self._run_listening(
            student=student,
            lesson=data["lesson_listening"],
            exercise=data["listening_ex"],
            questions=data["listening_qs"],
            scenario="ALL_CORRECT",
        )

        # Check unlock after listening pass
        self._check_unlock_status(student, data)

        # Step 4: Scenario B — Listening ALL WRONG
        head("BƯỚC 3B — Nộp lại LISTENING (đáp án SAI HẾT)")
        self._run_listening(
            student=student,
            lesson=data["lesson_listening"],
            exercise=data["listening_ex"],
            questions=data["listening_qs"],
            scenario="ALL_WRONG",
        )

        # Step 5: Scenario C — Reading MIXED (70% correct → PASS)
        head("BƯỚC 4 — Nộp bài READING (đáp án HỖN HỢP = 70% đúng)")
        self._run_reading(
            student=student,
            lesson=data["lesson_reading"],
            exercise=data["reading_ex"],
            questions=data["reading_qs"],
        )

        # Final summary
        head("KẾT QUẢ TỔNG QUÁT")
        self._print_summary(student, data)

        print(f"\n{SEP}")
        print("  SIMULATION COMPLETE — Xem chi tiết log trong logs/grading.log")
        print(f"{SEP}\n")

    # ──────────────────────────────────────────────────────────────────────────
    # DATA SEEDING
    # ──────────────────────────────────────────────────────────────────────────
    @transaction.atomic
    def _seed_data(self):
        from apps.curriculum.models import CEFRLevel, Course, Chapter, Lesson, LessonExercise, UnlockRule
        from apps.exercises.models import ListeningExercise, ReadingExercise, Question, QuestionOption

        info("Kiểm tra/tạo CEFRLevel A1...")
        level, _ = CEFRLevel.objects.get_or_create(
            code="A1",
            defaults={"name": "Beginner", "name_vi": "Sơ cấp", "order": 1},
        )
        ok(f"CEFRLevel: {level}")

        info("Tạo khoá học A1 — Everyday English...")
        course, created = Course.objects.get_or_create(
            slug="a1-everyday-english",
            defaults={
                "level": level,
                "title": "Everyday English A1",
                "description": "Khoá học tiếng Anh giao tiếp cơ bản A1",
                "order": 1,
                "is_premium": False,
                "is_active": True,
            },
        )
        if not created:
            ok(f"Khoá học đã tồn tại: {course.title}")
        else:
            ok(f"Tạo mới khoá học: {course.title}")

        info("Tạo chương 1: Greetings & Introductions...")
        chapter, _ = Chapter.objects.get_or_create(
            course=course,
            order=1,
            defaults={
                "title": "Greetings & Introductions",
                "description": "Chào hỏi và giới thiệu bản thân",
                "passing_score": 60,
            },
        )
        ok(f"Chapter: {chapter}")

        # ── Lesson 1: Listening ─────────────────────────────────────────────
        info("Tạo Lesson 1: Listening — A Morning Conversation...")
        lesson_listening, _ = Lesson.objects.get_or_create(
            chapter=chapter,
            order=1,
            defaults={
                "title": "Morning Conversation (Listening)",
                "lesson_type": "listening",
                "estimated_minutes": 10,
                "is_active": True,
            },
        )
        ok(f"Lesson 1 (Listening): id={lesson_listening.id}")

        # ── Lesson 2: Reading ──────────────────────────────────────────────
        info("Tạo Lesson 2: Reading — Describing a Daily Routine...")
        lesson_reading, _ = Lesson.objects.get_or_create(
            chapter=chapter,
            order=2,
            defaults={
                "title": "Daily Routine (Reading)",
                "lesson_type": "reading",
                "estimated_minutes": 15,
                "is_active": True,
            },
        )
        ok(f"Lesson 2 (Reading): id={lesson_reading.id}")

        # ── Lesson 3: Locked (requires Lesson 1 + Lesson 2 completed) ──────
        info("Tạo Lesson 3: Assessment — bị KHÓA cho đến khi qua L1 + L2...")
        lesson_locked, _ = Lesson.objects.get_or_create(
            chapter=chapter,
            order=3,
            defaults={
                "title": "Chapter Assessment (Locked)",
                "lesson_type": "assessment",
                "estimated_minutes": 20,
                "is_active": True,
            },
        )
        ok(f"Lesson 3 (Locked Assessment): id={lesson_locked.id}")

        # ── UnlockRules ────────────────────────────────────────────────────
        rule1, _ = UnlockRule.objects.get_or_create(
            lesson=lesson_locked,
            required_lesson=lesson_listening,
            defaults={"min_score": 60},
        )
        rule2, _ = UnlockRule.objects.get_or_create(
            lesson=lesson_locked,
            required_lesson=lesson_reading,
            defaults={"min_score": 60},
        )
        ok(f"UnlockRule: L3 cần L1 ≥ 60 và L2 ≥ 60")

        # ── ListeningExercise + Questions ──────────────────────────────────
        info("Tạo Listening Exercise + 5 câu hỏi trắc nghiệm (nguồn: source/a1/)...")
        listening_ex, _ = ListeningExercise.objects.get_or_create(
            title="Morning Conversation — Track 01",
            defaults={
                "audio_file": "source/a1/morning_conversation_01.mp3",
                "audio_duration_seconds": 90,
                "transcript": (
                    "A: Good morning! How are you today?\n"
                    "B: I'm fine, thank you. And you?\n"
                    "A: I'm great! What time do you usually wake up?\n"
                    "B: I wake up at six o'clock every morning.\n"
                    "A: Do you have breakfast at home?\n"
                    "B: Yes, I always have rice and eggs for breakfast."
                ),
                "context_hint": "Two friends meeting in the morning",
                "cefr_level": "A1",
            },
        )
        ok(f"ListeningExercise id={listening_ex.id}: '{listening_ex.title}'")

        # Create LessonExercise link
        LessonExercise.objects.get_or_create(
            lesson=lesson_listening,
            exercise_type="listening",
            exercise_id=listening_ex.id,
            defaults={"order": 1, "passing_score": 60},
        )

        # Create Questions for Listening
        listening_qs_data = [
            {
                "order": 1,
                "question_text": "How does Person B feel when greeted?",
                "question_type": "mc",
                "correct_answers_json": ["Fine"],
                "explanation": 'B says "I\'m fine, thank you."',
                "points": 2,
            },
            {
                "order": 2,
                "question_text": "What time does Person B wake up every morning?",
                "question_type": "mc",
                "correct_answers_json": ["Six o'clock"],
                "explanation": 'B says "I wake up at six o\'clock every morning."',
                "points": 2,
            },
            {
                "order": 3,
                "question_text": "What does Person B eat for breakfast?",
                "question_type": "mc",
                "correct_answers_json": ["Rice and eggs"],
                "explanation": 'B says "I always have rice and eggs for breakfast."',
                "points": 2,
            },
            {
                "order": 4,
                "question_text": "Does Person B have breakfast at home?",
                "question_type": "mc",
                "correct_answers_json": ["Yes"],
                "explanation": 'B says "Yes, I always have..."',
                "points": 2,
            },
            {
                "order": 5,
                "question_text": "Fill in the blank: 'I wake up _____ six o'clock.'",
                "question_type": "gap_fill",
                "correct_answers_json": ["at"],
                "explanation": "Preposition 'at' is used with clock times.",
                "points": 2,
            },
        ]

        listening_qs = []
        for qd in listening_qs_data:
            q, created = Question.objects.get_or_create(
                exercise_type="listening",
                exercise_id=listening_ex.id,
                order=qd["order"],
                defaults={
                    "question_type": qd["question_type"],
                    "question_text": qd["question_text"],
                    "correct_answers_json": qd["correct_answers_json"],
                    "explanation": qd["explanation"],
                    "points": qd["points"],
                },
            )
            listening_qs.append(q)

            # Add MC options if multiple choice
            if qd["question_type"] == "mc":
                _seed_mc_options(q, qd["correct_answers_json"][0])

        ok(f"Đã tạo {len(listening_qs)} câu hỏi Listening (tổng điểm = {sum(q.points for q in listening_qs)})")

        # ── ReadingExercise + Questions ────────────────────────────────────
        info("Tạo Reading Exercise + 5 câu hỏi (nguồn: source/a1/)...")
        reading_ex, _ = ReadingExercise.objects.get_or_create(
            title="My Daily Routine",
            defaults={
                "article_text": textwrap.dedent("""\
                    <h2>My Daily Routine</h2>
                    <p>
                        My name is Linh. I am a student. Every day I wake up at <strong>7:00 AM</strong>.
                        First, I brush my teeth and wash my face. Then I eat breakfast — usually
                        bread and milk. After breakfast, I go to school by bicycle.
                    </p>
                    <p>
                        School starts at <strong>8:00 AM</strong> and finishes at <strong>4:00 PM</strong>.
                        In the evening, I do my homework. I usually study for about <strong>two hours</strong>.
                        Before bed, I read a book for 30 minutes. I go to sleep at <strong>10:00 PM</strong>.
                    </p>
                """),
                "vocab_tooltip_json": [
                    {"word": "routine", "ipa": "/ruːˈtiːn/", "meaning_vi": "thói quen hằng ngày"},
                    {"word": "bicycle", "ipa": "/ˈbaɪsɪkl/", "meaning_vi": "xe đạp"},
                ],
                "cefr_level": "A1",
            },
        )
        ok(f"ReadingExercise id={reading_ex.id}: '{reading_ex.title}'")

        LessonExercise.objects.get_or_create(
            lesson=lesson_reading,
            exercise_type="reading",
            exercise_id=reading_ex.id,
            defaults={"order": 1, "passing_score": 60},
        )

        reading_qs_data = [
            {
                "order": 1,
                "question_text": "What time does Linh wake up every day?",
                "question_type": "mc",
                "correct_answers_json": ["7:00 AM"],
                "points": 2,
            },
            {
                "order": 2,
                "question_text": "How does Linh go to school?",
                "question_type": "mc",
                "correct_answers_json": ["By bicycle"],
                "points": 2,
            },
            {
                "order": 3,
                "question_text": "What time does school finish?",
                "question_type": "mc",
                "correct_answers_json": ["4:00 PM"],
                "points": 2,
            },
            {
                "order": 4,
                "question_text": "How many hours does Linh study in the evening?",
                "question_type": "mc",
                "correct_answers_json": ["Two hours"],
                "points": 2,
            },
            {
                "order": 5,
                "question_text": "What does Linh do before sleeping?",
                "question_type": "gap_fill",
                "correct_answers_json": ["read a book", "reads a book"],
                "points": 2,
            },
        ]

        reading_qs = []
        for qd in reading_qs_data:
            q, created = Question.objects.get_or_create(
                exercise_type="reading",
                exercise_id=reading_ex.id,
                order=qd["order"],
                defaults={
                    "question_type": qd["question_type"],
                    "question_text": qd["question_text"],
                    "correct_answers_json": qd["correct_answers_json"],
                    "explanation": qd.get("explanation", ""),
                    "points": qd["points"],
                },
            )
            reading_qs.append(q)
            if qd["question_type"] == "mc":
                _seed_mc_options(q, qd["correct_answers_json"][0])

        ok(f"Đã tạo {len(reading_qs)} câu hỏi Reading (tổng điểm = {sum(q.points for q in reading_qs)})")

        info(f"✦ Cấu trúc khoá học:")
        print(f"     {INFO_COLOR}Course: {course.title} (slug={course.slug}){RESET}")
        print(f"     {INFO_COLOR}  └── Chapter 1: {chapter.title} (passing_score={chapter.passing_score}){RESET}")
        print(f"     {INFO_COLOR}        ├── Lesson 1 [listening] id={lesson_listening.id} → ListeningEx id={listening_ex.id} (5 câu, 10 pts){RESET}")
        print(f"     {INFO_COLOR}        ├── Lesson 2 [reading]   id={lesson_reading.id}   → ReadingEx id={reading_ex.id} (5 câu, 10 pts){RESET}")
        print(f"     {INFO_COLOR}        └── Lesson 3 [assessment] id={lesson_locked.id}  → 🔒 Cần L1 ≥ 60 VÀ L2 ≥ 60{RESET}")

        return {
            "level": level,
            "course": course,
            "chapter": chapter,
            "lesson_listening": lesson_listening,
            "lesson_reading": lesson_reading,
            "lesson_locked": lesson_locked,
            "listening_ex": listening_ex,
            "reading_ex": reading_ex,
            "listening_qs": listening_qs,
            "reading_qs": reading_qs,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # STUDENT SETUP
    # ──────────────────────────────────────────────────────────────────────────
    @transaction.atomic
    def _setup_student(self, course):
        from apps.users.models import User
        from apps.progress.models import UserEnrollment

        info("Tạo học viên: student@english-study.vn ...")
        student, created = User.objects.get_or_create(
            email="student@english-study.vn",
            defaults={
                "username": "student_lan",
                "first_name": "Lan",
                "last_name": "Nguyễn Thị",
                "role": "student",
                "is_active": True,
            },
        )
        if created:
            student.set_password("TestPass123!")
            student.save()
            ok(f"Tạo student mới: id={student.id} email={student.email}")
        else:
            ok(f"Student đã tồn tại: id={student.id} email={student.email}")

        info(f"Đăng ký học viên vào khoá '{course.title}'...")
        enrollment, created = UserEnrollment.objects.get_or_create(
            user=student,
            course=course,
            defaults={"status": "active", "progress_percent": 0},
        )
        if created:
            ok(f"Đăng ký thành công: enrollment id={enrollment.id}")
        else:
            ok(f"Enrollment đã tồn tại: id={enrollment.id}, progress={enrollment.progress_percent}%")

        return student, enrollment

    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO: LISTENING
    # ──────────────────────────────────────────────────────────────────────────
    def _run_listening(self, student, lesson, exercise, questions, scenario):
        from apps.progress.grading import AutoGrader

        if scenario == "ALL_CORRECT":
            # Build answers from correct_answers_json
            user_answers = {
                str(q.id): q.correct_answers_json[0] for q in questions
            }
            info(f"Đáp án học viên (ĐÚNG HẾT): {user_answers}")
        else:
            # Wrong answers
            wrong_map = {
                "Fine": "Tired",
                "Six o'clock": "Seven o'clock",
                "Rice and eggs": "Bread and coffee",
                "Yes": "No",
                "at": "in",
            }
            user_answers = {}
            for q in questions:
                correct = q.correct_answers_json[0]
                user_answers[str(q.id)] = wrong_map.get(correct, "WRONG")
            info(f"Đáp án học viên (SAI HẾT): {user_answers}")

        result = AutoGrader.grade_listening(
            user=student,
            lesson=lesson,
            exercise=exercise,
            user_answers=user_answers,
            time_spent_seconds=185,
        )

        self._print_result(result, "LISTENING", scenario)

    # ──────────────────────────────────────────────────────────────────────────
    # SCENARIO: READING
    # ──────────────────────────────────────────────────────────────────────────
    def _run_reading(self, student, lesson, exercise, questions):
        from apps.progress.grading import AutoGrader

        # Q1, Q2, Q3 correct (6pts), Q4, Q5 wrong (0pts) → 60% → PASS
        correct_ids = [str(q.id) for q in questions[:3]]
        wrong_ids   = [str(q.id) for q in questions[3:]]

        user_answers = {}
        for q in questions[:3]:
            user_answers[str(q.id)] = q.correct_answers_json[0]
        user_answers[str(questions[3].id)] = "Three hours"  # wrong (correct: Two hours)
        user_answers[str(questions[4].id)] = "watch TV"     # wrong (correct: read a book)

        info(f"Đáp án học viên (câu 1-3 đúng, 4-5 sai): {user_answers}")

        result = AutoGrader.grade_reading(
            user=student,
            lesson=lesson,
            exercise=exercise,
            user_answers=user_answers,
            time_spent_seconds=420,
        )

        self._print_result(result, "READING", "PARTIAL_CORRECT")

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────────
    def _print_result(self, result, skill, scenario):
        from utils.formatters import fmt_percent, fmt_score
        color = PASS_COLOR if result.passed else FAIL_COLOR
        status = "PASS ✔" if result.passed else "FAIL ✘"
        print(f"\n  {color}┌─── RESULT [{skill}] {scenario} ───{RESET}")
        print(f"  {color}│  ExerciseResult id : {result.id}{RESET}")
        print(f"  {color}│  Điểm              : {fmt_score(result.score)} / 100  ({fmt_percent(result.score)}){RESET}")
        print(f"  {color}│  Kết quả           : {status}{RESET}")
        print(f"  {color}│  Chi tiết từng câu :{RESET}")
        for row in result.detail_json:
            icon = "✔" if row["is_correct"] else "✘"
            q_text = row.get("question_text", f"Q{row['question_id']}")[:50]
            print(f"  {color}│    {icon} Q{row['question_id']} | user={row['user_answer']!r:25} "
                  f"correct={row['correct_answers']!r:20} pts={row['points_awarded']}/{row['points_possible']}{RESET}")
        print(f"  {color}└────────────────────────────────────{RESET}\n")

    def _check_unlock_status(self, student, data):
        from apps.progress.models import LessonProgress
        from apps.curriculum.models import UnlockRule

        info("Kiểm tra trạng thái KHÓA/MỞ KHÓA bài tiếp theo...")

        def is_unlocked(lesson):
            """Return True if all unlock rules for lesson are satisfied."""
            rules = UnlockRule.objects.filter(lesson=lesson)
            if not rules.exists():
                return True
            for rule in rules:
                lp = LessonProgress.objects.filter(
                    user=student, lesson=rule.required_lesson, status="completed"
                ).filter(best_score__gte=rule.min_score).first()
                if lp is None:
                    return False
            return True

        lessons = [
            ("Lesson 1 (Listening)",  data["lesson_listening"]),
            ("Lesson 2 (Reading)",    data["lesson_reading"]),
            ("Lesson 3 (Assessment)", data["lesson_locked"]),
        ]

        for label, lesson in lessons:
            lp = LessonProgress.objects.filter(user=student, lesson=lesson).first()
            status  = lp.status if lp else "not_started"
            best    = f"{lp.best_score:.1f}" if lp and lp.best_score is not None else "—"
            unlock  = "🔓 MỞ KHOÁ" if is_unlocked(lesson) else "🔒 ĐANG KHOÁ"
            color   = PASS_COLOR if is_unlocked(lesson) else FAIL_COLOR
            print(f"  {color}  {label}: status={status}, best_score={best}  →  {unlock}{RESET}")

    def _print_summary(self, student, data):
        from apps.progress.models import UserEnrollment, LessonProgress, ExerciseResult
        from apps.curriculum.models import UnlockRule
        from utils.formatters import fmt_percent

        enrollment = UserEnrollment.objects.filter(user=student, course=data["course"]).first()
        l_progress = LessonProgress.objects.filter(user=student).order_by("lesson__order")

        print(f"\n  {INFO_COLOR}Học viên : {student.get_full_name() or student.email} ({student.email}){RESET}")
        print(f"  {INFO_COLOR}Khoá học : {data['course'].title}{RESET}")
        if enrollment:
            print(f"  {INFO_COLOR}Tiến độ  : {fmt_percent(enrollment.progress_percent)} ({enrollment.progress_percent}%){RESET}")

        print(f"\n  {'Lesson':<35} {'Status':<15} {'Best Score':<12} {'Attempts':<10}")
        print(f"  {'─'*35} {'─'*15} {'─'*12} {'─'*10}")

        for lp in l_progress:
            name  = lp.lesson.title[:33]
            score = f"{lp.best_score:.1f}" if lp.best_score is not None else "—"
            print(f"  {name:<35} {lp.status:<15} {score:<12} {lp.attempts_count:<10}")

        all_results = ExerciseResult.objects.filter(user=student).order_by("created_at")
        print(f"\n  Tổng submisions: {all_results.count()}")
        for r in all_results:
            tag = f"✔ PASS" if r.passed else "✘ FAIL"
            print(f"    [{r.exercise_type.upper():<10}] id={r.id} score={r.score:>6.2f}  {tag}")

        # Final unlock check
        print()
        self._check_unlock_status(student, data)

    # ──────────────────────────────────────────────────────────────────────────
    def _cleanup(self):
        from apps.users.models import User
        from apps.curriculum.models import Course, CEFRLevel
        from apps.progress.models import UserEnrollment, LessonProgress, ExerciseResult

        warn("Dọn dẹp dữ liệu test cũ...")
        User.objects.filter(email="student@english-study.vn").delete()
        Course.objects.filter(slug="a1-everyday-english").delete()
        ok("Đã xoá dữ liệu test.")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers ngoài class
# ──────────────────────────────────────────────────────────────────────────────
def _seed_mc_options(question, correct_answer: str):
    """Seed 4 MC options (A/B/C/D) for a question. Idempotent."""
    from apps.exercises.models import QuestionOption
    if QuestionOption.objects.filter(question=question).exists():
        return

    wrong_pool = {
        "Fine": ["Tired", "Angry", "Hungry"],
        "Six o'clock": ["Five o'clock", "Seven o'clock", "Eight o'clock"],
        "Rice and eggs": ["Bread and coffee", "Noodles", "Fruit"],
        "Yes": ["No", "Maybe", "Sometimes"],
        "7:00 AM": ["6:00 AM", "8:00 AM", "9:00 AM"],
        "By bicycle": ["By bus", "On foot", "By car"],
        "4:00 PM": ["3:00 PM", "5:00 PM", "6:00 PM"],
        "Two hours": ["One hour", "Three hours", "Four hours"],
    }
    wrongs = wrong_pool.get(correct_answer, ["Option B", "Option C", "Option D"])[:3]
    options = [correct_answer] + wrongs
    import random
    random.shuffle(options)

    for i, opt_text in enumerate(options, start=1):
        QuestionOption.objects.create(
            question=question,
            option_text=opt_text,
            order=i,
        )
