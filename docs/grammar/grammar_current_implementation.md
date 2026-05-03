# 📚 HỆ THỐNG GRAMMAR HIỆN TẠI — TỔNG QUAN TRIỂN KHAI
**Ngày tổng hợp:** 2024
**Phạm vi:** Backend (Django REST Framework) + Frontend (Vue.js 3)
**Trạng thái:** ✅ Hoàn thành Phase 0 (Core Learning Experience)
---
## I. KIẾN TRÚC TỔNG THỂ
```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vue.js 3)                      │
├─────────────────────────────────────────────────────────────────┤
│  GrammarView.vue          → Danh sách chủ điểm theo CEFR       │
│  GrammarDetailView.vue    → Chi tiết + Quiz auto-generated     │
└─────────────────────────────────────────────────────────────────┘
                              ↕ API calls (axios)
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Django REST Framework)              │
├─────────────────────────────────────────────────────────────────┤
│  /api/v1/grammar/           → List topics (paginated)          │
│  /api/v1/grammar/<slug>/    → Topic detail + rules + examples  │
│  /api/v1/grammar/<slug>/quiz/ → Submit quiz score             │
│  /api/v1/grammar/progress/  → User's quiz history              │
└─────────────────────────────────────────────────────────────────┘
                              ↕ ORM queries
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (PostgreSQL)                      │
├─────────────────────────────────────────────────────────────────┤
│  grammar_topic            → Chủ điểm ngữ pháp                  │
│  grammar_rule             → Quy tắc trong chủ điểm             │
│  grammar_example          → Ví dụ minh họa                     │
│  grammar_quiz_result      → Kết quả quiz của user              │
└─────────────────────────────────────────────────────────────────┘
```
---
## II. BACKEND — CHI TIẾT TRIỂN KHAI
### 1. Models (`backend/apps/grammar/models.py`)
#### **a) GrammarTopic** — Chủ điểm ngữ pháp
| Field | Type | Mô tả |
|-------|------|-------|
| `title` | CharField(200) | Tên chủ đề (VD: "Present Simple Tense") |
| `slug` | SlugField(unique) | URL-friendly identifier |
| `level` | CharField(2) | CEFR level (A1/A2/B1/B2/C1/C2) |
| `chapter` | CharField(200) | Chương để nhóm topics (VD: "Thì cơ bản") |
| `order` | PositiveIntegerField | Thứ tự sắp xếp trong chapter |
| `is_published` | BooleanField | Trạng thái hiển thị |
| `lesson` | OneToOne(Lesson) | Liên kết với Curriculum Lesson (optional) |
| `icon` | CharField(50) | Emoji đại diện |
| `description` | TextField | Mô tả ngắn |
| `analogy` | TextField | **Pedagogical**: Phép ẩn dụ so sánh |
| `real_world_use` | TextField | **Pedagogical**: Ứng dụng thực tế |
| `memory_hook` | TextField | **Pedagogical**: Mẹo nhớ tổng quát |
**Indexes:**
- `(level, order)` — Tối ưu list view
- `(level, chapter, order)` — Tối ưu grouping
- `(level, is_published)` — Filter nhanh
#### **b) GrammarRule** — Quy tắc cụ thể
| Field | Type | Mô tả |
|-------|------|-------|
| `topic` | FK(GrammarTopic) | Chủ điểm cha |
| `title` | CharField(255) | Tên quy tắc (VD: "Câu khẳng định") |
| `formula` | CharField(500) | Công thức (VD: "S + V(s/es) + O") |
| `explanation` | TextField | Giải thích chi tiết (hỗ trợ Markdown) |
| `memory_hook` | TextField | Mẹo nhớ riêng cho rule này |
| `is_exception` | BooleanField | Đánh dấu ngoại lệ (UI hiển thị cảnh báo đỏ) |
| `order` | PositiveIntegerField | Thứ tự hiển thị |
#### **c) GrammarExample** — Ví dụ minh họa
| Field | Type | Mô tả |
|-------|------|-------|
| `rule` | FK(GrammarRule) | Quy tắc mẹ |
| `sentence` | TextField | Câu tiếng Anh |
| `translation` | TextField | Dịch tiếng Việt |
| `context` | CharField(255) | **Pedagogical**: Ngữ cảnh cảm xúc |
| `highlight` | CharField(150) | Từ/cụm từ cần tô màu |
| `audio_url` | URLField | Link audio phát âm (S3/CDN) |
#### **d) GrammarQuizResult** — Lưu kết quả quiz
| Field | Type | Mô tả |
|-------|------|-------|
| `user` | FK(User) | Người học |
| `topic` | FK(GrammarTopic) | Chủ điểm đã làm quiz |
| `score` | FloatField | Điểm phần trăm (0-100) |
| `total_questions` | IntegerField | Tổng số câu hỏi |
| `correct_answers` | IntegerField | Số câu đúng |
| `attempted_at` | DateTimeField | Thời gian làm (auto update) |
**Unique constraint:** `(user, topic)` — Mỗi user chỉ lưu 1 kết quả mới nhất per topic
---
### 2. Views & API Endpoints (`backend/apps/grammar/views.py`)
| Endpoint | Method | View Class | Chức năng | Cache |
|----------|--------|------------|-----------|-------|
| `/api/v1/grammar/` | GET | `GrammarTopicListView` | List published topics, filter by level | 5 phút |
| `/api/v1/grammar/<slug>/` | GET | `GrammarTopicDetailView` | Detail + all rules + examples | Không cache |
| `/api/v1/grammar/<slug>/quiz/` | POST | `GrammarQuizSubmitView` | Submit quiz score (upsert) | Không cache |
| `/api/v1/grammar/progress/` | GET | `GrammarProgressView` | Get all quiz results for user | Không cache |
#### **Chi tiết logic quan trọng:**
**a) GrammarTopicListView:**
```python
# Query tối ưu với filter + pagination
qs = GrammarTopic.objects.filter(is_published=True).order_by("level", "order")
if level:
    qs = qs.filter(level=level.upper())
```
**b) GrammarTopicDetailView:**
```python
# Prefetch related để tránh N+1 queries
queryset = GrammarTopic.objects.filter(is_published=True).prefetch_related(
    "rules", "rules__examples"
)
```
**c) GrammarQuizSubmitView:**
```python
# Upsert pattern — cập nhật hoặc tạo mới
result, _ = GrammarQuizResult.objects.update_or_create(
    user=request.user,
    topic=topic,
    defaults={
        "score": d["score"],
        "total_questions": d["total_questions"],
        "correct_answers": d["correct_answers"],
    },
)
```
---
### 3. Serializers (`backend/apps/grammar/serializers.py`)
| Serializer | Mục đích | Fields chính |
|------------|----------|--------------|
| `GrammarExampleSerializer` | List examples | id, sentence, translation, context, highlight, audio_url |
| `GrammarRuleSerializer` | List rules + nested examples | id, title, formula, explanation, memory_hook, is_exception, order, **examples** |
| `GrammarTopicListSerializer` | List view (lightweight) | id, title, slug, level, chapter, icon, description, analogy, **rule_count** |
| `GrammarTopicDetailSerializer` | Detail view (full) | Tất cả fields + **rules**, prev_topic, next_topic |
| `GrammarQuizResultSerializer` | Trả kết quả quiz | id, topic, score, total_questions, correct_answers, attempted_at |
| `GrammarQuizSubmitSerializer` | Input validation | score, total_questions, correct_answers |
**Đặc biệt:** `GrammarTopicDetailSerializer` có method `_sibling()` để trả về prev/next topic cùng level, hỗ trợ navigation "Bài trước/Bài sau".
---
### 4. URL Configuration (`backend/apps/grammar/urls.py`)
```python
urlpatterns = [
    path("", GrammarTopicListView.as_view(), name="topic-list"),
    path("progress/", GrammarProgressView.as_view(), name="progress"),
    path("<slug:slug>/", GrammarTopicDetailView.as_view(), name="topic-detail"),
    path("<slug:slug>/quiz/", GrammarQuizSubmitView.as_view(), name="quiz-submit"),
]
```
---
## III. FRONTEND — CHI TIẾT TRIỂN KHAI
### 1. Component Tree
```
GrammarView.vue (List)
├── Level Tabs (All, A1, A2, B1, B2, C1)
├── Chapter Groups (theo level)
│   └── Topic Cards (grid 3 cột)
│       ├── Status indicator (🔒/🟢/🔵)
│       ├── Icon + Title + Description
│       ├── Rule count + Quiz score badge
│       └── Progress bar (nếu đã làm quiz)
└── Load More button
GrammarDetailView.vue (Detail)
├── Breadcrumb + Prev/Next navigation
├── SECTION 1: HOOK
│   ├── Title + Level badge + Chapter
│   ├── Description
│   ├── Analogy box (💡 Gợi nhớ)
│   └── Memory hook box (🧠 Mẹo nhớ)
├── SECTION 2: FORMULA
│   └── Rule Cards (stepper style)
│       ├── Step number + Title + Exception badge
│       ├── Formula pill
│       ├── Explanation
│       ├── Rule memory hook
│       └── Examples list
│           ├── Sentence với highlight
│           ├── Translation
│           ├── Context (tình huống)
│           └── Audio button (🔊)
├── SECTION 3: PRACTICE (Quiz auto-generated)
│   ├── Gap-fill questions (5 câu)
│   ├── Multiple Choice questions (5 câu)
│   ├── Error Correction questions (3 câu)
│   └── Score summary + Save indicator
├── SECTION 4: REAL WORLD
│   └── Practical application text
└── SECTION 5: MEMORY REINFORCEMENT
    └── Topic memory hook recap
```
---
### 2. GrammarView.vue — Logic chính
#### **a) Data flow:**
```javascript
// Fetch topics từ API
const res = await grammarApi.listTopics({ page_size: 100, level })
topics.value = res.data?.data?.results || []
// Fetch progress của user
const res = await grammarApi.getProgress()
progress.value = res.data?.data ?? {}  // { slug: { score, ... } }
```
#### **b) Grouping logic:**
```javascript
// Nhóm topics theo chapter → level
const chapters = computed(() => {
  const byLevel = new Map()
  for (const topic of topics.value) {
    if (!byLevel.has(topic.level)) byLevel.set(topic.level, new Map())
    const levelChapters = byLevel.get(topic.level)
    const chapterName = topic.chapter || ''
    if (!levelChapters.has(chapterName)) {
      levelChapters.set(chapterName, { name: chapterName, topics: [] })
    }
    levelChapters.get(chapterName).topics.push(topic)
  }
  // Sort theo CEFR order: A1 → A2 → B1 → B2 → C1
  return result.sort((a, b) => LEVEL_ORDER[a.level] - LEVEL_ORDER[b.level])
})
```
#### **c) Unlock logic (Course enrollment check):**
```javascript
const unlockedLevels = computed(() => {
  if (!isLoggedIn.value) return new Set()
  const enrolled = dashboard.enrolledCourses()
  const codes = enrolled.map(e => e.course_level_code)
  const maxOrder = Math.max(...codes.map(c => LEVEL_ORDER[c]))
  // Mở khóa tất cả levels <= max level đã đăng ký
  return new Set(LEVELS.filter(lv => LEVEL_ORDER[lv] <= maxOrder))
})
function isLocked(level) {
  return !unlockedLevels.value.has(level)
}
```
#### **d) UI states:**
- **Locked:** opacity 50%, cursor not-allowed, hiển thị 🔒
- **Completed (score ≥ 70%):** border xanh, hiển thị 🟢
- **In progress:** border default, hiển thị 🔵
---
### 3. GrammarDetailView.vue — Logic chính
#### **a) Auto-generated Quiz Engine (`buildQuiz()` function)**
**Loại 1: Gap-fill (5 câu)**
```javascript
// Replace highlighted part với "______"
const blank = ex.sentence.replace(
  new RegExp(ex.highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'),
  '<strong style="color:#818cf8">______</strong>'
)
// Generate wrong options từ highlights của examples khác
const wrongs = allExamples
  .filter(e => e.highlight !== ex.highlight)
  .map(e => e.highlight)
  .slice(0, 3)
questions.push({
  type: 'gap-fill',
  prompt: blank,
  options: shuffle([ex.highlight, ...wrongs]),
  correct: options.indexOf(ex.highlight),
  explanation: ex.translation,
})
```
**Loại 2: Multiple Choice (5 câu)**
```javascript
// Chọn 1 example đúng của rule hiện tại
const correct = rule.examples[0]
// Tìm examples từ rules KHÁC làm đáp án sai
const wrongExamples = rules
  .filter(r => r.id !== rule.id)
  .flatMap(r => r.examples || [])
  .slice(0, 3)
questions.push({
  type: 'mc',
  prompt: `Câu nào đúng theo quy tắc "${rule.title}"?`,
  options: shuffle([correct.sentence, ...wrongExamples.map(e => e.sentence)]),
  correct: options.indexOf(correct.sentence),
})
```
**Loại 3: Error Correction (3 câu)**
```javascript
// Tạo phiên bản lỗi bằng cách swap/modify highlighted word
const errorVersion = createErrorSentence(ex.sentence, ex.highlight)
questions.push({
  type: 'error',
  errorSentence: errorVersion,
  options: [
    `Lỗi ở "${ex.highlight}" — đúng phải là: "${ex.highlight}"`,
    `Câu này đúng, không có lỗi`,
    `Lỗi ở cấu trúc câu chung`,
  ],
})
```
#### **b) Quiz state management:**
```javascript
const quizQuestions = ref([])  // Array of reactive question objects
const quizDone = ref(false)
const quizSaved = ref(false)
// Track selected answer per question
q.selected = null  // Index of selected option (-1 nếu chưa chọn)
// Calculate score
const quizScore = computed(() =>
  quizQuestions.value.filter(q => q.selected === q.correct).length
)
const quizPercent = computed(() =>
  Math.round((quizScore.value / quizQuestions.value.length) * 100)
)
```
#### **c) Submit quiz result:**
```javascript
async function saveQuizResult() {
  try {
    await grammarApi.submitQuiz(route.params.slug, {
      score: quizPercent.value,
      total_questions: quizQuestions.value.length,
      correct_answers: quizScore.value,
    })
    quizSaved.value = true
  } catch (e) {
    console.error('Không thể lưu kết quả')
  }
}
```
#### **d) Pedagogical features:**
- **Immediate feedback:** Hiển thị ✓/✗ ngay sau khi chọn đáp án
- **Explanation:** Hiển thị dịch nghĩa + giải thích sau mỗi câu
- **Score summary:** Display emoji + message dựa trên % score
- **Navigation:** Tự động gợi ý "Bài tiếp →" sau khi hoàn thành
---
### 4. API Client (`frontend/src/api/curriculum.js`)
```javascript
export const grammarApi = {
  listTopics: (params = {}) => api.get('/grammar/', { params }),
  getTopic: (slug) => api.get(`/grammar/${slug}/`),
  getProgress: () => api.get('/grammar/progress/'),
  submitQuiz: (slug, data) => api.post(`/grammar/${slug}/quiz/`, data),
}
```
---
## IV. TÍNH NĂNG ĐÃ TRIỂN KHAI VS YÊU CẦU SƯ PHẠM
### ✅ **ĐẠT ĐƯỢC**
| Yêu cầu | Triển khai | Đánh giá |
|---------|-----------|----------|
| **Hierarchy rõ ràng** | Topic → Rule → Example | ⭐⭐⭐⭐⭐ Excellent |
| **Pedagogical metadata** | Analogy, Memory Hook, Context | ⭐⭐⭐⭐⭐ Excellent |
| **CEFR leveling** | A1-C2 với unlock logic | ⭐⭐⭐⭐ Very Good |
| **Chapter grouping** | Group topics by chapter | ⭐⭐⭐⭐ Very Good |
| **Auto-generated quiz** | 3 types từ content | ⭐⭐⭐⭐ Very Good |
| **Progress tracking** | Quiz score persistence | ⭐⭐⭐⭐ Very Good |
| **Audio support** | audio_url field + play button | ⭐⭐⭐ Good |
| **Navigation** | Prev/Next topic links | ⭐⭐⭐⭐ Very Good |
| **Responsive UI** | Grid layout, mobile-friendly | ⭐⭐⭐⭐ Very Good |
### ⚠️ **HẠN CHẾ**
| Vấn đề | Hiện trạng | Mức độ nghiêm trọng |
|--------|-----------|---------------------|
| **Quiz không integrate vào LessonProgress** | Grammar quiz tồn tại độc lập, không sync với Course completion | 🔴 High |
| **LessonExercise không support Grammar type** | Không thể add grammar như 1 exercise trong Lesson | 🔴 High |
| **Không có Spaced Repetition** | Học xong không nhắc nhở ôn tập | 🟡 Medium |
| **Không có difficulty level cho questions** | Mọi câu hỏi đều ngang nhau | 🟡 Medium |
| **Không có tagged error patterns** | Không track được lỗi sai phổ biến | 🟡 Medium |
| **Không có remedial path** | Sai nhiều không chuyển sang bài dễ hơn | 🟡 Medium |
| **Manual content creation** | Phải nhập tay mọi rules/examples | 🟢 Low |
| **Không có AI-generated explanations** | Giải thích do người biên soạn | 🟢 Low |
---
## V. DATA FLOW MINH HỌA
### **Scenario: Học viên học "Present Simple"**
```
1. USER mở /grammar
   → GrammarView.vue fetches /api/v1/grammar/?level=A1
   → Backend: GrammarTopicListView returns paginated list
   → Frontend groups by chapter, displays cards
2. USER click vào "Present Simple Tense"
   → Router navigates to /grammar/a1-present-simple-tense
   → GrammarDetailView.vue fetches /api/v1/grammar/a1-present-simple-tense/
   → Backend: GrammarTopicDetailView returns:
      {
        title: "Present Simple Tense",
        analogy: "Động từ to be giống như dấu bằng (=)",
        rules: [
          {
            title: "Câu khẳng định",
            formula: "S + V(s/es) + O",
            examples: [
              { sentence: "She goes to school", highlight: "goes", ... }
            ]
          }
        ]
      }
3. Frontend auto-generates quiz từ rules/examples
   → buildQuiz() creates 13 questions (5 gap-fill + 5 MC + 3 error)
4. USER làm quiz, chọn đáp án
   → Immediate feedback hiển thị ✓/✗
   → Sau 13 câu, tính score: 10/13 = 77%
5. USER click "Lưu kết quả"
   → Frontend POST /api/v1/grammar/a1-present-simple-tense/quiz/
      Body: { score: 77, total_questions: 13, correct_answers: 10 }
   → Backend: GrammarQuizSubmitView.upsert()
   → Database: grammar_quiz_result table updated
6. USER quay lại /grammar
   → GrammarView.vue fetches /api/v1/grammar/progress/
   → Card "Present Simple" hiển thị badge "77%" + progress bar xanh
   → Status đổi từ 🔵 → 🟢 (vì score ≥ 70%)
```
---
## VI. CÔNG NGHỆ SỬ DỤNG
### Backend
- **Framework:** Django 4.x + Django REST Framework
- **Database:** PostgreSQL (với indexes tối ưu)
- **Caching:** Redis (5-minute cache cho list endpoint)
- **Authentication:** JWT (IsAuthenticatedOrReadOnly permission)
### Frontend
- **Framework:** Vue.js 3 (Composition API, `<script setup>`)
- **State Management:** Pinia (auth store, dashboard store)
- **Routing:** Vue Router 4 (dynamic routes với slugs)
- **HTTP Client:** Axios (với interceptors)
- **Styling:** CSS Variables + Tailwind-like utility classes
- **Reactivity:** `ref()`, `computed()`, `watch()`, `reactive()`
### DevOps
- **Migrations:** Django migrations (0001_initial → 0003_grammarquizresult...)
- **Admin Interface:** Django Admin (custom inlines cho Rule/Example)
- **API Documentation:** DRF Schema (OpenAPI/Swagger)
---
## VII. CÁC FILE LIÊN QUAN
### Backend
```
backend/apps/grammar/
├── __init__.py
├── models.py          # 4 models chính
├── views.py           # 4 view classes
├── serializers.py     # 6 serializers
├── urls.py            # 4 endpoints
├── admin.py           # Custom admin inlines
├── apps.py
├── migrations/
│   ├── 0001_initial.py
│   ├── 0002_alter_grammarexample_sentence_and_more.py
│   └── 0003_grammarquizresult_grammartopic_chapter_and_more.py
└── management/commands/  # (nếu có seed commands)
```
### Frontend
```
frontend/src/
├── views/
│   ├── GrammarView.vue         # List view
│   └── GrammarDetailView.vue   # Detail + Quiz
├── api/
│   └── curriculum.js           # grammarApi client
├── router/
│   └── index.js                # Route definitions
└── stores/
    ├── auth.js                 # isLoggedIn ref
    └── dashboard.js            # enrolledCourses for unlock logic
```
---
## VIII. KẾT LUẬN
### **Tổng kết triển khai:**
✅ **Hoàn thành:**
- Core data model với pedagogical enrichment
- RESTful API đầy đủ CRUD operations
- Frontend list + detail views với UX cao cấp
- Auto-generated quiz engine (3 loại câu hỏi)
- Progress tracking với upsert pattern
- CEFR-based unlock logic
- Chapter grouping + navigation
⚠️ **Chưa hoàn thành (xem `grammar_improvement_roadmap.md`):**
- Integration với Curriculum (LessonExercise, LessonProgress)
- Spaced Repetition System
- Error Pattern Tracking + Remedial Path
- Adaptive Quiz Engine
- Question Bank với tagging system
### **Đánh giá tổng thể:**
- **Kiến trúc:** ⭐⭐⭐⭐⭐ (Rất tốt, dễ mở rộng)
- **Pedagogy:** ⭐⭐⭐⭐⭐ (Xuất sắc, có analogy/memory hooks)
- **UX:** ⭐⭐⭐⭐ (Rất tốt, còn thiếu adaptive features)
- **Integration:** ⭐⭐ (Yếu, chưa kết nối với curriculum)
- **Overall:** **7.5/10** — Nền tảng vững chắc, cần Phase 1-3 để hoàn thiện
---
**Tài liệu liên quan:**
- [`grammar_improvement_roadmap.md`](./grammar_improvement_roadmap.md) — Kế hoạch cải tiến Phase 1-3
- [`../architecture/overview.md`](../architecture/overview.md) — Tổng quan kiến trúc hệ thống
- [`../pedagogy/methodology.md`](../pedagogy/methodology.md) — Phương pháp sư phạm áp dụng