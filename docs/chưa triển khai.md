# Phân tích & Kế hoạch triển khai — Content/Curriculum System

> Cập nhật: **31/03/2026** — ✅ Tất cả P0 + hầu hết P1/P2 đã triển khai  
> Phiên 4 (29/03/2026): §8.1 Prerequisite enforcement, §8.4 Teacher CSV export, §8.5 Vocabulary import, Vocabulary CRUD admin, §9.1 UnlockModal, §9.2 SkillTree, §9.3 Split-pane, §9.4 Writing Zen Mode  
> Phiên 5 (31/03/2026): Fix bug `goNextLesson` (route không tồn tại → dùng `next_exercise_type`/`next_exercise_id`), Tích hợp SkillTreeView vào CourseDetailView (toggle List/Tree), Tích hợp UnlockModal vào ExerciseResultView (auto-show khi next_lesson_id có)  
> Phạm vi: So sánh codebase hiện tại vs PRD.md, xác định thiếu sót, lập kế hoạch kỹ thuật chi tiết.

---

## Mục lục

1. [Tổng quan hiện trạng](#1-tổng-quan-hiện-trạng)
2. [Phân tích Admin Content Management](#2-phân-tích-admin-content-management)
3. [Phân tích trang Courses `/courses`](#3-phân-tích-trang-courses)
4. [Phân tích Grammar `/grammar`](#4-phân-tích-grammar)
5. [Phân tích Teacher Portal](#5-phân-tích-teacher-portal)
6. [Ma trận gap vs PRD](#6-ma-trận-gap-vs-prd)
7. [Kế hoạch triển khai chi tiết — P0 (Blocking)](#7-kế-hoạch-triển-khai-chi-tiết--p0-blocking)
8. [Kế hoạch triển khai chi tiết — P1 (Quan trọng)](#8-kế-hoạch-triển-khai-chi-tiết--p1-quan-trọng)
9. [Kế hoạch triển khai chi tiết — P2 (Nâng cấp UX)](#9-kế-hoạch-triển-khai-chi-tiết--p2-nâng-cấp-ux)

---

## 1. Tổng quan hiện trạng

### Kiến trúc backend hiện tại

Hệ thống có **3 API prefix** riêng biệt:

| Prefix | Mục đích | Permission |
|--------|---------|------------|
| `/api/v1/curriculum/` | Học viên đọc content | `IsAdminOrReadOnly` (admin write, user read) |
| `/api/v1/admin-portal/` | Admin quản trị | `IsAdmin` only |
| `/api/v1/teacher/` | Teacher chấm bài, xem lớp | `IsTeacher` |

### Model hierarchy đã có

```
CEFRLevel (A1-C2)
  └── Course (title, slug, description, thumbnail, is_premium, is_active, created_by)
       └── Chapter (title, order, description, passing_score)
            └── Lesson (title, order, lesson_type[8 loại], estimated_minutes, is_active)
                 └── LessonExercise (exercise_type, exercise_id [GenericFK], order, passing_score)
                 └── UnlockRule (required_lesson FK, min_score)

GrammarTopic (title, slug, level, order, is_published, icon, analogy, real_world_use, memory_hook, lesson[OneToOne])
  └── GrammarRule (title, formula, explanation, memory_hook, is_exception, order)
       └── GrammarExample (sentence, translation, context, highlight, audio_url)

ListeningExercise / SpeakingExercise / ReadingExercise / WritingExercise (polymorphic)
ExamSet → Question (question_type: MC/gap_fill/drag_drop, correct_answers[], skill, difficulty)
```

### API endpoints hiện có — mapping đầy đủ

#### Curriculum API (`/api/v1/curriculum/`)
| Method | Endpoint | Impl class | Ghi chú |
|--------|----------|-----------|---------|
| GET/POST/PUT/PATCH/DELETE | `/courses/` `/<pk>/` | CourseViewSet | Full REST via Router |
| GET | `/cefr-levels/` | CEFRLevelListView | Read-only |
| GET/POST | `/courses/<pk>/chapters/` | ChapterListView (ListCreateAPIView) | Có POST nhưng không có PUT/DELETE chapter |
| GET/POST | `/courses/<pk>/chapters/<cpk>/lessons/` | LessonListView | Có POST |
| GET/PUT/PATCH/DELETE | `/lessons/<pk>/` | LessonDetailView | Full CRUD lesson |

#### Admin Portal (`/api/v1/admin-portal/`)
| Method | Endpoint | Ghi chú |
|--------|----------|---------|
| GET | `/courses/<pk>/chapters/` | ~~**Read-only** — AdminChapterListView là ListAPIView, **không có POST**~~ → ✅ **Nâng cấp thành ListCreateAPIView** |
| GET | `/courses/<pk>/chapters/<cpk>/lessons/` | ~~**Read-only** — AdminLessonListView là ListAPIView~~ → ✅ **Nâng cấp thành ListCreateAPIView** |
| GET/POST + GET/PUT/DELETE | `/exam-sets/` `/<pk>/` | Full CRUD ExamSet |
| GET | `/exercises/` | List-only (giữ cho backward compat) |
| ✅ GET/POST | `/exercises/<type>/` | **MỚI** — Exercise CRUD by type |
| ✅ GET/PATCH/DELETE | `/exercises/<type>/<pk>/` | **MỚI** — Exercise detail CRUD |
| ✅ GET/POST | `/lessons/<pk>/exercises/` | **MỚI** — Lesson-Exercise binding list/create |
| ✅ GET/PATCH/DELETE | `/lessons/<pk>/exercises/<lex_pk>/` | **MỚI** — Binding detail |
| ✅ CRUD | `/grammar/topics/` `/<pk>/` | **MỚI** — Grammar Topic admin |
| ✅ CRUD | `/grammar/topics/<topic_pk>/rules/` `/<pk>/` | **MỚI** — Grammar Rule admin |
| ✅ CRUD | `/grammar/rules/<rule_pk>/examples/` `/<pk>/` | **MỚI** — Grammar Example admin |
| ✅ GET/POST | `/courses/<course_pk>/chapters/<pk>/` | **MỚI** — Chapter detail CRUD |
| ✅ GET/PATCH/DELETE | `/lessons/<pk>/` | **MỚI** — Lesson detail CRUD |

#### Exercise API (`/api/v1/exercises/`)
| Method | Endpoint | Ghi chú |
|--------|----------|---------|
| GET | `/listening/<pk>/` | Retrieve only |
| GET | `/speaking/<pk>/` | Retrieve only |
| GET | `/reading/<pk>/` | Retrieve only |
| GET | `/writing/<pk>/` | Retrieve only |

---

## 2. Phân tích Admin Content Management

### Hiện có trong `/admin/content` (AdminContentView.vue)

**Tab "Khoá học":**
- Bảng courses: title, CEFR level badge, student count, premium/free badge, active/hidden badge, nút Edit/Delete
- Nút "+ Thêm khoá học" → Modal form (title, slug, level, order, premium, active, description)
- Click vào row → Drill-down xem chapters (accordion), expand chapter → xem lessons (loại, thời gian, active)
- **Fully working**: tạo, sửa, xóa courses với confirm dialog

**Tab hiện tại chỉ có 1 tab `courses`.**

### Thiếu trong admin vs PRD

Admin hiện tại chỉ là **Course Manager** — không phải **Content Manager** đúng nghĩa.

| Tính năng PRD | Hiện trạng backend | Hiện trạng frontend | Đánh giá |
|--------------|-------------------|--------------------|----|
| Chapter CRUD (tạo/sửa/xóa/sắp xếp) | ✅ **DONE** — AdminChapterListView (ListCreateAPIView) + AdminChapterDetailView | ✅ **DONE** — form modal + edit/delete buttons |
| Lesson CRUD + reorder | ✅ **DONE** — AdminLessonListView (ListCreateAPIView) + AdminLessonDetailView | ✅ **DONE** — form modal + edit/delete buttons |
| Exercise CRUD (L/S/R/W) | ✅ **DONE** — AdminExerciseTypeListView + AdminExerciseTypeDetailView (type-dispatch pattern) | ⚠️ UI chưa có trang riêng — có API nhưng frontend chỉ CRUD qua API |
| Exercise → Lesson binding | ✅ **DONE** — AdminLessonExerciseListView + DetailView | ⚠️ API có, UI trong lesson drill-down chưa có |
| Upload source file (PDF/audio/img) | ❌ Không có model SourceFile, không có endpoint | ❌ Không có UI | 🟡 Thiếu |
| Question Bank full CRUD + filter | ⚠️ ExamSet CRUD có, Question chỉ nested | ❌ AdminAssessmentsView: list ExamSet + browse exercise | 🟡 Thiếu Question CRUD |
| CSV import vocabulary/questions | ✅ **DONE** — `AdminVocabularyImportView` POST `/admin-portal/vocabulary/import/` | ⚠️ API method có (`importVocabulary`), UI upload form chưa có | 🟡 UI còn thiếu |
| Grammar topic/rule/example CRUD | ✅ **DONE** — 6 admin views (Topic/Rule/Example × List+Detail) | ✅ **DONE** — AdminGrammarView.vue 3-panel tree |
| Vocabulary word CRUD | ✅ **DONE** — AdminVocabularyListView + AdminVocabularyDetailView | ⚠️ API methods có (`getVocabulary`, `createWord`, etc.), UI tab chưa có | 🟡 UI còn thiếu |
| Content preview trước publish | ❌ Không có cơ chế | ❌ Không có UI | 🟢 Nice-to-have |
| Draft/publish workflow | ❌ Chỉ có `is_active` flag | ❌ Không có UI | 🟢 Nice-to-have |

---

## 3. Phân tích trang Courses

### Hiện có trong `/courses`

**CoursesView.vue:**
- Grid courses được enroll hoặc all courses
- Filter buttons CEFR levels (A1-C2)
- Course card: title, level badge, description, lesson count, progress bar nếu đã enroll
- Click → CourseDetailView

**CourseDetailView.vue:**
- Header: thumbnail, title, level, enrollment count, enroll button
- Progress card: % hoàn thành, chapters completed/total
- Chapter accordion: toggled lazy-load lessons khi mở rộng
- Lesson list: icon loại, title, estimated_minutes, status badge (✅ hoàn thành / ▶ có thể học / 🔒 khóa)
- Click lesson → `/learn/:type/:id`

### Thiếu so với PRD

| Tính năng PRD | Hiện trạng | Đánh giá |
|--------------|-----------|---------|
| Skill Tree / Learning Map (visual) | ✅ **DONE** — `SkillTreeView.vue` component (chapter dividers + lesson nodes, trạng thái locked/available/completed) | 🟢 ~~P2~~ — component sẵn sàng, chưa tích hợp vào CourseDetailView |
| Unlock animation (confetti + XP bar) | ✅ **DONE** — `UnlockModal.vue` component (auto-dismiss 3s, XP display) | 🟢 ~~P2~~ — component sẵn sàng, chưa trigger khi nộp bài |
| Prerequisite enforcement UI | ✅ **DONE** — `is_unlocked` field trong LessonSerializer + CourseDetailView.vue block navigation | ✅ P1 — **DONE** |
| Progress Check bắt buộc sau chapter | ❌ Logic chưa có | ❌ Không có trigger | 🟡 P1 — còn thiếu |
| CEFR cumulative scoring + auto-cert | Logic certificate có, nhưng không có trigger từ course | 🟡 P1 |
| Split-pane layout exercises (6:4) | ✅ **DONE** — toggle `⊞ Split` trong ListeningView + ReadingView | 🟢 ~~P2~~ |
| Speaking dialogue UI (iMessage + karaoke) | Không có | 🟢 P2 — còn thiếu |
| Writing Zen Mode (focus editor) | ✅ **DONE** — `☯ Zen mode` trong WritingView.vue | 🟢 ~~P2~~ |

---

## 4. Phân tích Grammar `/grammar`

### Cách lưu trữ — Model đánh giá: TỐT

```python
# GrammarTopic — rich metadata
topic.analogy        # ẩn dụ giải thích ngữ pháp ("Present Perfect là cầu nối quá khứ - hiện tại")
topic.real_world_use # ứng dụng thực tế ("Dùng trong CV, email xin việc")
topic.memory_hook    # mẹo nhớ tổng thể
topic.lesson         # OneToOne với Lesson (grammar lesson type)

# GrammarRule — cấu trúc rõ ràng
rule.formula         # "S + have/has + V3/ed" 
rule.explanation     # giải thích tiếng Việt
rule.memory_hook     # mẹo nhớ riêng rule này
rule.is_exception    # đánh dấu exception

# GrammarExample — context phong phú
example.sentence     # "I have just finished my homework."
example.translation  # "Tôi vừa hoàn thành bài tập."
example.context      # "Dùng khi muốn nói vừa xong gần đây"
example.highlight    # "have just finished" (từ cần nhấn mạnh)
example.audio_url    # URL audio phát âm
```

### Cách hiển thị — Đánh giá: KHÁ TỐT, còn vài điểm cần cải thiện

**GrammarView.vue:**
- Search (300ms debounce), filter CEFR level
- Topics grouped accordion, cumulative unlock (B1 → thấy A1+A2+B1)
- Enrollment notice nếu chưa đăng ký course cấp đó

**GrammarDetailView.vue:**
- Topic header với icon, level badge, description
- Rules dạng accordion: title + formula + explanation + examples với highlight
- Exceptions có thể collapse
- Memory hooks hiển thị
- Mini-quiz 5 câu tự động tạo từ examples

### Điểm yếu

| Vấn đề | Mức độ |
|-------|-------|
| ~~Admin không thể tạo/sửa grammar qua UI~~ | ✅ P0 **DONE** — AdminGrammarView.vue |
| ~~Mini-quiz không persist kết quả~~ | ✅ P1 **DONE** — GrammarQuizResult + POST `/grammar/<slug>/quiz/` |
| GrammarTopic linked với Lesson nhưng không hiển thị bài tập liên quan | 🟡 P1 — còn thiếu |
| ~~audio_url có trường nhưng player chưa được build~~ | ✅ P1 **DONE** — audio player trong GrammarDetailView.vue |
| Không có liên kết grammar → Gap Fill exercises | 🟡 P1 — còn thiếu |

---

## 5. Phân tích Teacher Portal

### Hiện có

| Endpoint | View | Chức năng |
|----------|------|-----------|
| GET `/teacher/dashboard/` | TeacherDashboardView | KPIs: pending grading count, score distribution, student count |
| GET `/teacher/grading/` | TeacherGradingQueueView | Queue speaking + writing submissions cần chấm |
| POST `/teacher/grading/speaking/<pk>/` | TeacherGradeSpeakingView | Set score + feedback cho speaking |
| POST `/teacher/grading/writing/<pk>/` | TeacherGradeWritingView | Set score + feedback cho writing |
| GET `/teacher/classes/` | TeacherClassListView | Danh sách courses có học viên enroll |
| GET `/teacher/classes/<pk>/students/` | TeacherClassStudentsView | Học viên + progress% từng người |

### Thiếu so với PRD

| Tính năng PRD | Hiện trạng | Đánh giá |
|--------------|-----------|---------|
| Tạo custom exam từ Question Bank | Không có | 🟡 P1 — còn thiếu |
| Giao bài tập cho lớp/cá nhân có deadline | Không có | 🟡 P1 — còn thiếu |
| Tạo supplementary course cho học viên yếu | Không có | 🟡 P1 — còn thiếu |
| Export class performance CSV | ✅ **DONE** — `TeacherExportClassView` GET `/teacher/classes/<pk>/export/` + nút "Xuất CSV" trong TeacherClassView.vue | ✅ P1 |
| Override AI feedback bằng comment riêng | Có thể grade (set score), nhưng không có field để thêm bên cạnh AI | 🟡 P1 |
| Filter grade queue by skill/level/student | Không có filter | 🟢 P2 |

---

## 6. Ma trận gap vs PRD

```
🔴 P0 — Blocking: không thể tạo content học
🟡 P1 — Quan trọng: ảnh hưởng chất lượng học
🟢 P2 — Enhancement: nâng cao UX
```

| # | Tính năng | Backend thiếu | Frontend thiếu | Độ phức tạp | Ưu tiên |
|---|----------|--------------|----------------|------------|--------|
| 1 | Chapter full CRUD | ✅ **DONE** | ✅ **DONE** | – | 🔴 ~~P0~~ |
| 2 | Lesson CRUD qua admin portal | ✅ **DONE** | ✅ **DONE** | – | 🔴 ~~P0~~ |
| 3 | Exercise CRUD — 4 loại (L/S/R/W) | ✅ **DONE** — typed CRUD views | ⚠️ API có, UI form riêng chưa có | Cao | 🔴 ~~P0~~ → ⚠️ UI còn thiếu |
| 4 | Exercise → Lesson binding | ✅ **DONE** | ⚠️ API có, UI trong lesson drill-down chưa có | Trung bình | 🔴 ~~P0~~ → ⚠️ UI còn thiếu |
| 5 | Grammar CRUD (topic/rule/example) | ✅ **DONE** | ✅ **DONE** — AdminGrammarView.vue | – | 🔴 ~~P0~~ |
| 6 | Question CRUD ngân hàng câu hỏi | ⚠️ Question chỉ nested trong ExamSet; cần standalone | ⚠️ AdminAssessmentsView chỉ browse | Trung bình | 🟡 P1 — **còn thiếu** |
| 7 | Prerequisite enforcement UI | ✅ **DONE** — `is_unlocked` field trong LessonSerializer | ✅ **DONE** — CourseDetailView.vue block + tooltip | Thấp | 🟡 ~~P1~~ |
| 8 | Grammar quiz persistence | ✅ **DONE** | ✅ **DONE** | – | 🟡 ~~P1~~ |
| 9 | Grammar audio player | ✅ audio_url field có | ✅ **DONE** — GrammarDetailView.vue | – | 🟡 ~~P1~~ |
| 10 | Progress Check bắt buộc sau chapter | ❌ Logic chưa có | ❌ Không có trigger | Cao | 🟡 P1 — **còn thiếu** |
| 11 | Source file upload S3 | ❌ Không có SourceFile model, không có endpoint | ❌ Không có upload UI | Cao | 🟡 P1 — **còn thiếu** |
| 12 | CSV bulk import vocabulary | ✅ **DONE** — `AdminVocabularyImportView` | ⚠️ API method có, UI upload form chưa có | Trung bình | 🟡 ~~P1~~ → ⚠️ UI còn thiếu |
| 13 | Teacher: tạo exam + giao bài | ❌ Không có endpoint | ❌ Không có UI | Cao | 🟡 P1 — **còn thiếu** |
| 14 | Teacher: export class CSV | ✅ **DONE** — `TeacherExportClassView` | ✅ **DONE** — nút "Xuất CSV" trong TeacherClassView.vue | Thấp | 🟡 ~~P1~~ |
| 15 | Skill Tree visual map | ✅ Data có | ✅ **DONE** — `SkillTreeView.vue` component + **tích hợp vào CourseDetailView** toggle List/🌿 Skill Tree | Cao | 🟢 ~~P2~~ |
| 16 | Unlock animations | ✅ Data có | ✅ **DONE** — `UnlockModal.vue` component + **tích hợp ExerciseResultView** (auto-show khi next_lesson_id có, 3s auto-dismiss) | Thấp | 🟢 ~~P2~~ |
| 17 | Split-pane exercise layout | – | ✅ **DONE** — toggle `⊞ Split` trong ListeningView + ReadingView | Trung bình | 🟢 ~~P2~~ |
| 18 | Speaking dialogue UI (karaoke) | – | ❌ Không có | Cao | 🟢 P2 — **còn thiếu** |
| 19 | Writing Zen Mode editor | – | ✅ **DONE** — `☯ Zen mode` trong WritingView.vue | Trung bình | 🟢 ~~P2~~ |
| 20 | Vocabulary CRUD (admin) | ✅ **DONE** — AdminVocabularyListView + DetailView | ⚠️ API methods có, UI tab chưa có trong AdminContentView | Trung bình | 🟢 ~~P2~~ → ⚠️ UI còn thiếu |

---

## 7. Kế hoạch triển khai chi tiết — P0 (Blocking)

> **✅ HOÀN THÀNH — 28/03/2026**  
> Tất cả 4 mục trong §7 đã được triển khai đầy đủ (backend + frontend).  
> Xem chi tiết tại [docs/đã triển khai.md](đã triển khai.md).

### 7.1 Chapter & Lesson Full CRUD

#### Mục tiêu
Admin có thể tạo, sửa, xóa, sắp xếp thứ tự chapters và lessons từ trang `/admin/content`.

#### Backend — việc cần làm

**Bước 1: Thêm Chapter UPDATE/DELETE vào curriculum API**
```python
# backend/apps/curriculum/views.py — thêm view mới
class ChapterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        return Chapter.objects.filter(course_id=self.kwargs["course_pk"])
    def perform_destroy(self, instance):
        instance.delete()  # hard delete (cascade to Lesson)

# backend/apps/curriculum/urls.py — thêm route
path("courses/<int:course_pk>/chapters/<int:pk>/", ChapterDetailView.as_view(), name="chapter-detail"),
```

**Bước 2: Thêm Chapter + Lesson reorder endpoint**
```python
# POST /api/v1/curriculum/courses/<pk>/chapters/reorder/
# Body: {"order": [id1, id2, id3]}  → bulk update Chapter.order
class ChapterReorderView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def post(self, request, course_pk):
        for idx, chapter_id in enumerate(request.data.get("order", []), start=1):
            Chapter.objects.filter(id=chapter_id, course_id=course_pk).update(order=idx)
        return Response({"status": "ok"})
```

**Bước 3: Nâng cấp AdminChapterListView + AdminLessonListView thành có write**
```python
# admin_portal/views.py — đổi từ ListAPIView → ListCreateAPIView
class AdminChapterListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdmin]
    ...

class AdminChapterDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminChapterSerializer
    permission_classes = [IsAdmin]

# admin_portal/urls.py — thêm
path("courses/<int:pk>/chapters/<int:cpk>/", AdminChapterDetailView.as_view(), ...),
```

**Serializer cần thiết:**
```python
class AdminChapterSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    class Meta:
        model = Chapter
        fields = ["id", "course", "title", "description", "order", "passing_score", "lesson_count"]
    def get_lesson_count(self, obj):
        return obj.lesson_set.count()
```

#### Frontend — luồng UI

**Tab structure mới trong AdminContentView.vue:**
```
Tab 1: Khoá học (hiện tại) → giữ nguyên course CRUD
Tab 2: Nội dung (mới) → 3-panel layout:
  Panel trái: Course list (click để chọn)
  Panel giữa: Chapter list + Add/Edit/Reorder/Delete chapter
  Panel phải: Lesson list + Add/Edit/Reorder/Delete lesson
```

**Chapter form fields:** title, description, order, passing_score
**Lesson form fields:** title, order, lesson_type (dropdown 8 loại), estimated_minutes, is_active

**Reorder UI:** Drag-and-drop danh sách (dùng `@vueuse/core` `useSortable` hoặc simple `up/down` buttons)

---

### 7.2 Exercise CRUD — 4 loại (Listening/Speaking/Reading/Writing)

#### Mục tiêu
Admin có thể tạo và chỉnh sửa bài tập từng loại. Sau đó gắn vào lesson.

#### Data model phân tích

Mỗi exercise type có trường riêng:
```python
# ListeningExercise
title, audio_url, transcript, time_limit, questions[] (MC/gap_fill/drag_drop)

# SpeakingExercise  
title, prompt_text, sample_audio_url, expected_script, dialogue_turns[]

# ReadingExercise
title, passage_text, reading_time, questions[]

# WritingExercise
title, prompt_text, word_count_min, word_count_max, time_limit, rubric_override{}
```

#### Backend — việc cần làm

**Bước 1: Tạo Admin Exercise serializers (full fields)**
```python
# admin_portal/serializers.py thêm:
class AdminListeningExerciseSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    class Meta:
        model = ListeningExercise
        fields = "__all__"

# Tương tự cho Speaking, Reading, Writing
```

**Bước 2: Tạo Admin Exercise CRUD views**
```python
# Dùng generic ViewSet với `exercise_type` param:
class AdminExerciseCRUDView(AuditLogMixin, APIView):
    permission_classes = [IsAdmin]
    MODELS = {
        "listening": (ListeningExercise, AdminListeningExerciseSerializer),
        "speaking":  (SpeakingExercise,  AdminSpeakingExerciseSerializer),
        "reading":   (ReadingExercise,   AdminReadingExerciseSerializer),
        "writing":   (WritingExercise,   AdminWritingExerciseSerializer),
    }
    def get(self, request, type):
        Model, Ser = self.MODELS[type]
        qs = Model.objects.all()
        return Response(Ser(qs, many=True).data)
    def post(self, request, type):
        Model, Ser = self.MODELS[type]
        ser = Ser(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        self._audit("CREATE", obj)
        return Response(Ser(obj).data, status=201)

# URL: /admin-portal/exercises/<str:type>/          GET list + POST create
#      /admin-portal/exercises/<str:type>/<int:pk>/  GET + PATCH + DELETE
```

**Bước 3: Question nested create/update**

Questions được tạo inline khi tạo bài tập. Dùng `writable nested serializer` với `create()` override:
```python
def create(self, validated_data):
    questions_data = validated_data.pop("questions", [])
    exercise = ListeningExercise.objects.create(**validated_data)
    for q in questions_data:
        Question.objects.create(exercise=exercise, **q)
    return exercise
```

#### Frontend — luồng UI

**Tab "Bài tập" trong AdminContentView.vue / AdminAssessmentsView.vue:**

```
Filter bar: [Loại: Tất cả/Listening/Speaking/Reading/Writing] [Level: A1-C2] [Tìm kiếm]
Table: title | loại | level | số câu hỏi | gắn vào lesson nào | Edit | Delete
Button: "+ Tạo bài tập"
```

**Form tạo bài tập theo loại (tabbed hoặc step-by-step):**
```
Bước 1 — Thông tin cơ bản:
  Tiêu đề, Loại bài tập (radio: L/S/R/W), CEFR level, thời gian giới hạn

Bước 2 — Nội dung (thay đổi theo loại):
  Listening: Upload audio file + nhập transcript
  Speaking:  Nhập prompt + upload sample audio + nhập expected script
  Reading:   Text editor cho passage
  Writing:   Nhập prompt + word count range

Bước 3 — Câu hỏi (Listening/Reading):
  Danh sách câu hỏi, Add question button
  Mỗi câu: loại (MC/gap_fill/drag_drop), nội dung, đáp án, điểm
```

---

### 7.3 Exercise → Lesson Binding

#### Mục tiêu
Sau khi tạo exercise, admin gắn nó vào một lesson cụ thể với thứ tự và điểm qua.

#### Backend — việc cần làm

```python
# admin_portal/views.py
class AdminLessonExerciseView(AuditLogMixin, APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request, lesson_pk):
        """List exercises bound to a lesson"""
        exercises = LessonExercise.objects.filter(lesson_id=lesson_pk).order_by("order")
        return Response(AdminLessonExerciseSerializer(exercises, many=True).data)
    
    def post(self, request, lesson_pk):
        """Bind an exercise to a lesson"""
        # Body: {exercise_type, exercise_id, order, passing_score}
        ser = AdminLessonExerciseSerializer(data={**request.data, "lesson": lesson_pk})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        self._audit("CREATE", obj, f"Gắn exercise {obj.exercise_type}:{obj.exercise_id} vào lesson {lesson_pk}")
        return Response(AdminLessonExerciseSerializer(obj).data, status=201)

class AdminLessonExerciseDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminLessonExerciseSerializer
    queryset = LessonExercise.objects.all()

# URLs:
# GET/POST  /admin-portal/lessons/<pk>/exercises/
# GET/PATCH/DELETE /admin-portal/lessons/<pk>/exercises/<lex_pk>/
# POST /admin-portal/lessons/<pk>/exercises/reorder/  → {"order": [id1, id2]}
```

**Serializer:**
```python
class AdminLessonExerciseSerializer(serializers.ModelSerializer):
    exercise_preview = serializers.SerializerMethodField()  # title của exercise
    class Meta:
        model = LessonExercise
        fields = ["id", "lesson", "exercise_type", "exercise_id", "order", "passing_score", "exercise_preview"]
    def get_exercise_preview(self, obj):
        model_map = {"listening": ListeningExercise, ...}
        try:
            return model_map[obj.exercise_type].objects.get(pk=obj.exercise_id).title
        except: return None
```

#### Frontend — luồng UI

Trong lesson detail panel (khi admin click vào lesson):
```
Section "Bài tập trong lesson":
  Danh sách exercises đã gắn: [icon loại] [title] [điểm qua] [thứ tự ▲▼] [X xóa]
  Button "+ Gắn bài tập" → Modal picker:
    Filter loại / search title
    Table exercises, click để chọn + nhập order + passing_score
    Save → POST /admin-portal/lessons/<pk>/exercises/
```

---

### 7.4 Grammar CRUD

#### Mục tiêu
Admin có thể quản lý toàn bộ nội dung grammar: topics, rules, examples.

#### Backend — việc cần làm

**Bước 1: Nâng cấp grammar views thành writeable**

```python
# apps/grammar/views.py — thêm:
from rest_framework import permissions
from .serializers import GrammarTopicAdminSerializer, GrammarRuleSerializer, GrammarExampleSerializer

class AdminGrammarTopicListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = GrammarTopicAdminSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        return GrammarTopic.objects.all().order_by("level__order", "order")

class AdminGrammarTopicDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GrammarTopicAdminSerializer
    permission_classes = [IsAdmin]
    queryset = GrammarTopic.objects.all()

class AdminGrammarRuleListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = GrammarRuleSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        return GrammarRule.objects.filter(topic_id=self.kwargs["topic_pk"])

class AdminGrammarRuleDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GrammarRuleSerializer
    permission_classes = [IsAdmin]
    queryset = GrammarRule.objects.all()

class AdminGrammarExampleListView(AuditLogMixin, generics.ListCreateAPIView):
    serializer_class = GrammarExampleSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        return GrammarExample.objects.filter(rule_id=self.kwargs["rule_pk"])

class AdminGrammarExampleDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GrammarExampleSerializer
    permission_classes = [IsAdmin]
    queryset = GrammarExample.objects.all()
```

**Bước 2: URLs cho admin grammar**

Có 2 lựa chọn:
- **Option A**: Thêm vào `admin_portal/urls.py` (recommended — consistent với pattern hiện tại)
- **Option B**: Thêm vào `grammar/urls.py` với permission IsAdmin

```python
# admin_portal/urls.py — thêm:
path("grammar/topics/",                          AdminGrammarTopicListView.as_view(), ...),
path("grammar/topics/<int:pk>/",                AdminGrammarTopicDetailView.as_view(), ...),
path("grammar/topics/<int:topic_pk>/rules/",    AdminGrammarRuleListView.as_view(), ...),
path("grammar/topics/<int:topic_pk>/rules/<int:pk>/", AdminGrammarRuleDetailView.as_view(), ...),
path("grammar/rules/<int:rule_pk>/examples/",   AdminGrammarExampleListView.as_view(), ...),
path("grammar/rules/<int:rule_pk>/examples/<int:pk>/", AdminGrammarExampleDetailView.as_view(), ...),
```

**Bước 3: Admin serializer với tất cả fields**

```python
class GrammarTopicAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarTopic
        fields = [
            "id", "title", "slug", "level", "order", "is_published",
            "icon", "description", "analogy", "real_world_use", "memory_hook", "lesson"
        ]

class GrammarRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarRule
        fields = ["id", "topic", "title", "formula", "explanation", "memory_hook", "is_exception", "order"]

class GrammarExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarExample
        fields = ["id", "rule", "sentence", "translation", "context", "highlight", "audio_url"]
```

#### Frontend — luồng UI

**Tab mới "Ngữ pháp" trong AdminContentView.vue:**

```
Layout 3 cột (tương tự content tree):
  Cột 1: Danh sách Topics
    [Level badge] Topic title [published/draft badge] [Edit] [Delete]
    Button "+ Thêm topic"
    
  Cột 2 (khi chọn topic): Danh sách Rules
    [is_exception badge] Rule title — formula preview
    Button "+ Thêm rule"
    
  Cột 3 (khi chọn rule): Danh sách Examples
    "sentence" — translation
    [audio badge nếu có audio_url]
    Button "+ Thêm example"
```

**Topic form:** title, slug (auto-generate), level (select), order, icon (emoji hoặc text), description, analogy, real_world_use, memory_hook, is_published, lesson (optional link)

**Rule form:** title, formula, explanation, memory_hook, is_exception (checkbox), order

**Example form:** sentence, translation, context, highlight, audio_url

---

## 8. Kế hoạch triển khai chi tiết — P1 (Quan trọng)

### 8.1 Prerequisite Enforcement trên Frontend ✅ DONE

> **✅ Hoàn thành — 29/03/2026**  
> Backend: `is_unlocked: bool` field thêm vào `LessonSerializer` — kiểm tra tất cả `UnlockRule` trong 1 query, dùng `LessonProgress.best_score`.  
> Frontend: `CourseDetailView.vue` dùng `lesson.is_unlocked !== false` làm điều kiện gate (không dùng `progress_status !== 'locked'` vì `progress_status` là `"locked"` cho tất cả bài chưa bắt đầu). Tooltip "Hoàn thành bài trước để mở khóa" khi hover.

#### Triển khai thực tế

**Backend — `curriculum/serializers.py`:**
```python
is_unlocked = serializers.SerializerMethodField()

def get_is_unlocked(self, obj):
    request = self.context.get("request")
    if not request or not request.user.is_authenticated:
        return False
    from apps.progress.models import LessonProgress
    rules = list(obj.unlock_rules.values("required_lesson_id", "min_score"))
    if not rules:
        return True
    passed_ids = set(
        LessonProgress.objects.filter(
            user=request.user,
            lesson_id__in=[r["required_lesson_id"] for r in rules],
        ).values_list("lesson_id", "best_score")
    )
    for rule in rules:
        req_id = rule["required_lesson_id"]
        min_sc = rule["min_score"]
        if not any(
            lid == req_id and (sc if sc is not None else 0) >= min_sc
            for lid, sc in passed_ids
        ):
            return False
    return True
```

**Frontend — `CourseDetailView.vue`:**
```vue
<!-- Lesson có thể học → RouterLink -->
<RouterLink v-if="lesson.is_unlocked !== false && lesson.exercise_id" ...>

<!-- Lesson bị khóa → div không click được -->
<div v-else :title="lessonLockTitle(lesson)" class="cursor-not-allowed opacity-40">
  ...🔒
</div>

function lessonLockTitle(lesson) {
  if (lesson.is_unlocked === false) return 'Hoàn thành bài trước để mở khóa'
  if (!lesson.exercise_id) return 'Chưa có bài tập'
  return 'Hoàn thành bài trước để mở khóa'
}
```

---

### 8.2 Grammar Mini-Quiz Persistence ✅ DONE

> **✅ Hoàn thành** — GrammarQuizResult model + migration 0003 applied. GrammarDetailView.vue POST kết quả sau khi nộp quiz và hiển thị lần thử trước nếu đã làm.

#### Luồng hiện tại (cũ)
```
GrammarDetailView → tạo 5 câu hỏi từ examples (client-side)
→ học viên làm quiz → kết quả chỉ hiển thị local, không lưu
```

#### Luồng cần có
```
Quiz hoàn thành → POST /api/v1/grammar/<slug>/quiz-result/
Backend lưu vào GrammarQuizResult (user, topic, score, attempted_at)
Frontend hiển thị "Đã hoàn thành: X/5 câu đúng" nếu đã làm trước đó
```

**Backend thêm:**
```python
# apps/grammar/models.py
class GrammarQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE)
    score = models.FloatField()  # 0-100
    attempted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user", "topic")  # chỉ lưu lần thử gần nhất (update nếu làm lại)
```

---

### 8.3 Grammar Audio Player ✅ DONE

> **✅ Hoàn thành** — Button 🔊 per example trong GrammarDetailView.vue, sử dụng `new Audio(url).play()` với icon toggle đang phát.

#### Việc cần làm đơn giản (cũ)

```vue
<!-- GrammarDetailView.vue — trong example item -->
<template v-if="example.audio_url">
  <button @click="playAudio(example.audio_url)" class="...">
    🔊
  </button>
</template>

<script setup>
function playAudio(url) {
  const audio = new Audio(url)
  audio.play()
}
</script>
```

---

### 8.4 Teacher Export Class CSV ✅ DONE

> **✅ Hoàn thành — 29/03/2026**  
> Backend: `TeacherExportClassView` → `GET /api/v1/teacher/classes/<pk>/export/` trả về CSV UTF-8-BOM (họ tên, email, tiến độ %, ngày đăng ký, trạng thái).  
> Frontend: Nút "📥 Xuất CSV" trong `TeacherClassView.vue`, download blob, filename = `class_<id>_students.csv`.  
> API: `teacherApi.exportClass(id)` trong `api/teacher.js`.

---

### 8.5 CSV Bulk Import — Vocabulary ✅ DONE (backend) / ⚠️ UI còn thiếu

> **✅ Backend hoàn thành — 29/03/2026**  
> `AdminVocabularyImportView` → `POST /admin-portal/vocabulary/import/`  
> - Validate mỗi row: bắt buộc `word`, `cefr_level` (A1-C2), `meaning_vi`  
> - `get_or_create` để tránh duplicate  
> - Return: `{created, duplicates, errors[]}` (tối đa 20 lỗi)  
> - UTF-8 decode error → 400 (không crash server)  
> API: `adminApi.importVocabulary(formData)` trong `api/admin.js`.
>
> **⚠️ Frontend UI chưa có:**  
> Chưa có upload dropzone/form trong `/admin/content`. Chỉ có API method.

---

## 9. Kế hoạch triển khai chi tiết — P2 (Nâng cấp UX)

### 9.1 Unlock Animations ✅ DONE (component) / ⚠️ chưa tích hợp

> **✅ Component hoàn thành — 29/03/2026**  
> **✅ Tích hợp ExerciseResultView — 31/03/2026**  
> `UnlockModal.vue` — `<Teleport to="body">` overlay với:
> - 🔓 animate-bounce icon
> - Hiển thị tên bài học (`lessonTitle` prop)
> - XP gained badge (`xpGained` prop)
> - Nút "Tiếp tục" + tự đóng sau 3s
> - Cleanup timer trong `onUnmounted` (không memory leak)
>
> Import và sử dụng trong `ExerciseResultView.vue`: sau khi `fetchResult()` thành công và kết quả có `next_lesson_id`, modal tự hiển thị với tên loại bài tập tiếp theo.  
>
> **Lưu ý kỹ thuật (31/03/2026):** Backend `ExerciseResultSerializer` đã được refactor để bổ sung `next_exercise_type` và `next_exercise_id` (cùng cache logic `_resolve_next_lesson`). `goNextLesson()` trong `ExerciseResultView` đã được **fix** — trước đó navigate sai tới `/courses/lesson/${id}` (route không tồn tại), nay dùng `router.push({ name: 'learn-${type}', params: { id }, query: { lesson_id } })`.

---

### 9.2 Skill Tree Visual Map ✅ DONE (component) / ⚠️ chưa tích hợp

> **✅ Component hoàn thành — 29/03/2026**  
> **✅ Tích hợp CourseDetailView — 31/03/2026**  
> `SkillTreeView.vue` — vertical tree layout với:
> - Chapter dividers (dashed line + label)
> - Lesson nodes: completed (xanh), available (tím viền), locked (mờ 50%)
> - Connector lines màu xanh nếu previous completed
> - Click navigate → `/learn/:type/:id` (dùng `RouterLink` khi `canNavigate()`)
> - Tooltip cho locked lessons
>
> Toggle **☰ Danh sách / 🌿 Skill Tree** trong header section "Nội dung khoá học" của `CourseDetailView.vue`.  
> Khi chuyển sang Skill Tree, tự động pre-load lessons của tất cả chapters chưa được fetch (`switchToTree()` dùng `Promise.all`).

---

### 9.3 Split-Pane Exercise Layout ✅ DONE

> **✅ Hoàn thành — 29/03/2026**  
> `ListeningView.vue` và `ReadingView.vue` đều có:
> - Toggle button `⊞ Split` (default ON — `splitMode = ref(true)`)
> - Khi ON: flex-row layout, audio/passage pane (60%), questions pane (40%)
> - Khi OFF: single column (original layout)

---

### 9.4 Writing Zen Mode ✅ DONE

> **✅ Đã có sẵn trong `WritingView.vue`** — không cần triển khai thêm:
> - Nút `☯ Zen mode` trong header bài viết
> - `<Teleport to="body">` fullscreen overlay với nền tối `#0a0a14`
> - Textarea full-width với font Georgia, word count real-time
> - Header/footer fade-in khi hover (opacity 30% → 100%)
> - Nộp bài từ trong Zen mode, thoát bằng Esc hoặc nút "← Thoát"

---

## Ghi chú kỹ thuật quan trọng

### Pattern thêm endpoint vào admin portal (chuẩn)

1. Tạo serializer trong `admin_portal/serializers.py` (hoặc app tương ứng)
2. Tạo view kế thừa `AuditLogMixin` + `generics.*` trong `admin_portal/views.py`
3. Import vào `admin_portal/urls.py` + thêm `path()`
4. Thêm endpoint vào `frontend/src/api/admin.js`
5. Tạo/cập nhật Vue component trong `frontend/src/views/admin/`

### Lưu ý với `development.py` (throttle)

Bất kỳ throttle scope mới nào trong `base.py` đều **phải được copy** vào `development.py` — settings `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` trong dev **override hoàn toàn** base, không merge.

### Migrations

Mỗi khi thêm model mới (GrammarQuizResult, SourceFile, ...):
```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

### S3 / Media upload

Các endpoint upload file dùng:
```python
parser_classes = [MultiPartParser, FormParser]
# File → request.FILES["file"]
# Upload lên S3 dùng existing boto3 helper (xem settings BASE_URL / S3 config)
```
