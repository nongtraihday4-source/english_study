from django.contrib import admin

from .models import AIGradingJob, ExerciseResult, LessonProgress, SpeakingSubmission, UserEnrollment, WritingSubmission


@admin.register(UserEnrollment)
class UserEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["user", "course", "progress_percent", "enrolled_at", "completed_at"]
    list_filter = ["course__level"]
    search_fields = ["user__email", "course__title"]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "lesson", "status", "best_score", "attempts_count"]
    list_filter = ["status"]
    search_fields = ["user__email"]


@admin.register(ExerciseResult)
class ExerciseResultAdmin(admin.ModelAdmin):
    list_display = ["user", "exercise_type", "exercise_id", "score", "passed", "created_at"]
    list_filter = ["exercise_type", "passed"]


@admin.register(SpeakingSubmission)
class SpeakingSubmissionAdmin(admin.ModelAdmin):
    list_display = ["user", "exercise_id", "status", "ai_score", "submitted_at"]
    list_filter = ["status"]
    readonly_fields = ["transcript", "error_list_json"]


@admin.register(WritingSubmission)
class WritingSubmissionAdmin(admin.ModelAdmin):
    list_display = ["user", "exercise_id", "status", "ai_score", "word_count", "submitted_at"]
    list_filter = ["status"]
    readonly_fields = ["feedback_text", "error_list_json", "vocab_cefr_json"]


@admin.register(AIGradingJob)
class AIGradingJobAdmin(admin.ModelAdmin):
    list_display = ["job_type", "submission_id", "status", "retry_count", "tokens_used", "queued_at"]
    list_filter = ["job_type", "status"]
