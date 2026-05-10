# 📖 CURRICULUM APP — Documentation Index

> **Tài liệu toàn diện về Curriculum App — Nơi quản lý toàn bộ cấu trúc khóa học**

---

## 🎯 Giới thiệu nhanh

Curriculum App là **trái tim** của hệ thống LMS English Study. Nó quản lý:

```
CEFR Level (A1, A2, B1, B2, C1)
    ↓
Course (Khóa học toàn bộ)
    ↓
Chapter (Chương/Module)
    ↓
Lesson (Bài học cơ bản)
    ↓
LessonContent (Nội dung phong phú)
    ↓
Exercises (Bài tập từ apps khác)
```

---

## 📚 TÀI LIỆU CHÍNH

### 1. **[CURRICULUM OVERVIEW](./01-CURRICULUM-OVERVIEW.md)** — Nên đọc trước tiên
   - ✅ Tổng quan kiến trúc app
   - ✅ Các models và dữ liệu
   - ✅ API endpoints cơ bản
   - ✅ Frontend Vue3 overview
   - ✅ Kết nối với apps khác
   - ✅ Sơ đồ quan hệ
   
   👉 **Dành cho:** Ai muốn hiểu toàn bộ hệ thống

---

### 2. **[INTEGRATION GUIDE](./02-INTEGRATION-GUIDE.md)** — Dành cho developers
   - ✅ Progress App Integration
   - ✅ Grammar App Integration
   - ✅ Vocabulary App Integration
   - ✅ Exercises App Integration
   - ✅ Gamification App Integration
   - ✅ Common patterns & best practices
   
   👉 **Dành cho:** Developers muốn kết nối curriculum với các apps

---

### 3. **[FRONTEND ARCHITECTURE](./03-FRONTEND-ARCHITECTURE.md)** — Dành cho Frontend developers
   - ✅ Vue3 cấu trúc thư mục
   - ✅ Views chi tiết (CoursesView, CourseDetailView, LessonDetailView)
   - ✅ Components (ReadingSection, GrammarSection, ListeningSection, v.v.)
   - ✅ API integration module
   - ✅ State management (Pinia)
   - ✅ Routing
   - ✅ Styling & themes
   
   👉 **Dành cho:** Frontend developers làm việc với Vue3

---

### 4. **[API REFERENCE](./04-API-REFERENCE.md)** — Quick lookup
   - ✅ Tất cả endpoints
   - ✅ Request/response formats
   - ✅ Query parameters
   - ✅ Status codes
   - ✅ Testing examples
   - ✅ Error responses
   
   👉 **Dành cho:** API consumers, testers, postman users

---

## 🏗️ KIẾN TRÚC TỔNG QUAN

### Backend Structure

```
backend/apps/curriculum/
├── models.py               # 8 models chính
├── serializers.py          # Serialization logic
├── views.py                # ViewSets & APIViews
├── urls.py                 # URL routing
├── admin.py                # Django admin
├── management/commands/    # Data seeding
│   ├── seed_courses.py
│   ├── seed_grammar_lessons.py
│   ├── seed_vocab_lessons.py
│   └── seed_lesson_content.py
└── migrations/             # Database migrations
```

### Frontend Structure

```
frontend/src/
├── views/
│   ├── CoursesView.vue
│   ├── CourseDetailView.vue
│   └── LessonDetailView.vue
├── components/lesson/
│   ├── ReadingSection.vue
│   ├── GrammarSection.vue
│   ├── ListeningSection.vue
│   ├── SpeakingSection.vue
│   └── WritingSection.vue
├── api/
│   └── curriculum.js
└── router/
    └── index.js
```

---

## 📊 MODELS CHÍNH

| Model | Mục đích | Quan hệ |
|---|---|---|
| `CEFRLevel` | Cấp độ CEFR (A1-C1) | 1:N → Course |
| `Course` | Khóa học toàn bộ | 1:N → Chapter |
| `Chapter` | Chương/Module | 1:N → Lesson |
| `Lesson` | Bài học cơ bản | 1:1 → LessonContent |
| `LessonContent` | Nội dung phong phú | 1:1 ← Lesson |
| `LessonExercise` | Link bài tập (polymorphic) | N:1 → Lesson |
| `UnlockRule` | Quy tắc mở khoá | N:1 → Lesson |
| `SourceFile` | Tệp đính kèm (S3) | N:1 → Lesson |

---

## 🔄 INTEGRATION DIAGRAM

```
┌─────────────────────────────────────────────────┐
│           CURRICULUM APP (Core)                 │
├─────────────────────────────────────────────────┤
│  ├─ CEFRLevel, Course, Chapter                 │
│  ├─ Lesson, LessonContent                      │
│  ├─ LessonExercise (polymorphic)               │
│  └─ UnlockRule (prerequisites)                 │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────┬──────────┐
    ↓            ↓            ↓          ↓          ↓
┌────────┐  ┌────────┐  ┌──────────┐ ┌────────┐ ┌─────────┐
│Progress│  │Grammar │  │Vocabulary│ │Exercise│ │Gamifctn │
├────────┤  ├────────┤  ├──────────┤ ├────────┤ ├─────────┤
│Tracking│  │Topics  │  │Words/SRS │ │4-skills│ │XP/Badge │
│Enroll  │  │Linking │  │Flashcard │ │Polymorp│ │Streak   │
└────────┘  └────────┘  └──────────┘ └────────┘ └─────────┘
```

---

## 📱 API ENDPOINTS

### Quick Reference

```
# Courses
GET    /curriculum/courses/
GET    /curriculum/courses/{id}/
POST   /curriculum/courses/                    (admin)
PATCH  /curriculum/courses/{id}/               (admin)

# Chapters
GET    /curriculum/courses/{course_pk}/chapters/
POST   /curriculum/courses/{course_pk}/chapters/

# Lessons
GET    /curriculum/courses/{course_pk}/chapters/{chapter_pk}/lessons/
GET    /curriculum/lessons/{id}/
GET    /curriculum/lessons/{id}/content/
POST   /curriculum/lessons/                    (admin)
PATCH  /curriculum/lessons/{id}/               (admin)

# Progress (integrated)
POST   /progress/enroll/
POST   /progress/lessons/{id}/complete/
GET    /progress/lessons/{id}/
```

👉 **Full reference:** See [API-REFERENCE.md](./04-API-REFERENCE.md)

---

## 🎨 FRONTEND COMPONENTS

### Content Sections

| Component | Mục đích | Input |
|---|---|---|
| `ReadingSection` | Đọc + vocab + Q&A | `reading_passage`, `vocab_items`, `reading_questions` |
| `GrammarSection` | Ngữ pháp + exercises | `grammar_sections[]` (JSON) |
| `ListeningSection` | Audio + dictation | `listening_content` (JSON) |
| `SpeakingSection` | Repeat/Shadow/Dialogue | `speaking_content` (JSON) |
| `WritingSection` | Gap-fill/Completion | `writing_content` (JSON) |
| `VocabFootnote` | Vocab tooltip | `vocab` object |

### Views

| View | Route | Mục đích |
|---|---|---|
| `CoursesView` | `/courses` | List + filter courses |
| `CourseDetailView` | `/courses/{id}` | Course detail + chapters |
| `LessonDetailView` | `/lessons/{id}` | Full lesson content |

---

## 🧪 QUICK START

### Backend (Django)

```bash
# Seed data
python manage.py seed_courses
python manage.py seed_grammar_lessons
python manage.py seed_vocab_lessons
python manage.py seed_lesson_content

# Start server
python manage.py runserver

# Admin panel
http://localhost:8000/admin
```

### Frontend (Vue3)

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build
npm run build
```

### API Testing

```bash
# Get courses
curl http://localhost:8000/api/curriculum/courses/

# Get lesson content
curl http://localhost:8000/api/curriculum/lessons/1/content/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💡 KEY FEATURES

### ✅ Đã Triển Khai

| Tính năng | Status |
|---|---|
| Hierarchical course structure | ✅ |
| Rich lesson content (reading, grammar, listening, v.v.) | ✅ |
| Polymorphic exercise linking | ✅ |
| Unlock rules & prerequisites | ✅ |
| Progress tracking integration | ✅ |
| Vocabulary inline display | ✅ |
| Grammar section linking | ✅ |
| Admin management | ✅ |
| Data seeding | ✅ |

### 🚀 Tiềm năng mở rộng

- [ ] Lesson difficulty levels
- [ ] A/B testing (content variants)
- [ ] AI-generated content (Qwen)
- [ ] Performance analytics
- [ ] Lesson recommendations
- [ ] Multi-language support
- [ ] Adaptive learning paths

---

## 📋 CÔNG NGHỆ

### Backend
- **Framework:** Django REST Framework
- **Database:** PostgreSQL
- **ORM:** Django ORM
- **Serialization:** DRF Serializers
- **Admin:** Django Admin

### Frontend
- **Framework:** Vue 3 (Composition API)
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Routing:** Vue Router
- **State (Optional):** Pinia

### API
- **Format:** JSON
- **Auth:** JWT (Bearer token)
- **Versioning:** URL-based

---

## 🔐 PERMISSIONS

| Action | Anonymous | Student | Teacher | Admin |
|---|---|---|---|---|
| View courses | ✅ | ✅ | ✅ | ✅ |
| View lessons | ✅ | ✅ | ✅ | ✅ |
| View content | ✅ | ✅ | ✅ | ✅ |
| Complete lesson | ❌ | ✅ | ✅ | ✅ |
| Create course | ❌ | ❌ | ❌ | ✅ |
| Edit course | ❌ | ❌ | ❌ | ✅ |
| Delete course | ❌ | ❌ | ❌ | ✅ |

---

## 📚 RELATED APPS

| App | Tương tác | Dữ liệu trao đổi |
|---|---|---|
| **progress** | Enrollment, tracking | `UserEnrollment`, `LessonProgress` |
| **grammar** | Topic linking | `grammar_topic_id` in LessonContent |
| **vocabulary** | Word linking, SRS | `vocab_word_ids`, SRS queue |
| **exercises** | Polymorphic linking | `LessonExercise` (exercise_type + exercise_id) |
| **gamification** | XP awards | `completion_xp`, `bonus_xp` |

---

## 🎓 LEARNING PATH

### Để hiểu Curriculum App:

1. **[START HERE] OVERVIEW** (15 min)
   - Đọc tổng quan kiến trúc
   - Hiểu các models
   - Xem sơ đồ quan hệ

2. **Backend Deep Dive** (30 min)
   - Đọc models chi tiết
   - Xem serializers
   - Hiểu views

3. **Frontend Deep Dive** (30 min)
   - Xem components
   - Đọc views
   - Hiểu routing

4. **Integration** (20 min)
   - Đọc integration guide
   - Hiểu cách kết nối apps
   - Xem examples

5. **API Reference** (10 min)
   - Bookmark API reference
   - Test endpoints
   - Chơi với Postman

---

## 🔗 QUICK LINKS

### Code Files
- [models.py](/backend/apps/curriculum/models.py)
- [serializers.py](/backend/apps/curriculum/serializers.py)
- [views.py](/backend/apps/curriculum/views.py)
- [curriculum.js](/frontend/src/api/curriculum.js)
- [CoursesView.vue](/frontend/src/views/CoursesView.vue)

### Data
- [Database design](/docs/database-design.md)
- [Dataset directory](/dataset)

---

## ❓ FAQ

**Q: Làm thế nào để thêm bài học mới?**
A: Dùng Django admin hoặc API: `POST /curriculum/courses/{id}/chapters/{id}/lessons/`

**Q: Làm thế nào để lock một bài học?**
A: Tạo `UnlockRule` với `required_lesson` và `min_score`

**Q: Làm thế nào để thêm bài tập vào lesson?**
A: Tạo `LessonExercise` với `exercise_type` + `exercise_id` từ exercises app

**Q: Tôi có thể tùy chỉnh nội dung lesson không?**
A: Có! Dùng `PATCH /curriculum/lessons/{id}/content/` để update JSON fields

**Q: Làm thế nào để thêm vocabulary?**
A: Thêm `vocab_items` array vào `LessonContent`

---

## 📞 SUPPORT

### Khí gặp vấn đề:

1. Kiểm tra [API Reference](./04-API-REFERENCE.md) để xem endpoint đó
2. Kiểm tra [Integration Guide](./02-INTEGRATION-GUIDE.md) để hiểu cách kết nối
3. Xem [Frontend Architecture](./03-FRONTEND-ARCHITECTURE.md) để debug components
4. Xem logs: `tail -f backend/logs/*.log`

---

## 📝 CHANGELOG

### v1.0 (06/05/2026) — Production Release

- ✅ Complete models implementation
- ✅ Full API endpoints
- ✅ Vue3 components
- ✅ Integration with 5 apps
- ✅ Admin management
- ✅ Data seeding
- ✅ Comprehensive documentation

---

## 🎯 NEXT STEPS

1. **Bạn muốn nắm rõ hệ thống?**
   → Đọc [OVERVIEW](./01-CURRICULUM-OVERVIEW.md)

2. **Bạn là backend developer?**
   → Đọc [INTEGRATION GUIDE](./02-INTEGRATION-GUIDE.md)

3. **Bạn là frontend developer?**
   → Đọc [FRONTEND ARCHITECTURE](./03-FRONTEND-ARCHITECTURE.md)

4. **Bạn cần test API?**
   → Dùng [API REFERENCE](./04-API-REFERENCE.md)

---

## 📄 DOCUMENT METADATA

| Thông tin | Chi tiết |
|---|---|
| **Phiên bản** | 1.0 |
| **Cập nhật lần cuối** | 06/05/2026 |
| **Trạng thái** | ✅ Production Ready |
| **Tổng số tài liệu** | 5 files |
| **Tổng số trang** | ~150 (nếu in) |
| **Độ bao phủ** | ~95% |

---

## 🙏 CREDITS

**Documentation created:** 06/05/2026  
**By:** Curriculum Development Team  
**For:** English Study LMS Project

---

**Happy learning! 🚀**
