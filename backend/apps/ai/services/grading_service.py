import re
import json
import hashlib
import time

from .qwen_client import QwenClient

INJECTION_RE = re.compile(r"(<script|{{|}}|ignore previous|system prompt)", re.IGNORECASE)


def sanitize_input(text: str) -> str | None:
    if not text or not text.strip():
        return None
    words = text.split()
    if len(words) < 3:
        return None
    clean = re.sub(INJECTION_RE, "", text)
    clean = re.sub(r"<[^>]+>", "", clean)
    return clean.strip()


def build_writing_prompt(student_text: str, grammar_hint: str = "") -> list:
    system_prompt = (
        "You are an expert ESL Teacher. Grade the student's writing strictly based on the rubric. "
        "Output MUST be valid JSON: {score: 0-100, feedback: string, rubric: {grammar: 0-100, vocab: 0-100, coherence: 0-100}}. "
        "Do not output markdown or extra text."
    )
    user_prompt = f"Grammar Hint: {grammar_hint}\nStudent Text: {student_text}"
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]


class GradingService:
    @staticmethod
    def parse_response(raw_json: str) -> dict | None:
        try:
            data = json.loads(raw_json)
            if "score" not in data or not (0 <= data["score"] <= 100):
                return None
            return data
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def grade_writing(submission_id: int, student_text: str, grammar_hint: str = "") -> dict:
        start = time.time()
        clean_text = sanitize_input(student_text)

        if not clean_text:
            return {
                "score": 0,
                "feedback": "Bài viết quá ngắn hoặc trống.",
                "status": "fallback",
            }

        messages = build_writing_prompt(clean_text, grammar_hint)
        prompt_hash = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        try:
            client = QwenClient()
            raw_result = client.generate_json(messages)
            parsed = GradingService.parse_response(json.dumps(raw_result))

            if parsed:
                latency = int((time.time() - start) * 1000)
                return {**parsed, "status": "success", "latency_ms": latency, "prompt_hash": prompt_hash}

            raise ValueError("Invalid JSON structure from LLM")

        except Exception as e:
            latency = int((time.time() - start) * 1000)
            word_count = len(clean_text.split())
            fallback_score = min(100, max(10, word_count * 5))
            return {
                "score": fallback_score,
                "feedback": "AI grading tạm thời không khả dụng. Điểm ước lượng dựa trên độ dài.",
                "status": "fallback",
                "error": str(e),
                "latency_ms": latency,
                "prompt_hash": prompt_hash,
            }