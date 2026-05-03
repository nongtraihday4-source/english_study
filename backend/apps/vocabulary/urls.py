"""apps/vocabulary/urls.py"""
from django.urls import path

from .views import (
    DeckStudyHistoryView,
    DeckWordBrowserView,
    FlashcardAddWordView,
    FlashcardDeckListView,
    FlashcardQuizView,
    FlashcardRemoveWordView,
    FlashcardStudyView,
    MultiDeckQuizView,
    SM2UpdateView,
    StudySessionCompleteView,
    ToggleMasteredView,
    WordDetailView,
    WordFlashcardStatusView,
    WordListView,
)

urlpatterns = [
    path("words/", WordListView.as_view(), name="word-list"),
    path("words/<int:pk>/", WordDetailView.as_view(), name="word-detail"),
    path("words/<int:pk>/flashcard-status/", WordFlashcardStatusView.as_view(), name="word-flashcard-status"),
    path("flashcard-decks/", FlashcardDeckListView.as_view(), name="flashcard-deck-list"),
    path("flashcard-decks/<int:pk>/study/", FlashcardStudyView.as_view(), name="flashcard-study"),
    path("flashcard-decks/<int:pk>/words/", DeckWordBrowserView.as_view(), name="flashcard-deck-words"),
    path("flashcard-decks/<int:pk>/words/toggle-mastered/", ToggleMasteredView.as_view(), name="flashcard-toggle-mastered"),
    path("flashcard-decks/<int:pk>/session-complete/", StudySessionCompleteView.as_view(), name="flashcard-session-complete"),
    path("flashcard-decks/<int:pk>/history/", DeckStudyHistoryView.as_view(), name="flashcard-deck-history"),
    path("flashcard-decks/<int:pk>/quiz/", FlashcardQuizView.as_view(), name="flashcard-deck-quiz"),
    path("flashcards/add-word/", FlashcardAddWordView.as_view(), name="flashcard-add-word"),
    path("flashcards/remove-word/", FlashcardRemoveWordView.as_view(), name="flashcard-remove-word"),
    path("flashcards/sm2/", SM2UpdateView.as_view(), name="flashcard-sm2"),
    path("quiz/generate/", MultiDeckQuizView.as_view(), name="flashcard-quiz-generate"),
]
