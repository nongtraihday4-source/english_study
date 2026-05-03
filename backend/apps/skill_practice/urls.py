from django.urls import path

from .views import (
    DictationCheckView,
    OnDemandTTSView,
    PassageDetailView,
    PassageListView,
    ProgressSummaryView,
    ShadowingCompleteView,
    TopicListView,
)

urlpatterns = [
    # Topics
    path("topics/", TopicListView.as_view(), name="skill-practice-topics"),

    # Passage list + detail
    path("passages/", PassageListView.as_view(), name="skill-practice-passages"),
    path("passages/<int:pk>/", PassageDetailView.as_view(), name="skill-practice-passage-detail"),

    # Dictation
    path("passages/<int:pk>/dictation/check/", DictationCheckView.as_view(), name="skill-practice-dictation-check"),

    # Shadowing
    path("passages/<int:pk>/shadowing/complete/", ShadowingCompleteView.as_view(), name="skill-practice-shadowing-complete"),

    # On-demand TTS fallback
    path("passages/<int:pk>/tts/<int:sentence_index>/", OnDemandTTSView.as_view(), name="skill-practice-tts"),

    # Progress summary
    path("progress/summary/", ProgressSummaryView.as_view(), name="skill-practice-progress-summary"),
]
