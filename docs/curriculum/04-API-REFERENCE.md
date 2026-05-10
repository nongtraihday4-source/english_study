# 📡 CURRICULUM APP — API Reference

> Quick reference cho tất cả endpoints, request/response formats

---

## BASE URL

```
http://localhost:8000/api/curriculum/
```

---

## ENDPOINTS

### 1️⃣ CEFR LEVELS

#### `GET /cefr-levels/`

Lấy danh sách tất cả CEFR levels

**Query Parameters:** Không có

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "code": "A1",
    "name": "Beginner",
    "name_vi": "Sơ cấp",
    "order": 1,
    "is_active": true
  },
  {
    "id": 2,
    "code": "A2",
    "name": "Elementary",
    "name_vi": "Tiền trung cấp",
    "order": 2,
    "is_active": true
  }
]
```

---

### 2️⃣ COURSES

#### `GET /courses/`

Lấy danh sách khóa học

**Query Parameters:**
```
?level__code=A1          # Filter by CEFR level
?is_premium=true         # Filter by premium status
?search=foundations      # Search by title/description
?ordering=-created_at    # Order by field
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Nền tảng tiếng Anh",
    "slug": "nen-tang-tieng-anh",
    "description": "Khoá học A1 xây dựng nền tảng vững chắc...",
    "level": {
      "id": 1,
      "code": "A1",
      "name": "Beginner",
      "name_vi": "Sơ cấp"
    },
    "is_premium": false,
    "total_lessons": 49,
    "thumbnail": null,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-03-20T14:15:00Z"
  }
]
```

---

#### `GET /courses/{id}/`

Lấy chi tiết khóa học cùng tất cả chapters

**Path Parameters:**
```
id: Course ID (integer)
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Nền tảng tiếng Anh",
  "slug": "nen-tang-tieng-anh",
  "description": "...",
  "level": {...},
  "is_premium": false,
  "is_active": true,
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "thumbnail": "https://...",
  "chapters": [
    {
      "id": 1,
      "title": "Giới thiệu bản thân",
      "order": 1,
      "description": "...",
      "passing_score": 60,
      "lesson_count": 7,
      "lessons": [
        {
          "id": 1,
          "title": "Vocabulary: Introduction",
          "lesson_type": "vocabulary",
          "order": 1,
          "estimated_minutes": 10,
          "is_active": true,
          "chapter_id": 1,
          "course_id": 1,
          "progress_status": "locked",
          "is_unlocked": false,
          "exercise_type": "vocabulary",
          "exercise_id": 42,
          "unlock_rules": []
        },
        {
          "id": 2,
          "title": "Grammar: Present Simple",
          "lesson_type": "grammar",
          "order": 2,
          "estimated_minutes": 15,
          "progress_status": "locked",
          "is_unlocked": false,
          "unlock_rules": [
            {
              "id": 1,
              "required_lesson": 1,
              "required_lesson_title": "Vocabulary: Introduction",
              "min_score": 60
            }
          ]
        }
      ]
    }
  ]
}
```

---

#### `POST /courses/` *(Admin only)*

Tạo khóa học mới

**Request Body:**
```json
{
  "title": "Nền tảng tiếng Anh",
  "slug": "nen-tang-tieng-anh",
  "description": "Khoá học A1...",
  "level": 1,
  "is_premium": false,
  "thumbnail": "file.png"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "...",
  "slug": "...",
  "...": "..."
}
```

---

#### `PATCH /courses/{id}/` *(Admin only)*

Cập nhật khóa học

**Request Body:** (Partial update)
```json
{
  "title": "Nền tảng tiếng Anh (Updated)",
  "is_premium": true
}
```

**Response:** `200 OK`

---

#### `DELETE /courses/{id}/` *(Admin only)*

Xoá khóa học (soft delete)

**Response:** `204 No Content`

---

### 3️⃣ CHAPTERS

#### `GET /courses/{course_pk}/chapters/`

Lấy danh sách chapters của khóa học

**Path Parameters:**
```
course_pk: Course ID
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Giới thiệu bản thân",
    "order": 1,
    "description": "...",
    "passing_score": 60,
    "lesson_count": 7,
    "lessons": [...]
  }
]
```

---

#### `POST /courses/{course_pk}/chapters/` *(Admin only)*

Tạo chapter mới

**Request Body:**
```json
{
  "title": "Gia đình & Bạn bè",
  "order": 2,
  "description": "Học về gia đình...",
  "passing_score": 70
}
```

**Response:** `201 Created`

---

### 4️⃣ LESSONS

#### `GET /courses/{course_pk}/chapters/{chapter_pk}/lessons/`

Lấy danh sách lessons trong chapter

**Path Parameters:**
```
course_pk: Course ID
chapter_pk: Chapter ID
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Vocabulary: Introduction",
    "lesson_type": "vocabulary",
    "order": 1,
    "estimated_minutes": 10,
    "is_active": true,
    "chapter_id": 1,
    "course_id": 1,
    "progress_status": "locked",
    "is_unlocked": false,
    "exercise_type": "vocabulary",
    "exercise_id": 42,
    "unlock_rules": []
  }
]
```

---

#### `GET /lessons/{id}/`

Lấy chi tiết lesson

**Path Parameters:**
```
id: Lesson ID
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Vocabulary: Introduction",
  "lesson_type": "vocabulary",
  "order": 1,
  "estimated_minutes": 10,
  "is_active": true,
  "chapter_id": 1,
  "course_id": 1,
  "progress_status": "in_progress",
  "is_unlocked": true,
  "exercise_type": "vocabulary",
  "exercise_id": 42,
  "unlock_rules": []
}
```

---

#### `POST /courses/{course_pk}/chapters/{chapter_pk}/lessons/` *(Admin only)*

Tạo lesson mới

**Request Body:**
```json
{
  "title": "Reading: Alice in Wonderland",
  "lesson_type": "reading",
  "order": 3,
  "estimated_minutes": 20
}
```

**Response:** `201 Created`

---

#### `PATCH /lessons/{id}/` *(Admin only)*

Cập nhật lesson

**Request Body:**
```json
{
  "title": "Reading: Updated",
  "estimated_minutes": 25
}
```

**Response:** `200 OK`

---

#### `DELETE /lessons/{id}/` *(Admin only)*

Xoá lesson (soft delete)

**Response:** `204 No Content`

---

### 5️⃣ LESSON CONTENT

#### `GET /lessons/{pk}/content/`

Lấy nội dung chi tiết của lesson (reading, grammar, vocab, exercises, v.v.)

**Path Parameters:**
```
pk: Lesson ID
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "lesson": 1,
  "reading_passage": "<p>Alice walked through the forest...</p>",
  "reading_image_url": "https://...",
  "reading_questions": [
    {
      "question": "What did Alice see in the forest?",
      "options": ["a tree", "a rabbit", "a cat"],
      "correct": 1,
      "explanation": "The passage says Alice saw a rabbit..."
    }
  ],
  "vocab_items": [
    {
      "word": "walked",
      "pos": "verb",
      "ipa": "/wɔːkt/",
      "meaning_vi": "đi bộ",
      "definition_en": "To move on foot",
      "example_en": "She walked to school.",
      "example_vi": "Cô ấy đi bộ tới trường.",
      "collocations": ["walk to", "walk around", "walk back"],
      "highlight_in_passage": true,
      "id": 123
    }
  ],
  "vocab_word_ids": [123, 124, 125],
  "grammar_topic_id": 42,
  "grammar_title": "Present Simple",
  "grammar_note": "Use for habitual actions...",
  "grammar_examples": [
    {
      "en": "I walk to school every day",
      "vi": "Tôi đi bộ tới trường mỗi ngày",
      "highlight": "walk"
    }
  ],
  "grammar_sections": [
    {
      "title": "Present Simple Usage",
      "grammar_topic_id": 42,
      "note": "Describe habitual actions or general truths",
      "examples": [...],
      "exercises": [
        {
          "type": "gap-fill",
          "prompt": "I ___ (walk) to school every day.",
          "options": ["walk", "walks", "walked"],
          "correct": 0,
          "explanation": "Subject 'I' takes base form 'walk'"
        }
      ]
    }
  ],
  "skill_sections": {
    "dictation": [...],
    "shadowing": [...],
    "guided_writing": [...]
  },
  "listening_content": {
    "audio_text": "Alice walked through the forest...",
    "translation_vi": "Alice đi bộ qua khu rừng...",
    "sentences": [...],
    "speed": 0.9,
    "comprehension_questions": [...],
    "dictation_sentences": [...]
  },
  "speaking_content": {
    "mode": "repeat",
    "sentences": [
      {
        "text": "I walk to school.",
        "translation_vi": "Tôi đi bộ tới trường.",
        "speed": 0.85,
        "focus_words": ["walk", "school"]
      }
    ],
    "dialogue": [...]
  },
  "writing_content": {
    "exercises": [
      {
        "type": "gap_fill",
        "prompt": "Complete the sentence: I ___ to school.",
        "prompt_vi": "Hoàn thành câu: Tôi ___ tới trường.",
        "grammar_hint": "Use Present Simple",
        "correct_answer": "walk",
        "min_words": 1,
        "max_words": 50,
        "sample_answer": "I walk to school every day."
      }
    ]
  },
  "exercises": [
    {
      "type": "gap-fill",
      "prompt": "I ___ (be) happy.",
      "options": ["am", "is", "are"],
      "correct": 0,
      "explanation": "..."
    }
  ],
  "srs_review_count": 5,
  "completion_xp": 10,
  "bonus_xp": 50,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-03-20T14:15:00Z"
}
```

---

#### `PATCH /lessons/{pk}/content/` *(Admin only)*

Cập nhật nội dung lesson

**Request Body:**
```json
{
  "reading_passage": "<p>New passage...</p>",
  "vocab_items": [...],
  "grammar_sections": [...],
  "completion_xp": 15,
  "bonus_xp": 60
}
```

**Response:** `200 OK`

---

## 🔐 AUTHENTICATION

Tất cả endpoints (trừ public endpoints) cần header:

```
Authorization: Bearer {access_token}
```

**Public endpoints (không cần auth):**
- `GET /cefr-levels/`
- `GET /courses/`
- `GET /courses/{id}/`
- `GET /courses/{course_pk}/chapters/`
- `GET /courses/{course_pk}/chapters/{chapter_pk}/lessons/`
- `GET /lessons/{id}/`

**Auth required endpoints:**
- `GET /lessons/{id}/content/` (read allowed, write requires admin)
- Tất cả `POST`, `PATCH`, `DELETE`

---

## ⚠️ ERROR RESPONSES

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "field_errors": {
    "title": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 📋 STATUS CODES

| Code | Meaning |
|---|---|
| `200 OK` | Success (GET, PATCH) |
| `201 Created` | Resource created (POST) |
| `204 No Content` | Success, no content (DELETE) |
| `400 Bad Request` | Invalid request |
| `401 Unauthorized` | Not authenticated |
| `403 Forbidden` | Not authorized |
| `404 Not Found` | Resource not found |
| `500 Server Error` | Server error |

---

## 🔗 RELATED ENDPOINTS

### Progress Integration

```
POST /progress/enroll/
Request: { "course_id": 1 }
Response: { "enrollment_id": 1, "status": "active" }

POST /progress/lessons/{id}/complete/
Request: { "score": 85 }
Response: { "status": "completed", "best_score": 85, "xp_awarded": 60 }

GET /progress/lessons/{id}/
Response: { "lesson_id": 1, "status": "completed", "best_score": 85 }
```

### Exercise Integration

```
GET /exercises/listening/{id}/
GET /exercises/speaking/{id}/
GET /exercises/reading/{id}/
GET /exercises/writing/{id}/
```

### Grammar Integration

```
GET /grammar/{slug}/
GET /grammar/progress/
```

### Vocabulary Integration

```
GET /vocabulary/words/{id}/
POST /vocabulary/flashcards/add-word/
```

---

## 🧪 TESTING EXAMPLES

### 1. Get all courses (Beginner level)

```bash
curl -X GET "http://localhost:8000/api/curriculum/courses/?level__code=A1" \
  -H "Accept: application/json"
```

### 2. Get course detail

```bash
curl -X GET "http://localhost:8000/api/curriculum/courses/1/" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Get lesson content

```bash
curl -X GET "http://localhost:8000/api/curriculum/lessons/1/content/" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Mark lesson complete

```bash
curl -X POST "http://localhost:8000/api/progress/lessons/1/complete/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"score": 85}'
```

### 5. Create course (Admin)

```bash
curl -X POST "http://localhost:8000/api/curriculum/courses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "title": "New Course",
    "slug": "new-course",
    "level": 1,
    "is_premium": false
  }'
```

---

## 📚 REQUEST/RESPONSE EXAMPLES

### Example 1: Student viewing course

**Request:**
```http
GET /api/curriculum/courses/1/ HTTP/1.1
Host: localhost:8000
Authorization: Bearer student_token
```

**Response:**
```json
{
  "id": 1,
  "title": "Nền tảng tiếng Anh",
  "chapters": [
    {
      "id": 1,
      "lessons": [
        {
          "id": 1,
          "title": "Vocabulary",
          "is_unlocked": true,
          "progress_status": "in_progress"
        },
        {
          "id": 2,
          "title": "Grammar",
          "is_unlocked": false,
          "unlock_rules": [
            {
              "required_lesson": 1,
              "min_score": 60
            }
          ]
        }
      ]
    }
  ]
}
```

### Example 2: Student completing lesson

**Request:**
```http
POST /api/progress/lessons/1/complete/ HTTP/1.1
Host: localhost:8000
Authorization: Bearer student_token
Content-Type: application/json

{
  "score": 85
}
```

**Response:**
```json
{
  "lesson_id": 1,
  "status": "completed",
  "best_score": 85,
  "xp_awarded": 60,
  "unlocked_lessons": [2]
}
```

---

## ⚙️ CONFIGURATION

### Pagination (if enabled)

```
GET /courses/?page=1&page_size=10
```

### Filtering

```
GET /courses/?level__code=A1&is_premium=false
```

### Searching

```
GET /courses/?search=foundations
```

### Ordering

```
GET /courses/?ordering=-created_at,title
```

---

**Last updated:** 06/05/2026  
**API Version:** 1.0  
**Status:** ✅ Production Ready
