# 📚 CURRICULUM APP — Tài Liệu Triển Khai Toàn Diện

> **Ngày cập nhật:** 06/05/2026  
> **Phiên bản:** 1.0  
> **Trạng thái:** ✅ Triển khai hoàn tất

---

## 📋 MỤC LỤC

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Mô hình dữ liệu](#2-mô-hình-dữ-liệu)
3. [API Backend](#3-api-backend)
4. [Frontend Vue3](#4-frontend-vue3)
5. [Kết nối với các apps khác](#5-kết-nối-với-các-apps-khác)
6. [Quản lý dữ liệu](#6-quản-lý-dữ-liệu)
7. [Tính năng triển khai](#7-tính-năng-triển-khai)
8. [Sơ đồ quan hệ](#8-sơ-đồ-quan-hệ)

---

## 1. TỔNG QUAN KIẾN TRÚC

### Vai trò của Curriculum App

`curriculum` là trái tim của hệ thống LMS, quản lý **cấu trúc hierarchical** của toàn bộ khóa học:

```
CEFRLevel (A1, A2, B1, B2, C1)
    ↓
Course (Khóa học)
    ↓
Chapter (Chương)
    ↓
Lesson (Bài học)
    ↓
LessonContent (Nội dung phong phú)
    ↓
Exercise (Bài tập từ các app khác)
```

### Điều khác biệt của Curriculum

- **Polymorphic Exercise Linking**: Lesson có thể liên kết với Exercise từ bất kỳ app nào (`listening`, `speaking`, `reading`, `writing`)
- **Rich Content Storage**: `LessonContent` lưu trữ đầy đủ nội dung: reading passage, vocabulary, grammar, exercises
- **Unlock Rules**: Hỗ trợ prerequisite (bài cần hoàn thành trước mới mở khoá bài tiếp)
- **Granular Progress Tracking**: Kết nối chặt chẽ với `progress` app để theo dõi từng bài học

---

## 2. MÔ HÌNH DỮ LIỆU

### 2.1 CEFRLevel — Cấp độ CEFR

Định nghĩa các cấp độ CEFR (A1-C2)

```python
class CEFRLevel(models.Model):
    code = models.CharField(max_length=3, unique=True)          # A1, A2, B1, B2, C1, C2
    name = models.CharField(max_length=50)                      # "Beginner", "Elementary"
    name_vi = models.CharField(max_length=50)                   # "Sơ cấp", "Tiền trung cấp"
    order = models.SmallIntegerField(db_index=True)             # 1, 2, 3, 4, 5, 6
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

**Dữ liệu mẫu:**

| Mã | Name | Name_VI | Order |
|---|---|---|---|
| A1 | Beginner | Sơ cấp | 1 |
| A2 | Elementary | Tiền trung cấp | 2 |
| B1 | Intermediate | Trung cấp | 3 |
| B2 | Upper-Intermediate | Cao trung cấp | 4 |
| C1 | Advanced | Nâng cao | 5 |

---

### 2.2 Course — Khóa học

Đại diện cho một khóa học toàn bộ ở một cấp độ CEFR.

```python
class Course(models.Model):
    level = models.ForeignKey(CEFRLevel, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    order = models.SmallIntegerField(db_index=True)
    is_premium = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name="created_courses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Quan hệ:**
- Một `CEFRLevel` có **nhiều** `Course` (1:N)
- Một `Course` do một `User` tạo ra (tác giả)

**Ví dụ:**
```
A1 → "Nền tảng tiếng Anh" (Beginner Course)
A1 → "Daily English" (Beginner Course 2)
A2 → "Giao tiếp hàng ngày" (Elementary Course)
```

---

### 2.3 Chapter — Chương

Nhóm các bài học trong một khóa học.

```python
class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=200)
    order = models.SmallIntegerField(db_index=True)
    description = models.TextField(null=True, blank=True)
    passing_score = models.SmallIntegerField(default=60)  # 0-100
    created_at = models.DateTimeField(auto_now_add=True)
```

**Quan hệ:**
- Một `Course` có **nhiều** `Chapter` (1:N)
- Mỗi Chapter có ngưỡng điểm đạt (`passing_score`, mặc định 60%)

**Ví dụ:**
```
"Nền tảng tiếng Anh" → Ch1: "Giới thiệu bản thân"
"Nền tảng tiếng Anh" → Ch2: "Gia đình & Bạn bè"
"Nền tảng tiếng Anh" → Ch3: "Mua sắm"
```

---

### 2.4 Lesson — Bài học

Đơn vị học tập cơ bản.

```python
class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ("listening", "Nghe"),
        ("speaking", "Nói"),
        ("reading", "Đọc"),
        ("writing", "Viết"),
        ("grammar", "Ngữ pháp"),
        ("vocabulary", "Từ vựng"),
        ("pronunciation", "Phát âm"),
        ("assessment", "Kiểm tra"),
    ]

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    order = models.SmallIntegerField(db_index=True)
    lesson_type = models.CharField(max_length=15, choices=LESSON_TYPE_CHOICES, db_index=True)
    estimated_minutes = models.SmallIntegerField(default=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Quan hệ:**
- Một `Chapter` có **nhiều** `Lesson` (1:N)

**Ví dụ:**
```
Ch1: "Giới thiệu bản thân" → Lesson 1: Vocabulary (~10 min)
Ch1: "Giới thiệu bản thân" → Lesson 2: Grammar (~15 min)
Ch1: "Giới thiệu bản thân" → Lesson 3: Reading (~15 min)
Ch1: "Giới thiệu bản thân" → Lesson 4: Listening (~10 min)
Ch1: "Giới thiệu bản thân" → Lesson 5: Speaking (~8 min)
Ch1: "Giới thiệu bản thân" → Lesson 6: Writing (~10 min)
Ch1: "Giới thiệu bản thân" → Lesson 7: Assessment (~10 min)
```

---

### 2.5 LessonContent — Nội dung bài học

**Nơi lưu trữ tất cả nội dung phong phú của một bài học** — đọc, từ vựng, ngữ pháp, bài tập, điều hành v.v.

```python
class LessonContent(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="content")
    
    # ── Reading ──
    reading_passage = models.TextField(blank=True, default="")
    reading_image_url = models.CharField(max_length=500, blank=True, default="")
    reading_questions = models.JSONField(default=list, blank=True)
    
    # ── Vocabulary ──
    vocab_items = models.JSONField(default=list, blank=True)
    vocab_word_ids = models.JSONField(default=list, blank=True)
    
    # ── Grammar ──
    grammar_topic_id = models.IntegerField(null=True, blank=True)
    grammar_title = models.CharField(max_length=200, blank=True, default="")
    grammar_note = models.TextField(blank=True, default="")
    grammar_examples = models.JSONField(default=list, blank=True)
    grammar_sections = models.JSONField(default=list, blank=True)
    
    # ── Skill Practice ──
    skill_sections = models.JSONField(default=dict, blank=True)
    listening_content = models.JSONField(default=dict, blank=True)
    speaking_content = models.JSONField(default=dict, blank=True)
    writing_content = models.JSONField(default=dict, blank=True)
    
    # ── Exercises ──
    exercises = models.JSONField(default=list, blank=True)
    
    # ── SRS & Rewards ──
    srs_review_count = models.SmallIntegerField(default=5)
    completion_xp = models.SmallIntegerField(default=10)
    bonus_xp = models.SmallIntegerField(default=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Tính chất:**
- OneToOne với `Lesson` (mỗi bài học chỉ có một nội dung)
- Nội dung được lưu dưới dạng **JSON** để linh hoạt
- Hỗ trợ **nhiều loại nội dung**: reading, vocabulary, grammar, listening, speaking, writing, exercises

**Ví dụ vocab_items:**
```json
[
  {
    "word": "headache",
    "pos": "noun",
    "ipa": "/ˈhed.eɪk/",
    "meaning_vi": "đau đầu",
    "definition_en": "A pain inside your head.",
    "example_en": "I have a headache.",
    "example_vi": "Tôi bị đau đầu.",
    "collocations": ["have a ~", "splitting ~"],
    "highlight_in_passage": true
  }
]
```

**Ví dụ grammar_sections:**
```json
[
  {
    "title": "Present Simple",
    "grammar_topic_id": 42,
    "note": "Dùng cho hành động thường xuyên...",
    "examples": [
      {"en": "I eat rice.", "vi": "Tôi ăn cơm.", "highlight": "eat"},
      {"en": "She drinks coffee.", "vi": "Cô ấy uống cà phê.", "highlight": "drinks"}
    ],
    "exercises": [
      {"type": "gap-fill", "prompt": "I ___ (eat) rice every day.", "options": ["eat", "eats", "ate"], "correct": 0}
    ]
  }
]
```

---

### 2.6 LessonExercise — Liên kết bài tập (Polymorphic)

Kết nối Lesson với Exercise từ bất kỳ app nào qua **polymorphic reference**.

```python
class LessonExercise(models.Model):
    EXERCISE_TYPES = [
        ("listening", "Listening"),
        ("speaking", "Speaking"),
        ("reading", "Reading"),
        ("writing", "Writing"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="exercises")
    exercise_type = models.CharField(max_length=15, choices=EXERCISE_TYPES)
    exercise_id = models.BigIntegerField()
    order = models.SmallIntegerField(default=1)
    passing_score = models.SmallIntegerField(default=60)
```

**Cách hoạt động:**
- `exercise_type` + `exercise_id` → xác định bảng và ID trong `exercises` app
- Ví dụ: `("listening", 7)` → `exercises_listeningexercise` với `id=7`

**Lợi ích:**
- Flexible: dễ mở rộng thêm loại exercise mới
- DRY: Exercise được quản lý riêng trong `exercises` app
- Performance: Không cần foreign key trực tiếp

---

### 2.7 UnlockRule — Quy tắc mở khoá

Định nghĩa các điều kiện tiên quyết: bài học chỉ mở khoá khi bài trước đạt điểm nhất định.

```python
class UnlockRule(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="unlock_rules")
    required_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="unlocks")
    min_score = models.SmallIntegerField(default=60)
```

**Ví dụ:**
```
Lesson "Bài 2: Grammar" unlock_rule:
  → required_lesson = "Bài 1: Vocabulary"
  → min_score = 60

→ Học sinh phải đạt ≥60% ở Bài 1 mới mở khoá Bài 2
```

**Tính chất:**
- Một bài có thể có **nhiều** prerequisites (AND logic — phải đủ hết)
- Mặc định: `min_score = 60`

---

### 2.8 SourceFile — Tệp đính kèm

Lưu trữ metadata cho tệp (audio, PDF, image, video) trên S3.

```python
class SourceFile(models.Model):
    FILE_TYPES = [
        ("audio", "Audio"),
        ("pdf", "PDF"),
        ("image", "Image"),
        ("video", "Video"),
        ("other", "Other"),
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="source_files")
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default="other")
    s3_key = models.CharField(max_length=500, blank=True, default="")
    original_name = models.CharField(max_length=255)
    file_size_bytes = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name="uploaded_source_files")
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 3. API BACKEND

### 3.1 Endpoints

#### **CEFR Levels**

```
GET /curriculum/cefr-levels/
```

**Response:**
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

#### **Courses CRUD**

```
GET /curriculum/courses/                      # List
GET /curriculum/courses/?level__code=A1       # Filter by level
GET /curriculum/courses/?is_premium=true      # Filter by premium
GET /curriculum/courses/?search=<query>       # Search
GET /curriculum/courses/<id>/                 # Detail
POST /curriculum/courses/                     # Create (admin only)
PATCH /curriculum/courses/<id>/               # Update (admin only)
DELETE /curriculum/courses/<id>/              # Delete (admin only)
```

**List Response:**
```json
{
  "id": 1,
  "title": "Nền tảng tiếng Anh",
  "slug": "nen-tang-tieng-anh",
  "description": "Khoá học A1...",
  "level": {
    "id": 1,
    "code": "A1",
    "name": "Beginner",
    "name_vi": "Sơ cấp"
  },
  "is_premium": false,
  "total_lessons": 49,
  "thumbnail": null
}
```

**Detail Response:**
```json
{
  "id": 1,
  "title": "Nền tảng tiếng Anh",
  "slug": "nen-tang-tieng-anh",
  "description": "...",
  "level": {...},
  "is_premium": false,
  "chapters": [
    {
      "id": 1,
      "title": "Giới thiệu bản thân",
      "order": 1,
      "lesson_count": 7,
      "passing_score": 60,
      "lessons": [
        {"id": 1, "title": "Vocabulary", "lesson_type": "vocabulary", ...},
        {"id": 2, "title": "Grammar", "lesson_type": "grammar", ...}
      ]
    }
  ]
}
```

---

#### **Chapters**

```
GET /curriculum/courses/<course_pk>/chapters/
POST /curriculum/courses/<course_pk>/chapters/
```

---

#### **Lessons**

```
GET /curriculum/courses/<course_pk>/chapters/<chapter_pk>/lessons/
POST /curriculum/courses/<course_pk>/chapters/<chapter_pk>/lessons/
GET /curriculum/lessons/<id>/
PATCH /curriculum/lessons/<id>/
DELETE /curriculum/lessons/<id>/
```

**Lesson Response:**
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
  "progress_status": "completed",  // locked, in_progress, completed
  "is_unlocked": true,
  "exercise_type": "vocabulary",
  "exercise_id": 42,
  "unlock_rules": [
    {
      "id": 1,
      "required_lesson": 0,
      "required_lesson_title": "Lesson 0",
      "min_score": 60
    }
  ]
}
```

---

#### **Lesson Content**

```
GET /curriculum/lessons/<pk>/content/
PATCH /curriculum/lessons/<pk>/content/
```

**Content Response:**
```json
{
  "id": 1,
  "lesson": 1,
  "reading_passage": "<p>Alice walked through...</p>",
  "reading_image_url": "https://...",
  "reading_questions": [
    {
      "question": "What did Alice see?",
      "options": ["a tree", "a rabbit", "a cat"],
      "correct": 1,
      "explanation": "The text says..."
    }
  ],
  "vocab_items": [
    {"word": "walked", "meaning_vi": "đi bộ", ...},
    {"word": "through", "meaning_vi": "qua", ...}
  ],
  "grammar_sections": [...],
  "listening_content": {...},
  "speaking_content": {...},
  "writing_content": {...},
  "exercises": [...],
  "completion_xp": 10,
  "bonus_xp": 50
}
```

---

### 3.2 Serializers

| Serializer | Mục đích |
|---|---|
| `CEFRLevelSerializer` | Serialization CEFRLevel |
| `LessonSerializer` | Basic Lesson (list/detail) |
| `ChapterSerializer` | Chapter với embedded lessons |
| `CourseListSerializer` | Course list view (minimal) |
| `CourseDetailSerializer` | Course detail (full hierarchy) |
| `CourseWriteSerializer` | Create/Update course (validation) |
| `LessonContentSerializer` | Rich content (read/write) |

**Tính chất đặc biệt:**
- `LessonSerializer.get_is_unlocked()`: Kiểm tra unlock rules + progress
- `LessonSerializer.get_progress_status()`: Lấy status từ `progress.LessonProgress`

---

### 3.3 Permissions & Filters

**Permissions:**
```python
- CEFRLevelListView: AllowAny (public)
- CourseViewSet: IsAdminOrReadOnly (admin create/update, everyone read)
- ChapterListView: IsAdminOrReadOnly
- LessonListView: IsAdminOrReadOnly
- LessonDetailView: IsAdminOrReadOnly
- LessonContentView: IsAuthenticatedOrReadOnly
```

**Filters:**
```python
- Search: title, description
- Filter: level__code, is_premium
- Ordering: created_at, title
```

---

## 4. FRONTEND VUE3

### 4.1 Cấu trúc thư mục

```
frontend/src/
├── api/
│   └── curriculum.js          # API calls for curriculum
├── views/
│   ├── CoursesView.vue        # List all courses
│   ├── CourseDetailView.vue   # Course detail + chapters
│   └── LessonDetailView.vue   # Lesson detail + content
├── components/
│   ├── lesson/
│   │   ├── ReadingSection.vue
│   │   ├── GrammarSection.vue
│   │   ├── ListeningSection.vue
│   │   ├── SpeakingSection.vue
│   │   ├── WritingSection.vue
│   │   └── VocabFootnote.vue
│   ├── SkillTreeView.vue
│   └── UnlockModal.vue
└── stores/
    └── (curriculum state management nếu cần)
```

---

### 4.2 Views

#### **CoursesView.vue**

Hiển thị tất cả khóa học, có lọc theo cấp độ CEFR.

```vue
<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold">Khoá học</h1>
    
    <!-- Filters -->
    <div class="flex gap-2 mb-6">
      <button v-for="level in cefrLevels" :key="level"
              @click="activeLevel = activeLevel === level ? '' : level"
              class="px-3 py-1.5 rounded-lg">
        {{ level }}
      </button>
    </div>
    
    <!-- Courses Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <RouterLink v-for="course in filteredCourses" :key="course.id"
                  :to="`/courses/${course.id}`"
                  class="course-card">
        <span class="badge">{{ course.level?.code }}</span>
        <h3>{{ course.title }}</h3>
        <p>{{ course.total_lessons }} bài</p>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { curriculumApi } from '@/api/curriculum'

const courses = ref([])
const cefrLevels = ref([])
const activeLevel = ref('')
const loading = ref(false)
const error = ref(null)

const filteredCourses = computed(() => 
  activeLevel.value 
    ? courses.value.filter(c => c.level?.code === activeLevel.value)
    : courses.value
)

onMounted(async () => {
  loading.value = true
  try {
    const [levelsRes, coursesRes] = await Promise.all([
      curriculumApi.getCefrLevels(),
      curriculumApi.getCourses()
    ])
    cefrLevels.value = levelsRes.data.map(l => l.code)
    courses.value = coursesRes.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
```

**Tính năng:**
- Lấy danh sách tất cả khóa học
- Lọc theo cấp độ CEFR
- Navigation tới course detail

---

#### **CourseDetailView.vue**

Hiển thị chi tiết khóa học + các chương và bài học.

```vue
<template>
  <div class="max-w-4xl mx-auto p-6">
    <button @click="$router.back()" class="mb-6">← Quay lại</button>
    
    <div v-if="course" class="space-y-6">
      <!-- Course header -->
      <div class="course-header">
        <span class="badge">{{ course.level?.code }}</span>
        <h1 class="text-2xl font-bold">{{ course.title }}</h1>
        <p class="text-gray-600">{{ course.description }}</p>
        
        <button v-if="!isEnrolled" @click="enroll" :disabled="enrolling"
                class="btn-primary">
          {{ enrolling ? 'Đang đăng ký...' : 'Đăng ký học' }}
        </button>
      </div>
      
      <!-- Chapters -->
      <div v-for="chapter in course.chapters" :key="chapter.id"
           class="chapter-section">
        <h2 class="text-lg font-bold">Ch{{ chapter.order }}: {{ chapter.title }}</h2>
        
        <!-- Lessons in chapter -->
        <div class="lessons-list">
          <RouterLink v-for="lesson in chapter.lessons" :key="lesson.id"
                      :to="`/lessons/${lesson.id}`"
                      class="lesson-item"
                      :class="{ locked: !lesson.is_unlocked, completed: lesson.progress_status === 'completed' }">
            <span class="lesson-icon">{{ lessonIcon(lesson.lesson_type) }}</span>
            <div class="lesson-info">
              <h3>{{ lesson.title }}</h3>
              <p class="text-xs text-gray-600">~{{ lesson.estimated_minutes }} phút</p>
            </div>
            <span v-if="!lesson.is_unlocked" class="lock-icon">🔒</span>
            <span v-else-if="lesson.progress_status === 'completed'" class="check-icon">✓</span>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { curriculumApi } from '@/api/curriculum'

const route = useRoute()
const course = ref(null)
const isEnrolled = ref(false)
const enrolling = ref(false)

const lessonIcon = (type) => {
  const icons = {
    listening: '🎧', speaking: '🎤', reading: '📖', 
    writing: '✏️', grammar: '📝', vocabulary: '📚'
  }
  return icons[type] || '📄'
}

onMounted(async () => {
  const data = await curriculumApi.getCourse(route.params.id)
  course.value = data.data
  // Check enrollment status...
})

const enroll = async () => {
  enrolling.value = true
  try {
    await curriculumApi.enroll(route.params.id)
    isEnrolled.value = true
  } finally {
    enrolling.value = false
  }
}
</script>
```

---

#### **LessonDetailView.vue**

Hiển thị chi tiết bài học + tất cả nội dung (reading, vocabulary, grammar, exercises, v.v.).

```vue
<template>
  <div class="max-w-6xl mx-auto p-6 pb-24">
    <button @click="$router.back()" class="mb-5">← Quay lại</button>
    
    <!-- Lesson Header -->
    <div v-if="lesson" class="lesson-header">
      <span class="badge">{{ lesson.lesson_type }}</span>
      <h1 class="text-2xl font-bold">{{ lesson.title }}</h1>
      <span class="status-badge" :class="progress.status">{{ statusLabel(progress.status) }}</span>
    </div>
    
    <!-- Locked state -->
    <div v-if="progress.status === 'locked'" class="locked-gate">
      <p class="text-4xl">🔒</p>
      <p>Bài học chưa được mở. Hoàn thành bài học trước để mở khoá.</p>
    </div>
    
    <!-- Content sections -->
    <template v-else-if="content">
      <!-- Reading Section -->
      <ReadingSection
        v-if="content.reading_passage"
        :passage="content.reading_passage"
        :questions="content.reading_questions || []"
        :vocab-items="content.vocab_items || []"
        @progress="onReadingProgress"
      />
      
      <!-- Grammar Sections -->
      <template v-for="(gs, gi) in (content.grammar_sections || [])" :key="gi">
        <GrammarSection
          :section="gs"
          :mode="grammarMode"
          @progress="onGrammarProgress(gi, $event)"
        />
      </template>
      
      <!-- Listening Section -->
      <ListeningSection
        v-if="content.listening_content?.audio_text"
        :content="content.listening_content"
        @progress="onListeningProgress"
      />
      
      <!-- Speaking Section -->
      <SpeakingSection
        v-if="content.speaking_content?.sentences"
        :content="content.speaking_content"
        @progress="onSpeakingProgress"
      />
      
      <!-- Writing Section -->
      <WritingSection
        v-if="content.writing_content?.exercises"
        :content="content.writing_content"
        @progress="onWritingProgress"
      />
      
      <!-- Complete Button -->
      <button @click="completeLesson" :disabled="completing"
              class="btn-primary mt-8">
        {{ completing ? 'Đang lưu...' : 'Hoàn thành bài học' }}
      </button>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { curriculumApi } from '@/api/curriculum'
import ReadingSection from '@/components/lesson/ReadingSection.vue'
import GrammarSection from '@/components/lesson/GrammarSection.vue'
// ...other imports

const route = useRoute()
const lesson = ref(null)
const content = ref(null)
const progress = ref({ status: 'locked' })
const loading = ref(true)
const completing = ref(false)

onMounted(async () => {
  try {
    const [lessonRes, contentRes, progressRes] = await Promise.all([
      curriculumApi.getLesson(route.params.id),
      curriculumApi.getLessonContent(route.params.id),
      curriculumApi.getLessonProgress(route.params.id)
    ])
    lesson.value = lessonRes.data
    content.value = contentRes.data
    progress.value = progressRes.data
  } finally {
    loading.value = false
  }
})

const completeLesson = async () => {
  completing.value = true
  try {
    const data = await curriculumApi.markLessonComplete(route.params.id, {
      score: 85  // Calculate from sections
    })
    progress.value = data.data
  } finally {
    completing.value = false
  }
}
</script>
```

---

### 4.3 Components

#### **ReadingSection.vue**

```vue
<template>
  <div class="reading-section">
    <div class="reading-content">
      <img v-if="imageUrl" :src="imageUrl" class="reading-image">
      <div class="passage" v-html="passage"></div>
      
      <!-- Vocabulary Footnotes -->
      <div v-for="vocab in vocabItems" :key="vocab.word"
           class="vocab-footnote">
        <span>{{ vocab.word }}</span>
        <span class="definition">{{ vocab.meaning_vi }}</span>
      </div>
    </div>
    
    <div class="reading-questions">
      <h3>Câu hỏi</h3>
      <div v-for="(q, idx) in questions" :key="idx"
           class="question-item">
        <p class="question-text">{{ q.question }}</p>
        <label v-for="(opt, oi) in q.options" :key="oi">
          <input type="radio" :name="`q-${idx}`" :value="oi"
                 @change="answered[idx] = oi">
          {{ opt }}
        </label>
      </div>
      
      <button @click="submitAnswers" class="btn-primary">Kiểm tra</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  passage: String,
  imageUrl: String,
  questions: Array,
  vocabItems: Array
})

const emit = defineEmits(['progress'])
const answered = ref({})

const submitAnswers = () => {
  // Calculate score
  let score = 0
  props.questions.forEach((q, idx) => {
    if (answered.value[idx] === q.correct) score++
  })
  const percent = Math.round((score / props.questions.length) * 100)
  
  emit('progress', { type: 'reading', score: percent })
}
</script>
```

#### **GrammarSection.vue**

Tương tự — hiển thị giải thích ngữ pháp + bài tập.

#### **ListeningSection.vue**

- Audio player với kiểm soát tốc độ (0.75x - 1.5x)
- Dictation mode
- Comprehension questions

#### **SpeakingSection.vue**

- Repeat mode (ghi âm + so sánh với mẫu)
- Shadowing (lặp lại theo tốc độ từng câu)
- Dialogue (role-play)

#### **WritingSection.vue**

- Gap-fill exercises
- Sentence completion
- Guided writing (với gợi ý)
- Free writing (để viết tự do)

---

### 4.4 API Module (`curriculum.js`)

```javascript
import api from './client.js'

export const curriculumApi = {
  // CEFR Levels
  getCefrLevels: () =>
    api.get('/curriculum/cefr-levels/'),

  // Courses
  getCourses: (params = {}) =>
    api.get('/curriculum/courses/', { params }),
  getCourse: (id) =>
    api.get(`/curriculum/courses/${id}/`),

  // Chapters
  getChapters: (courseId) =>
    api.get(`/curriculum/courses/${courseId}/chapters/`),

  // Lessons
  getLessons: (courseId, chapterId) =>
    api.get(`/curriculum/courses/${courseId}/chapters/${chapterId}/lessons/`),
  getLesson: (id) =>
    api.get(`/curriculum/lessons/${id}/`),
  getLessonContent: (id) =>
    api.get(`/curriculum/lessons/${id}/content/`),

  // Progress
  enroll: (courseId) =>
    api.post('/progress/enroll/', { course_id: courseId }),
  markLessonComplete: (lessonId, data = {}) =>
    api.post(`/progress/lessons/${lessonId}/complete/`, data),
  getLessonProgress: (lessonId) =>
    api.get(`/progress/lessons/${lessonId}/`),
}
```

---

## 5. KẾT NỐI VỚI CÁC APPS KHÁC

### 5.1 Progress App 📊

**Quan hệ:**
- `progress.UserEnrollment` → `curriculum.Course`
- `progress.LessonProgress` → `curriculum.Lesson`

**Dữ liệu trao đổi:**
1. **Enroll**: Học sinh `POST /progress/enroll/` với `course_id`
2. **Tracking**: `LessonProgress` lưu `status` (locked/in_progress/completed), `best_score`, v.v.
3. **Unlock Check**: LessonSerializer gọi `LessonProgress.objects.filter(...)` để kiểm tra unlock rules

**Ví dụ:**
```
Student enrolls Course A1 → UserEnrollment(user=1, course=1, status='active')
Student completes Lesson 1 with score 85 → LessonProgress(user=1, lesson=1, status='completed', best_score=85)
Lesson 2 có unlock_rule(required_lesson=1, min_score=60) → Kiểm tra LessonProgress(lesson=1, best_score≥60) → UNLOCKED ✓
```

---

### 5.2 Grammar App 🎓

**Quan hệ:**
- `LessonContent.grammar_topic_id` → `grammar.GrammarTopic.id` (soft reference)

**Dữ liệu trao đổi:**
1. **Linking**: Bài học có thể tham chiếu đến một `GrammarTopic`
2. **Deep linking**: Click grammar topic → `GrammarDetailView` → `grammarApi.getTopic(slug)`

**Ví dụ:**
```json
{
  "id": 1,
  "lesson": "Lesson 2: Grammar",
  "grammar_topic_id": 42,
  "grammar_title": "Present Simple",
  "grammar_sections": [
    {
      "title": "Usage",
      "grammar_topic_id": 42,
      "examples": [...]
    }
  ]
}
```

---

### 5.3 Vocabulary App 📚

**Quan hệ:**
- `LessonContent.vocab_word_ids` → `vocabulary.Word.id` (JSON list)

**Dữ liệu trao đổi:**
1. **Highlighting**: Từ vựng được highlight trong reading passage
2. **SRS Tracking**: Từ vựng trong lesson được thêm vào SRS queue
3. **Flashcard**: Học sinh có thể add từ vựng vào flashcard

**Ví dụ:**
```json
{
  "vocab_items": [
    {"word": "headache", "id": 123, ...}
  ],
  "vocab_word_ids": [123, 124, 125]
}
```

---

### 5.4 Exercises App 💪

**Quan hệ:**
- `LessonExercise.exercise_type + exercise_id` → `exercises_*exercise`

**Dữ liệu trao đổi:**
1. **Polymorphic**: Lesson liên kết tới Listening, Speaking, Reading, Writing exercises
2. **Content**: `LessonContent.listening_content/speaking_content/...` chứa exercise data
3. **Submission**: Khi học sinh submit → `ExerciseResult` được tạo

**Ví dụ:**
```python
# Lesson 1 có 2 bài tập
LessonExercise(lesson=1, exercise_type='listening', exercise_id=7, passing_score=60)
LessonExercise(lesson=1, exercise_type='reading', exercise_id=42, passing_score=70)

# Khi submit → LessonExercise được truy vấn, thông tin từ exercises app được lấy
```

---

### 5.5 Gamification App 🎮

**Quan hệ:**
- `LessonContent.completion_xp` → XP grant khi hoàn thành
- `LessonContent.bonus_xp` → XP thưởng nếu ≥80%

**Dữ liệu trao đổi:**
1. **XP Grant**: Khi `markLessonComplete()` → gọi `gamification` để cộng XP
2. **Badges**: Nếu hoàn thành tất cả lesson trong chapter → badge
3. **Achievements**: Streak, perfect score, v.v.

**Ví dụ:**
```
Lesson 1 completed with score 85 → 10 XP + 50 bonus XP = 60 XP total
User now has 60 XP → Check if eligible for badges
```

---

## 6. QUẢN LÝ DỮ LIỆU

### 6.1 Management Commands

Các lệnh Django để seed/quản lý dữ liệu curriculum.

#### **seed_courses.py**

Tạo CEFR levels, courses, chapters, và skeleton lessons.

```bash
python manage.py seed_courses                    # Create (skip nếu exists)
python manage.py seed_courses --level A2         # Chỉ A2
python manage.py seed_courses --clear            # Delete + recreate
```

**Cấu trúc tạo:**
- 5 CEFR Levels (A1-C1)
- 1 Course per level
- 3 Chapters per course
- 7 Lessons per chapter

**Ví dụ:**
```
A1 → "Nền tảng tiếng Anh"
  → Ch1: "Giới thiệu bản thân"
    → Lesson 1: vocabulary, Lesson 2: grammar, ...
  → Ch2: "Gia đình & Bạn bè"
    → Lesson 8: vocabulary, Lesson 9: grammar, ...
```

#### **seed_grammar_lessons.py**

Link lessons tới grammar topics.

```bash
python manage.py seed_grammar_lessons
```

#### **seed_vocab_lessons.py**

Link lessons tới vocabulary words (SRS tracking).

```bash
python manage.py seed_vocab_lessons
```

#### **seed_lesson_content.py**

Populate `LessonContent` với reading passage, grammar notes, exercises, v.v.

```bash
python manage.py seed_lesson_content
```

---

### 6.2 Django Admin

Tất cả models được đăng ký trong `admin.py`.

```python
@admin.register(CEFRLevel)
class CEFRLevelAdmin(admin.ModelAdmin):
    list_display = ["code", "name_vi", "order", "is_active"]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "level", "is_premium"]
    inlines = [ChapterInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order", "passing_score"]
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "chapter", "lesson_type", "estimated_minutes"]

@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ["lesson", "lesson_type_display", "has_reading", "vocab_count", ...]
```

**Tính năng:**
- Inline editing (Chapter từ Course detail, Lesson từ Chapter detail)
- Search & Filter
- Bulk actions

---

## 7. TÍNH NĂNG TRIỂN KHAI

### ✅ Đã Triển Khai

| Tính năng | Backend | Frontend | Status |
|---|---|---|---|
| **CEFR Level Management** | ✅ Models, serializers, views | ✅ CoursesView filter | ✅ |
| **Course CRUD** | ✅ ViewSet, serializers | ✅ CoursesView, CourseDetailView | ✅ |
| **Chapter Management** | ✅ Models, views | ✅ CourseDetailView | ✅ |
| **Lesson Management** | ✅ Models, views | ✅ LessonDetailView | ✅ |
| **Rich Content (LessonContent)** | ✅ Models, serializers | ✅ Rendering sections | ✅ |
| **Reading Section** | ✅ JSON storage | ✅ ReadingSection.vue | ✅ |
| **Vocabulary Inline** | ✅ JSON vocab_items | ✅ VocabFootnote.vue | ✅ |
| **Grammar Sections** | ✅ JSON grammar_sections | ✅ GrammarSection.vue | ✅ |
| **Listening Content** | ✅ JSON listening_content | ✅ ListeningSection.vue | ✅ |
| **Speaking Content** | ✅ JSON speaking_content | ✅ SpeakingSection.vue | ✅ |
| **Writing Content** | ✅ JSON writing_content | ✅ WritingSection.vue | ✅ |
| **Unlock Rules** | ✅ Models, serializers | ✅ Check in serializer | ✅ |
| **Progress Integration** | ✅ Relation fields | ✅ Status display | ✅ |
| **Exercise Linking** | ✅ LessonExercise polymorphic | ✅ Exercise rendering | ✅ |
| **Admin Interface** | ✅ ModelAdmin classes | N/A | ✅ |
| **Management Commands** | ✅ seed_courses, etc. | N/A | ✅ |

---

### 🚀 Tính năng mở rộng tiềm năng

- [ ] Lesson dependencies (complex DAG graph)
- [ ] A/B testing (different content versions)
- [ ] AI-generated content (Qwen integration)
- [ ] Lesson difficulty adjustment
- [ ] Performance analytics per lesson
- [ ] Lesson recommendations
- [ ] Multi-language content

---

## 8. SƠ ĐỒ QUAN HỆ

### 8.1 Entity-Relationship Diagram (ERD)

```
CEFRLevel (1) ──────→ (N) Course
                      │
                      ├─ slug (unique)
                      ├─ title
                      └─ thumbnail
                      │
                      ↓
                   (1) ──────→ (N) Chapter
                            │
                            ├─ title
                            ├─ passing_score
                            │
                            ↓
                         (1) ──────→ (N) Lesson
                                  │
                                  ├─ lesson_type
                                  ├─ estimated_minutes
                                  │
                                  ├─→ (1) LessonContent
                                  │        ├─ reading_passage
                                  │        ├─ vocab_items
                                  │        ├─ grammar_sections
                                  │        ├─ listening_content
                                  │        ├─ speaking_content
                                  │        ├─ writing_content
                                  │        ├─ exercises
                                  │        └─ completion_xp
                                  │
                                  ├─→ (N) LessonExercise
                                  │        ├─ exercise_type
                                  │        ├─ exercise_id
                                  │        └─ passing_score
                                  │
                                  └─→ (N) UnlockRule
                                          ├─ required_lesson (FK→Lesson)
                                          └─ min_score
                      
                        ↓
                    progress_userenrollment (FK→Course)
                    progress_lessonprogress (FK→Lesson)
```

### 8.2 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vue3)                          │
├─────────────────────────────────────────────────────────────┤
│  CoursesView → GET /curriculum/courses/                   │
│  CourseDetailView → GET /curriculum/courses/{id}/         │
│  LessonDetailView → GET /curriculum/lessons/{id}/content/ │
└────────────────────────┬────────────────────────────────────┘
                         │
                    API Layer
                         │
                    curriculumApi.js
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   BACKEND (Django)                          │
├─────────────────────────────────────────────────────────────┤
│  ViewSets/Generics ──→ Serializers ──→ Models            │
│  ├─ CourseViewSet                                         │
│  ├─ ChapterListView                                       │
│  ├─ LessonListView                                        │
│  └─ LessonContentView                                     │
│                                                            │
│  Serializer Methods:                                       │
│  ├─ get_is_unlocked() ──→ LessonProgress (progress app)  │
│  ├─ get_progress_status() ──→ LessonProgress             │
│  └─ get_exercise_type() ──→ LessonExercise               │
│                                                            │
│  Database:                                                 │
│  ├─ curriculum_cefrlevel                                 │
│  ├─ curriculum_course                                    │
│  ├─ curriculum_chapter                                   │
│  ├─ curriculum_lesson                                    │
│  ├─ curriculum_lessoncontent                             │
│  ├─ curriculum_lessonexercise                            │
│  └─ curriculum_unlockrule                                │
└────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
    progress.py    grammar.py      vocabulary.py
    (enrollment,   (topic link)    (word linking)
     progress)
```

---

## 🎯 Kết luận

**Curriculum App** là nền tảng của hệ thống, cung cấp:

1. ✅ **Hierarchical course structure** (CEFR → Course → Chapter → Lesson)
2. ✅ **Rich, flexible content** (JSON-based storage)
3. ✅ **Polymorphic exercise linking** (flexible integration)
4. ✅ **Unlock rules & prerequisites** (engagement & progression)
5. ✅ **Progress tracking** (integration with progress app)
6. ✅ **Multi-skill lessons** (reading, listening, speaking, writing, grammar)
7. ✅ **Admin management** (Django admin + seed commands)

**Frontend** cung cấp:
- ✅ Course browsing & enrollment
- ✅ Rich lesson rendering
- ✅ Multi-section content display
- ✅ Progress visualization
- ✅ Unlock gate handling

---

**Tài liệu này được cập nhật:** 06/05/2026
**Phiên bản mô hình:** 1.0
**Trạng thái:** Production Ready ✅
