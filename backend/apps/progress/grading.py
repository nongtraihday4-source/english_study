"""
apps/progress/grading.py
─────────────────────────────────────────────────────────────────────────────
AutoGrader: direct scoring for Listening & Reading (MC / gap-fill / drag-drop)
─────────────────────────────────────────────────────────────────────────────
DEBUG LOGGING:
  Every grading flow is wrapped in utils.logging.GradingLogger so you get
  a full, structured log line per question with:
    • question_id, question_type, user_answer, correct_answer, is_correct, points
  And a summary line:
    • score (0-100), correct/total, pass/fail, time taken (ms)
"""
import logging
import time
from typing import Any

from django.db import transaction
from django.utils import timezone

from utils.formatters import fmt_percent, fmt_score
from utils.logging import GradingLogger, log_score_detail, log_progress_update

logger = logging.getLogger("es.grading")


# ─── Helper: answer comparison ────────────────────────────────────────────────

def _normalise(value: Any) -> str:
    """Lowercase + strip whitespace for case-insensitive comparison."""
    return str(value).strip().lower()


def _check_answer(question, user_answer: Any) -> bool:
    """
    Returns True if user_answer matches any correct answer.
    Handles multiple correct answers (drag-drop / multi-select) and
    single-answer (MC / gap-fill).
    """
    correct_list = question.correct_answers_json  # list[str]
    if not correct_list:
        logger.warning("Question %s has no correct_answers_json — skipping", question.pk)
        return False

    if isinstance(user_answer, list):
        # Drag-drop / multi-select: sorted comparison
        user_set = sorted([_normalise(a) for a in user_answer])
        correct_set = sorted([_normalise(c) for c in correct_list])
        return user_set == correct_set

    return _normalise(user_answer) in [_normalise(c) for c in correct_list]


# ─── Core scoring engine ──────────────────────────────────────────────────────

def _calculate_score(questions, user_answers: dict) -> dict:
    """
    questions     : QuerySet[Question]
    user_answers  : {str(question_id): answer_value, ...}

    Returns:
        {
            "score": float,          # 0-100
            "correct_count": int,
            "total_questions": int,
            "total_points": int,
            "earned_points": int,
            "detail_json": list[dict],   # per-question breakdown
        }
    """
    detail = []
    earned_points = 0
    total_points = 0
    correct_count = 0

    for q in questions:
        q_id = str(q.pk)
        user_ans = user_answers.get(q_id)
        is_correct = _check_answer(q, user_ans) if user_ans is not None else False
        pts = q.points if is_correct else 0
        earned_points += pts
        total_points += q.points
        if is_correct:
            correct_count += 1

        row = {
            "question_id": q.pk,
            "question_type": q.question_type,
            "user_answer": user_ans,
            "correct_answers": q.correct_answers_json,
            "is_correct": is_correct,
            "points_awarded": pts,
            "points_possible": q.points,
        }
        detail.append(row)

        # Per-question debug log
        log_score_detail(
            q_id=q.pk,
            q_type=q.question_type,
            user_ans=user_ans,
            correct_ans=q.correct_answers_json,
            is_correct=is_correct,
            pts=pts,
        )

    score = round((earned_points / total_points) * 100, 2) if total_points > 0 else 0.0

    return {
        "score": score,
        "correct_count": correct_count,
        "total_questions": len(detail),
        "total_points": total_points,
        "earned_points": earned_points,
        "detail_json": detail,
    }


# ─── Progress updaters ────────────────────────────────────────────────────────

def _update_lesson_progress(user, lesson, score: float, passing_score: int) -> None:
    """
    Create or update LessonProgress.
    Upsert pattern: avoid race-conditions for concurrent submissions.
    """
    from apps.progress.models import LessonProgress

    passed = score >= passing_score
    new_status = "completed" if passed else "in_progress"

    lp, created = LessonProgress.objects.get_or_create(
        user=user, lesson=lesson,
        defaults={
            "status": new_status,
            "best_score": int(score),
            "attempts_count": 1,
            "completed_at": timezone.now() if passed else None,
        },
    )

    if not created:
        updated_fields = ["attempts_count", "status"]
        lp.attempts_count = lp.attempts_count + 1

        if int(score) > (lp.best_score or 0):
            lp.best_score = int(score)
            updated_fields.append("best_score")

        if new_status == "completed" and lp.status != "completed":
            lp.status = "completed"
            lp.completed_at = timezone.now()
            updated_fields.append("completed_at")
        elif lp.status != "completed":
            lp.status = new_status

        lp.save(update_fields=updated_fields)

    log_progress_update(
        user_id=user.pk,
        lesson_id=lesson.pk,
        score=score,
        passed=passed,
        attempts=lp.attempts_count,
    )


def _unlock_next_lessons(user, lesson, score: float) -> None:
    """
    After grading, check UnlockRule entries that require `lesson` as prerequisite.
    For each dependent lesson: if student score meets min_score, set its
    LessonProgress.status → 'available' (only if currently 'locked').
    """
    from apps.curriculum.models import UnlockRule
    from apps.progress.models import LessonProgress

    rules = UnlockRule.objects.filter(required_lesson=lesson).select_related("lesson")
    for rule in rules:
        if score < rule.min_score:
            logger.debug(
                "UnlockRule | lesson=%s requires lesson=%s at %d%% — score %.2f < min_score → STILL LOCKED",
                rule.lesson_id, lesson.pk, rule.min_score, score,
            )
            continue

        lp, created = LessonProgress.objects.get_or_create(
            user=user, lesson=rule.lesson,
            defaults={"status": "available"},
        )
        if not created and lp.status == "locked":
            lp.status = "available"
            lp.save(update_fields=["status"])
            created = True  # treat as newly unlocked for logging

        if created or lp.status == "available":
            logger.info(
                "🔓 UNLOCK | lesson=%s '%s' → status=available (score=%.2f ≥ min=%d)",
                rule.lesson_id, rule.lesson.title, score, rule.min_score,
            )


def _check_chapter_completion(user, lesson) -> dict:
    """
    Check if ALL active lessons in lesson.chapter are completed.
    Returns dict with chapter_completed bool and metadata.
    """
    from apps.progress.models import LessonProgress

    chapter = lesson.chapter
    total = chapter.lessons.filter(is_active=True).count()
    if total == 0:
        return {"chapter_completed": False}

    completed = LessonProgress.objects.filter(
        user=user,
        lesson__chapter=chapter,
        lesson__is_active=True,
        status="completed",
    ).count()

    if completed >= total:
        scores = list(
            LessonProgress.objects.filter(
                user=user,
                lesson__chapter=chapter,
                lesson__is_active=True,
            ).values_list("best_score", flat=True)
        )
        valid_scores = [s for s in scores if s is not None]
        avg = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0
        logger.info(
            "🏆 CHAPTER COMPLETE | chapter=%s '%s' user=%s avg_score=%.1f",
            chapter.pk, chapter.title, user.pk, avg,
        )
        return {
            "chapter_completed": True,
            "chapter_id": chapter.pk,
            "chapter_title": chapter.title,
            "chapter_avg_score": avg,
        }
    return {"chapter_completed": False}


def _update_course_enrollment(user, lesson) -> None:
    """Recalculate enrollment.progress_percent after a lesson is completed."""
    from apps.progress.models import UserEnrollment, LessonProgress
    from apps.curriculum.models import Lesson as LessonModel

    course = lesson.chapter.course
    try:
        enrollment = UserEnrollment.objects.get(user=user, course=course, is_deleted=False)
    except UserEnrollment.DoesNotExist:
        return

    total = LessonModel.objects.filter(chapter__course=course).count()
    if total == 0:
        return

    done = LessonProgress.objects.filter(
        user=user,
        lesson__chapter__course=course,
        status="completed",
    ).count()

    new_pct = round((done / total) * 100, 2)
    enrollment.progress_percent = new_pct
    if new_pct >= 100:
        enrollment.completed_at = timezone.now()
    enrollment.save(update_fields=["progress_percent", "completed_at"])

    logger.debug(
        "EnrollmentProgress | user=%s course=%s progress=%s%%",
        user.pk, course.pk, fmt_percent(new_pct),
    )


def _update_cumulative_score(user, level_code: str, skill: str, new_score: float) -> None:
    """Rolling-average update for CumulativeScore. skill ∈ {listening, reading, grammar}."""
    from apps.progress.models import CumulativeScore
    from apps.curriculum.models import CEFRLevel

    # grammar uses the reading_avg column (no dedicated grammar_avg column yet)
    db_skill = "reading" if skill == "grammar" else skill

    try:
        level = CEFRLevel.objects.get(code=level_code)
    except CEFRLevel.DoesNotExist:
        return

    cs, _ = CumulativeScore.objects.get_or_create(user=user, level=level)
    field = f"{db_skill}_avg"   # listening_avg or reading_avg (grammar → reading_avg)
    current = getattr(cs, field, 0) or 0
    n = cs.total_exercises_done or 0

    # Incremental mean formula: new_avg = (old_avg * n + new_score) / (n + 1)
    new_avg = round((float(current) * n + new_score) / (n + 1), 2)
    cs.total_exercises_done = n + 1
    setattr(cs, field, new_avg)

    # Recompute overall_avg from all 4 skills
    avgs = [
        float(cs.listening_avg or 0), float(cs.speaking_avg or 0),
        float(cs.reading_avg or 0), float(cs.writing_avg or 0),
    ]
    cs.overall_avg = round(sum(avgs) / 4, 2)
    cs.save()

    logger.debug(
        "CumulativeScore | user=%s level=%s skill=%s prev=%.2f new=%.2f overall=%.2f",
        user.pk, level_code, skill, current, new_avg, cs.overall_avg,
    )


# ─── Public API ───────────────────────────────────────────────────────────────

class AutoGrader:
    """
    Usage:
        result = AutoGrader.grade_listening(
            user=request.user,
            lesson=lesson_obj,
            exercise=listening_exercise_obj,
            user_answers={"42": "B", "43": ["A", "C"]},
            time_spent_seconds=180,
        )
    Returns an ExerciseResult instance (already saved to DB).
    """

    @staticmethod
    @transaction.atomic
    def grade_listening(user, lesson, exercise, user_answers: dict, time_spent_seconds: int = 0):
        return AutoGrader._grade_objective(
            user=user, lesson=lesson, exercise=exercise,
            exercise_type="listening", user_answers=user_answers,
            time_spent_seconds=time_spent_seconds,
        )

    @staticmethod
    @transaction.atomic
    def grade_grammar(user, lesson, topic_id: int, user_answers: dict, time_spent_seconds: int = 0):
        """
        Grade a grammar comprehension quiz attached to a GrammarTopic.
        `user_answers` maps str(question_id) → user answer string.
        `exercise_type='grammar'`, `exercise_id=topic_id` in Question table.
        """
        return AutoGrader._grade_objective(
            user=user, lesson=lesson,
            exercise=type("_GrammarExercise", (), {"pk": topic_id})(),
            exercise_type="grammar", user_answers=user_answers,
            time_spent_seconds=time_spent_seconds,
        )

    @staticmethod
    @transaction.atomic
    def grade_reading(user, lesson, exercise, user_answers: dict, time_spent_seconds: int = 0):
        return AutoGrader._grade_objective(
            user=user, lesson=lesson, exercise=exercise,
            exercise_type="reading", user_answers=user_answers,
            time_spent_seconds=time_spent_seconds,
        )

    @staticmethod
    def _grade_objective(user, lesson, exercise, exercise_type: str, user_answers: dict, time_spent_seconds: int):
        """Shared grading engine for Listening and Reading (objective questions)."""
        from apps.exercises.models import Question
        from apps.progress.models import ExerciseResult

        t_start = time.perf_counter()
        passing_score = lesson.chapter.passing_score

        with GradingLogger(skill=exercise_type, user_id=user.pk, exercise_id=exercise.pk) as glog:
            questions = list(
                Question.objects.filter(
                    exercise_type=exercise_type,
                    exercise_id=exercise.pk,
                ).order_by("order")
            )

            if not questions:
                logger.warning(
                    "No questions for %s exercise_id=%s — score=0",
                    exercise_type, exercise.pk,
                )

            result_data = _calculate_score(questions, user_answers)
            score = result_data["score"]
            passed = score >= passing_score

            elapsed_ms = int((time.perf_counter() - t_start) * 1000)

            glog.summary(
                score=score,
                correct=result_data["correct_count"],
                total=result_data["total_questions"],
                passed=passed,
                elapsed_ms=elapsed_ms,
            )

            logger.info(
                "GRADING DONE | type=%s user=%s exercise=%s score=%s (%s) passed=%s "
                "correct=%d/%d elapsed=%dms time_spent=%ds",
                exercise_type.upper(),
                user.pk,
                exercise.pk,
                fmt_score(score),
                fmt_percent(score),
                passed,
                result_data["correct_count"],
                result_data["total_questions"],
                elapsed_ms,
                time_spent_seconds,
            )

        # Persist ExerciseResult
        ex_result = ExerciseResult.objects.create(
            user=user,
            exercise_type=exercise_type,
            exercise_id=exercise.pk,
            score=score,
            passed=passed,
            detail_json=result_data["detail_json"],
            time_spent_seconds=time_spent_seconds,
        )

        # Update lesson progress + course enrollment + unlock next lessons
        _update_lesson_progress(user, lesson, score, passing_score)
        _unlock_next_lessons(user, lesson, score)
        _update_course_enrollment(user, lesson)

        # Check if the chapter is now fully completed
        chapter_info = _check_chapter_completion(user, lesson)
        ex_result._chapter_info = chapter_info

        # Update rolling cumulative score
        level_code = lesson.chapter.course.level.code
        _update_cumulative_score(user, level_code, exercise_type, score)

        return ex_result
