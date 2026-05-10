"""
apps/curriculum/tests/test_scoring.py
TDD: Backend Score SSOT Contract.
Test → Fail → Implement → Pass workflow.
"""
from django.test import TestCase
from apps.curriculum.services.scoring_service import ScoringService


class ScoringServiceTest(TestCase):
    def test_calculate_score_reading_only_all_correct(self):
        content_data = {
            "reading_questions": [
                {"correct": 0},
                {"correct": 1},
                {"correct": 2},
            ],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [0, 1, 2]}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["xp_gained"], 60)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["correct_count"], 3)
        self.assertEqual(result["total_count"], 3)

    def test_calculate_score_reading_only_partial(self):
        content_data = {
            "reading_questions": [
                {"correct": 0},
                {"correct": 1},
                {"correct": 2},
            ],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [0, 0, 0]}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 33)
        self.assertEqual(result["xp_gained"], 10)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["correct_count"], 1)
        self.assertEqual(result["total_count"], 3)

    def test_perfect_score_triggers_bonus(self):
        content_data = {
            "reading_questions": [{"correct": 0}],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [0]}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["xp_gained"], 60)

    def test_80_percent_triggers_bonus(self):
        content_data = {
            "reading_questions": [{"correct": 0}, {"correct": 1}, {"correct": 2}, {"correct": 3}, {"correct": 4}],
            "completion_xp": 20,
            "bonus_xp": 100,
        }
        raw_answers = {"reading": [0, 1, 0, 0, 0]}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 40)
        self.assertEqual(result["xp_gained"], 20)

    def test_79_percent_no_bonus(self):
        content_data = {
            "reading_questions": [{"correct": 0}] * 100,
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [0] * 79 + [1] * 21}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 79)
        self.assertEqual(result["xp_gained"], 10)

    def test_empty_questions_returns_zero(self):
        content_data = {
            "reading_questions": [],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": []}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["xp_gained"], 10)
        self.assertEqual(result["status"], "failed")

    def test_missing_raw_answers_key(self):
        content_data = {
            "reading_questions": [{"correct": 0}, {"correct": 1}],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["correct_count"], 0)
        self.assertEqual(result["total_count"], 2)

    def test_grammar_sections_scoring(self):
        content_data = {
            "reading_questions": [],
            "grammar_sections": [
                {
                    "title": "Tense 1",
                    "exercises": [
                        {"correct": 0},
                        {"correct": 1},
                    ],
                },
                {
                    "title": "Tense 2",
                    "exercises": [
                        {"correct": 0},
                    ],
                },
            ],
            "completion_xp": 15,
            "bonus_xp": 30,
        }
        raw_answers = {
            "grammar": {
                "Tense 1": [0, 1],
                "Tense 2": [1],
            }
        }
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 67)
        self.assertEqual(result["correct_count"], 2)
        self.assertEqual(result["total_count"], 3)

    def test_listening_comprehension_scoring(self):
        content_data = {
            "reading_questions": [],
            "listening_content": {
                "comprehension_questions": [
                    {"correct": 0},
                    {"correct": 1},
                    {"correct": 2},
                ],
            },
            "completion_xp": 20,
            "bonus_xp": 40,
        }
        raw_answers = {"listening": [0, 1, 1]}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 67)
        self.assertEqual(result["correct_count"], 2)
        self.assertEqual(result["total_count"], 3)

    def test_mixed_question_types(self):
        content_data = {
            "reading_questions": [{"correct": 0}, {"correct": 1}],
            "grammar_sections": [
                {
                    "title": "G1",
                    "exercises": [{"correct": 0}, {"correct": 1}],
                }
            ],
            "listening_content": {
                "comprehension_questions": [{"correct": 0}],
            },
            "completion_xp": 30,
            "bonus_xp": 60,
        }
        raw_answers = {
            "reading": [0, 0],
            "grammar": {"G1": [0, 1]},
            "listening": [0],
        }
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 80)
        self.assertEqual(result["xp_gained"], 90)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["correct_count"], 4)
        self.assertEqual(result["total_count"], 5)

    def test_status_failed_under_50_percent(self):
        content_data = {
            "reading_questions": [{"correct": 0}, {"correct": 1}, {"correct": 2}],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [0, 0, 0]}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 33)
        self.assertEqual(result["status"], "failed")

    def test_status_completed_at_50_percent(self):
        content_data = {
            "reading_questions": [{"correct": 0}, {"correct": 1}],
            "completion_xp": 10,
            "bonus_xp": 50,
        }
        raw_answers = {"reading": [0, 0]}
        result = ScoringService.calculate_lesson_score(content_data, raw_answers)
        self.assertEqual(result["score"], 50)
        self.assertEqual(result["status"], "completed")