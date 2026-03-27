"""apps/exercises/urls.py"""
from django.urls import path

from .views import ListeningDetailView, ReadingDetailView, SpeakingDetailView, WritingDetailView, ExamListView, ExamDetailView

urlpatterns = [
    path("listening/<int:pk>/", ListeningDetailView.as_view(), name="exercise-listening"),
    path("speaking/<int:pk>/", SpeakingDetailView.as_view(), name="exercise-speaking"),
    path("reading/<int:pk>/", ReadingDetailView.as_view(), name="exercise-reading"),
    path("writing/<int:pk>/", WritingDetailView.as_view(), name="exercise-writing"),
    path("exams/", ExamListView.as_view(), name="exam-list"),
    path("exams/<int:pk>/", ExamDetailView.as_view(), name="exam-detail"),
]
