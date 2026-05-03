"""
Management command: seed_vocab_lessons
Creates a system FlashcardDeck per curriculum chapter and populates it with
Flashcard records for every Word whose topic appears in that chapter's
vocab_topics list.

Naming convention for system decks:
    FlashcardDeck.name  = chapter.title
    FlashcardDeck.cefr_level = course level code
    FlashcardDeck.owner = None  (system deck)

Usage:
    python manage.py seed_vocab_lessons
    python manage.py seed_vocab_lessons --level A2
    python manage.py seed_vocab_lessons --clear   # delete existing system decks for levels, then re-create
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.curriculum.models import CEFRLevel
from apps.vocabulary.models import Flashcard, FlashcardDeck, Word

# (level_code, chapter_order) → list of Word.topic strings that belong to this chapter
VOCAB_TOPIC_MAP = {
    # ── A2 ─────────────────────────────────────────────────────────────────
    ("A2", 1):  ["Daily Life - Daily Routines & Habits", "Daily Life - Personal Care & Hygiene"],
    ("A2", 2):  ["Daily Life - Housing & Accommodation", "Daily Life - Household Chores & Cleaning"],
    ("A2", 3):  ["Daily Life - Family & Relationships", "Daily Life - Emotions & Feelings"],
    ("A2", 4):  ["Daily Life - Weather & Climate"],
    ("A2", 5):  ["Daily Life - Shopping & Supermarket", "Daily Life - Supermarket Aisles & Groceries"],
    ("A2", 6):  ["Daily Life - Personal Finance, Taxes & Mortgages", "Daily Life - Banking & Personal Finance"],
    ("A2", 7):  ["Travel - Booking Flights & Hotels"],
    ("A2", 8):  ["Travel - At the Airport & Immigration", "Travel - Luggage & Packing"],
    ("A2", 9):  ["Travel - Sightseeing & Attractions", "Travel - Directions & Navigation"],
    ("A2", 10): ["Travel - Public Transportation", "Travel - Travel Emergencies & Problems"],
    ("A2", 11): ["Food - Cooking Methods & Recipes", "Food - At the Restaurant & Ordering"],
    ("A2", 12): ["Food - Ingredients & Spices", "Food - Diets & Nutrition", "Food - Beverages & Drinks"],
    ("A2", 13): ["Health - At the Hospital & Clinic", "Health - Symptoms & Illnesses", "Health - Medicines & Treatments"],
    ("A2", 14): ["Health - Fitness & Workout", "Daily Life - Cosmetics, Skincare & Grooming"],
    ("A2", 15): ["Life Events - Weddings & Marriage", "Life Events - Graduation & Anniversaries", "Life Events - Moving House & Relocation"],
    ("A2", 16): ["Communication - Small Talk & Icebreakers", "Communication - Complaining & Apologizing"],

    # ── B1 ─────────────────────────────────────────────────────────────────
    ("B1", 1):  ["Modern Career - Job Interviews & CVs"],
    ("B1", 2):  ["Modern Career - Remote Work & Telecommuting", "Modern Career - Freelancing & Gig Economy"],
    ("B1", 3):  ["Modern Career - Leadership & Management", "Modern Career - Business Presentations & Public Speaking"],
    ("B1", 4):  ["Modern Career - Startup & Entrepreneurship", "Modern Career - Networking & Professional Relationships"],
    ("B1", 5):  ["Digital Life - E-commerce & Online Shopping", "Digital Life - Social Media & Networking"],
    ("B1", 6):  ["Digital Life - Software Development & Coding", "Digital Life - Data Privacy & Cyber Ethics"],
    ("B1", 7):  ["Entertainment - Movies, Cinema & Oscars", "Entertainment - Music Genres & Concerts"],
    ("B1", 8):  ["Entertainment - Books, Literature & Publishing", "Entertainment - Fashion, Beauty & Trends"],
    ("B1", 9):  ["Leisure - Outdoor Activities & Camping", "Leisure - Sports Competitions & Olympics"],
    ("B1", 10): ["Social Trends - Mental Well-being & Self-care", "Social Trends - Personal Development & Productivity"],
    ("B1", 11): ["Social Trends - Veganism & Plant-based Diets", "Industry - Culinary Arts & Fine Dining"],
    ("B1", 12): ["Communication - Email Writing & Etiquette", "Communication - Negotiating & Persuading"],
    ("B1", 13): ["Society - Cultural Diversity & Inclusion", "Society - Gender Equality & Feminism"],
    ("B1", 14): ["Social Trends - Sustainability & Eco-friendly Living", "Trends - Eco-friendly Living & Zero Waste"],
    ("B1", 15): [],

    # ── B2 ─────────────────────────────────────────────────────────────────
    ("B2", 1):  ["TOEIC - Purchasing & Procurement", "TOEIC - Contracts & Legal Agreements"],
    ("B2", 2):  ["TOEIC - Board Meetings & Committees", "TOEIC - Corporate Planning & Strategy"],
    ("B2", 3):  ["TOEIC - Sales & Marketing", "TOEIC - Customer Service & Support"],
    ("B2", 4):  ["TOEIC - Human Resources & Recruiting", "TOEIC - Accounting & Finance"],
    ("B2", 5):  ["TOEIC - Manufacturing & Production", "TOEIC - Quality Control & Inspections"],
    ("B2", 6):  ["TOEIC - Shipping & Logistics", "Industry - Logistics & Warehousing"],
    ("B2", 7):  ["TOEIC - Property & Real Estate", "TOEIC - Banking & Investments"],
    ("B2", 8):  ["Digital Life - Cryptocurrencies & Blockchain", "Digital Life - Virtual Reality & Metaverse"],
    ("B2", 9):  ["Entertainment - Video Games & E-sports", "Entertainment - Photography & Visual Arts"],
    ("B2", 10): ["Industry - Construction & Heavy Machinery", "Industry - Agriculture & Farming"],
    ("B2", 11): ["Industry - Law Enforcement & Policing", "Industry - Firefighting & Emergency Services"],
    ("B2", 12): ["Industry - Aviation & Aerospace", "Industry - Maritime, Shipping & Ports"],
    ("B2", 13): ["Modern Career - Workplace Conflict & Resolution", "Communication - Expressing Opinions & Debating"],
    ("B2", 14): [],

    # ── C1 ─────────────────────────────────────────────────────────────────
    ("C1", 1):  ["IELTS & Academic - Global Issues & Globalization", "Advanced Business - International Trade & Tariffs"],
    ("C1", 2):  ["IELTS & Academic - Crime, Law & Justice", "Law & Society - Legal Proceedings & Courtrooms"],
    ("C1", 3):  ["IELTS & Academic - Media, News & Journalism", "Industry - Journalism, Broadcasting & Podcasting"],
    ("C1", 4):  ["IELTS & Academic - Arts, Culture & Museums", "Culture - Fine Arts, Sculptures & Exhibitions"],
    ("C1", 5):  ["IELTS & Academic - City Life & Urbanization", "Arts & Design - Architecture & Urban Planning"],
    ("C1", 6):  ["Academic - Philosophy & Ethics", "Academic - Psychology & Cognitive Science"],
    ("C1", 7):  ["Academic - Political Science & Government", "Academic - Macroeconomics & Microeconomics"],
    ("C1", 8):  ["Academic - Physics & Quantum Mechanics", "Academic - Chemistry & Materials Science", "Academic - Biology & Anatomy"],
    ("C1", 9):  ["Science - Artificial Intelligence & Data", "Science - Robotics & Automation"],
    ("C1", 10): ["Science - Environment & Conservation", "Science - Climate Change & Global Warming", "Science - Renewable Energy & Green Tech"],
    ("C1", 11): ["Medicine - Surgery & Operating Room", "Medicine - Pharmacology & Drugs", "Medicine - Pediatrics & Child Healthcare"],
    ("C1", 12): ["Advanced Business - Mergers & Acquisitions", "Advanced Business - Corporate Social Responsibility", "Advanced Business - Venture Capital & Fundraising"],
    ("C1", 13): ["Law & Society - Immigration, Refugees & Borders", "Law & Society - Human Rights & Civil Liberties", "Law & Society - Elections & Voting Systems"],
    ("C1", 14): ["Academic - Linguistics & Language Learning", "Academic - Research & Methodology"],
    ("C1", 15): [],
}

# Which Word.cefr_level values to include for each course level
LEVEL_WORD_RANGE = {
    "A1": ["A1"],
    "A2": ["A1", "A2"],
    "B1": ["A2", "B1"],
    "B2": ["B1", "B2"],
    "C1": ["B2", "C1"],
}


def _back_text(word: Word) -> str:
    """Return the best available back-of-card text for a word."""
    return word.meaning_vi or word.definition_en or ""


class Command(BaseCommand):
    help = "Create system FlashcardDecks (one per chapter) and populate with relevant Words"

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
            help="Delete existing system decks for the selected levels, then re-create",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        levels = options["levels"] or ["A1", "A2", "B1", "B2", "C1"]

        for level_code in levels:
            try:
                cefr = CEFRLevel.objects.get(code=level_code)
            except CEFRLevel.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  [{level_code}] CEFRLevel not found — run seed_courses first")
                )
                continue

            course = cefr.courses.filter(is_active=True).first()
            if not course:
                self.stdout.write(self.style.WARNING(f"  [{level_code}] No active course found"))
                continue

            if options["clear"]:
                deleted, _ = FlashcardDeck.objects.filter(
                    cefr_level=level_code, owner=None
                ).delete()
                self.stdout.write(f"  [{level_code}] Cleared {deleted} existing system deck(s)")

            word_levels = LEVEL_WORD_RANGE.get(level_code, [level_code])
            decks_created = cards_created = 0

            for chapter in course.chapters.order_by("order"):
                key = (level_code, chapter.order)
                topic_list = VOCAB_TOPIC_MAP.get(key, [])
                if not topic_list:
                    continue

                # Get or create the system deck for this chapter
                deck, created = FlashcardDeck.objects.get_or_create(
                    name=chapter.title,
                    cefr_level=level_code,
                    owner=None,
                    defaults={
                        "description": f"Từ vựng chương '{chapter.title}' — {level_code}",
                        "is_public": True,
                    },
                )
                if created:
                    decks_created += 1

                # Populate with words (skip if deck already has cards)
                if not deck.cards.exists():
                    words = Word.objects.filter(
                        topic__in=topic_list, cefr_level__in=word_levels
                    ).order_by("topic", "word")

                    cards = [
                        Flashcard(
                            deck=deck,
                            word=w,
                            front_text=w.word,
                            back_text=_back_text(w),
                            card_type="word_to_def",
                            order=idx + 1,
                        )
                        for idx, w in enumerate(words)
                    ]
                    Flashcard.objects.bulk_create(cards)
                    cards_created += len(cards)

            self.stdout.write(
                self.style.SUCCESS(
                    f"  [{level_code}] {decks_created} deck(s) created, {cards_created} card(s) added"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nDone — seed_vocab_lessons complete."))
