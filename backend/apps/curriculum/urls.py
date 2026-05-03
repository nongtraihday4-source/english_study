"""apps/curriculum/urls.py"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CEFRLevelListView, ChapterListView, CourseViewSet, LessonContentView, LessonDetailView, LessonListView

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("cefr-levels/", CEFRLevelListView.as_view(), name="cefr-levels"),
    path("", include(router.urls)),
    path("courses/<int:course_pk>/chapters/", ChapterListView.as_view(), name="chapter-list"),
    path("courses/<int:course_pk>/chapters/<int:chapter_pk>/lessons/", LessonListView.as_view(), name="lesson-list"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
    path("lessons/<int:pk>/content/", LessonContentView.as_view(), name="lesson-content"),
]
