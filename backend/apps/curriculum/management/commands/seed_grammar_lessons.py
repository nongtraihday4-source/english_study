"""
Management command: seed_grammar_lessons
Links GrammarTopic records to curriculum Lesson records (type='grammar')
already created by seed_courses.

For each level, it finds all grammar Lesson rows in the relevant Course,
then assigns them to GrammarTopic.lesson (OneToOneField) in chapter order.

Matching strategy:
  - Level A1-B2: match by grammar chapter order within the curriculm chapter.
    Each curriculum chapter's grammar Lesson receives the first N unassigned
    GrammarTopics from the same CEFR level, respecting grammar chapter order.
  - Level C1: all 16 topics distributed sequentially across chapters.

Usage:
    python manage.py seed_grammar_lessons
    python manage.py seed_grammar_lessons --level B1
    python manage.py seed_grammar_lessons --clear   # unlink all then re-link
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.curriculum.models import CEFRLevel, Lesson
from apps.grammar.models import GrammarTopic

# Manual mapping: which grammar chapter name goes into which curriculum chapter (by order).
# Values are substrings matched against GrammarChapter.name (case-insensitive).
# If a curriculum chapter has no grammar match — the lesson is left as a free-standing
# grammar intro (uses first unmatched grammar topic).

GRAMMAR_CHAPTER_MAP = {
    "A1": {
        1:  "Present tenses",
        2:  "Articles, nouns",
        3:  "Present tenses",       # Daily Routines → present simple rules
        4:  "there and it",
        5:  "Articles, nouns",
        6:  "Present tenses",       # Weather → present continuous
        7:  "Questions",
        8:  "Future",
        9:  "Adjectives and adverbs",
        10: "Prepositions",
        11: "Past tenses",
        12: None,                   # Review chapter — no linked grammar topic
    },
    "A2": {
        1:  "Present tenses",
        2:  "Modals",
        3:  "Adjectives",
        4:  "Future",
        5:  "Articles, nouns",
        6:  "Conditionals",
        7:  "Future",
        8:  "Past tenses",
        9:  "Present tenses",       # present perfect
        10: "Adjectives",
        11: "Articles, nouns",
        12: "Modals",
        13: "Modals",
        14: "-ing and the infinitive",
        15: "Past tenses",
        16: "Questions",
    },
    "B1": {
        1:  "Present tenses",
        2:  "Conditionals",
        3:  "Passive",
        4:  "Relative clauses",
        5:  "Conditionals",
        6:  "Passive",
        7:  "Past tenses",
        8:  "Reported speech",
        9:  "Future",
        10: "Modals",
        11: "Adjectives",
        12: "Conjunctions",
        13: "Articles, nouns",
        14: "Passive",
        15: None,
    },
    "B2": {
        1:  "Conditionals",
        2:  "Reported speech",
        3:  "Modals",
        4:  "Inversion",
        5:  "Passive",
        6:  "Passive",
        7:  "Conditionals",
        8:  "Modals",
        9:  "Past tenses",
        10: "Passive",
        11: "Relative clauses",
        12: "-ing and the infinitive",
        13: "Conditionals",
        14: None,
    },
    "C1": {
        # C1 has no grammar chapters — topics distributed round-robin
    },
}


class Command(BaseCommand):
    help = "Link GrammarTopic records to curriculum grammar Lessons"

    def add_arguments(self, parser):
        parser.add_argument(
            "--level",
            dest="levels",
            action="append",
            choices=["A1", "A2", "B1", "B2", "C1"],
            default=None,
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Unlink all grammar topics from curriculum lessons before re-linking",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        levels = options["levels"] or ["A1", "A2", "B1", "B2", "C1"]

        for level_code in levels:
            if options["clear"]:
                unlinked = GrammarTopic.objects.filter(level=level_code).update(lesson=None)
                self.stdout.write(self.style.WARNING(f"  [{level_code}] Unlinked {unlinked} grammar topics"))

            try:
                cefr = CEFRLevel.objects.get(code=level_code)
            except CEFRLevel.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  [{level_code}] CEFRLevel not found — run seed_courses first"))
                continue

            # Find the course for this level (first one)
            course = cefr.courses.filter(is_active=True).first()
            if not course:
                self.stdout.write(self.style.WARNING(f"  [{level_code}] No active course found — run seed_courses first"))
                continue

            # Grammar lessons grouped by curriculum chapter order
            grammar_lessons = (
                Lesson.objects
                .filter(chapter__course=course, lesson_type="grammar")
                .select_related("chapter")
                .order_by("chapter__order", "order")
            )

            # All grammar topics for this level, ordered by chapter then position
            grammar_topics = (
                GrammarTopic.objects
                .filter(level=level_code, is_published=True)
                .select_related("chapter")
                .order_by("chapter__order", "order")
            )

            chapter_map = GRAMMAR_CHAPTER_MAP.get(level_code, {})
            linked = 0
            skipped = 0

            # C1 special case: no grammar chapters, distribute topics round-robin
            if level_code == "C1":
                unlinked_topics = [gt for gt in grammar_topics if gt.lesson_id is None]
                for i, gl in enumerate(grammar_lessons):
                    if i < len(unlinked_topics):
                        unlinked_topics[i].lesson = gl
                        unlinked_topics[i].save(update_fields=["lesson"])
                        linked += 1
                    else:
                        skipped += 1
            else:
                for gl in grammar_lessons:
                    ch_order = gl.chapter.order
                    hint = chapter_map.get(ch_order)
                    if hint is None:
                        skipped += 1
                        continue

                    # Find the first unlinked topic matching the hint
                    matched = None
                    for gt in grammar_topics:
                        if gt.lesson_id is not None:
                            continue  # already linked
                        ch_name = gt.chapter.name if gt.chapter else ""
                        if hint.lower() in ch_name.lower():
                            matched = gt
                            break

                    if matched:
                        matched.lesson = gl
                        matched.save(update_fields=["lesson"])
                        linked += 1
                    else:
                        skipped += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  [{level_code}] Linked: {linked} grammar topics, skipped: {skipped}"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nDone — seed_grammar_lessons complete."))
