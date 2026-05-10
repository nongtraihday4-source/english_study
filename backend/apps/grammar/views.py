"""apps/grammar/views.py"""
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from utils.pagination import StandardPagination
from .models import GrammarChapter, GrammarQuizResult, GrammarTopic
from .services import pregenerate_quiz,submit_quiz_attempt
from datetime import timedelta
from .models import GrammarReviewSchedule
from django.utils import timezone
from .serializers import (
    GrammarChapterSerializer,
    GrammarQuizResultSerializer,
    GrammarQuizSubmitSerializer,
    GrammarTopicDetailSerializer,
    GrammarTopicListSerializer,
    GrammarQuizQuestionSerializer,
    GrammarQuizSubmitInputSerializer
)

logger = logging.getLogger("es.curriculum")


class GrammarChapterListView(ListAPIView):
    """
    GET /api/v1/grammar/chapters/
    GET /api/v1/grammar/chapters/?level=A1

    Returns ordered list of grammar chapters (optionally filtered by level).
    """
    serializer_class = GrammarChapterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # always return full list

    def get_queryset(self):
        qs = GrammarChapter.objects.order_by("level", "order")
        level = self.request.query_params.get("level")
        if level:
            qs = qs.filter(level=level.upper())
        return qs


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
        qs = (
            GrammarTopic.objects
            .select_related("chapter")
            .filter(is_published=True)
            .order_by("level", "chapter__order", "order")
        )
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
    queryset = GrammarTopic.objects.filter(is_published=True).select_related("chapter").prefetch_related(
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
    Payload: { answers: [{question_source_id, selected_option}], idempotency_key? }
    Server-side validation & scoring. Idempotent.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        serializer = GrammarQuizSubmitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Idempotency check (tránh duplicate submit khi network lag)
        idem_key = serializer.validated_data.get("idempotency_key")
        if idem_key:
            cache_key = f"quiz_submit_idem:{request.user.id}:{slug}:{idem_key}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result, status=status.HTTP_200_OK)

        try:
            result_data = submit_quiz_attempt(
                user=request.user,
                topic_slug=slug,
                answers_payload=serializer.validated_data["answers"]
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Cache idempotency result 5 phút
        if idem_key:
            cache.set(cache_key, result_data, 300)
        return Response(result_data, status=status.HTTP_200_OK)

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

class GrammarQuizRetrieveView(APIView):
    """
    GET /api/v1/grammar/<slug>/quiz/questions/
    Returns pre-generated & cached quiz questions.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, slug):
        questions = pregenerate_quiz(slug)
        if not questions:
            return Response(
                {"detail": "Chưa có bài tập cho chủ điểm này."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = GrammarQuizQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GrammarReviewTodayView(APIView):
    """GET /api/v1/grammar/reviews/today/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        schedules = GrammarReviewSchedule.objects.filter(
            user=request.user, next_review__lte=today
        ).select_related("rule__topic").order_by("next_review")[:5]

        data = [
            {
                "rule_id": s.rule.id,
                "rule_title": s.rule.title,
                "topic_slug": s.rule.topic.slug,
                "topic_title": s.rule.topic.title,
                "interval_days": s.interval_days,
            }
            for s in schedules
        ]
        return Response({"reviews": data, "count": len(data)})