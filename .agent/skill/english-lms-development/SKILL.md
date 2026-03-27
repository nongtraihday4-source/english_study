---
name: english-lms-development
description: Hướng dẫn phát triển LMS English Study. Sử dụng skill này khi tạo Django app mới, thiết kế database schema, viết service layer, hoặc xây dựng API cho hệ thống học tiếng Anh 5 cấp (Level → Course → Chapter → Lesson → Exercise).
---

# English LMS Development

Skill này cung cấp conventions cụ thể cho dự án English Study — một LMS học tiếng Anh A1-C1 với cấu trúc 5 cấp và AI grading.

## LMS Hierarchy

```
Level (A1/A2/B1/B2/C1)
  └── Course (e.g., "A1 Foundations")
        └── Chapter (e.g., "Unit 1: Greetings")
              └── Lesson (có passing_score, thường 60-80%)
                    └── Exercise (MC / Gap Fill / Drag & Drop / Speaking / Writing)
```

**Unlock Logic (bất biến):** Lesson kế tiếp chỉ mở khi `latest_score >= lesson.passing_score`. Bao giờ cũng kiểm tra trong Service Layer, KHÔNG phải trong View.

## Django App Structure

Mỗi app trong `backend/apps/` phải có cấu trúc:

```
apps/<app_name>/
├── models.py          # Data models
├── serializers.py     # Input + Output serializers (tách riêng)
├── services.py        # 100% business logic
├── views.py           # HTTP concerns only (ViewSet/APIView)
├── urls.py            # URL routing
├── tasks.py           # Celery async tasks (nếu có)
├── admin.py           # Django Admin config
├── apps.py
└── tests/
    ├── test_services.py
    ├── test_views.py
    └── test_models.py
```

## Database Schema Conventions

### Chung
- Primary key: UUID (`models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)`)
- Timestamps: `created_at`, `updated_at` (dùng `auto_now_add`, `auto_now`)
- Soft delete: `is_active = models.BooleanField(default=True)` (không xóa thật)

### Scoring Fields
```python
class Lesson(models.Model):
    passing_score = models.PositiveSmallIntegerField(default=60)  # 0-100
    order = models.PositiveSmallIntegerField()

class ExerciseResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)  # 0.00-100.00
    answers_json = models.JSONField()       # Input user
    detail_json = models.JSONField()        # Scoring detail
    is_passed = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)
```

## Service Layer Pattern

```python
# apps/exercises/services.py
class ExerciseService:
    @staticmethod
    @transaction.atomic
    def submit_answer(user, exercise_id: str, answers: dict) -> dict:
        """Returns DTO dict, KHÔNG trả về Model instance."""
        exercise = Exercise.objects.select_related(
            'lesson__chapter__course__level'
        ).get(id=exercise_id, lesson__is_active=True)

        # 1. Kiểm tra access (enrolled + unlocked)
        LessonAccessService.assert_accessible(user, exercise.lesson)

        # 2. Tính điểm
        score, detail = ScoringEngine.calculate(exercise, answers)

        # 3. Lưu kết quả
        result = ExerciseResult.objects.create(
            user=user, exercise=exercise,
            score=score, detail_json=detail,
            answers_json=answers,
            is_passed=(score >= exercise.lesson.passing_score)
        )

        # 4. Thử unlock bài tiếp theo
        unlocked = UnlockService.try_unlock_next(user, exercise.lesson, score)

        # 5. Trả về DTO (dict)
        return {
            'result_id': str(result.id),
            'score': float(score),
            'is_passed': result.is_passed,
            'detail': detail,
            'unlocked_next_lesson': unlocked,
        }
```

## Scoring Rules

| Exercise Type | Logic |
|--------------|-------|
| Multiple Choice (MC) | `100 / total_questions` per đáp án đúng. Không trừ điểm. |
| Gap Fill | Case-insensitive + strip whitespace. Partial score: đúng n/total * 100. |
| Drag & Drop | Partial scoring: mỗi slot đúng = điểm tương ứng. |
| Speaking | AI Whisper → transcript → GPT-4o rubric scoring (async Celery). |
| Writing | GPT-4o rubric scoring theo 4 criteria (async Celery). |

## API Response DTOs

### Exercise Submit Response
```json
{
    "result_id": "uuid",
    "score": 75.0,
    "is_passed": true,
    "detail": {
        "questions": [
            {"id": "q1", "correct": true, "score": 25.0},
            {"id": "q2", "correct": false, "score": 0}
        ]
    },
    "unlocked_next_lesson": {"id": "uuid", "title": "Lesson 2"}
}
```

### Error Response
```json
{
    "error": {
        "code": "LESSON_LOCKED",
        "message": "Bạn cần hoàn thành bài trước để mở khóa.",
        "details": {"required_score": 60, "current_score": 45}
    }
}
```

## Tạo Django App mới

```bash
cd backend
python manage.py startapp <app_name> apps/<app_name>
```

Sau đó:
1. Thêm vào `INSTALLED_APPS` trong `settings/base.py`: `'apps.<app_name>'`
2. Tạo cấu trúc thư mục `tests/` với `__init__.py`
3. Đăng ký URL trong `english_study/urls.py`
4. Tạo migration: `python manage.py makemigrations <app_name>`
