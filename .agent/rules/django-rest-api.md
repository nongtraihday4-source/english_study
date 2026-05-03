---
trigger: always_on
---

# Django REST API Conventions

## Tech Stack
- Django 5.x + Django REST Framework (DRF)
- Database: PostgreSQL + Redis (cache, session, Celery broker)
- Task Queue: Celery + Redis
- AI Integration: OpenAI GPT-4o (Writing grading), Whisper (Speaking transcription)

## API Design Standards

### URL Patterns
- Prefix: `/api/v1/`
- RESTful naming: `/api/v1/courses/`, `/api/v1/lessons/{id}/exercises/`
- Nested resources: max 2 levels deep
- Actions: `/api/v1/exercises/{id}/submit/`, `/api/v1/lessons/{id}/unlock/`

### Serializer Conventions
- Input: sử dụng `Serializer` riêng cho create/update (VD: `ExerciseSubmitSerializer`)
- Output: sử dụng `Serializer` riêng cho response (VD: `ExerciseResultSerializer`)
- Không dùng `ModelSerializer` cho cả input lẫn output → tách rõ ràng.
- Datetime fields: luôn format theo `Asia/Ho_Chi_Minh` timezone.

### ViewSet / APIView
```python
# Pattern chuẩn cho ViewSet
class ExerciseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'submit':
            return ExerciseSubmitSerializer
        return ExerciseDetailSerializer

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Delegate to service layer
        result = ExerciseService.submit_answer(
            user=request.user,
            exercise_id=pk,
            answers=serializer.validated_data
        )
        return Response(ExerciseResultSerializer(result).data)
```

### Service Layer Pattern
```python
# backend/apps/exercises/services.py
class ExerciseService:
    @staticmethod
    @transaction.atomic
    def submit_answer(user, exercise_id, answers):
        exercise = Exercise.objects.select_related('lesson__chapter__course').get(id=exercise_id)
        # Validate unlock status
        # Calculate score
        # Save ExerciseResult
        # Check & trigger unlock for next lesson
        # Return DTO dict (NOT model instance)
        return {
            'score': score,
            'detail_json': detail,
            'is_passed': score >= exercise.lesson.passing_score,
            'unlocked_next': unlocked,
        }
```

### Authentication
- JWT via `djangorestframework-simplejwt`
- Access token: short-lived (15 min)
- Refresh token: long-lived (7 days)
- Custom claims: `user_id`, `role` (admin/teacher/student), `subscription_status`

### Pagination
- Default: `PageNumberPagination` với `page_size=20`
- Cho lists lớn (Question Bank): `CursorPagination`

### Error Response Format
```json
{
    "error": {
        "code": "EXERCISE_LOCKED",
        "message": "Bạn cần hoàn thành bài trước để mở khóa.",
        "details": {
            "required_score": 60,
            "current_score": 45
        }
    }
}
```

### Permission Classes
- `IsAdmin`: Full access
- `IsTeacher`: CRUD own classes, view student progress
- `IsStudent`: Access enrolled courses, submit exercises
- `IsPremium`: Access premium content, AI grading

## Celery Tasks
- AI Grading tasks: `@shared_task(bind=True, max_retries=3, default_retry_delay=60)`
- Long-running tasks phải có progress tracking (lưu vào Redis)
- Task naming: `apps.{app_name}.tasks.{action_name}` (VD: `apps.exercises.tasks.grade_speaking`)

## Database Conventions
- Soft delete: `is_deleted` flag + `deleted_at` timestamp
- Timestamps: `created_at`, `updated_at` trên mọi model (dùng `TimeStampedModel` base)
- UUID primary keys cho user-facing models (Exercise, Course, ...)
- Integer PKs cho internal models (Score records, logs)
