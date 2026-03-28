"""
apps/admin_portal/views.py
─────────────────────────────────────────────────────────────────────────────
GET  /api/v1/admin-portal/dashboard/             → KPI stats + activity feed
GET  /api/v1/admin-portal/courses/               → List all courses
POST /api/v1/admin-portal/courses/               → Create course
GET/PATCH/DELETE /api/v1/admin-portal/courses/<pk>/
GET  /api/v1/admin-portal/courses/<pk>/chapters/ → Chapters for a course
GET  /api/v1/admin-portal/courses/<pk>/chapters/<cpk>/lessons/
POST /api/v1/admin-portal/users/<pk>/ban/        → Toggle is_active (ban/unban)
─────────────────────────────────────────────────────────────────────────────
"""
import csv
import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from utils.permissions import IsAdmin
from apps.curriculum.models import CEFRLevel, Chapter, Course, Lesson, LessonExercise
from apps.grammar.models import GrammarTopic, GrammarRule, GrammarExample
from apps.payments.models import Coupon, PaymentTransaction, SubscriptionPlan, UserSubscription
from apps.exercises.models import ExamSet, ListeningExercise, ReadingExercise, SpeakingExercise, WritingExercise
from apps.progress.models import AIGradingJob, SpeakingSubmission, UserEnrollment, WritingSubmission
from apps.gamification.models import Achievement, Certificate, XPLog
from apps.notifications.models import Notification, NotificationTemplate

from .models import AuditLog, StaffPermission, SystemSetting
from .serializers import (
    AdminChapterSerializer,
    AdminCourseSerializer,
    AdminLessonSerializer,
    AdminPlanSerializer,
    AdminCouponSerializer,
    AdminTransactionSerializer,
    AdminSubscriptionSerializer,
    AdminExamSetSerializer,
    AdminListeningExerciseSerializer,
    AdminSpeakingExerciseSerializer,
    AdminReadingExerciseSerializer,
    AdminWritingExerciseSerializer,
    AdminListeningExerciseFullSerializer,
    AdminSpeakingExerciseFullSerializer,
    AdminReadingExerciseFullSerializer,
    AdminWritingExerciseFullSerializer,
    AdminLessonExerciseSerializer,
    AdminGrammarTopicSerializer,
    AdminGrammarRuleSerializer,
    AdminGrammarExampleSerializer,
    AdminGradingJobSerializer,
    AdminSpeakingSubmissionSerializer,
    AdminWritingSubmissionSerializer,
    AdminAchievementSerializer,
    AdminCertificateSerializer,
    AdminXPLogSerializer,
    AdminNotificationTemplateSerializer,
    AdminNotificationHistorySerializer,
    AdminStaffPermissionSerializer,
    AdminAuditLogSerializer,
    AdminSystemSettingSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")


def _log_action(request, action, model_name, object_id=None, description="", changes=None):
    try:
        AuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            changes_json=changes,
            ip_address=_get_client_ip(request),
        )
    except Exception as exc:
        logger.warning("AuditLog write failed: %s", exc)


class AuditLogMixin:
    """
    Mixin for DRF generic views that auto-log create / update / destroy.

    Class attributes (optional overrides):
        audit_model_name  – explicit model name; auto-detected from serializer if omitted.
        audit_label_field – instance field used in the description (default: 'name').

    Custom perform_* overrides can call  self._audit(action, obj)  directly.
    """
    audit_model_name: str = ""
    audit_label_field: str = "name"

    def _audit_model(self) -> str:
        if self.audit_model_name:
            return self.audit_model_name
        try:
            return self.get_serializer_class().Meta.model.__name__
        except Exception:
            return "Unknown"

    def _audit(self, action: str, obj, description: str = "") -> None:
        model = self._audit_model()
        label = str(getattr(obj, self.audit_label_field, getattr(obj, "pk", ""))) \
            if self.audit_label_field else str(getattr(obj, "pk", ""))
        desc = description or f"{action.capitalize()} {model} {label}"
        _log_action(self.request, action, model, getattr(obj, "pk", None), desc)

    def perform_create(self, serializer):
        obj = serializer.save()
        self._audit("create", obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        self._audit("update", obj)

    def perform_destroy(self, instance):
        # Capture label before delete
        self._audit("delete", instance)
        instance.delete()


# ── Dashboard ─────────────────────────────────────────────────────────────────

class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            total_users = User.objects.filter(is_deleted=False).count()
            new_today = User.objects.filter(
                is_deleted=False, date_joined__gte=today_start
            ).count()
            active_today = User.objects.filter(
                is_deleted=False, last_login__gte=today_start
            ).count()

            revenue_month = (
                PaymentTransaction.objects.filter(
                    status="success", created_at__gte=month_start
                ).aggregate(total=Sum("amount_vnd"))["total"]
                or 0
            )

            pending_speaking = SpeakingSubmission.objects.filter(
                status="pending", is_deleted=False
            ).count()
            pending_writing = WritingSubmission.objects.filter(
                status="pending", is_deleted=False
            ).count()

            total_courses = Course.objects.filter(is_active=True).count()

            # 7-day user growth
            user_growth = []
            for i in range(6, -1, -1):
                day = today_start - timedelta(days=i)
                day_end = day + timedelta(days=1)
                count = User.objects.filter(
                    is_deleted=False, date_joined__gte=day, date_joined__lt=day_end
                ).count()
                user_growth.append({"date": day.strftime("%d/%m"), "count": count})

            # Recent activity feed — convert datetimes to ISO string to avoid sort issues
            recent_signups = list(
                User.objects.filter(is_deleted=False)
                .order_by("-date_joined")
                .values("id", "email", "first_name", "last_name", "date_joined")[:5]
            )
            recent_payments = list(
                PaymentTransaction.objects.filter(status="success")
                .select_related("user", "plan")
                .order_by("-created_at")
                .values("id", "user__email", "plan__name", "amount_vnd", "created_at")[:5]
            )

            activity = []
            for s in recent_signups:
                ts = s["date_joined"]
                activity.append({
                    "type": "signup",
                    "icon": "👤",
                    "description": f"Người dùng mới: {s['email']}",
                    "timestamp": ts.isoformat() if hasattr(ts, 'isoformat') else str(ts),
                })
            for p in recent_payments:
                ts = p["created_at"]
                activity.append({
                    "type": "payment",
                    "icon": "💰",
                    "description": f"{p['user__email']} mua {p['plan__name']} ({int(p['amount_vnd']):,}đ)",
                    "timestamp": ts.isoformat() if hasattr(ts, 'isoformat') else str(ts),
                })
            activity.sort(key=lambda x: x["timestamp"], reverse=True)
            activity = activity[:10]

            return Response({
                "stats": {
                    "total_users": total_users,
                    "new_today": new_today,
                    "active_today": active_today,
                    "revenue_month": int(revenue_month),
                    "pending_submissions": pending_speaking + pending_writing,
                    "total_courses": total_courses,
                },
                "user_growth": user_growth,
                "recent_activity": activity,
            })
        except Exception as exc:
            logger.exception("AdminDashboardView error: %s", exc)
            return Response(
                {"detail": f"Lỗi server: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ── User ban/unban ─────────────────────────────────────────────────────────────

class AdminUserBanView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_deleted=False)
        except User.DoesNotExist:
            return Response({"detail": "Không tìm thấy người dùng."}, status=status.HTTP_404_NOT_FOUND)

        if user == request.user:
            return Response(
                {"detail": "Không thể tự khoá tài khoản của mình."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        action = "khoá" if not user.is_active else "mở khoá"
        return Response({"detail": f"Đã {action} tài khoản {user.email}.", "is_active": user.is_active})


# ── Courses ────────────────────────────────────────────────────────────────────

class AdminCourseListView(generics.ListCreateAPIView):
    serializer_class = AdminCourseSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return (
            Course.objects.select_related("level")
            .annotate(student_count=Count("enrollments", filter=Q(enrollments__is_deleted=False)))
            .order_by("level__order", "order")
        )


class AdminCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminCourseSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return (
            Course.objects.select_related("level")
            .annotate(student_count=Count("enrollments", filter=Q(enrollments__is_deleted=False)))
        )


# ── Chapters ───────────────────────────────────────────────────────────────────

class AdminChapterListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"

    def get_queryset(self):
        return (
            Chapter.objects.filter(course_id=self.kwargs["pk"])
            .annotate(lesson_count=Count("lessons"))
            .order_by("order")
        )

    def perform_create(self, serializer):
        obj = serializer.save(course_id=self.kwargs["pk"])
        self._audit("create", obj)


class AdminChapterDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"

    def get_queryset(self):
        return (
            Chapter.objects.filter(course_id=self.kwargs["course_pk"])
            .annotate(lesson_count=Count("lessons"))
        )


# ── Lessons ────────────────────────────────────────────────────────────────────

class AdminLessonListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminLessonSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"

    def get_queryset(self):
        return Lesson.objects.filter(
            chapter_id=self.kwargs["cpk"],
            chapter__course_id=self.kwargs["pk"],
        ).order_by("order")

    def perform_create(self, serializer):
        obj = serializer.save(chapter_id=self.kwargs["cpk"])
        self._audit("create", obj)


class AdminLessonDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminLessonSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"
    queryset = Lesson.objects.all()


# ── Lesson-Exercise binding ─────────────────────────────────────────────────────

class AdminLessonExerciseListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminLessonExerciseSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "exercise_type"

    def get_queryset(self):
        return LessonExercise.objects.filter(lesson_id=self.kwargs["pk"]).order_by("order")

    def perform_create(self, serializer):
        obj = serializer.save(lesson_id=self.kwargs["pk"])
        self._audit("create", obj)


class AdminLessonExerciseDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminLessonExerciseSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "exercise_type"

    def get_queryset(self):
        return LessonExercise.objects.filter(lesson_id=self.kwargs["lesson_pk"])


# ── Exercise type CRUD ─────────────────────────────────────────────────────────

_EXERCISE_TYPE_MAP = {
    "listening": (ListeningExercise, AdminListeningExerciseFullSerializer),
    "speaking":  (SpeakingExercise,  AdminSpeakingExerciseFullSerializer),
    "reading":   (ReadingExercise,   AdminReadingExerciseFullSerializer),
    "writing":   (WritingExercise,   AdminWritingExerciseFullSerializer),
}


class AdminExerciseTypeListView(AuditLogMixin, APIView):
    """GET/POST /admin-portal/exercises/<exercise_type>/"""
    permission_classes = [IsAdmin]
    audit_label_field = "title"

    def _get_parts(self, exercise_type):
        parts = _EXERCISE_TYPE_MAP.get(exercise_type)
        if not parts:
            return None, None
        return parts

    def get(self, request, exercise_type):
        model_cls, serializer_cls = self._get_parts(exercise_type)
        if model_cls is None:
            return Response({"detail": "Loại bài tập không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        qs = model_cls.objects.all()
        level = request.query_params.get("level")
        if level:
            qs = qs.filter(cefr_level=level)
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        qs = qs.order_by("-created_at")
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            return paginator.get_paginated_response(serializer_cls(page, many=True).data)
        return Response(serializer_cls(qs, many=True).data)

    def post(self, request, exercise_type):
        model_cls, serializer_cls = self._get_parts(exercise_type)
        if model_cls is None:
            return Response({"detail": "Loại bài tập không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_cls(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        _log_action(request, "create", model_cls.__name__, obj.pk, f"Create {exercise_type} exercise: {obj.title}")
        return Response(serializer_cls(obj).data, status=status.HTTP_201_CREATED)


class AdminExerciseTypeDetailView(AuditLogMixin, APIView):
    """GET/PATCH/DELETE /admin-portal/exercises/<exercise_type>/<pk>/"""
    permission_classes = [IsAdmin]

    def _get_obj(self, exercise_type, pk):
        parts = _EXERCISE_TYPE_MAP.get(exercise_type)
        if not parts:
            return None, None, None
        model_cls, serializer_cls = parts
        return model_cls, serializer_cls, get_object_or_404(model_cls, pk=pk)

    def get(self, request, exercise_type, pk):
        model_cls, serializer_cls, obj = self._get_obj(exercise_type, pk)
        if model_cls is None:
            return Response({"detail": "Loại bài tập không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer_cls(obj).data)

    def patch(self, request, exercise_type, pk):
        model_cls, serializer_cls, obj = self._get_obj(exercise_type, pk)
        if model_cls is None:
            return Response({"detail": "Loại bài tập không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_cls(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        _log_action(request, "update", model_cls.__name__, obj.pk, f"Update {exercise_type} exercise: {obj.title}")
        return Response(serializer_cls(obj).data)

    def delete(self, request, exercise_type, pk):
        model_cls, serializer_cls, obj = self._get_obj(exercise_type, pk)
        if model_cls is None:
            return Response({"detail": "Loại bài tập không hợp lệ."}, status=status.HTTP_400_BAD_REQUEST)
        _log_action(request, "delete", model_cls.__name__, obj.pk, f"Delete {exercise_type} exercise: {obj.title}")
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Grammar admin CRUD ──────────────────────────────────────────────────────────

class AdminGrammarTopicListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminGrammarTopicSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = GrammarTopic.objects.prefetch_related("rules").order_by("level", "order")
        level = self.request.query_params.get("level")
        if level:
            qs = qs.filter(level=level)
        chapter = self.request.query_params.get("chapter")
        if chapter:
            qs = qs.filter(chapter__icontains=chapter)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        return qs


class AdminGrammarTopicDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminGrammarTopicSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"
    queryset = GrammarTopic.objects.prefetch_related("rules")


class AdminGrammarRuleListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminGrammarRuleSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"

    def get_queryset(self):
        return GrammarRule.objects.filter(topic_id=self.kwargs["topic_pk"]).order_by("order")

    def perform_create(self, serializer):
        obj = serializer.save(topic_id=self.kwargs["topic_pk"])
        self._audit("create", obj)


class AdminGrammarRuleDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminGrammarRuleSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"

    def get_queryset(self):
        return GrammarRule.objects.filter(topic_id=self.kwargs["topic_pk"])


class AdminGrammarExampleListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminGrammarExampleSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "sentence"

    def get_queryset(self):
        return GrammarExample.objects.filter(rule_id=self.kwargs["rule_pk"])

    def perform_create(self, serializer):
        obj = serializer.save(rule_id=self.kwargs["rule_pk"])
        self._audit("create", obj)


class AdminGrammarExampleDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminGrammarExampleSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "sentence"

    def get_queryset(self):
        return GrammarExample.objects.filter(rule_id=self.kwargs["rule_pk"])


# ── CEFRLevels (for dropdowns) ─────────────────────────────────────────────────

class AdminCEFRLevelListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        levels = CEFRLevel.objects.filter(is_active=True).order_by("order").values(
            "id", "code", "name", "name_vi"
        )
        return Response(list(levels))


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENTS
# ─────────────────────────────────────────────────────────────────────────────

class AdminPlanListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminPlanSerializer
    permission_classes = [IsAdmin]
    queryset = SubscriptionPlan.objects.all().order_by("sort_order", "id")


class AdminPlanDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminPlanSerializer
    permission_classes = [IsAdmin]
    queryset = SubscriptionPlan.objects.all()


class AdminCouponListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminCouponSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "code"

    def get_queryset(self):
        qs = Coupon.objects.select_related("plan_restriction").all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(code__icontains=search)
        return qs.order_by("-created_at")


class AdminCouponDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminCouponSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "code"
    queryset = Coupon.objects.select_related("plan_restriction").all()


class AdminTransactionListView(generics.ListAPIView):
    serializer_class = AdminTransactionSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = PaymentTransaction.objects.select_related("user", "plan").order_by("-created_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        gateway = self.request.query_params.get("gateway")
        if gateway:
            qs = qs.filter(gateway=gateway)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(user__email__icontains=search) | Q(gateway_txn_id__icontains=search))
        return qs


class AdminSubscriptionListView(generics.ListAPIView):
    serializer_class = AdminSubscriptionSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = UserSubscription.objects.select_related("user", "plan").order_by("-updated_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(user__email__icontains=search)
        return qs


class AdminSubscriptionExtendView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        sub = get_object_or_404(UserSubscription, pk=pk)
        try:
            days = int(request.data.get("days", 30))
            if days <= 0 or days > 3650:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"detail": "days phải là số nguyên 1-3650."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        base = sub.expires_at if (sub.expires_at and sub.expires_at > now) else now
        sub.expires_at = base + timedelta(days=days)
        sub.status = "active"
        sub.save(update_fields=["expires_at", "status"])
        _log_action(request, "update", "UserSubscription", sub.id,
                    f"Extended subscription for {sub.user.email} by {days} days")
        return Response({
            "detail": f"Đã gia hạn {days} ngày.",
            "expires_at": sub.expires_at.isoformat(),
        })


# ─────────────────────────────────────────────────────────────────────────────
# ASSESSMENTS
# ─────────────────────────────────────────────────────────────────────────────

class AdminExamSetListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminExamSetSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination
    audit_label_field = "title"

    def get_queryset(self):
        qs = ExamSet.objects.select_related("created_by").order_by("-created_at")
        for field in ("skill", "cefr_level", "exam_type", "is_active"):
            val = self.request.query_params.get(field)
            if val is not None:
                if field == "is_active":
                    qs = qs.filter(is_active=val.lower() == "true")
                else:
                    qs = qs.filter(**{field: val})
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def perform_create(self, serializer):
        # ExamSet requires created_by from the request user
        obj = serializer.save(created_by=self.request.user)
        self._audit("create", obj)


class AdminExamSetDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminExamSetSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "title"
    queryset = ExamSet.objects.select_related("created_by").all()


class AdminExerciseListView(APIView):
    """GET /admin-portal/exercises/?type=listening|speaking|reading|writing&level=A1"""
    permission_classes = [IsAdmin]

    _TYPE_MAP = {
        "listening": (ListeningExercise, AdminListeningExerciseSerializer),
        "speaking":  (SpeakingExercise,  AdminSpeakingExerciseSerializer),
        "reading":   (ReadingExercise,   AdminReadingExerciseSerializer),
        "writing":   (WritingExercise,   AdminWritingExerciseSerializer),
    }

    def get(self, request):
        ex_type = request.query_params.get("type", "listening")
        if ex_type not in self._TYPE_MAP:
            return Response({"detail": "type phải là listening/speaking/reading/writing."},
                            status=status.HTTP_400_BAD_REQUEST)
        model_cls, serializer_cls = self._TYPE_MAP[ex_type]
        qs = model_cls.objects.all()
        level = request.query_params.get("level")
        if level:
            qs = qs.filter(cefr_level=level)
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        qs = qs.order_by("-created_at")[:100]
        return Response(serializer_cls(qs, many=True).data)


# ─────────────────────────────────────────────────────────────────────────────
# AI GRADING
# ─────────────────────────────────────────────────────────────────────────────

class AdminGradingStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        jobs = AIGradingJob.objects
        stats = {
            "queued":     jobs.filter(status="queued").count(),
            "processing": jobs.filter(status="processing").count(),
            "completed":  jobs.filter(status="completed").count(),
            "failed":     jobs.filter(status="failed").count(),
            "retrying":   jobs.filter(status="retrying").count(),
            "tokens_total": jobs.filter(status="completed")
                               .aggregate(t=Sum("tokens_used"))["t"] or 0,
        }
        return Response(stats)


class AdminGradingJobListView(generics.ListAPIView):
    serializer_class = AdminGradingJobSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = AIGradingJob.objects.order_by("-queued_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        job_type = self.request.query_params.get("job_type")
        if job_type:
            qs = qs.filter(job_type=job_type)
        return qs


class AdminGradingJobRetryView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        job = get_object_or_404(AIGradingJob, pk=pk)
        if job.status not in ("failed", "retrying"):
            return Response({"detail": "Chỉ có thể retry job ở trạng thái failed/retrying."},
                            status=status.HTTP_400_BAD_REQUEST)
        job.status = "queued"
        job.retry_count += 1
        job.error_message = ""
        job.save(update_fields=["status", "retry_count", "error_message"])
        _log_action(request, "update", "AIGradingJob", job.id, f"Retried grading job {job.id}")
        # If Celery task function exists, dispatch here (import guarded)
        try:
            if job.job_type == "speaking":
                from apps.progress.tasks import grade_speaking_submission
                grade_speaking_submission.delay(job.submission_id)
            else:
                from apps.progress.tasks import grade_writing_submission
                grade_writing_submission.delay(job.submission_id)
        except ImportError:
            pass  # Celery tasks may not exist; job is re-queued for worker pickup
        return Response({"detail": "Đã đưa job vào hàng chờ retry."})


class AdminSpeakingSubmissionListView(generics.ListAPIView):
    serializer_class = AdminSpeakingSubmissionSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = SpeakingSubmission.objects.select_related("user").filter(
            is_deleted=False
        ).order_by("-submitted_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(user__email__icontains=search)
        return qs


class AdminWritingSubmissionListView(generics.ListAPIView):
    serializer_class = AdminWritingSubmissionSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = WritingSubmission.objects.select_related("user").filter(
            is_deleted=False
        ).order_by("-submitted_at")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(user__email__icontains=search)
        return qs


# ─────────────────────────────────────────────────────────────────────────────
# GAMIFICATION
# ─────────────────────────────────────────────────────────────────────────────

class AdminAchievementListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminAchievementSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = Achievement.objects.all().order_by("category", "threshold_value")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs


class AdminAchievementDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminAchievementSerializer
    permission_classes = [IsAdmin]
    queryset = Achievement.objects.all()


class AdminCertificateListView(generics.ListAPIView):
    serializer_class = AdminCertificateSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Certificate.objects.select_related("user", "course", "level").order_by("-issued_at")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(user__email__icontains=search)
        is_valid = self.request.query_params.get("is_valid")
        if is_valid is not None:
            qs = qs.filter(is_valid=is_valid.lower() == "true")
        return qs


class AdminXPLogListView(generics.ListAPIView):
    serializer_class = AdminXPLogSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = XPLog.objects.select_related("user").order_by("-created_at")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(user__email__icontains=search)
        return qs


class AdminXPGrantView(APIView):
    """POST /admin-portal/xp-log/grant/  { user_id, amount, source, description }"""
    permission_classes = [IsAdmin]

    def post(self, request):
        user_id = request.data.get("user_id")
        amount  = request.data.get("amount")
        source  = request.data.get("source", "admin_grant")
        description = request.data.get("description", "Admin manual XP grant")

        if not user_id or not amount:
            return Response({"detail": "user_id và amount là bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"detail": "amount phải là số nguyên dương."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, pk=user_id, is_deleted=False)
        log = XPLog.objects.create(user=user, amount=amount, source=source, description=description)
        user.total_xp = (user.total_xp or 0) + amount
        user.save(update_fields=["total_xp"])
        _log_action(request, "create", "XPLog", log.id,
                    f"Granted {amount} XP to {user.email}")
        return Response({"detail": f"Đã cộng {amount} XP cho {user.email}.", "xp_log_id": log.id})


# ─────────────────────────────────────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────

class AdminNotificationTemplateListView(generics.ListAPIView):
    serializer_class = AdminNotificationTemplateSerializer
    permission_classes = [IsAdmin]
    queryset = NotificationTemplate.objects.all().order_by("notification_type")


class AdminNotificationTemplateDetailView(AuditLogMixin, generics.RetrieveUpdateAPIView):
    serializer_class = AdminNotificationTemplateSerializer
    permission_classes = [IsAdmin]
    audit_label_field = "notification_type"
    queryset = NotificationTemplate.objects.all()
    lookup_field = "notification_type"

    def perform_update(self, serializer):
        # Also stamp updated_at before delegating to mixin audit
        obj = serializer.save(updated_at=timezone.now())
        self._audit("update", obj)


class AdminBroadcastNotificationView(APIView):
    """POST /admin-portal/notifications/broadcast/  { title, message, target: 'all'|'premium'|'free' }"""
    permission_classes = [IsAdmin]

    def post(self, request):
        title   = request.data.get("title", "").strip()
        message = request.data.get("message", "").strip()
        target  = request.data.get("target", "all")

        if not title or not message:
            return Response({"detail": "title và message là bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)
        if target not in ("all", "premium", "free"):
            return Response({"detail": "target phải là all/premium/free."}, status=status.HTTP_400_BAD_REQUEST)

        qs = User.objects.filter(is_active=True, is_deleted=False)
        if target == "premium":
            qs = qs.filter(subscriptions__status="active")
        elif target == "free":
            qs = qs.exclude(subscriptions__status="active")

        notifications = [
            Notification(user=u, title=title, message=message, notification_type="system_announcement")
            for u in qs
        ]
        Notification.objects.bulk_create(notifications, batch_size=500, ignore_conflicts=True)
        count = len(notifications)
        _log_action(request, "bulk_action", "Notification", description=f"Broadcast to {count} users (target={target})")
        return Response({"detail": f"Đã gửi thông báo tới {count} người dùng."})


class AdminNotificationHistoryView(generics.ListAPIView):
    serializer_class = AdminNotificationHistorySerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Notification.objects.select_related("user").order_by("-created_at")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(user__email__icontains=search) | Q(title__icontains=search))
        ntype = self.request.query_params.get("notification_type")
        if ntype:
            qs = qs.filter(notification_type=ntype)
        return qs


# ─────────────────────────────────────────────────────────────────────────────
# STAFF RBAC
# ─────────────────────────────────────────────────────────────────────────────

class AdminStaffPermissionView(APIView):
    """GET/PUT /admin-portal/staff/<pk>/permissions/"""
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        staff = get_object_or_404(User, pk=pk)
        perm, _ = StaffPermission.objects.get_or_create(user=staff)
        return Response(AdminStaffPermissionSerializer(perm).data)

    def put(self, request, pk):
        staff = get_object_or_404(User, pk=pk)
        perm, _ = StaffPermission.objects.get_or_create(user=staff)
        serializer = AdminStaffPermissionSerializer(perm, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        _log_action(request, "update", "StaffPermission", obj.id,
                    f"Updated permissions for {staff.email}")
        return Response(AdminStaffPermissionSerializer(obj).data)


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────────────────────────────────────

class AdminAuditLogListView(generics.ListAPIView):
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = AuditLog.objects.select_related("admin_user").order_by("-created_at")
        action = self.request.query_params.get("action")
        if action:
            qs = qs.filter(action=action)
        model_name = self.request.query_params.get("model_name")
        if model_name:
            qs = qs.filter(model_name__icontains=model_name)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(admin_user__email__icontains=search) | Q(description__icontains=search)
            )
        return qs


class AdminAuditLogExportView(APIView):
    """GET /admin-portal/audit-log/export/ → download filtered log as CSV"""
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = AuditLog.objects.select_related("admin_user").order_by("-created_at")
        action = request.query_params.get("action")
        if action:
            qs = qs.filter(action=action)
        model_name = request.query_params.get("model_name")
        if model_name:
            qs = qs.filter(model_name__icontains=model_name)
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(admin_user__email__icontains=search) | Q(description__icontains=search)
            )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="audit-log.csv"'
        writer = csv.writer(response)
        writer.writerow(["ID", "Thời gian", "Admin", "Hành động", "Model", "Object ID", "Mô tả", "IP"])
        for log in qs:
            writer.writerow([
                log.id,
                log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
                log.admin_user.email if log.admin_user else "",
                log.action,
                log.model_name,
                log.object_id or "",
                log.description,
                log.ip_address or "",
            ])
        return response


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

class AdminSystemSettingListView(generics.ListAPIView):
    serializer_class = AdminSystemSettingSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = SystemSetting.objects.all().order_by("category", "key")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs


class AdminSystemSettingDetailView(APIView):
    """GET/PATCH /admin-portal/settings/<key>/"""
    permission_classes = [IsAdmin]

    def get(self, request, key):
        setting = get_object_or_404(SystemSetting, key=key)
        return Response(AdminSystemSettingSerializer(setting).data)

    def patch(self, request, key):
        setting = get_object_or_404(SystemSetting, key=key)
        if not setting.is_editable:
            return Response({"detail": "Cài đặt này không thể chỉnh sửa."}, status=status.HTTP_403_FORBIDDEN)
        new_value = request.data.get("value")
        if new_value is None:
            return Response({"detail": "Trường value là bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)
        old_value = setting.value
        setting.value = str(new_value)
        setting.updated_by = request.user
        setting.updated_at = timezone.now()
        setting.save(update_fields=["value", "updated_by", "updated_at"])
        _log_action(request, "update", "SystemSetting", setting.id,
                    f"Setting {key}: {old_value} → {new_value}")
        return Response(AdminSystemSettingSerializer(setting).data)


# ─────────────────────────────────────────────────────────────────────────────
# REFUND REQUESTS (Admin review — created by support staff)
# ─────────────────────────────────────────────────────────────────────────────

class AdminRefundRequestListView(generics.ListAPIView):
    """Admin: list all refund requests with filter by status."""
    permission_classes = [IsAdmin]
    pagination_class = StandardPagination

    def get_queryset(self):
        from apps.support.models import RefundRequest
        qs = RefundRequest.objects.select_related(
            "transaction__user", "transaction__plan",
            "requested_by", "reviewed_by"
        ).order_by("-created_at")
        refund_status = self.request.query_params.get("status")
        if refund_status:
            qs = qs.filter(status=refund_status)
        return qs

    def get_serializer_class(self):
        from apps.support.serializers import RefundRequestSerializer
        return RefundRequestSerializer


class AdminRefundReviewView(APIView):
    """
    Admin: POST /admin-portal/refund-requests/<pk>/review/
    Body: { action: "approve" | "reject", notes: str }
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        from apps.support.models import RefundRequest
        from apps.support.serializers import RefundRequestSerializer
        refund = get_object_or_404(RefundRequest, pk=pk)

        if refund.status != "pending":
            return Response(
                {"detail": "Chỉ có thể duyệt yêu cầu có trạng thái 'pending'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = request.data.get("action")
        if action not in ("approve", "reject"):
            return Response(
                {"detail": "action phải là 'approve' hoặc 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notes = request.data.get("notes", "")
        refund.status = "approved" if action == "approve" else "rejected"
        refund.reviewed_by = request.user
        refund.reviewed_at = timezone.now()
        refund.notes = notes
        refund.save(update_fields=["status", "reviewed_by", "reviewed_at", "notes", "updated_at"])

        action_label = "Duyệt" if action == "approve" else "Từ chối"
        _log_action(
            request, "update", "RefundRequest", refund.id,
            f"{action_label} yêu cầu hoàn tiền #{refund.id} "
            f"({refund.amount_vnd}VND cho giao dịch #{refund.transaction_id})"
        )

        return Response(RefundRequestSerializer(refund).data)

