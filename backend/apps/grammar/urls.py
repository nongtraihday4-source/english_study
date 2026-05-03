"""apps/grammar/urls.py"""
from django.urls import path
from .views import (
    GrammarChapterListView,
    GrammarProgressView,
    GrammarQuizSubmitView,
    GrammarTopicDetailView,
    GrammarTopicListView,
)

app_name = "grammar"

urlpatterns = [
    path("", GrammarTopicListView.as_view(), name="topic-list"),
    path("chapters/", GrammarChapterListView.as_view(), name="chapter-list"),
    path("progress/", GrammarProgressView.as_view(), name="progress"),
    path("<slug:slug>/", GrammarTopicDetailView.as_view(), name="topic-detail"),
    path("<slug:slug>/quiz/", GrammarQuizSubmitView.as_view(), name="quiz-submit"),
]
