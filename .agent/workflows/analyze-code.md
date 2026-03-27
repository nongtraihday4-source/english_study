---
description: Phân tích và review code cho dự án English Study LMS (Django + DRF + Vue 3 + TailwindCSS)
---

# Quy trình Phân tích Code — English Study LMS

## Bước 1: Thu thập Context

Trước khi phân tích, xác định rõ:
- Đây là phần nào của hệ thống? (backend app nào trong `backend/apps/`, hay component Vue nào trong `frontend/src/`?)
- Phạm vi ảnh hưởng: chỉ 1 file, 1 module, hay toàn bộ flow (ví dụ: submit exercise → score → unlock)?
- Cấp bậc LMS liên quan: Level → Course → Chapter → Lesson → Exercise?

## Bước 2: Diễn giải Logic (Ngôn ngữ tự nhiên)

Diễn giải lại logic bằng tiếng Việt để kiểm tra sự thấu hiểu. Nếu diễn giải không khớp ý định → dừng và hỏi lại.

## Bước 3: Phát hiện Điểm Mù (Audit Mode)

Kiểm tra theo thứ tự ưu tiên:

### 3a. Bảo mật (OWASP Top 10 cho LMS)
- **Unlock bypass**: API submit có kiểm tra `passing_score` trước khi unlock lesson tiếp theo không?
- **XSS**: User-generated content (writing submission, comment) có bị escape đúng không?
- **IDOR**: API `/exercises/{id}/submit/` có kiểm tra user đã enroll course chưa?
- **AI Prompt Injection**: Input của user có được sanitize trước khi đưa vào GPT-4o prompt không?
- **JWT**: Token có custom claims đúng (`user_id`, `role`, `subscription_status`) không?

### 3b. Performance
- **N+1 Queries**: Có dùng `select_related`/`prefetch_related` đầy đủ chưa?
- **Cache**: Dữ liệu tĩnh (vocabulary list, course structure) có được cache Redis không?
- **Celery**: AI grading tasks (Whisper, GPT-4o) có chạy async qua Celery không? Tuyệt đối không block request.

### 3c. Logic Nghiệp vụ
- **Temporal Consistency**: Unlock logic có đảm bảo bài trước đã pass trước khi mở bài sau?
- **Scoring Rules**: MC = `100 / total_questions` per correct (no penalty). Gap Fill: case-insensitive + trim. Drag & Drop: partial scoring.
- **Spaced Repetition**: `next_review_date` có dùng timezone `Asia/Ho_Chi_Minh` không?

### 3d. Architecture (Clean Architecture)
- Service Layer: Business logic có nằm trong `services.py`, KHÔNG trong `views.py` hay `models.py`?
- DTO: Service có trả về `dict` thay vì Model instance không?
- Vue Frontend: Logic UI phức tạp có tách ra composable `use*.js` không?

## Bước 4: Đề xuất Refactor

- Áp dụng SOLID và DRY.
- Chỉ đề xuất thay đổi cần thiết — không refactor code ngoài scope.
- Với Django: ưu tiên readability + performance.
- Với Vue 3: ưu tiên `<script setup>` + Pinia cho global state.

## Bước 5: Kế hoạch Test

Mỗi đề xuất thay đổi phải kèm test plan:
- **Django**: `python manage.py test apps.<app_name>` với ít nhất 1 unit test và 1 integration test.
- **AI Grading**: Kiểm thử prompt với ≥10 bài mẫu đã chấm tay trước khi deploy.
- **Frontend**: Manual test flow trên browser + kiểm tra Network tab cho API calls.