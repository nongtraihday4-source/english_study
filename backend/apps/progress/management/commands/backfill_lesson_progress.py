"""
Backfill LessonProgress(available) for the first lesson of each chapter
for every existing UserEnrollment that has no LessonProgress rows yet.

Usage:
    python manage.py backfill_lesson_progress
    python manage.py backfill_lesson_progress --dry-run
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.progress.models import LessonProgress, UserEnrollment


class Command(BaseCommand):
    help = "Backfill missing LessonProgress rows for existing enrollments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview without writing to the database",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        from apps.curriculum.models import Chapter, Lesson

        enrollments = (
            UserEnrollment.objects
            .filter(is_deleted=False)
            .select_related("user", "course")
        )

        total_enrollments = enrollments.count()
        self.stdout.write(f"Found {total_enrollments} active enrollments")

        fixed = 0
        total_created = 0

        for enrollment in enrollments:
            user = enrollment.user
            course = enrollment.course

            # Check if this user already has any LessonProgress for this course
            existing = LessonProgress.objects.filter(
                user=user,
                lesson__chapter__course=course,
            ).exists()

            if existing:
                continue  # Already initialized

            # Collect first lesson of each chapter
            chapters = Chapter.objects.filter(course=course).order_by("order")
            to_create = []
            for chapter in chapters:
                first = (
                    Lesson.objects.filter(chapter=chapter, is_active=True)
                    .order_by("order")
                    .first()
                )
                if first:
                    to_create.append(
                        LessonProgress(user=user, lesson=first, status="available")
                    )

            if not to_create:
                continue

            self.stdout.write(
                f"  → user={user.pk} ({user.username}) course={course.pk} ({course.title}): "
                f"{len(to_create)} lessons to unlock"
            )

            if not dry_run:
                with transaction.atomic():
                    LessonProgress.objects.bulk_create(to_create, ignore_conflicts=True)

            fixed += 1
            total_created += len(to_create)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Would fix {fixed} enrollments, create {total_created} LessonProgress rows"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nDone: fixed {fixed} enrollments, created {total_created} LessonProgress rows"
                )
            )
