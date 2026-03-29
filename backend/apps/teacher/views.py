"""
apps/teacher/views.py
─────────────────────────────────────────────────────────────────────────────
GET  /api/v1/teacher/dashboard/             → Stats overview
GET  /api/v1/teacher/grading-queue/         → Pending/all submissions (Speaking + Writing)
POST /api/v1/teacher/grade/speaking/<pk>/   → Grade a SpeakingSubmission
POST /api/v1/teacher/grade/writing/<pk>/    → Grade a WritingSubmission
GET  /api/v1/teacher/classes/               → Courses with enrolled student count
GET  /api/v1/teacher/classes/<pk>/students/ → Enrolled students + progress for a course
─────────────────────────────────────────────────────────────────────────────
"""
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
import csv
import io

from utils.permissions import IsTeacher
from apps.progress.models import SpeakingSubmission, WritingSubmission, UserEnrollment
from apps.curriculum.models import Course

from .serializers import (
    SpeakingSubmissionTeacherSerializer,
    WritingSubmissionTeacherSerializer,
    TeacherGradeSerializer,
    StudentProgressSerializer,
)

User = get_user_model()


class TeacherDashboardView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        pending_speaking = SpeakingSubmission.objects.filter(
            status="pending", is_deleted=False
        ).count()
        pending_writing = WritingSubmission.objects.filter(
            status="pending", is_deleted=False
        ).count()

        total_students = User.objects.filter(
            role="student", is_active=True, is_deleted=False
        ).count()

        # Unique active courses (as proxy for "classes")
        active_courses = Course.objects.filter(is_active=True).count()

        # Recent 10 graded submissions avg score
        avg_speaking = SpeakingSubmission.objects.filter(
            status="completed", ai_score__isnull=False
        ).aggregate(avg=Avg("ai_score"))["avg"] or 0

        avg_writing = WritingSubmission.objects.filter(
            status="completed", ai_score__isnull=False
        ).aggregate(avg=Avg("ai_score"))["avg"] or 0

        # Score distribution buckets (0-59, 60-74, 75-89, 90-100)
        def score_dist(qs):
            total = qs.count()
            if not total:
                return []
            buckets = [
                {"label": "0–59",   "min": 0,  "max": 59},
                {"label": "60–74",  "min": 60, "max": 74},
                {"label": "75–89",  "min": 75, "max": 89},
                {"label": "90–100", "min": 90, "max": 100},
            ]
            result = []
            for b in buckets:
                count = qs.filter(ai_score__gte=b["min"], ai_score__lte=b["max"]).count()
                result.append({"label": b["label"], "count": count,
                                "percent": round(count / total * 100)})
            return result

        sp_dist = score_dist(
            SpeakingSubmission.objects.filter(status="completed", ai_score__isnull=False)
        )
        wr_dist = score_dist(
            WritingSubmission.objects.filter(status="completed", ai_score__isnull=False)
        )

        return Response({
            "pending_grading": pending_speaking + pending_writing,
            "pending_speaking": pending_speaking,
            "pending_writing": pending_writing,
            "total_students": total_students,
            "active_courses": active_courses,
            "avg_speaking_score": round(avg_speaking, 1),
            "avg_writing_score": round(avg_writing, 1),
            "speaking_score_distribution": sp_dist,
            "writing_score_distribution": wr_dist,
        })


class TeacherGradingQueueView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        status_filter = request.query_params.get("status", "pending")
        sub_type      = request.query_params.get("type", "all")   # speaking|writing|all
        search        = request.query_params.get("search", "").strip()
        sort          = request.query_params.get("sort", "-submitted_at")

        # Build queryset for both types
        sp_qs = SpeakingSubmission.objects.filter(is_deleted=False).select_related("user")
        wr_qs = WritingSubmission.objects.filter(is_deleted=False).select_related("user")

        if status_filter != "all":
            sp_qs = sp_qs.filter(status=status_filter)
            wr_qs = wr_qs.filter(status=status_filter)

        if search:
            sp_qs = sp_qs.filter(
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
            wr_qs = wr_qs.filter(
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )

        # Allowed sort fields
        _allowed = {"submitted_at", "-submitted_at", "ai_score", "-ai_score"}
        if sort not in _allowed:
            sort = "-submitted_at"

        speaking_data = []
        writing_data = []

        if sub_type in ("all", "speaking"):
            speaking_data = SpeakingSubmissionTeacherSerializer(
                sp_qs.order_by(sort)[:100], many=True
            ).data

        if sub_type in ("all", "writing"):
            writing_data = WritingSubmissionTeacherSerializer(
                wr_qs.order_by(sort)[:100], many=True
            ).data

        # Merge and re-sort by submitted_at desc
        merged = list(speaking_data) + list(writing_data)
        merged.sort(key=lambda x: x.get("submitted_at", ""), reverse=(sort.startswith("-")))

        return Response({
            "count": len(merged),
            "results": merged,
        })


class TeacherGradeSpeakingView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, pk):
        try:
            sub = SpeakingSubmission.objects.get(pk=pk, is_deleted=False)
        except SpeakingSubmission.DoesNotExist:
            return Response({"detail": "Không tìm thấy bài nộp."}, status=404)

        serializer = TeacherGradeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        sub.ai_score = data["score"]
        sub.feedback_vi = data["feedback"]
        sub.status = "completed"
        sub.graded_at = timezone.now()
        sub.save(update_fields=["ai_score", "feedback_vi", "status", "graded_at"])

        return Response(SpeakingSubmissionTeacherSerializer(sub).data)


class TeacherGradeWritingView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, pk):
        try:
            sub = WritingSubmission.objects.get(pk=pk, is_deleted=False)
        except WritingSubmission.DoesNotExist:
            return Response({"detail": "Không tìm thấy bài nộp."}, status=404)

        serializer = TeacherGradeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        sub.ai_score = data["score"]
        sub.feedback_text = data["feedback"]
        sub.status = "completed"
        sub.graded_at = timezone.now()
        sub.save(update_fields=["ai_score", "feedback_text", "status", "graded_at"])

        return Response(WritingSubmissionTeacherSerializer(sub).data)


class TeacherClassListView(APIView):
    """List all active courses with enrolled student count."""
    permission_classes = [IsTeacher]

    def get(self, request):
        courses = Course.objects.filter(is_active=True).select_related("level").annotate(
            student_count=Count(
                "enrollments",
                filter=Q(enrollments__is_deleted=False, enrollments__status="active"),
            )
        ).order_by("level__order", "title")

        data = [
            {
                "id": c.id,
                "title": c.title,
                "cefr_level": c.level.code,
                "student_count": c.student_count,
                "is_active": c.is_active,
            }
            for c in courses
        ]
        return Response({"count": len(data), "results": data})


class TeacherClassStudentsView(APIView):
    """List enrolled students + progress for a course."""
    permission_classes = [IsTeacher]

    def get(self, request, pk):
        try:
            course = Course.objects.select_related("level").get(pk=pk, is_active=True)
        except Course.DoesNotExist:
            return Response({"detail": "Khóa học không tồn tại."}, status=404)

        enrollments = (
            UserEnrollment.objects
            .filter(course=course, is_deleted=False)
            .select_related("user", "course")
            .order_by("user__last_name", "user__first_name")
        )

        serializer = StudentProgressSerializer(enrollments, many=True)
        return Response({
            "course": {"id": course.id, "title": course.title, "cefr_level": course.level.code},
            "count": enrollments.count(),
            "students": serializer.data,
        })


class TeacherExportClassView(APIView):
    """Export class students + progress as CSV."""
    permission_classes = [IsTeacher]

    def get(self, request, pk):
        try:
            course = Course.objects.select_related("level").get(pk=pk, is_active=True)
        except Course.DoesNotExist:
            return Response({"detail": "Khóa học không tồn tại."}, status=404)

        enrollments = (
            UserEnrollment.objects
            .filter(course=course, is_deleted=False)
            .select_related("user")
            .order_by("user__last_name", "user__first_name")
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Họ tên", "Email", "Tiến độ (%)", "Ngày đăng ký", "Trạng thái"])
        for e in enrollments:
            u = e.user
            writer.writerow([
                f"{u.last_name} {u.first_name}".strip() or u.email,
                u.email,
                float(e.progress_percent) if e.progress_percent is not None else 0,
                e.enrolled_at.strftime("%d/%m/%Y") if e.enrolled_at else "",
                e.status,
            ])

        response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = f'attachment; filename="class_{pk}_students.csv"'
        return response
