"""apps/grammar/views.py"""
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from utils.pagination import StandardPagination
from .models import GrammarTopic
from .serializers import GrammarTopicDetailSerializer, GrammarTopicListSerializer

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
