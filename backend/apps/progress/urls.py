"""apps/progress/urls.py"""
from django.urls import path

from .views import (
    DashboardView,
    EnrollView,
    ExamResultView,
    LessonProgressView,
    ListeningResultView,
    MarkLessonCompleteView,
    MyAssignmentsView,
    ReadingResultView,
    SpeakingSubmissionStatusView,
    SubmitListeningView,
    SubmitExamView,
    SubmitReadingView,
    SubmitSpeakingView,
    SubmitWritingView,
    WritingSubmissionStatusView,
)

urlpatterns = [
    path("enroll/", EnrollView.as_view(), name="progress-enroll"),
    path("dashboard/", DashboardView.as_view(), name="progress-dashboard"),
    # Submissions
    path("submit/listening/", SubmitListeningView.as_view(), name="submit-listening"),
    path("submit/exam/", SubmitExamView.as_view(), name="submit-exam"),
    path("submit/reading/", SubmitReadingView.as_view(), name="submit-reading"),
    path("submit/speaking/", SubmitSpeakingView.as_view(), name="submit-speaking"),
    path("submit/writing/", SubmitWritingView.as_view(), name="submit-writing"),
    # Status polling for async submissions
    path("submissions/speaking/<int:pk>/", SpeakingSubmissionStatusView.as_view(), name="speaking-status"),
    path("submissions/writing/<int:pk>/", WritingSubmissionStatusView.as_view(), name="writing-status"),
    # Detail for auto-graded submissions
    path("submissions/listening/<int:pk>/", ListeningResultView.as_view(), name="listening-result"),
    path("submissions/reading/<int:pk>/", ReadingResultView.as_view(), name="reading-result"),
    path("submissions/exam/<int:pk>/", ExamResultView.as_view(), name="exam-result"),
    # Lesson progress
    path("lessons/<int:lesson_pk>/", LessonProgressView.as_view(), name="lesson-progress"),
    path("lessons/<int:lesson_pk>/complete/", MarkLessonCompleteView.as_view(), name="lesson-complete"),
    # Student: my assignments
    path("my-assignments/", MyAssignmentsView.as_view(), name="my-assignments"),
]
