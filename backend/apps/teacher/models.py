"""
apps/teacher/models.py
─────────────────────────────────────────────────────────────────────────────
ClassAssignment: teacher assigns an ExamSet to students in a course
AssignmentStudent: explicit student list (when assign_to_all=False)
"""
from django.conf import settings
from django.db import models


class ClassAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignments_created",
    )
    course = models.ForeignKey(
        "curriculum.Course",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    exam_set = models.ForeignKey(
        "exercises.ExamSet",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    due_date = models.DateTimeField()
    assign_to_all = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teacher_classassignment"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} (course={self.course_id})"


class AssignmentStudent(models.Model):
    """Explicit student list when assign_to_all=False."""
    assignment = models.ForeignKey(
        ClassAssignment,
        on_delete=models.CASCADE,
        related_name="students",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_to",
    )

    class Meta:
        db_table = "teacher_assignmentstudent"
        unique_together = ("assignment", "student")

    def __str__(self):
        return f"Assignment {self.assignment_id} → Student {self.student_id}"
