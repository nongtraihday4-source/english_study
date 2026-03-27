from django.urls import path

from .views import (
    LessonCompleteView,
    LessonDetailBySlugView,
    LessonDetailView,
    MinimalPairSetDetailView,
    MinimalPairSetListView,
    PhonemeChartView,
    StageLessonsView,
    StageListView,
    TTSGenerateView,
)

urlpatterns = [
    path("stages/", StageListView.as_view(), name="pronunciation-stages"),
    path("stages/<int:pk>/lessons/", StageLessonsView.as_view(), name="pronunciation-stage-lessons"),
    # lesson detail: by id and by slug
    path("lessons/by-slug/<slug:slug>/", LessonDetailBySlugView.as_view(), name="pronunciation-lesson-by-slug"),
    path("lessons/<int:pk>/complete/", LessonCompleteView.as_view(), name="pronunciation-lesson-complete"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="pronunciation-lesson-detail"),
    path("phonemes/", PhonemeChartView.as_view(), name="pronunciation-phoneme-chart"),
    path("minimal-pairs/", MinimalPairSetListView.as_view(), name="pronunciation-minimal-pairs"),
    path("minimal-pairs/<int:pk>/", MinimalPairSetDetailView.as_view(), name="pronunciation-minimal-pair-detail"),
    path("tts/", TTSGenerateView.as_view(), name="tts-generate"),
]
