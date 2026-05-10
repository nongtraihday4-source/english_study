import logging

from celery import shared_task
from django.db import transaction

from .models import AIGradingLog
from .services.grading_service import GradingService

logger = logging.getLogger("es.grading")


@shared_task(bind=True, max_retries=3, soft_time_limit=30, time_limit=45)
def grade_submission_task(
    self, submission_id: int, submission_type: str, text: str, hint: str = ""
):
    try:
        logger.info(
            f"Starting grading for submission {submission_id} ({submission_type})"
        )

        result = GradingService.grade_writing(submission_id, text, hint)

        with transaction.atomic():
            AIGradingLog.objects.create(
                submission_id=submission_id,
                submission_type=submission_type,
                prompt_hash=result.get("prompt_hash", ""),
                response_raw=str(result),
                score=result.get("score"),
                latency_ms=result.get("latency_ms", 0),
                status=result.get("status", "unknown"),
            )

        logger.info(
            f"Grading complete for {submission_id}: "
            f"score={result['score']}, status={result['status']}"
        )
        return result

    except Exception as exc:
        logger.error(f"Grading failed for {submission_id}: {exc}")
        raise self.retry(exc=exc, countdown=5 * (3 ** self.request.retries))
