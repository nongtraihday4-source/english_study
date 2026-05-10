"""
apps/curriculum/services/scoring_service.py
Backend Score SSOT Contract.
Frontend gửi raw_answers, backend tính điểm.
"""
from typing import Dict, Any


class ScoringService:
    @staticmethod
    def calculate_lesson_score(content_data: dict, raw_answers: dict) -> dict:
        """
        Backend SSOT scoring. Frontend chỉ gửi raw_answers.
        Trả về: {score, xp_gained, status, correct_count, total_count}
        """
        total_questions = 0
        correct_answers = 0

        reading_qs = content_data.get("reading_questions", [])
        reading_ans = raw_answers.get("reading", [])
        total_questions += len(reading_qs)
        for i, q in enumerate(reading_qs):
            if i < len(reading_ans) and reading_ans[i] == q.get("correct"):
                correct_answers += 1

        for gs in content_data.get("grammar_sections", []):
            exercises = gs.get("exercises", [])
            grammar_ans = raw_answers.get("grammar", {}).get(str(gs.get("title", "")), [])
            total_questions += len(exercises)
            for i, ex in enumerate(exercises):
                if i < len(grammar_ans) and grammar_ans[i] == ex.get("correct"):
                    correct_answers += 1

        listening_qs = (
            content_data.get("listening_content", {}).get("comprehension_questions", [])
        )
        listening_ans = raw_answers.get("listening", [])
        total_questions += len(listening_qs)
        for i, q in enumerate(listening_qs):
            if i < len(listening_ans) and listening_ans[i] == q.get("correct"):
                correct_answers += 1

        score = (
            round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        )
        base_xp = content_data.get("completion_xp", 10)
        bonus_xp = content_data.get("bonus_xp", 0) if score >= 80 else 0

        return {
            "score": score,
            "xp_gained": base_xp + bonus_xp,
            "status": "completed" if score >= 50 else "failed",
            "correct_count": correct_answers,
            "total_count": total_questions,
        }