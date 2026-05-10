"""apps/grammar/urls.py"""
from django.urls import path
from .views import (
    GrammarChapterListView,
    GrammarProgressView,
    GrammarQuizSubmitView,
    GrammarTopicDetailView,
    GrammarTopicListView,
    GrammarQuizRetrieveView,
    GrammarReviewTodayView
)

app_name = "grammar"

urlpatterns = [
    path("", GrammarTopicListView.as_view(), name="topic-list"),
    path("chapters/", GrammarChapterListView.as_view(), name="chapter-list"),
    path("progress/", GrammarProgressView.as_view(), name="progress"),
    # ── Dynamic slug routes (cụ thể → chung) ────────────────────────────
    path("<slug:slug>/quiz/questions/", GrammarQuizRetrieveView.as_view(), name="quiz-questions"), # ← Route mới
    path("<slug:slug>/quiz/", GrammarQuizSubmitView.as_view(), name="quiz-submit"),
    path("<slug:slug>/", GrammarTopicDetailView.as_view(), name="topic-detail"),

    path("reviews/today/", GrammarReviewTodayView.as_view(), name="reviews-today"),
]
