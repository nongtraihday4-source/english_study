"""apps/grammar/views.py"""
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.pagination import StandardPagination
from .models import GrammarQuizResult, GrammarTopic
from .serializers import (
    GrammarQuizResultSerializer,
    GrammarQuizSubmitSerializer,
    GrammarTopicDetailSerializer,
    GrammarTopicListSerializer,
)

logger = logging.getLogger("es.curriculum")


class GrammarTopicListView(ListAPIView):
    """
    GET /api/v1/grammar/
    GET /api/v1/grammar/?level=A1
    GET /api/v1/grammar/?level=B1&page=2

    Returns paginated list of published grammar topics.
    Cache 5 minutes per level (public content, rarely changes).
    """
    serializer_class = GrammarTopicListSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = GrammarTopic.objects.filter(is_published=True).order_by("level", "order")
        level = self.request.query_params.get("level")
        if level:
            qs = qs.filter(level=level.upper())
        logger.debug(
            "GrammarTopicList | user=%s level=%s",
            getattr(self.request.user, "pk", None), level,
        )
        return qs


class GrammarTopicDetailView(RetrieveAPIView):
    """
    GET /api/v1/grammar/<slug>/

    Returns a grammar topic with all rules and examples.
    """
    serializer_class = GrammarTopicDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    queryset = GrammarTopic.objects.filter(is_published=True).prefetch_related(
        "rules", "rules__examples"
    )

    def get_object(self):
        obj = super().get_object()
        logger.debug(
            "GrammarTopicDetail | user=%s slug=%s level=%s",
            getattr(self.request.user, "pk", None),
            obj.slug, obj.level,
        )
        return obj


class GrammarQuizSubmitView(APIView):
    """
    POST /api/v1/grammar/<slug>/quiz/
    Body: { score, total_questions, correct_answers }

    Upserts quiz result for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        topic = GrammarTopic.objects.filter(slug=slug, is_published=True).first()
        if not topic:
            return Response({"detail": "Không tìm thấy chủ điểm."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GrammarQuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        result, _ = GrammarQuizResult.objects.update_or_create(
            user=request.user,
            topic=topic,
            defaults={
                "score": d["score"],
                "total_questions": d["total_questions"],
                "correct_answers": d["correct_answers"],
            },
        )
        return Response(GrammarQuizResultSerializer(result).data, status=status.HTTP_200_OK)


class GrammarProgressView(APIView):
    """
    GET /api/v1/grammar/progress/

    Returns all quiz results for the authenticated user,
    keyed by topic slug for easy lookup on the frontend.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = GrammarQuizResult.objects.filter(user=request.user).select_related("topic")
        data = {
            r.topic.slug: {
                "score": r.score,
                "total_questions": r.total_questions,
                "correct_answers": r.correct_answers,
                "attempted_at": r.attempted_at.isoformat(),
            }
            for r in results
        }
        return Response(data)
