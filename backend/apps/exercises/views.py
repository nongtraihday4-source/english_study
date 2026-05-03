"""
apps/exercises/views.py
Read-only exercise detail views + admin CRUD.
"""
from rest_framework import generics, permissions

from utils.permissions import IsAdmin, IsAdminOrReadOnly, IsPremium
from .models import ListeningExercise, ReadingExercise, SpeakingExercise, WritingExercise, ExamSet
from .serializers import (
    ListeningExerciseSerializer,
    ReadingExerciseSerializer,
    SpeakingExerciseSerializer,
    WritingExerciseSerializer,
    ExamSetListSerializer,
    ExamSetDetailSerializer,
)


class ListeningDetailView(generics.RetrieveAPIView):
    serializer_class = ListeningExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ListeningExercise.objects.all()


class SpeakingDetailView(generics.RetrieveAPIView):
    serializer_class = SpeakingExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SpeakingExercise.objects.all()


class ReadingDetailView(generics.RetrieveAPIView):
    serializer_class = ReadingExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ReadingExercise.objects.all()


class WritingDetailView(generics.RetrieveAPIView):
    serializer_class = WritingExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = WritingExercise.objects.all()


# ── ExamSet views ──────────────────────────────────────────────────────────────

class ExamListView(generics.ListAPIView):
    """GET /exercises/exams/ — list all active exams."""
    serializer_class = ExamSetListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ExamSet.objects.filter(is_active=True).order_by("exam_type", "cefr_level")
        exam_type = self.request.query_params.get("exam_type")
        if exam_type:
            qs = qs.filter(exam_type=exam_type)
        return qs


class ExamDetailView(generics.RetrieveAPIView):
    """GET /exercises/exams/:id/ — exam detail with questions."""
    serializer_class = ExamSetDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExamSet.objects.filter(is_active=True)
