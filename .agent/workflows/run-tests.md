---
description: Chạy test suite cho English Study (Django unit/integration tests)
---

# Chạy Tests — English Study

## Backend Tests (Django)

### Chạy toàn bộ test suite
```bash
cd backend
source ../.venv/bin/activate
DJANGO_SETTINGS_MODULE=english_study.settings.development python manage.py test apps --verbosity=2
```

### Chạy test cho một app cụ thể
```bash
# Chạy test cho exercises app
python manage.py test apps.exercises --verbosity=2

# Chạy test cho curriculum app
python manage.py test apps.curriculum --verbosity=2

# Chạy test cho vocabulary app
python manage.py test apps.vocabulary --verbosity=2
```

### Chạy một test case cụ thể
```bash
python manage.py test apps.exercises.tests.ExerciseSubmitServiceTest --verbosity=2
```

### Chạy test với coverage report
```bash
pip install coverage  # nếu chưa có
coverage run --source='.' manage.py test apps
coverage report -m
coverage html  # tạo report HTML trong htmlcov/
```

---

## Tiêu chuẩn Test cho từng loại code

### Service Layer Tests (quan trọng nhất)
Mỗi Service method phải có:
1. **Happy path**: Input hợp lệ → output đúng
2. **Edge case**: Input biên (bài trống, điểm = passing_score chính xác)
3. **Failure case**: Input sai → exception đúng loại

```python
# Ví dụ: tests/test_exercise_service.py
class ExerciseSubmitServiceTest(TestCase):
    def test_submit_mc_correct_scores_100(self): ...
    def test_submit_mc_partial_scores_partial(self): ...
    def test_submit_locked_exercise_raises_exception(self): ...
    def test_submit_unlocks_next_lesson_when_passed(self): ...
```

### AI Grading Tests
Trước khi deploy AI grading prompt mới:
- Chạy với ≥10 bài mẫu đã chấm tay
- Kết quả AI phải trong ±10 điểm so với chấm tay
- Kiểm tra edge cases: bài trắng, bài quá ngắn (<20 từ), bài chứa tiếng Việt

```bash
# Chạy AI grading validation script
python scripts/validate_ai_grading.py --samples 10
```

### API Integration Tests
```bash
# Test toàn bộ exercise submission flow
python manage.py test apps.exercises.tests.ExerciseAPITest --verbosity=2
```

---

## Checklist trước khi commit

- [ ] Tất cả tests pass: `python manage.py test apps`
- [ ] Không có N+1 query mới (kiểm tra Django Debug Toolbar hoặc log SQL)
- [ ] Unlock logic đúng: bài kế tiếp chỉ mở khi `score >= passing_score`
- [ ] AI tasks chạy async (không block request)
- [ ] Không có hardcoded credentials trong code

---

## Troubleshooting

| Lỗi | Fix |
|-----|-----|
| `Database does not exist` | Tạo DB test: Django tự tạo nhưng cần quyền PostgreSQL |
| `Import error` trong test | Kiểm tra `DJANGO_SETTINGS_MODULE` đã đúng chưa |
| Test bị treo (AI grading) | Mock OpenAI/Whisper client trong test: `@patch('apps.exercises.services.openai_client')` |
