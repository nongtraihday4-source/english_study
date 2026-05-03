#!/usr/bin/env python3
"""
Assembles grammar_A1.json from the 4 part files.
Run: python scripts/grammar_fixtures/build_grammar_a1.py
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))

from gen_a1_p1 import TOPICS as P1
from gen_a1_p2 import TOPICS as P2
from gen_a1_p3 import TOPICS as P3
from gen_a1_p4 import TOPICS as P4
from gen_a1_p5 import TOPICS as P5

CHAPTERS = [
    {"name": "Present tenses", "slug": "present-tenses", "order": 1, "icon": "⏰", "description": ""},
    {"name": "Past tenses", "slug": "past-tenses", "order": 2, "icon": "🕐", "description": ""},
    {"name": "Future", "slug": "future", "order": 3, "icon": "🔮", "description": ""},
    {"name": "Modals, the imperative, etc .", "slug": "modals-the-imperative-etc", "order": 4, "icon": "💭", "description": ""},
    {"name": "-ing and the infinitive", "slug": "ing-and-the-infinitive", "order": 5, "icon": "📐", "description": ""},
    {"name": "Articles, nouns, pronouns, and determiners.", "slug": "articles-nouns-pronouns-and-determiners", "order": 6, "icon": "📦", "description": ""},
    {"name": "there and it", "slug": "there-and-it", "order": 7, "icon": "📚", "description": ""},
    {"name": "Adjectives and adverbs", "slug": "adjectives-and-adverbs", "order": 8, "icon": "⚡", "description": ""},
    {"name": "Conjunctions", "slug": "conjunctions", "order": 9, "icon": "🔗", "description": ""},
    {"name": "Prepositions", "slug": "prepositions", "order": 10, "icon": "📍", "description": ""},
    {"name": "Questions", "slug": "questions", "order": 11, "icon": "❓", "description": ""},
    {"name": "Word order", "slug": "word-order", "order": 12, "icon": "🔀", "description": ""},
]

ALL_TOPICS = sorted(P1 + P2 + P3 + P4 + P5, key=lambda t: t["order"])

# Validate
assert len(ALL_TOPICS) == 39, f"Expected 39 topics, got {len(ALL_TOPICS)}"
slugs = [t["slug"] for t in ALL_TOPICS]
assert len(slugs) == len(set(slugs)), "Duplicate slugs found!"
for i, t in enumerate(ALL_TOPICS):
    assert t["order"] == i + 1, f"Topic {t['slug']} has order {t['order']}, expected {i+1}"

output = {"chapters": CHAPTERS, "topics": ALL_TOPICS}

output_path = os.path.join(os.path.dirname(__file__), "grammar_A1.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ Written {len(ALL_TOPICS)} topics to {output_path}")
print(f"   Chapters: {len(CHAPTERS)}")
for t in ALL_TOPICS:
    print(f"   [{t['order']:2d}] {t['slug']} ({t['chapter']})")
