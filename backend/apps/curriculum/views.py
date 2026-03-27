"""
apps/curriculum/views.py
Course & Lesson Management APIs (admin CRUD + student read-only).
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from utils.permissions import IsAdmin, IsAdminOrReadOnly, IsTeacher
from .models import CEFRLevel, Chapter, Course, Lesson
from .serializers import (
    CEFRLevelSerializer,
    ChapterSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseWriteSerializer,
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

    def perform_create(self, serializer):
        serializer.save(chapter_id=self.kwargs["chapter_pk"])


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Lesson.objects.filter(is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
