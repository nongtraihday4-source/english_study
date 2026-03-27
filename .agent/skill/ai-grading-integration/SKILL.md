---
name: ai-grading-integration
description: Hướng dẫn tích hợp AI chấm điểm Speaking và Writing. Sử dụng skill này khi implement Whisper transcription, GPT-4o rubric grading, Celery async tasks, hoặc xử lý lỗi AI API trong dự án English Study.
---

# AI Grading Integration

Skill này cung cấp patterns cụ thể cho tích hợp AI chấm điểm Speaking/Writing trong English Study.

**Stack:** OpenAI Whisper (Speech-to-Text) + GPT-4o (Rubric Scoring) + Celery (Async Tasks) + Redis (Broker)

---

## Architecture Overview

```
User submits audio/text
        ↓
API View → ExerciseService.submit_answer()
        ↓
Celery task created (returns task_id ngay lập tức)
        ↓ (async)
Worker: Whisper transcription (Speaking only)
        ↓
Worker: GPT-4o rubric scoring
        ↓
ExerciseResult saved, Progress updated
        ↓
Frontend polls /api/v1/results/{task_id}/status/
```

⚠️ **Tuyệt đối không** gọi Whisper/GPT-4o trực tiếp trong View hoặc đồng bộ trong request-response cycle.

---

## Celery Task Pattern

```python
# apps/exercises/tasks.py
from celery import shared_task
from django.utils import timezone

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,  # 30 giây giữa các retry
    queue='ai_grading'
)
def grade_speaking_task(self, result_id: str):
    """Async task: Whisper transcription → GPT-4o rubric scoring."""
    from .services import SpeakingGradingService
    try:
        SpeakingGradingService.grade_and_save(result_id)
    except openai.RateLimitError as exc:
        # Retry khi bị rate limit
        raise self.retry(exc=exc, countdown=60)
    except openai.APIError as exc:
        # Retry với backoff
        raise self.retry(exc=exc)
    except Exception as exc:
        # Lỗi không recover được: lưu error state
        ExerciseResult.objects.filter(id=result_id).update(
            grading_status='failed',
            error_message=str(exc)[:500]
        )
```

---

## Whisper Integration (Speaking)

```python
# apps/exercises/services.py
import openai
from django.conf import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class SpeakingGradingService:
    @staticmethod
    def transcribe_audio(audio_file_path: str) -> str:
        """Chuyển audio → text. Input: đường dẫn file WAV/MP3/WebM."""
        with open(audio_file_path, 'rb') as audio_file:
            response = client.audio.transcriptions.create(
                model='whisper-1',
                file=audio_file,
                language='en',   # Force English để tránh hallucinate tiếng Việt
                response_format='text'
            )
        return response.strip()
```

**Lưu ý bảo mật:** Sanitize transcript trước khi đưa vào GPT-4o prompt (chống prompt injection):

```python
def sanitize_user_content(text: str) -> str:
    """Loại bỏ potential prompt injection từ nội dung của user."""
    # Giới hạn độ dài
    text = text[:2000]
    # Escape các ký tự đặc biệt có thể override prompt
    dangerous_patterns = ['ignore previous', 'disregard', 'system:', 'assistant:']
    for pattern in dangerous_patterns:
        text = text.replace(pattern, '[removed]')
    return text
```

---

## GPT-4o Rubric Scoring

### Speaking Rubric Prompt Template

```python
SPEAKING_RUBRIC_PROMPT = """
You are an English language examiner. Grade the following spoken response strictly based on the rubric.

**Task prompt given to student:** {task_prompt}
**Transcribed student response:** {transcript}
**Target level:** {cefr_level}

**Rubric (100 points total):**
- Fluency & Coherence (25 pts): smooth delivery, logical flow
- Pronunciation (25 pts): intelligibility, word stress, intonation
- Lexical Resource (25 pts): range and accuracy of vocabulary
- Grammar (25 pts): range and accuracy of grammatical structures

Respond ONLY with valid JSON, no explanation:
{{
    "total_score": <0-100>,
    "criteria": {{
        "fluency_coherence": {{"score": <0-25>, "feedback": "<1 sentence>"}},
        "pronunciation": {{"score": <0-25>, "feedback": "<1 sentence>"}},
        "lexical_resource": {{"score": <0-25>, "feedback": "<1 sentence>"}},
        "grammar": {{"score": <0-25>, "feedback": "<1 sentence>"}}
    }},
    "overall_feedback": "<2-3 sentences encouragement + main improvement point>",
    "error_list": [
        {{"original": "<student's phrase>", "correction": "<correct phrase>", "explanation": "<brief>"}}
    ]
}}
"""
```

### Writing Rubric Prompt Template

```python
WRITING_RUBRIC_PROMPT = """
You are an English writing examiner. Grade the essay strictly based on the rubric.

**Task prompt:** {task_prompt}
**Student essay:** {essay}
**Word count:** {word_count}
**Target level:** {cefr_level}

**Rubric (100 points total):**
- Task Achievement (25 pts): addresses all parts of the task
- Coherence & Cohesion (25 pts): organization, paragraphing, linking words
- Lexical Resource (25 pts): range and accuracy of vocabulary
- Grammatical Range & Accuracy (25 pts)

Respond ONLY with valid JSON:
{{
    "total_score": <0-100>,
    "criteria": {{...}},
    "overall_feedback": "<string>",
    "error_list": [...]
}}
"""
```

---

## Gọi GPT-4o với Error Handling

```python
import json

def call_gpt4o_rubric(prompt: str) -> dict:
    """Gọi GPT-4o và parse JSON response. Raises exception nếu format sai."""
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.1,      # Thấp để kết quả nhất quán
        response_format={'type': 'json_object'},
        timeout=30,           # 30 giây timeout
    )

    raw = response.choices[0].message.content
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"GPT-4o trả về JSON không hợp lệ: {raw[:200]}")

    # Validate required fields
    required = ['total_score', 'criteria', 'overall_feedback', 'error_list']
    if not all(k in result for k in required):
        raise ValueError(f"GPT-4o response thiếu fields: {result.keys()}")

    # Clamp score
    result['total_score'] = max(0, min(100, int(result['total_score'])))
    return result
```

---

## ExerciseResult Model cho AI Grading

```python
class ExerciseResult(models.Model):
    GRADING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('grading', 'Grading'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    grading_status = models.CharField(
        max_length=20, choices=GRADING_STATUS_CHOICES, default='pending'
    )
    celery_task_id = models.CharField(max_length=255, blank=True)
    ai_feedback_json = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
```

---

## Frontend Polling Pattern (Vue 3)

```javascript
// composables/useAIGrading.js
export function useAIGrading() {
    const gradingStatus = ref('pending')
    const result = ref(null)
    let pollInterval = null

    function startPolling(taskId) {
        pollInterval = setInterval(async () => {
            const res = await exerciseApi.getGradingStatus(taskId)
            gradingStatus.value = res.status
            if (res.status === 'completed' || res.status === 'failed') {
                result.value = res
                clearInterval(pollInterval)
            }
        }, 2000) // Poll mỗi 2 giây
    }

    onUnmounted(() => clearInterval(pollInterval))
    return { gradingStatus, result, startPolling }
}
```

---

## Validation cho AI Grading (trước khi gọi API)

Kiểm tra trước khi tốn token OpenAI:

```python
def validate_speaking_submission(audio_duration_sec: float, transcript: str):
    if audio_duration_sec < 5:
        raise ValidationError("Recording too short (minimum 5 seconds)")
    if audio_duration_sec > 120:
        raise ValidationError("Recording too long (maximum 2 minutes)")

def validate_writing_submission(essay: str, min_words: int = 50):
    word_count = len(essay.split())
    if word_count < min_words:
        raise ValidationError(f"Essay too short: {word_count} words (min {min_words})")
    if len(essay) > 5000:
        raise ValidationError("Essay too long (max 5000 characters)")
```
