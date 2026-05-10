"""
apps/curriculum/views.py
Course & Lesson Management APIs (admin CRUD + student read-only).
"""

from .services.unlock_service import UnlockService
from .services.progress_service import ProgressService

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from utils.permissions import IsAdmin, IsAdminOrReadOnly, IsTeacher
from .models import CEFRLevel, Chapter, Course, Lesson, LessonContent
from .serializers import (
    CEFRLevelSerializer,
    ChapterSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseWriteSerializer,
    LessonContentSerializer,
    LessonSerializer,
)


class CEFRLevelListView(generics.ListAPIView):
    serializer_class = CEFRLevelSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CEFRLevel.objects.filter(is_active=True).order_by("order")


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["level__code", "is_premium"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        return Course.objects.select_related("level").filter(is_active=True).order_by("level__order", "created_at")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return CourseWriteSerializer
        return CourseListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ChapterListView(generics.ListCreateAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Chapter.objects.filter(
            course_id=self.kwargs["course_pk"],
        ).prefetch_related("lessons").order_by("order")

    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs["course_pk"])


class LessonListView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Lesson.objects.filter(
            chapter_id=self.kwargs["chapter_pk"],
            is_active=True,
        ).prefetch_related("unlock_rules").order_by("order")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Đánh giá queryset một lần để truyền vào service
        queryset = list(self.get_queryset())
        user = self.request.user
        
        # Batch resolve một lần duy nhất
        context["unlock_map"] = UnlockService.batch_check_unlocked(user, queryset)
        context["progress_map"] = ProgressService.batch_get_status(user, queryset)
        return context
    

class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Lesson.objects.filter(is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class LessonContentView(generics.RetrieveUpdateAPIView):
    """GET/PATCH the rich integrated content for a lesson."""
    serializer_class = LessonContentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        lesson = generics.get_object_or_404(
            Lesson.objects.filter(is_active=True), pk=self.kwargs["pk"]
        )
        content, _ = LessonContent.objects.get_or_create(lesson=lesson)
        return content
