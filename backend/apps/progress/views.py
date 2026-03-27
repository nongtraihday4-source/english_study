"""
apps/progress/views.py
─────────────────────────────────────────────────────────────────────────────
POST /api/progress/enroll/                     → Enroll in a course
POST /api/progress/submit/listening/           → Auto-graded immediately
POST /api/progress/submit/reading/             → Auto-graded immediately
POST /api/progress/submit/speaking/            → Enqueues Celery AI task
POST /api/progress/submit/writing/             → Enqueues Celery AI task
GET  /api/progress/lessons/<lesson_pk>/        → Lesson progress status
GET  /api/dashboard/                           → Dashboard stats
─────────────────────────────────────────────────────────────────────────────
"""
import logging

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from utils.formatters import fmt_vn
from .grading import AutoGrader
from .models import (
    AIGradingJob,
    CumulativeScore,
    DailyStreak,
    ExerciseResult,
    LessonProgress,
    SpeakingSubmission,
    UserEnrollment,
    WritingSubmission,
)
from .serializers import (
    CumulativeScoreSerializer,
    DailyStreakSerializer,
    DashboardStatsSerializer,
    ExerciseResultSerializer,
    LessonProgressSerializer,
    SpeakingSubmissionSerializer,
    SubmitListeningSerializer,
    SubmitExamSerializer,
    SubmitReadingSerializer,
    SubmitSpeakingSerializer,
    SubmitWritingSerializer,
    UserEnrollmentSerializer,
    WritingSubmissionSerializer,
)
from .tasks import grade_speaking_task, grade_writing_task

progress_logger = logging.getLogger("es.progress")


# ── Enrollment ────────────────────────────────────────────────────────────────

class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from apps.curriculum.models import Course

        course_id = request.data.get("course_id")
        if not course_id:
            return Response({"detail": "course_id là bắt buộc."}, status=400)

        try:
            course = Course.objects.get(pk=course_id, is_active=True)
        except Course.DoesNotExist:
            return Response({"detail": "Khóa học không tồn tại."}, status=404)

        enrollment, created = UserEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={"is_deleted": False},
        )
        if not created and enrollment.is_deleted:
            enrollment.is_deleted = False
            enrollment.save(update_fields=["is_deleted"])
            created = True

        progress_logger.info(
            "Enroll | user=%s course=%s new=%s", request.user.pk, course_id, created
        )
        return Response(
            UserEnrollmentSerializer(enrollment).data,
            status=201 if created else 200,
        )


# ── Submission views ──────────────────────────────────────────────────────────

class SubmitListeningView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "submission"

    def post(self, request):
        from apps.curriculum.models import Lesson
        from apps.exercises.models import ListeningExercise

        serializer = SubmitListeningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            lesson = Lesson.objects.get(pk=data["lesson_id"])
            exercise = ListeningExercise.objects.get(pk=data["exercise_id"])
        except (Lesson.DoesNotExist, ListeningExercise.DoesNotExist):
            return Response({"detail": "Bài học hoặc bài tập không tồn tại."}, status=404)

        result = AutoGrader.grade_listening(
            user=request.user,
            lesson=lesson,
            exercise=exercise,
            user_answers=data["answers"],
            time_spent_seconds=data.get("time_spent_seconds", 0),
        )
        return Response(ExerciseResultSerializer(result).data, status=201)


class SubmitReadingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "submission"

    def post(self, request):
        from apps.curriculum.models import Lesson
        from apps.exercises.models import ReadingExercise

        serializer = SubmitReadingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            lesson = Lesson.objects.get(pk=data["lesson_id"])
            exercise = ReadingExercise.objects.get(pk=data["exercise_id"])
        except (Lesson.DoesNotExist, ReadingExercise.DoesNotExist):
            return Response({"detail": "Bài học hoặc bài tập không tồn tại."}, status=404)

        result = AutoGrader.grade_reading(
            user=request.user,
            lesson=lesson,
            exercise=exercise,
            user_answers=data["answers"],
            time_spent_seconds=data.get("time_spent_seconds", 0),
        )
        return Response(ExerciseResultSerializer(result).data, status=201)


class SubmitExamView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "submission"

    def post(self, request):
        from apps.curriculum.models import Lesson
        from apps.exercises.models import ExamSet, Question

        serializer = SubmitExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            exam = ExamSet.objects.get(pk=data["exam_id"], is_active=True)
        except ExamSet.DoesNotExist:
            return Response({"detail": "Bài thi không tồn tại."}, status=404)

        lesson = None
        lesson_id = data.get("lesson_id")
        if lesson_id:
            try:
                lesson = Lesson.objects.get(pk=lesson_id)
            except Lesson.DoesNotExist:
                return Response({"detail": "Bài học không tồn tại."}, status=404)

        questions = list(
            Question.objects.filter(exercise_type="exam", exercise_id=exam.id)
            .prefetch_related("options")
            .order_by("order")
        )
        if not questions:
            return Response({"detail": "Bài thi chưa có câu hỏi."}, status=400)

        user_answers = data["answers"]
        detail = []
        total_points = 0
        earned_points = 0

        for q in questions:
            correct = q.correct_answers_json
            if not isinstance(correct, list):
                correct = [correct]
            correct_norm = [str(x) for x in correct]

            raw_ans = user_answers.get(str(q.id))
            if isinstance(raw_ans, list):
                ans_norm = [str(x) for x in raw_ans]
            elif raw_ans is None:
                ans_norm = []
            else:
                ans_norm = [str(raw_ans)]

            is_correct = sorted(ans_norm) == sorted(correct_norm)
            total_points += q.points
            if is_correct:
                earned_points += q.points

            detail.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "user_answer": raw_ans,
                "correct_answer": correct,
                "is_correct": is_correct,
                "points": q.points,
                "section": q.exercise_type,
            })

        score = round((earned_points / total_points) * 100) if total_points else 0
        passed = score >= exam.passing_score

        result = ExerciseResult.objects.create(
            user=request.user,
            lesson=lesson,
            exercise_type="exam",
            exercise_id=exam.id,
            score=score,
            passed=passed,
            time_spent_seconds=data.get("time_spent_seconds", 0),
            detail_json=detail,
        )
        return Response(ExerciseResultSerializer(result).data, status=201)


class SubmitSpeakingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "submission"
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        import uuid
        from django.conf import settings as django_settings
        from pathlib import Path
        from apps.curriculum.models import Lesson

        serializer = SubmitSpeakingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Resolve audio_s3_key: either provided directly (production) or
        # derived by saving the uploaded audio_file locally (dev / fallback).
        audio_key = data.get("audio_s3_key")
        if not audio_key:
            audio_file = data.get("audio_file")
            if not audio_file:
                return Response(
                    {"detail": "audio_s3_key hoặc audio_file là bắt buộc."},
                    status=400,
                )
            # Save to MEDIA_ROOT/speaking/
            ext = Path(audio_file.name).suffix or ".webm"
            filename = f"{uuid.uuid4().hex}{ext}"
            save_dir = Path(django_settings.MEDIA_ROOT) / "speaking"
            save_dir.mkdir(parents=True, exist_ok=True)
            saved_path = save_dir / filename
            with open(saved_path, "wb") as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            audio_key = f"speaking/{filename}"

        try:
            lesson = Lesson.objects.get(pk=data["lesson_id"])
        except Lesson.DoesNotExist:
            return Response({"detail": "Bài học không tồn tại."}, status=404)

        sub = SpeakingSubmission.objects.create(
            user=request.user,
            lesson=lesson,
            exercise_id=data["exercise_id"],
            audio_s3_key=audio_key,
            target_sentence=data["target_sentence"],
            status="pending",
        )

        # Enqueue Celery task
        try:
            task = grade_speaking_task.delay(sub.pk)
            AIGradingJob.objects.create(
                job_type="speaking",
                submission_id=sub.pk,
                celery_task_id=task.id,
                status="pending",
            )
            task_id = task.id
        except Exception as broker_exc:
            progress_logger.warning(
                "Celery broker unavailable for speaking sub=%s: %s", sub.pk, broker_exc
            )
            task_id = None

        progress_logger.info(
            "Speaking submitted | user=%s sub=%s task=%s",
            request.user.pk, sub.pk, task_id,
        )
        return Response(
            {"submission_id": sub.pk, "status": "pending", "message": "Bài đang được chấm..."},
            status=202,
        )


# ── Submission detail (result) for auto-graded exercises ─────────────────────

class ListeningResultView(generics.RetrieveAPIView):
    serializer_class = ExerciseResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExerciseResult.objects.filter(user=self.request.user, exercise_type="listening")


class ReadingResultView(generics.RetrieveAPIView):
    serializer_class = ExerciseResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExerciseResult.objects.filter(user=self.request.user, exercise_type="reading")


class ExamResultView(generics.RetrieveAPIView):
    serializer_class = ExerciseResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExerciseResult.objects.filter(user=self.request.user, exercise_type="exam")


class SubmitWritingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "submission"

    def post(self, request):
        from apps.curriculum.models import Lesson

        serializer = SubmitWritingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            lesson = Lesson.objects.get(pk=data["lesson_id"])
        except Lesson.DoesNotExist:
            return Response({"detail": "Bài học không tồn tại."}, status=404)

        content = data["content_text"]
        word_count = len(content.split())

        sub = WritingSubmission.objects.create(
            user=request.user,
            lesson=lesson,
            exercise_id=data["exercise_id"],
            content_text=content,
            word_count=word_count,
            status="pending",
        )

        try:
            task = grade_writing_task.delay(sub.pk)
            AIGradingJob.objects.create(
                job_type="writing",
                submission_id=sub.pk,
                celery_task_id=task.id,
                status="pending",
            )
            task_id = task.id
        except Exception as broker_exc:
            # Celery broker unavailable (e.g. Redis not running) — submission
            # saved; background grading will run when the worker comes online.
            progress_logger.warning(
                "Celery broker unavailable for writing sub=%s: %s", sub.pk, broker_exc
            )
            task_id = None

        progress_logger.info(
            "Writing submitted | user=%s sub=%s words=%d task=%s",
            request.user.pk, sub.pk, word_count, task_id,
        )
        return Response(
            {
                "submission_id": sub.pk,
                "word_count": word_count,
                "word_count_display": fmt_vn(word_count),
                "status": "pending",
                "message": "Bài đang được AI chấm...",
            },
            status=202,
        )


# ── Submission status (polling) ────────────────────────────────────────────────

class SpeakingSubmissionStatusView(generics.RetrieveAPIView):
    serializer_class = SpeakingSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SpeakingSubmission.objects.filter(user=self.request.user)


class WritingSubmissionStatusView(generics.RetrieveAPIView):
    serializer_class = WritingSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WritingSubmission.objects.filter(user=self.request.user)


# ── Lesson Progress ────────────────────────────────────────────────────────────

class LessonProgressView(generics.RetrieveAPIView):
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        lp, _ = LessonProgress.objects.get_or_create(
            user=self.request.user,
            lesson_id=self.kwargs["lesson_pk"],
            defaults={"status": "locked"},
        )
        return lp


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        streak = DailyStreak.objects.filter(user=user).first()
        cum_scores = CumulativeScore.objects.filter(user=user).select_related("level")
        enrollments = (
            UserEnrollment.objects.filter(user=user, is_deleted=False)
            .select_related("course__level")
            .order_by("-enrolled_at")[:5]
        )
        recent_results = (
            ExerciseResult.objects.filter(user=user)
            .order_by("-created_at")[:10]
        )

        from apps.gamification.models import XPLog
        total_xp = XPLog.objects.filter(user=user).values_list("xp_amount", flat=True)
        total_xp_sum = sum(total_xp)

        data = {
            "streak": streak,
            "cumulative_scores": cum_scores,
            "enrolled_courses": enrollments,
            "recent_results": recent_results,
            "total_xp": total_xp_sum,
            "total_xp_display": f"{fmt_vn(total_xp_sum)} XP",
        }
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)
