# English Study LMS — API Specification

> **Base URL:** `http://localhost:8000/api/v1`  
> **Production:** `https://api.english-study.vn/api/v1`  
> **Format:** JSON (`Content-Type: application/json`)  
> **Timezone:** `Asia/Ho_Chi_Minh` (UTC+7) — tất cả timestamps trả về đều theo ISO 8601 với offset `+07:00`  
> **Số tiền:** đơn vị VNĐ (integer), kèm field `*_display` định dạng kiểu `"150.000 ₫"`  
> **Phân trang:** `?page=N` (mặc định 20 items/trang) — xem [Pagination](#pagination)

---

## Mục lục

1. [Authentication & Bảo mật](#1-authentication--bảo-mật)
2. [Users & Profile](#2-users--profile)
3. [Curriculum (Khoá học, Chương, Bài học)](#3-curriculum-khoá-học-chương-bài-học)
4. [Exercises (Bài tập 4 kỹ năng)](#4-exercises-bài-tập-4-kỹ-năng)
5. [Progress & Submissions (Nộp bài & Tiến độ)](#5-progress--submissions-nộp-bài--tiến-độ)
6. [Grammar (Ngữ pháp)](#6-grammar-ngữ-pháp)
7. [Vocabulary & Flashcards (Từ vựng & Thẻ ghi nhớ)](#7-vocabulary--flashcards-từ-vựng--thẻ-ghi-nhớ)
8. [Gamification (Điểm XP, Huy hiệu, Bảng xếp hạng)](#8-gamification-điểm-xp-huy-hiệu-bảng-xếp-hạng)
9. [Payments (Thanh toán)](#9-payments-thanh-toán)
10. [Notifications (Thông báo)](#10-notifications-thông-báo)
11. [Dashboard (Tổng quan học viên)](#11-dashboard-tổng-quan-học-viên)
12. [Admin Endpoints](#12-admin-endpoints)
13. [Mã lỗi chung](#13-mã-lỗi-chung)
14. [Pagination](#14-pagination)

---

## 1. Authentication & Bảo mật

### Cơ chế xác thực

Hệ thống sử dụng **JWT 5 lớp bảo mật**:

| Lớp | Mô tả |
|-----|-------|
| Layer 1 | `simplejwt` blacklist — token bị thu hồi khi logout |
| Layer 2 | Custom claims: `role`, `account_type`, `current_level` được nhúng vào Access Token |
| Layer 3 | `SessionToken` — mỗi thiết bị đăng nhập lưu JTI riêng, có thể thu hồi từng phiên |
| Layer 4 | Throttle: `5/min` cho login/register, `30/min` cho submissions |
| Layer 5 | `IsAdmin`, `IsPremium`, `IsAdminOrReadOnly` permission classes |

**Token được lưu trong HttpOnly Cookie** (không trong `localStorage`/`sessionStorage`):

| Cookie | Nội dung | Max-Age |
|--------|----------|---------|
| `es_access` | Access Token (JWT) | 60 phút |
| `es_refresh` | Refresh Token (JWT) | 7 ngày |

> FE **không cần** gắn `Authorization: Bearer ...` header — cookies được gửi tự động khi `credentials: 'include'`.

---

### POST `/auth/auth/register/`

Đăng ký tài khoản mới. Trả về access/refresh token trong cookie.

**Request Body:**
```json
{
  "email": "hoc.vien@example.com",
  "first_name": "Học",
  "last_name": "Viên",
  "password": "SecurePass@123",
  "password2": "SecurePass@123"
}
```

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `email` | string | ✅ | Dùng làm username đăng nhập |
| `first_name` | string | ✅ | Tên |
| `last_name` | string | ✅ | Họ |
| `password` | string | ✅ | Mật khẩu (phải qua `validate_password`) |
| `password2` | string | ✅ | Xác nhận mật khẩu |

**Response `201 Created`:**
```json
{
  "message": "Đăng ký thành công!",
  "user_id": 42
}
```
*Kèm theo: Set-Cookie `es_access` và `es_refresh`.*

**Lỗi phổ biến:**
- `400` — email đã tồn tại, password không khớp, password quá yếu

---

### POST `/auth/auth/login/`

Đăng nhập, nhận JWT trong cookie. Throttle: **5 lần/phút** theo IP.

**Request Body:**
```json
{
  "email": "hoc.vien@example.com",
  "password": "SecurePass@123"
}
```

**Response `200 OK`:**
```json
{
  "message": "Đăng nhập thành công!",
  "user": {
    "id": 42,
    "email": "hoc.vien@example.com",
    "full_name": "Học Viên",
    "role": "student",
    "account_type": "free",
    "current_level": "A1"
  }
}
```

| Field `user` | Type | Mô tả |
|-------------|------|-------|
| `id` | integer | ID người dùng |
| `email` | string | Email đăng ký |
| `full_name` | string | Họ tên |
| `role` | enum: `student`, `teacher`, `admin` | Phân quyền |
| `account_type` | enum: `free`, `premium` | Loại tài khoản |
| `current_level` | enum: `A1`, `A2`, `B1`, `B2`, `C1` | Trình độ hiện tại |

**Lỗi phổ biến:**
- `401` — sai email/password
- `429` — quá nhiều lần thử

---

### POST `/auth/auth/logout/`

Đăng xuất: blacklist refresh token, thu hồi `SessionToken`, xoá cookie.

*Không có request body.*

**Response `200 OK`:**
```json
{ "message": "Đăng xuất thành công!" }
```

---

### POST `/auth/auth/token/refresh/`

Gia hạn Access Token từ Refresh Token trong cookie. FE nên gọi tự động khi nhận `401`.

*Không có request body — đọc cookie `es_refresh` tự động.*

**Response `200 OK`:**
```json
{ "message": "Token đã gia hạn." }
```
*Kèm theo: Set-Cookie mới cho `es_access` (và `es_refresh` nếu được rotate).*

---

## 2. Users & Profile

### GET/PATCH `/auth/me/`

Lấy hoặc cập nhật thông tin cá nhân.

**Response `200 OK`:**
```json
{
  "id": 42,
  "email": "hoc.vien@example.com",
  "first_name": "Học",
  "last_name": "Viên",
  "role": "student",
  "account_type": "free",
  "current_level": "A1",
  "target_level": "B2",
  "date_joined": "2026-01-15T08:00:00+07:00",
  "profile": {
    "avatar_url": "https://cdn.example.com/avatars/42.jpg",
    "bio": "Đang học B1",
    "nationality": "VN",
    "native_language": "vi",
    "timezone": "Asia/Ho_Chi_Minh",
    "study_reminder_time": "07:00:00",
    "daily_goal_minutes": 30
  },
  "settings": {
    "ui_language": "vi",
    "audio_autoplay": true,
    "show_phonetic": true,
    "dark_mode": false,
    "email_notifications": true
  }
}
```

**PATCH Body** (tất cả optional):
```json
{
  "first_name": "Học",
  "last_name": "Viên Pro",
  "target_level": "B1",
  "profile": {
    "bio": "Đang học B1",
    "daily_goal_minutes": 45
  },
  "settings": {
    "dark_mode": true,
    "email_notifications": false
  }
}
```
> `email`, `role`, `date_joined` là **read-only**, không thể PATCH.

---

### PATCH `/auth/me/password/`

Đổi mật khẩu.

**Request Body:**
```json
{
  "old_password": "SecurePass@123",
  "new_password": "NewPass@456"
}
```

**Response `200 OK`:**
```json
{ "message": "Đổi mật khẩu thành công." }
```

---

### GET `/auth/me/devices/`

Danh sách phiên đăng nhập đang hoạt động (thiết bị).

**Response `200 OK`:**
```json
[
  {
    "id": 7,
    "device_name": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "ip_address": "123.45.67.89",
    "created_at": "2026-03-20T10:30:00+07:00",
    "expires_at": 1743500000
  }
]
```

---

### DELETE `/auth/me/devices/{id}/`

Thu hồi phiên đăng nhập trên thiết bị cụ thể (đăng xuất từ xa).

**Response `200 OK`:**
```json
{ "message": "Thiết bị đã bị thu hồi." }
```

---

## 3. Curriculum (Khoá học, Chương, Bài học)

### GET `/curriculum/cefr-levels/`

Danh sách cấp độ CEFR. **Không cần đăng nhập.**

**Response `200 OK`:**
```json
[
  { "id": 1, "code": "A1", "name": "Beginner", "name_vi": "Sơ cấp", "order": 1, "is_active": true },
  { "id": 2, "code": "A2", "name": "Elementary", "name_vi": "Tiền trung cấp", "order": 2, "is_active": true },
  { "id": 3, "code": "B1", "name": "Intermediate", "name_vi": "Trung cấp", "order": 3, "is_active": true },
  { "id": 4, "code": "B2", "name": "Upper-Intermediate", "name_vi": "Trên trung cấp", "order": 4, "is_active": true },
  { "id": 5, "code": "C1", "name": "Advanced", "name_vi": "Nâng cao", "order": 5, "is_active": true }
]
```

---

### GET `/curriculum/courses/`

Danh sách khoá học. **Không cần đăng nhập.** Hỗ trợ filter/search.

**Query Params:**

| Param | Type | Mô tả |
|-------|------|-------|
| `level__code` | string | Filter theo cấp độ, VD: `A1` |
| `is_premium` | boolean | `true` / `false` |
| `search` | string | Tìm theo title/description |
| `ordering` | string | `created_at`, `-created_at`, `title` |

**Response `200 OK`:**
```json
{
  "count": 12,
  "next": "http://localhost:8000/api/v1/curriculum/courses/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "A1 Foundation",
      "slug": "a1-foundation",
      "description": "Khoá học cơ bản cho người mới bắt đầu",
      "level": { "id": 1, "code": "A1", "name": "Beginner", "name_vi": "Sơ cấp", "order": 1, "is_active": true },
      "is_premium": false,
      "thumbnail_url": "https://cdn.example.com/courses/a1.jpg",
      "total_lessons": 48
    }
  ]
}
```

---

### GET `/curriculum/courses/{id}/`

Chi tiết khoá học, bao gồm danh sách chương (chapters).

**Response `200 OK`:**
```json
{
  "id": 1,
  "title": "A1 Foundation",
  "slug": "a1-foundation",
  "description": "...",
  "level": { "code": "A1", ... },
  "is_premium": false,
  "thumbnail_url": "...",
  "total_lessons": 48,
  "chapters": [
    {
      "id": 10,
      "title": "Chapter 1: Greetings",
      "order": 1,
      "passing_score": 60,
      "lesson_count": 8,
      "lessons": [
        {
          "id": 101,
          "title": "Listening: Hello World",
          "lesson_type": "listening",
          "order": 1,
          "estimated_minutes": 15,
          "is_free_preview": true,
          "unlock_rules": [],
          "progress_status": "available"
        }
      ]
    }
  ]
}
```

**`progress_status`** (yêu cầu đăng nhập để có giá trị thực):

| Giá trị | Mô tả |
|---------|-------|
| `locked` | Chưa mở khoá |
| `available` | Có thể học |
| `in_progress` | Đang học |
| `completed` | Đã hoàn thành |

---

### POST `/curriculum/courses/` *(Admin/Teacher)*

Tạo khoá học mới.

**Request Body:**
```json
{
  "title": "B1 Intermediate",
  "slug": "b1-intermediate",
  "description": "...",
  "level": 3,
  "is_premium": true,
  "thumbnail_s3_key": "thumbnails/b1.jpg"
}
```

**Response `201 Created`:** Trả về object khoá học vừa tạo.

---

### GET `/curriculum/courses/{course_pk}/chapters/`

Danh sách chương trong khoá học.

**Response `200 OK`:** Array of `ChapterSerializer` (xem trên).

---

### GET `/curriculum/courses/{course_pk}/chapters/{chapter_pk}/lessons/`

Danh sách bài học trong chương.

**Response `200 OK`:** Array of `LessonSerializer`.

---

### GET `/curriculum/lessons/{id}/`

Chi tiết bài học.

**Response `200 OK`:**
```json
{
  "id": 101,
  "title": "Listening: Hello World",
  "lesson_type": "listening",
  "order": 1,
  "estimated_minutes": 15,
  "is_free_preview": true,
  "unlock_rules": [
    {
      "id": 5,
      "required_lesson": 100,
      "required_lesson_title": "Grammar: Present Simple",
      "min_score": 60.0
    }
  ],
  "progress_status": "locked"
}
```

> **`lesson_type`** có thể là: `listening`, `speaking`, `reading`, `writing`, `grammar`, `vocabulary`, `pronunciation`, `assessment`

---

## 4. Exercises (Bài tập 4 kỹ năng)

> Tất cả endpoint bên dưới **yêu cầu đăng nhập**.

---

### GET `/exercises/listening/{id}/`

Lấy bài tập Nghe với câu hỏi. Audio URL là **presigned S3 URL** (hết hạn sau `AWS_PRESIGNED_URL_EXPIRY` giây).

**Response `200 OK`:**
```json
{
  "id": 5,
  "title": "Airport Conversation",
  "cefr_level": "A2",
  "audio_url": "https://s3.amazonaws.com/bucket/audio/a2_airport.mp3?X-Amz-Expires=3600&...",
  "context_hint": "Nghe một cuộc hội thoại tại sân bay",
  "duration_seconds": 180,
  "total_points": 10,
  "questions": [
    {
      "id": 201,
      "question_text": "Where is the man going?",
      "question_type": "multiple_choice",
      "order": 1,
      "points": 2,
      "hint_text": null,
      "options": [
        { "id": 301, "option_text": "London", "order": 1 },
        { "id": 302, "option_text": "Paris", "order": 2 },
        { "id": 303, "option_text": "Tokyo", "order": 3 },
        { "id": 304, "option_text": "New York", "order": 4 }
      ]
    }
  ]
}
```

> ⚠️ `correct_answers_json` **không bao giờ trả về** cho học viên.

---

### GET `/exercises/speaking/{id}/`

Lấy bài tập Nói dạng role-play.

**Response `200 OK`:**
```json
{
  "id": 8,
  "title": "Ordering Coffee",
  "cefr_level": "A1",
  "scenario": "Bạn đang gọi đồ uống tại một quán cà phê",
  "dialogue_json": [
    { "speaker": "Barista", "text": "Good morning! What can I get you?" },
    { "speaker": "Student", "text": "___STUDENT_TURN___" },
    { "speaker": "Barista", "text": "Sure! Would you like that hot or iced?" }
  ],
  "target_sentence": "I'd like a large latte, please.",
  "karaoke_words_json": ["I'd", "like", "a", "large", "latte", "please"],
  "time_limit_seconds": 30
}
```

---

### GET `/exercises/reading/{id}/`

Lấy bài tập Đọc với đoạn văn và câu hỏi.

**Response `200 OK`:**
```json
{
  "id": 12,
  "title": "The Green City",
  "cefr_level": "B1",
  "article_title": "Singapore: The Garden City",
  "article_text": "Singapore is known for its green initiatives...",
  "vocab_tooltip_json": {
    "initiatives": { "meaning_vi": "sáng kiến", "ipa": "/ɪˈnɪʃ.ə.tɪvz/" }
  },
  "total_points": 15,
  "questions": [
    {
      "id": 250,
      "question_text": "What is Singapore known for?",
      "question_type": "multiple_choice",
      "order": 1,
      "points": 3,
      "hint_text": null,
      "options": [...]
    }
  ]
}
```

---

### GET `/exercises/writing/{id}/`

Lấy đề bài viết.

**Response `200 OK`:**
```json
{
  "id": 15,
  "title": "Describe Your School",
  "cefr_level": "A2",
  "prompt_text": "Write about your school. Describe the building, your favourite room, and the people there.",
  "prompt_image_url": null,
  "min_words": 80,
  "max_words": 150,
  "time_limit_minutes": 20,
  "structure_tips_json": {
    "paragraph_1": "Mô tả tổng quan (2-3 câu)",
    "paragraph_2": "Phòng yêu thích (3-4 câu)",
    "paragraph_3": "Con người (2-3 câu)"
  }
}
```

---

## 5. Progress & Submissions (Nộp bài & Tiến độ)

> Tất cả endpoint **yêu cầu đăng nhập**. Throttle submissions: **30 lần/phút**.

---

### POST `/progress/enroll/`

Đăng ký tham gia khoá học.

**Request Body:**
```json
{ "course_id": 1 }
```

**Response `201 Created`** (hoặc `200` nếu đã tồn tại):
```json
{
  "id": 10,
  "course": 1,
  "course_title": "A1 Foundation",
  "progress_percent": 0.0,
  "progress_display": "0,00%",
  "enrolled_at": "2026-03-24T09:00:00+07:00",
  "completed_at": null
}
```

---

### POST `/progress/submit/listening/`

Nộp đáp án bài Nghe. **Chấm tự động ngay lập tức**.

**Request Body:**
```json
{
  "lesson_id": 101,
  "exercise_id": 5,
  "answers": {
    "201": "301",
    "202": "305",
    "203": ["308", "309"]
  },
  "time_spent_seconds": 145
}
```

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `lesson_id` | integer | ✅ | ID bài học chứa bài tập |
| `exercise_id` | integer | ✅ | ID `ListeningExercise` |
| `answers` | object | ✅ | Key = `question_id` (string), Value = ID đáp án hoặc array |
| `time_spent_seconds` | integer | ❌ | Thời gian làm bài (giây), mặc định `0` |

**Response `201 Created`:**
```json
{
  "id": 1001,
  "exercise_type": "listening",
  "exercise_id": 5,
  "score": 85.0,
  "score_display": "85,00",
  "passed": true,
  "detail_json": {
    "total_questions": 5,
    "correct": 4,
    "wrong_ids": [203],
    "passing_score": 60
  },
  "created_at": "2026-03-24T09:05:00+07:00"
}
```

> Nếu `passed=true` và có `UnlockRule`, bài học tiếp theo sẽ được **tự động mở khoá**.

---

### POST `/progress/submit/reading/`

Nộp đáp án bài Đọc. **Chấm tự động ngay lập tức.** Cùng cấu trúc với Listening.

**Request Body:**
```json
{
  "lesson_id": 102,
  "exercise_id": 12,
  "answers": {
    "250": "401",
    "251": "405"
  },
  "time_spent_seconds": 320
}
```

**Response `201 Created`:** Cùng cấu trúc `ExerciseResult` như Listening.

---

### POST `/progress/submit/speaking/`

Nộp bài Nói (file audio). **Chấm bất đồng bộ qua Celery + AI.**

> ⚠️ FE cần **upload file lên S3 trước** (qua presigned PUT URL), rồi gửi `audio_s3_key` xuống.

**Request Body:**
```json
{
  "lesson_id": 103,
  "exercise_id": 8,
  "audio_s3_key": "submissions/speaking/user42/2026/03/24_abc123.webm",
  "target_sentence": "I'd like a large latte, please."
}
```

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `lesson_id` | integer | ✅ | ID bài học |
| `exercise_id` | integer | ✅ | ID `SpeakingExercise` |
| `audio_s3_key` | string (max 500) | ✅ | S3 key của file âm thanh đã upload |
| `target_sentence` | string (max 500) | ✅ | Câu mục tiêu cần đọc |

**Response `202 Accepted`:**
```json
{
  "submission_id": 55,
  "status": "pending",
  "message": "Bài đang được chấm..."
}
```

> FE **poll** `GET /progress/submissions/speaking/55/` để nhận kết quả (xem bên dưới).

---

### GET `/progress/submissions/speaking/{id}/`

Kiểm tra trạng thái chấm bài Nói.

**Response `200 OK`:**

*Khi đang chấm (`pending`):*
```json
{
  "id": 55,
  "exercise_id": 8,
  "status": "pending",
  "transcript": null,
  "ai_score": null,
  "ai_score_display": "Đang chấm...",
  "score_pronunciation": null,
  "score_fluency": null,
  "score_intonation": null,
  "score_vocabulary": null,
  "error_list_json": null,
  "submitted_at": "2026-03-24T09:10:00+07:00"
}
```

*Khi đã chấm xong (`completed`):*
```json
{
  "id": 55,
  "exercise_id": 8,
  "status": "completed",
  "transcript": "I'd like a large latte please",
  "ai_score": 78.5,
  "ai_score_display": "78,50",
  "score_pronunciation": 80.0,
  "score_fluency": 75.0,
  "score_intonation": 82.0,
  "score_vocabulary": 76.0,
  "error_list_json": [
    { "word": "latte", "error": "missing final /t/ aspiration", "ipa_expected": "/ˈlɑː.teɪ/" }
  ],
  "submitted_at": "2026-03-24T09:10:00+07:00"
}
```

**`status`** có thể là: `pending` | `processing` | `completed` | `failed`

**Rubric chấm Speaking (Whisper + GPT-4o):**
| Tiêu chí | Trọng số | Field |
|----------|---------|-------|
| Phát âm | 35% | `score_pronunciation` |
| Độ trôi chảy | 25% | `score_fluency` |
| Ngữ điệu | 20% | `score_intonation` |
| Từ vựng | 20% | `score_vocabulary` |

---

### POST `/progress/submit/writing/`

Nộp bài viết luận. **Chấm bất đồng bộ qua Celery + AI.**

**Request Body:**
```json
{
  "lesson_id": 104,
  "exercise_id": 15,
  "content_text": "My school is a large building near the city centre. It has three floors and many classrooms. My favourite room is the library because it is quiet and has many books. The teachers are kind and helpful. I enjoy studying here every day."
}
```

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `lesson_id` | integer | ✅ | ID bài học |
| `exercise_id` | integer | ✅ | ID `WritingExercise` |
| `content_text` | string (min 20 từ) | ✅ | Nội dung bài viết |

**Response `202 Accepted`:**
```json
{
  "submission_id": 88,
  "word_count": 42,
  "word_count_display": "42",
  "status": "pending",
  "message": "Bài đang được AI chấm..."
}
```

---

### GET `/progress/submissions/writing/{id}/`

Kiểm tra trạng thái chấm bài Viết.

**Response `200 OK`** (khi xong):
```json
{
  "id": 88,
  "exercise_id": 15,
  "status": "completed",
  "word_count": 42,
  "ai_score": 72.0,
  "ai_score_display": "72,00",
  "score_task_achievement": 70.0,
  "score_grammar": 75.0,
  "score_vocabulary": 68.0,
  "score_coherence": 74.0,
  "feedback_text": "Bài viết có cấu trúc tốt nhưng cần đa dạng từ vựng hơn.",
  "error_list_json": [
    { "original": "large building near", "suggestion": "large building located near", "type": "preposition" }
  ],
  "vocab_cefr_json": {
    "large": "A2", "centre": "B1", "library": "A2"
  },
  "teacher_comment": null,
  "submitted_at": "2026-03-24T09:15:00+07:00"
}
```

**Rubric chấm Writing (GPT-4o):**
| Tiêu chí | Trọng số | Field |
|----------|---------|-------|
| Task Achievement | 25% | `score_task_achievement` |
| Grammar | 25% | `score_grammar` |
| Vocabulary | 25% | `score_vocabulary` |
| Coherence & Cohesion | 25% | `score_coherence` |

---

### GET `/progress/lessons/{lesson_id}/`

Trạng thái tiến độ của một bài học.

**Response `200 OK`:**
```json
{
  "id": 200,
  "lesson": 101,
  "lesson_title": "Listening: Hello World",
  "status": "completed",
  "best_score": 85.0,
  "best_score_display": "85,00",
  "attempts_count": 2,
  "last_attempt_at": "2026-03-24T09:05:00+07:00",
  "completed_at": "2026-03-24T09:05:00+07:00"
}
```

---

## 6. Grammar (Ngữ pháp)

> Không bắt buộc đăng nhập nhưng có xác thực sẽ hiển thị progress.  
> **Cache 5 phút** server-side (nội dung ít thay đổi).

---

### GET `/grammar/`

Danh sách chủ đề ngữ pháp (phân trang). Hỗ trợ filter theo cấp độ.

**Query Params:**

| Param | Type | Mô tả |
|-------|------|-------|
| `level` | string | `A1`, `A2`, `B1`, `B2`, `C1` |
| `page` | integer | Số trang |

**Response `200 OK`:**
```json
{
  "count": 427,
  "next": "http://localhost:8000/api/v1/grammar/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The present simple of be – FORM",
      "slug": "a1-the-present-simple-of-be-form",
      "level": "A1",
      "order": 1,
      "icon": null,
      "description": "Cấu trúc động từ 'be' ở thì hiện tại đơn",
      "analogy": null,
      "is_published": true,
      "rule_count": 4
    }
  ]
}
```

---

### GET `/grammar/{slug}/`

Chi tiết chủ đề ngữ pháp với tất cả quy tắc và ví dụ.

**Response `200 OK`:**
```json
{
  "id": 1,
  "title": "The present simple of be – FORM",
  "slug": "a1-the-present-simple-of-be-form",
  "level": "A1",
  "order": 1,
  "icon": null,
  "description": "Cấu trúc động từ 'be' ở thì hiện tại đơn",
  "analogy": null,
  "real_world_use": "Dùng để giới thiệu bản thân, mô tả đặc điểm",
  "memory_hook": null,
  "is_published": true,
  "lesson": null,
  "created_at": "2026-03-20T14:00:00+07:00",
  "updated_at": "2026-03-20T14:00:00+07:00",
  "rules": [
    {
      "id": 10,
      "title": "Affirmative form",
      "formula": "Subject + am/is/are + ...",
      "explanation": "I am, He/She/It is, We/You/They are",
      "memory_hook": null,
      "is_exception": false,
      "order": 1,
      "examples": [
        {
          "id": 100,
          "sentence": "I am a student.",
          "translation": "Tôi là học sinh.",
          "context": null,
          "highlight": "am",
          "audio_url": null
        }
      ]
    }
  ]
}
```

---

## 7. Vocabulary & Flashcards (Từ vựng & Thẻ ghi nhớ)

> Tất cả **yêu cầu đăng nhập**.

---

### GET `/vocabulary/words/`

Tra cứu từ vựng Oxford. Hỗ trợ filter đầy đủ.

**Query Params:**

| Param | Type | Mô tả |
|-------|------|-------|
| `cefr_level` | string | `A1`...`C1` |
| `domain` | string | `general`, `academic`, `business`, `technology`... |
| `part_of_speech` | string | `noun`, `verb`, `adjective`, `adverb`... |
| `is_oxford_3000` | boolean | `true`/`false` |
| `is_oxford_5000` | boolean | `true`/`false` |
| `search` | string | Tìm theo từ hoặc nghĩa tiếng Việt |
| `ordering` | string | `word`, `-word`, `frequency_rank` |

**Response `200 OK`:**
```json
{
  "count": 5000,
  "results": [
    {
      "id": 1,
      "word": "ability",
      "part_of_speech": "noun",
      "cefr_level": "B2",
      "domain": "general",
      "ipa_uk": "/əˈbɪl.ɪ.ti/",
      "ipa_us": "/əˈbɪl.ɪ.ti/",
      "audio_uk_url": "https://s3.../audio/ability_uk.mp3?X-Amz-...",
      "audio_us_url": "https://s3.../audio/ability_us.mp3?X-Amz-...",
      "meaning_vi": "khả năng, năng lực",
      "example_en": "She has the ability to speak three languages.",
      "example_vi": "Cô ấy có khả năng nói ba thứ tiếng.",
      "collocations_json": ["natural ability", "great ability", "ability to do"],
      "synonyms_json": ["capability", "skill", "capacity"],
      "is_oxford_3000": true,
      "is_oxford_5000": true,
      "frequency_rank": 1250
    }
  ]
}
```

---

### GET `/vocabulary/words/{id}/`

Chi tiết một từ vựng.

---

### GET `/vocabulary/flashcard-decks/`

Danh sách bộ thẻ (công khai + bộ của user).

**Query Params:** `cefr_level`, `domain`, `search`

**Response `200 OK`:**
```json
[
  {
    "id": 3,
    "name": "A1 Essential 300",
    "description": "300 từ A1 Oxford quan trọng nhất",
    "cefr_level": "A1",
    "domain": "general",
    "is_public": true,
    "card_count": 300
  }
]
```

---

### POST `/vocabulary/flashcard-decks/`

Tạo bộ thẻ mới (bộ của user).

**Request Body:**
```json
{
  "name": "My Custom Deck",
  "description": "Từ vựng tôi gặp trong tuần",
  "cefr_level": "B1",
  "domain": "business",
  "is_public": false
}
```

---

### GET `/vocabulary/flashcard-decks/{id}/study/`

Lấy toàn bộ thẻ trong deck + tiến độ cá nhân (dùng cho phiên học SM-2).

**Response `200 OK`:**
```json
{
  "id": 3,
  "name": "A1 Essential 300",
  "cefr_level": "A1",
  "card_count": 300,
  "flashcards": [
    {
      "id": 50,
      "front_text": "ability",
      "back_text": "khả năng, năng lực",
      "card_type": "word_meaning",
      "word_detail": { "word": "ability", "ipa_uk": "/əˈbɪl.ɪ.ti/", ... }
    }
  ]
}
```

---

### POST `/vocabulary/flashcards/sm2/`

Cập nhật tiến độ SM-2 sau khi đánh giá một thẻ. Tính lại `interval_days` và `next_review_date`.

**Request Body:**
```json
{
  "flashcard_id": 50,
  "rating": 3
}
```

| `rating` | Nghĩa |
|---------|-------|
| 0 | Again — Không nhớ gì |
| 1 | Hard — Nhớ rất khó khăn |
| 2 | Good — Nhớ được sau một chút |
| 3 | Easy — Nhớ được |
| 4 | Very Easy — Nhớ rất dễ |
| 5 | Perfect — Nhớ hoàn toàn ngay lập tức |

**Response `200 OK`:**
```json
{
  "flashcard": 50,
  "ease_factor": 2.5,
  "interval_days": 4,
  "repetitions": 2,
  "next_review_date": "2026-03-28",
  "last_rating": 3,
  "is_mastered": false
}
```

---

## 8. Gamification (Điểm XP, Huy hiệu, Bảng xếp hạng)

> Tất cả **yêu cầu đăng nhập**.

---

### GET `/gamification/achievements/`

Danh sách tất cả huy hiệu trong hệ thống (đã đạt và chưa).

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "First Step",
    "name_vi": "Bước Đầu Tiên",
    "description": "Hoàn thành bài học đầu tiên",
    "category": "lesson",
    "condition_type": "lesson_count",
    "threshold_value": 1,
    "icon_url": null,
    "icon_emoji": "🎯",
    "xp_reward": 50
  }
]
```

---

### GET `/gamification/my-achievements/`

Các huy hiệu đã đạt được của user hiện tại.

**Response `200 OK`:**
```json
[
  {
    "id": 5,
    "earned_at": "2026-03-20T10:00:00+07:00",
    "achievement": {
      "id": 1,
      "name": "First Step",
      "name_vi": "Bước Đầu Tiên",
      "icon_emoji": "🎯",
      "xp_reward": 50
    }
  }
]
```

---

### GET `/gamification/xp-log/`

Lịch sử nhận XP (50 giao dịch gần nhất).

**Response `200 OK`:**
```json
[
  {
    "id": 101,
    "source": "lesson_complete",
    "xp_amount": 20,
    "xp_amount_display": "+20 XP",
    "note": "Hoàn thành bài Listening A1",
    "created_at": "2026-03-24T09:05:00+07:00"
  }
]
```

---

### GET `/gamification/leaderboard/`

Bảng xếp hạng XP. Top 100 user.

**Query Params:**

| Param | Type | Mô tả |
|-------|------|-------|
| `period` | string | `weekly` (mặc định) \| `monthly` \| `alltime` |

**Response `200 OK`:**
```json
[
  {
    "rank": 1,
    "user": 15,
    "user_name": "Nguyễn An",
    "xp_total": 4500,
    "xp_display": "4.500 XP",
    "is_self": false
  },
  {
    "rank": 7,
    "user": 42,
    "user_name": "Học Viên",
    "xp_total": 1200,
    "xp_display": "1.200 XP",
    "is_self": true
  }
]
```

---

### GET `/gamification/certificates/`

Chứng chỉ hoàn thành khoá học của user.

**Response `200 OK`:**
```json
[
  {
    "id": 2,
    "verification_code": "ES-A1-20260324-ABC123",
    "issued_at": "2026-03-24T10:00:00+07:00",
    "pdf_s3_key": "certificates/user42/a1-foundation.pdf",
    "course_title": "A1 Foundation",
    "level_name": "Beginner"
  }
]
```

---

## 9. Payments (Thanh toán)

---

### GET `/payments/plans/`

Danh sách gói đăng ký. **Không cần đăng nhập.**

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "monthly",
    "name_vi": "Gói Tháng",
    "billing_period": "monthly",
    "price_vnd": 199000,
    "price_display": "199.000 ₫",
    "original_price_vnd": 299000,
    "original_price_display": "299.000 ₫",
    "discount_percent": "33%",
    "features_json": ["Không giới hạn bài học", "Chấm Speaking AI", "Chấm Writing AI"],
    "max_lessons_per_day": 999
  }
]
```

---

### POST `/payments/coupons/validate/`

Kiểm tra mã giảm giá. **Yêu cầu đăng nhập.**

**Request Body:**
```json
{
  "code": "HOCTOT2026",
  "plan_id": 1
}
```

**Response `200 OK`:**
```json
{
  "code": "HOCTOT2026",
  "discount_type": "percent",
  "discount_value": 20.0,
  "discount_display": "Giảm 20%",
  "final_price_display": "159.200 ₫"
}
```

**Lỗi phổ biến:**
- `404` — coupon không tồn tại
- `400` — hết hạn, hết lượt, đã dùng, không áp dụng cho gói này

---

### POST `/payments/checkout/`

Khởi tạo thanh toán. **Yêu cầu đăng nhập.**

**Request Body:**
```json
{
  "plan_id": 1,
  "gateway": "vnpay",
  "coupon_code": "HOCTOT2026",
  "return_url": "https://english-study.vn/payment/result"
}
```

| Field | Type | Required | Mô tả |
|-------|------|----------|-------|
| `plan_id` | integer | ✅ | ID gói đăng ký |
| `gateway` | enum: `vnpay`, `stripe` | ✅ | Cổng thanh toán |
| `coupon_code` | string | ❌ | Mã giảm giá (nếu có) |
| `return_url` | URL | ❌ | URL redirect sau thanh toán |

**Response `201 Created`:**
```json
{
  "transaction_id": 500,
  "amount_vnd": 159200,
  "amount_display": "159.200 ₫",
  "discount_vnd": 39800,
  "payment_url": "https://payment-gateway.example.com/pay?txn=500&amount=159200"
}
```

> FE redirect user đến `payment_url`. Sau khi thanh toán, cổng gọi webhook.

---

### POST `/payments/webhooks/vnpay/` *(Webhook — không cần auth)*

VNPay IPN callback. **Công khai**, hệ thống xác minh bằng HMAC nội bộ.

**Request Body (form params từ VNPay):**
```
vnp_TxnRef=500
vnp_ResponseCode=00
vnp_Amount=15920000
vnp_SecureHash=...
```

**Response `200 OK`:**
```json
{ "RspCode": "00", "Message": "Confirm Success" }
```

> Khi `vnp_ResponseCode=00`: kích hoạt subscription, cập nhật `account_type=premium`.

---

### POST `/payments/webhooks/stripe/` *(Webhook — không cần auth)*

Stripe webhook. Xác minh `Stripe-Signature` header bằng `STRIPE_WEBHOOK_SECRET`.

---

### GET `/payments/transactions/`

Lịch sử thanh toán của user. **Yêu cầu đăng nhập.**

**Response `200 OK`:**
```json
[
  {
    "id": 500,
    "plan": 1,
    "plan_name": "Gói Tháng",
    "gateway": "vnpay",
    "status": "success",
    "amount_vnd": 159200,
    "amount_display": "159.200 ₫",
    "discount_vnd": 39800,
    "gateway_txn_id": "VNP-2026032412345",
    "created_at": "2026-03-24T10:00:00+07:00"
  }
]
```

**`status`**: `pending` | `success` | `failed` | `refunded`

---

## 10. Notifications (Thông báo)

> Tất cả **yêu cầu đăng nhập**.

---

### GET `/notifications/`

50 thông báo gần nhất.

**Response `200 OK`:**
```json
[
  {
    "id": 30,
    "notification_type": "grade_ready",
    "title": "Bài Speaking đã được chấm",
    "body": "Bài bài Ordering Coffee của bạn đạt 78.5 điểm",
    "is_read": false,
    "read_at": null,
    "created_at": "2026-03-24T09:12:00+07:00"
  }
]
```

---

### PATCH `/notifications/{id}/read/`

Đánh dấu thông báo đã đọc.

**Response `200 OK`:**
```json
{ "message": "Đã đánh dấu đã đọc." }
```

---

## 11. Dashboard (Tổng quan học viên)

> **Yêu cầu đăng nhập.**

### GET `/progress/dashboard/`

*(Chú thích: URL thực là `/api/v1/progress/dashboard/` — xem `DashboardView` trong `progress/views.py`)*

Tổng hợp toàn bộ thống kê học tập.

**Response `200 OK`:**
```json
{
  "streak": {
    "current_streak": 5,
    "longest_streak": 14,
    "last_activity_date": "2026-03-23",
    "streak_protected_until": null
  },
  "cumulative_scores": [
    {
      "level_code": "A1",
      "avg_listening": 85.0,
      "avg_speaking": 72.0,
      "avg_reading": 90.0,
      "avg_writing": 68.0,
      "overall_avg": 78.75,
      "overall_display": "78,75%",
      "total_exercises_done": 24,
      "cefr_equivalent": "A2"
    }
  ],
  "enrolled_courses": [
    {
      "id": 10,
      "course": 1,
      "course_title": "A1 Foundation",
      "progress_percent": 66.67,
      "progress_display": "66,67%",
      "enrolled_at": "2026-03-01T08:00:00+07:00",
      "completed_at": null
    }
  ],
  "recent_results": [
    {
      "id": 1001,
      "exercise_type": "listening",
      "exercise_id": 5,
      "score": 85.0,
      "score_display": "85,00",
      "passed": true,
      "detail_json": { ... },
      "created_at": "2026-03-24T09:05:00+07:00"
    }
  ],
  "total_xp": 1200,
  "total_xp_display": "1.200 XP"
}
```

---

## 12. Admin Endpoints

> Yêu cầu `role=admin`.

### GET `/auth/admin/users/`

Danh sách tất cả user. Hỗ trợ filter/search/ordering.

**Query Params:** `role`, `account_type`, `is_active`, `search` (email/tên), `ordering`

**Response `200 OK`:** Array of:
```json
{
  "id": 42,
  "email": "hoc.vien@example.com",
  "first_name": "Học",
  "last_name": "Viên",
  "role": "student",
  "account_type": "free",
  "current_level": "A1",
  "is_active": true,
  "date_joined": "2026-01-15T08:00:00+07:00",
  "last_login": "2026-03-24T09:00:00+07:00"
}
```

### GET/PATCH/DELETE `/auth/admin/users/{id}/`

Quản lý chi tiết user. Cho phép thay đổi `role`, `is_active`, `account_type`.

---

## 13. Mã lỗi chung

| HTTP | Tình huống | Response body |
|------|-----------|---------------|
| `400 Bad Request` | Dữ liệu không hợp lệ | `{ "field_name": ["error message"] }` |
| `401 Unauthorized` | Chưa đăng nhập hoặc token hết hạn | `{ "detail": "..." }` |
| `403 Forbidden` | Không có quyền | `{ "detail": "..." }` |
| `404 Not Found` | Tài nguyên không tồn tại | `{ "detail": "..." }` |
| `429 Too Many Requests` | Quá rate limit | `{ "detail": "Request was throttled..." }` |
| `500 Internal Server Error` | Lỗi máy chủ | `{ "detail": "..." }` |

---

## 14. Pagination

Tất cả endpoint trả về **list** (trừ một số endpoint nhỏ) đều dùng `StandardPagination`.

**Response structure:**
```json
{
  "count": 427,
  "next": "http://localhost:8000/api/v1/grammar/?page=2",
  "previous": null,
  "results": [...]
}
```

**Query Params:**
- `?page=N` — Trang N (bắt đầu từ 1)
- `?page_size=N` — Số item/trang (mặc định 20, tối đa 100)

---

## Phụ lục: Luồng FE điển hình

### Luồng đăng nhập và học bài Listening

```
1. POST /auth/auth/login/          → nhận cookie
2. GET  /curriculum/courses/?level__code=A1  → chọn khoá học
3. POST /progress/enroll/          → course_id=1
4. GET  /curriculum/courses/1/     → lấy chapters & lessons
5. GET  /curriculum/lessons/101/   → kiểm tra progress_status = "available"
6. GET  /exercises/listening/5/    → lấy audio_url + questions
7. [User nghe audio, làm trắc nghiệm]
8. POST /progress/submit/listening/ → { lesson_id, exercise_id, answers }
9. Response: { score: 85, passed: true }  → UI hiển thị kết quả
10. GET /curriculum/lessons/102/   → progress_status = "available" (vừa mở khoá)
```

### Luồng nộp bài Speaking

```
1. GET  /exercises/speaking/8/     → lấy target_sentence, dialogue
2. [User ghi âm → upload file lên S3 presigned URL]
3. POST /progress/submit/speaking/ → { audio_s3_key, target_sentence, ... }
4. Response: { submission_id: 55, status: "pending" }
5. [Poll mỗi 3-5 giây]
   GET /progress/submissions/speaking/55/ → status: "pending"
   GET /progress/submissions/speaking/55/ → status: "completed", ai_score: 78.5
6. UI hiển thị điểm + error_list_json (lỗi phát âm từng từ)
```

### Luồng nộp bài Writing

```
1. GET  /exercises/writing/15/     → lấy prompt_text, min_words, max_words
2. [User viết bài trong textarea, đếm từ realtime]
3. POST /progress/submit/writing/  → { content_text: "..." }
4. Response: { submission_id: 88, word_count: 42, status: "pending" }
5. [Poll]
   GET /progress/submissions/writing/88/ → status: "completed"
6. UI hiển thị: ai_score, 4 tiêu chí rubric, feedback_text, error_list_json
```

### Luồng thanh toán VNPay

```
1. GET  /payments/plans/           → hiển thị 3 gói
2. POST /payments/coupons/validate/ → kiểm tra mã giảm giá
3. POST /payments/checkout/        → { plan_id, gateway: "vnpay", coupon_code }
4. Response: { payment_url: "https://..." }
5. FE redirect → user thanh toán trên VNPay
6. VNPay gọi POST /payments/webhooks/vnpay/ (server-to-server)
7. Backend kích hoạt subscription → account_type = "premium"
8. User redirect về return_url
9. GET /auth/me/ → account_type: "premium" ✅
```
