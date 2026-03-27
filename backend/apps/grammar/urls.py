"""apps/grammar/urls.py"""
from django.urls import path
from .views import GrammarTopicDetailView, GrammarTopicListView

app_name = "grammar"

urlpatterns = [
    path("", GrammarTopicListView.as_view(), name="topic-list"),
    path("<slug:slug>/", GrammarTopicDetailView.as_view(), name="topic-detail"),
]
