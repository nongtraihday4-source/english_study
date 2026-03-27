"""Structured loggers for each domain flow."""
import logging
import time
from functools import wraps


grading_log = logging.getLogger("es.grading")
auth_log = logging.getLogger("es.auth")
progress_log = logging.getLogger("es.progress")
payments_log = logging.getLogger("es.payments")
curriculum_log = logging.getLogger("es.curriculum")


class GradingLogger:
    """
    Decorator / context helper for logging the full grading pipeline.
    Usage:
        with GradingLogger.flow("speaking", user_id=1, exercise_id=5) as gl:
            gl.step("Whisper transcription received", transcript=transcript)
            gl.step("GPT-4o rubric scores",
                    pronunciation=72, fluency=80, total=76)
            gl.done(score=76)
    """

    def __init__(self, skill: str, user_id: int, exercise_id: int):
        self.skill = skill.upper()
        self.user_id = user_id
        self.exercise_id = exercise_id
        self._start = time.monotonic()

    def __enter__(self):
        grading_log.debug(
            "▶ START %s grading | user=%s exercise=%s",
            self.skill, self.user_id, self.exercise_id,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.monotonic() - self._start) * 1000
        if exc_type:
            grading_log.error(
                "❌ FAILED %s grading | user=%s exercise=%s elapsed=%.0fms | %s",
                self.skill, self.user_id, self.exercise_id, elapsed, exc_val,
            )
        else:
            grading_log.debug(
                "✅ DONE %s grading | user=%s exercise=%s elapsed=%.0fms",
                self.skill, self.user_id, self.exercise_id, elapsed,
            )
        return False  # Re-raise exceptions

    def step(self, label: str, **kwargs):
        kv = "  ".join(f"{k}={v}" for k, v in kwargs.items())
        grading_log.debug("  [%s] %s | %s", self.skill, label, kv)

    def summary(self, score: float, correct: int, total: int, passed: bool, elapsed_ms: int):
        """Log grading summary after all questions scored."""
        grading_log.info(
            "  [%s] SUMMARY | user=%s exercise=%s | score=%.2f correct=%d/%d passed=%s elapsed=%dms",
            self.skill, self.user_id, self.exercise_id,
            score, correct, total, passed, elapsed_ms,
        )

    def done(self, score: int, **kwargs):
        kv = "  ".join(f"{k}={v}" for k, v in kwargs.items())
        grading_log.info(
            "  [%s] SCORE=%s | user=%s exercise=%s | %s",
            self.skill, score, self.user_id, self.exercise_id, kv,
        )

    @classmethod
    def flow(cls, skill: str, user_id: int, exercise_id: int):
        return cls(skill, user_id, exercise_id)


def log_score_detail(
    q_id: int,
    q_type: str,
    user_ans,
    correct_ans,
    is_correct: bool,
    pts: int,
):
    """Per-question debug log during objective auto-grading."""
    icon = "✔" if is_correct else "✘"
    grading_log.debug(
        "  %s Q%-4s [%-10s] user=%-25r correct=%-25r pts=%s",
        icon, q_id, q_type, user_ans, correct_ans, pts,
    )


def log_progress_update(
    user_id: int,
    lesson_id: int,
    score: float,
    passed: bool,
    attempts: int,
):
    """Log when LessonProgress is updated after a submission."""
    progress_log.debug(
        "[PROGRESS] user=%s lesson=%s | score=%.2f passed=%s attempts=%d",
        user_id, lesson_id, score, passed, attempts,
    )
