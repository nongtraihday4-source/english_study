"""
apps/progress/tasks.py
─────────────────────────────────────────────────────────────────────────────
Celery AI-grading pipeline for Speaking and Writing submissions.

SPEAKING rubric (total 100):
  Pronunciation  35%
  Fluency        25%
  Intonation     20%
  Vocabulary     20%

WRITING rubric (total 100):
  Task Achievement  25%
  Grammar           25%
  Vocabulary        25%
  Coherence         25%
─────────────────────────────────────────────────────────────────────────────
Every step is logged via GradingLogger so logs/grading.log shows the
complete audit trail including token usage, rubric breakdown, and sub-scores.
"""
import json
import logging
import time

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from utils.formatters import fmt_score
from utils.logging import GradingLogger, log_score_detail

logger = logging.getLogger("es.grading")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_openai():
    import openai
    openai.api_key = settings.OPENAI_API_KEY
    return openai


def _update_ai_grading_job(job, status: str, tokens: int = 0, error: str = ""):
    job.status = status
    job.tokens_used = tokens
    if error:
        job.error_message = error
    job.save(update_fields=["status", "tokens_used", "error_message"])


# ─── Speaking grader ──────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=settings.AI_GRADING_TIMEOUT,
    name="progress.grade_speaking",
)
def grade_speaking_task(self, submission_id: int):
    """
    1. Load SpeakingSubmission
    2. Call Whisper API → transcript
    3. Call GPT-4o with rubric
    4. Parse 4 sub-scores → compute weighted ai_score
    5. Save to DB + push notification
    """
    from apps.progress.models import SpeakingSubmission, AIGradingJob, ExerciseResult
    from apps.notifications.models import Notification

    t_start = time.perf_counter()

    try:
        sub = SpeakingSubmission.objects.select_related("user", "lesson").get(pk=submission_id)
    except SpeakingSubmission.DoesNotExist:
        logger.error("grade_speaking_task: SpeakingSubmission %s not found", submission_id)
        return

    # Mark processing
    sub.status = "processing"
    sub.save(update_fields=["status"])

    job = AIGradingJob.objects.filter(
        job_type="speaking", submission_id=submission_id
    ).first()
    if not job:
        job = AIGradingJob.objects.create(
            job_type="speaking",
            submission_id=submission_id,
            celery_task_id=self.request.id or "",
            status="processing",
        )
    else:
        job.celery_task_id = self.request.id or ""
        job.status = "processing"
        job.retry_count = self.request.retries
        job.save(update_fields=["celery_task_id", "status", "retry_count"])

    with GradingLogger(skill="speaking", user_id=sub.user_id, exercise_id=sub.exercise_id) as glog:
        try:
            openai = _get_openai()
            total_tokens = 0

            # ── Step 1: Whisper transcription ─────────────────────────────────
            logger.debug(
                "SPEAKING | user=%s sub=%s | Whisper START | s3_key=%s",
                sub.user_id, submission_id, sub.audio_s3_key,
            )
            import boto3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            audio_obj = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=sub.audio_s3_key,
            )
            audio_bytes = audio_obj["Body"].read()

            whisper_resp = openai.audio.transcriptions.create(
                model=settings.OPENAI_WHISPER_MODEL,
                file=("audio.webm", audio_bytes, "audio/webm"),
                language="en",
            )
            transcript = whisper_resp.text
            logger.debug(
                "SPEAKING | user=%s sub=%s | Whisper DONE | len=%d chars",
                sub.user_id, submission_id, len(transcript),
            )

            # ── Step 2: GPT-4o rubric scoring ────────────────────────────────
            system_prompt = (
                "You are an expert English pronunciation and fluency evaluator. "
                "Score the student's speech on 4 criteria. "
                "Return ONLY valid JSON with keys: "
                "pronunciation (0-100), fluency (0-100), intonation (0-100), vocabulary (0-100), "
                "error_list (array of {word, issue, suggestion}), "
                "feedback_vi (brief feedback in Vietnamese)."
            )
            user_prompt = (
                f"Target sentence: \"{sub.target_sentence}\"\n"
                f"Student transcript: \"{transcript}\"\n\n"
                "Evaluate and return JSON only."
            )

            gpt_resp = openai.chat.completions.create(
                model=settings.OPENAI_GRADING_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
                timeout=settings.AI_GRADING_TIMEOUT,
            )
            total_tokens = gpt_resp.usage.total_tokens
            raw = json.loads(gpt_resp.choices[0].message.content)

            # ── Step 3: Parse sub-scores ──────────────────────────────────────
            score_pronunciation = min(100, max(0, float(raw.get("pronunciation", 0))))
            score_fluency = min(100, max(0, float(raw.get("fluency", 0))))
            score_intonation = min(100, max(0, float(raw.get("intonation", 0))))
            score_vocabulary = min(100, max(0, float(raw.get("vocabulary", 0))))

            # Weighted average (pronunciation 35, fluency 25, intonation 20, vocab 20)
            ai_score = round(
                score_pronunciation * 0.35
                + score_fluency * 0.25
                + score_intonation * 0.20
                + score_vocabulary * 0.20,
                2,
            )

            for name, val in [
                ("pronunciation", score_pronunciation),
                ("fluency", score_fluency),
                ("intonation", score_intonation),
                ("vocabulary", score_vocabulary),
            ]:
                log_score_detail(
                    q_id=name, q_type="rubric_criterion",
                    user_ans=val, correct_ans=100,
                    is_correct=val >= 70, pts=val,
                )

            elapsed_ms = int((time.perf_counter() - t_start) * 1000)
            glog.summary(
                score=ai_score,
                correct=int(ai_score),
                total=100,
                passed=ai_score >= 60,
                elapsed_ms=elapsed_ms,
            )

            logger.info(
                "SPEAKING done | user=%s sub=%s ai_score=%s "
                "pron=%.1f flu=%.1f into=%.1f vocab=%.1f "
                "tokens=%d elapsed=%dms",
                sub.user_id, submission_id, fmt_score(ai_score),
                score_pronunciation, score_fluency, score_intonation, score_vocabulary,
                total_tokens, elapsed_ms,
            )

            # ── Step 4: Persist ───────────────────────────────────────────────
            sub.transcript = transcript
            sub.ai_score = ai_score
            sub.score_pronunciation = score_pronunciation
            sub.score_fluency = score_fluency
            sub.score_intonation = score_intonation
            sub.score_vocabulary = score_vocabulary
            sub.error_list_json = raw.get("error_list", [])
            sub.feedback_vi = raw.get("feedback_vi", "")
            sub.status = "completed"
            sub.save()

            _update_ai_grading_job(job, "completed", total_tokens)

            # Create ExerciseResult
            ExerciseResult.objects.create(
                user=sub.user,
                exercise_type="speaking",
                exercise_id=sub.exercise_id,
                score=ai_score,
                passed=ai_score >= 60,
                detail_json={
                    "pronunciation": score_pronunciation,
                    "fluency": score_fluency,
                    "intonation": score_intonation,
                    "vocabulary": score_vocabulary,
                },
            )

            # Notify user
            Notification.objects.create(
                user_id=sub.user_id,
                notification_type="grading_done",
                title="Bài Speaking đã được chấm!",
                message=f"Điểm của bạn: {fmt_score(ai_score)} / 100",
                reference_id=sub.pk,
                reference_type="speaking_submission",
            )

        except Exception as exc:
            elapsed = int((time.perf_counter() - t_start) * 1000)
            logger.error(
                "grade_speaking_task FAILED | sub=%s attempt=%d err=%s elapsed=%dms",
                submission_id, self.request.retries + 1, str(exc), elapsed,
            )
            sub.status = "failed"
            sub.save(update_fields=["status"])
            _update_ai_grading_job(job, "failed", error=str(exc))
            raise self.retry(exc=exc)


# ─── Writing grader ───────────────────────────────────────────────────────────

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=settings.AI_GRADING_TIMEOUT,
    name="progress.grade_writing",
)
def grade_writing_task(self, submission_id: int):
    """
    1. Load WritingSubmission
    2. Call GPT-4o with IELTS-style rubric
    3. Parse 4 sub-scores + error_list + vocab_cefr_json
    4. Save to DB + push notification
    """
    from apps.progress.models import WritingSubmission, AIGradingJob, ExerciseResult
    from apps.exercises.models import WritingExercise
    from apps.notifications.models import Notification

    t_start = time.perf_counter()

    try:
        sub = WritingSubmission.objects.select_related("user").get(pk=submission_id)
    except WritingSubmission.DoesNotExist:
        logger.error("grade_writing_task: WritingSubmission %s not found", submission_id)
        return

    sub.status = "processing"
    sub.save(update_fields=["status"])

    job = AIGradingJob.objects.filter(
        job_type="writing", submission_id=submission_id
    ).first()
    if not job:
        job = AIGradingJob.objects.create(
            job_type="writing",
            submission_id=submission_id,
            celery_task_id=self.request.id or "",
            status="processing",
        )
    else:
        job.celery_task_id = self.request.id or ""
        job.status = "processing"
        job.retry_count = self.request.retries
        job.save(update_fields=["celery_task_id", "status", "retry_count"])

    with GradingLogger(skill="writing", user_id=sub.user_id, exercise_id=sub.exercise_id) as glog:
        try:
            openai = _get_openai()

            exercise_prompt = ""
            try:
                ex = WritingExercise.objects.get(pk=sub.exercise_id)
                exercise_prompt = ex.prompt_text
            except WritingExercise.DoesNotExist:
                pass

            system_prompt = (
                "You are an expert English writing evaluator. "
                "Score the student's essay. Return ONLY valid JSON with keys: "
                "task_achievement (0-100), grammar (0-100), vocabulary (0-100), coherence (0-100), "
                "feedback_vi (brief encouraging feedback in Vietnamese, max 200 chars), "
                "error_list (array of {original, suggestion, explanation_vi}), "
                "vocab_cefr_json (object mapping {word: cefr_level} for notable vocabulary used)."
            )
            user_prompt = (
                f"Writing prompt: \"{exercise_prompt}\"\n\n"
                f"Student essay ({sub.word_count} words):\n\"{sub.content_text}\"\n\n"
                "Evaluate and return JSON only."
            )

            gpt_resp = _get_openai().chat.completions.create(
                model=settings.OPENAI_GRADING_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
                timeout=settings.AI_GRADING_TIMEOUT,
            )
            total_tokens = gpt_resp.usage.total_tokens
            raw = json.loads(gpt_resp.choices[0].message.content)

            score_task = min(100, max(0, float(raw.get("task_achievement", 0))))
            score_grammar = min(100, max(0, float(raw.get("grammar", 0))))
            score_vocab = min(100, max(0, float(raw.get("vocabulary", 0))))
            score_coherence = min(100, max(0, float(raw.get("coherence", 0))))

            # Equal 25% weighting
            ai_score = round((score_task + score_grammar + score_vocab + score_coherence) / 4, 2)

            for name, val in [
                ("task_achievement", score_task),
                ("grammar", score_grammar),
                ("vocabulary", score_vocab),
                ("coherence", score_coherence),
            ]:
                log_score_detail(
                    q_id=name, q_type="rubric_criterion",
                    user_ans=val, correct_ans=100,
                    is_correct=val >= 70, pts=val,
                )

            elapsed_ms = int((time.perf_counter() - t_start) * 1000)
            glog.summary(
                score=ai_score,
                correct=int(ai_score),
                total=100,
                passed=ai_score >= 60,
                elapsed_ms=elapsed_ms,
            )

            logger.info(
                "WRITING done | user=%s sub=%s ai_score=%s "
                "task=%.1f gram=%.1f vocab=%.1f cohe=%.1f "
                "tokens=%d elapsed=%dms",
                sub.user_id, submission_id, fmt_score(ai_score),
                score_task, score_grammar, score_vocab, score_coherence,
                total_tokens, elapsed_ms,
            )

            sub.ai_score = ai_score
            sub.score_task_achievement = score_task
            sub.score_grammar = score_grammar
            sub.score_vocabulary = score_vocab
            sub.score_coherence = score_coherence
            sub.feedback_text = raw.get("feedback_vi", "")
            sub.error_list_json = raw.get("error_list", [])
            sub.vocab_cefr_json = raw.get("vocab_cefr_json", {})
            sub.status = "completed"
            sub.save()

            _update_ai_grading_job(job, "completed", total_tokens)

            ExerciseResult.objects.create(
                user=sub.user,
                exercise_type="writing",
                exercise_id=sub.exercise_id,
                score=ai_score,
                passed=ai_score >= 60,
                detail_json={
                    "task_achievement": score_task,
                    "grammar": score_grammar,
                    "vocabulary": score_vocab,
                    "coherence": score_coherence,
                },
            )

            Notification.objects.create(
                user_id=sub.user_id,
                notification_type="grading_done",
                title="Bài Writing đã được chấm!",
                message=f"Điểm của bạn: {fmt_score(ai_score)} / 100",
                reference_id=sub.pk,
                reference_type="writing_submission",
            )

        except Exception as exc:
            elapsed = int((time.perf_counter() - t_start) * 1000)
            logger.error(
                "grade_writing_task FAILED | sub=%s attempt=%d err=%s elapsed=%dms",
                submission_id, self.request.retries + 1, str(exc), elapsed,
            )
            sub.status = "failed"
            sub.save(update_fields=["status"])
            _update_ai_grading_job(job, "failed", error=str(exc))
            raise self.retry(exc=exc)
