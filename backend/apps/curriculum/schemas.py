"""
apps/curriculum/schemas.py
Pydantic JSON Schema Validation cho LessonContent.
Chặn malformed/blank/injection JSON trước khi lưu.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import List, Optional
import re

INJECTION_PATTERN = re.compile(
    r"(<script|</script|{{|}}|ignore previous|system prompt)",
    re.IGNORECASE,
)

def _check_injection(v: str) -> str:
    if v and INJECTION_PATTERN.search(v):
        raise ValueError("Chứa ký tự không an toàn hoặc prompt injection")
    return v


class ReadingQuestionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(..., min_length=1)
    options: List[str] = Field(..., min_length=2)
    correct: int = Field(..., ge=0)
    explanation: Optional[str] = ""

    @field_validator("question", "explanation")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)

    @model_validator(mode="after")
    def check_correct_index(self):
        if self.options and self.correct >= len(self.options):
            raise ValueError("correct index vượt quá số lượng options")
        return self


class VocabItemSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    word: str = Field(..., min_length=1)
    meaning_vi: str = Field(..., min_length=1)
    pos: Optional[str] = ""
    ipa: Optional[str] = ""
    definition_en: Optional[str] = ""
    example_en: Optional[str] = ""
    example_vi: Optional[str] = ""
    collocations: List[str] = []
    highlight_in_passage: bool = False

    @field_validator("word", "meaning_vi", "example_en", "example_vi", "definition_en")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)


class GrammarExampleSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: str
    vi: str
    highlight: Optional[str] = ""

    @field_validator("en", "vi", "highlight")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)


class GrammarExerciseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    prompt: str
    options: List[str] = []
    correct: int = Field(..., ge=0)
    explanation: Optional[str] = ""

    @field_validator("prompt", "explanation")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)

    @model_validator(mode="after")
    def check_correct_index(self):
        if self.options and self.correct >= len(self.options):
            raise ValueError("correct index vượt quá số lượng options")
        return self


class GrammarSectionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    grammar_topic_id: Optional[int] = None
    note: str = ""
    examples: List[GrammarExampleSchema] = []
    exercises: List[GrammarExerciseSchema] = []

    @field_validator("title", "note")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)


class DictationSentenceSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    hint: Optional[str] = ""
    translation_vi: str = ""

    @field_validator("text", "hint", "translation_vi")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)


class ListeningContentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    audio_text: Optional[str] = ""
    translation_vi: Optional[str] = ""
    sentences: List[dict] = []
    speed: Optional[float] = 0.9
    comprehension_questions: List[ReadingQuestionSchema] = []
    dictation_sentences: List[DictationSentenceSchema] = []

    @field_validator("audio_text", "translation_vi")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)


class SpeakingContentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mode: str = "repeat"
    sentences: List[dict] = []
    dialogue: List[dict] = []


class WritingExerciseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    prompt: str = ""
    prompt_vi: str = ""
    grammar_hint: str = ""
    items: List[List[str]] = []
    correct_answer: str = ""
    min_words: int = 8
    max_words: int = 25
    sample_answer: str = ""

    @field_validator("prompt", "prompt_vi", "grammar_hint", "sample_answer")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return _check_injection(v)


class WritingContentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    exercises: List[WritingExerciseSchema] = []


class LessonContentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    learning_objectives: List[str] = []
    reading_questions: List[ReadingQuestionSchema] = []
    vocab_items: List[VocabItemSchema] = []
    grammar_sections: List[GrammarSectionSchema] = []
    skill_sections: dict = {}
    listening_content: Optional[ListeningContentSchema] = None
    speaking_content: Optional[SpeakingContentSchema] = None
    writing_content: Optional[WritingContentSchema] = None
    completion_xp: int = 10
    bonus_xp: int = 50

    @model_validator(mode="after")
    def validate_listening_comprehension(self):
        lc = self.listening_content
        if lc:
            for q in lc.comprehension_questions:
                if q.options and q.correct >= len(q.options):
                    raise ValueError(
                        f"Listening comprehension question correct index exceeds options length"
                    )
        return self