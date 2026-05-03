"""apps/teacher/urls.py"""
from django.urls import path

from .views import (
    TeacherDashboardView,
    TeacherGradingQueueView,
    TeacherGradeSpeakingView,
    TeacherGradeWritingView,
    TeacherClassListView,
    TeacherClassStudentsView,
    TeacherExportClassView,
    TeacherAssignmentListView,
    TeacherAssignmentDetailView,
    TeacherAssignmentSubmissionsView,
)

urlpatterns = [
    path("dashboard/",                          TeacherDashboardView.as_view(),              name="teacher-dashboard"),
    path("grading-queue/",                      TeacherGradingQueueView.as_view(),           name="teacher-grading-queue"),
    path("grade/speaking/<int:pk>/",            TeacherGradeSpeakingView.as_view(),          name="teacher-grade-speaking"),
    path("grade/writing/<int:pk>/",             TeacherGradeWritingView.as_view(),           name="teacher-grade-writing"),
    path("classes/",                            TeacherClassListView.as_view(),              name="teacher-classes"),
    path("classes/<int:pk>/students/",          TeacherClassStudentsView.as_view(),          name="teacher-class-students"),
    path("classes/<int:pk>/export/",            TeacherExportClassView.as_view(),            name="teacher-class-export"),
    path("assignments/",                        TeacherAssignmentListView.as_view(),         name="teacher-assignment-list"),
    path("assignments/<int:pk>/",               TeacherAssignmentDetailView.as_view(),       name="teacher-assignment-detail"),
    path("assignments/<int:pk>/submissions/",   TeacherAssignmentSubmissionsView.as_view(),  name="teacher-assignment-submissions"),
]
