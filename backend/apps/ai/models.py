from django.db import models


class AIGradingLog(models.Model):
    submission_id = models.BigIntegerField(db_index=True)
    submission_type = models.CharField(max_length=20)
    prompt_hash = models.CharField(max_length=64)
    response_raw = models.TextField()
    score = models.SmallIntegerField(null=True)
    latency_ms = models.IntegerField()
    status = models.CharField(max_length=20, default="success")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_grading_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"AIGradingLog({self.submission_id}) [{self.status}]"