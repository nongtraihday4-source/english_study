# Nhật ký triển khai — English Study LMS

> Cập nhật: **29/03/2026**

---

## Phiên 1 — Public Support System

**Backend:**
- `apps/support/` — Models: `SupportTicket`, `TicketReply`
- API: tạo ticket (anonymous + auth), xem danh sách (staff), trả lời, đóng ticket
- Business hours SLA: T2-T7 08:00–17:00 (múi giờ VN), nghỉ lễ cố định
- Email notification khi ticket được trả lời (Celery task)

**Frontend:**
- `PublicSupportRequestView.vue` — form tạo ticket (public, không cần đăng nhập)
- `SupportTicketListView.vue` — danh sách ticket (staff/admin)
- `SupportTicketDetailView.vue` — chi tiết + thread trả lời
- Fix: thêm alias `getTicketDetail` vào API client

---

## Phiên 2 — Content Analysis

- Tạo `docs/chưa triển khai.md` — phân tích gap toàn bộ hệ thống vs PRD
- 20 item gap matrix với P0/P1/P2 priority
- Kế hoạch chi tiết cho P0 (Chapter CRUD, Lesson CRUD, Exercise CRUD, Grammar CRUD)

---

## Phiên 3 — Grammar Page Redesign + Quiz Persistence (P1 items)

### Backend — `apps/grammar/`

| Thay đổi | File | Ghi chú |
|---------|------|---------|
| Thêm field `chapter` vào `GrammarTopic` | `models.py` | CharField max_length=200, indexed. **Ngoài kế hoạch ban đầu** — cần thiết để hiển thị UI mới |
| Thêm `GrammarQuizResult` model | `models.py` | user+topic unique_together, field: score/total_questions/correct_answers/attempted_at |
| Thêm `chapter` vào serializers | `serializers.py` | GrammarTopicListSerializer + GrammarTopicDetailSerializer |
| Thêm `prev_topic` / `next_topic` vào detail serializer | `serializers.py` | Sibling lookup theo level+order. **Ngoài kế hoạch ban đầu** |
| `GrammarQuizResultSerializer` + `GrammarQuizSubmitSerializer` | `serializers.py` | |
| `GrammarQuizSubmitView` — POST `/grammar/<slug>/quiz/` | `views.py` | update_or_create, IsAuthenticated |
| `GrammarProgressView` — GET `/grammar/progress/` | `views.py` | trả về dict slug→score |
| Cập nhật URLs | `urls.py` | Thêm `progress/` + `<slug>/quiz/` routes |
| Migration `0003` | `migrations/` | Applied ✅ |

**Tương đương với kế hoạch:** §8.2 (Grammar mini-quiz persistence) ✅

### Frontend — Grammar

| Thay đổi | File | Ghi chú |
|---------|------|---------|
| `grammarApi.getProgress()` + `grammarApi.submitQuiz()` | `api/curriculum.js` | |
| **Redesign GrammarView.vue** — learning path card grid | `views/GrammarView.vue` | Chapter-based grouping (data-driven), quiz score badges + progress bar per topic card |
| **Redesign GrammarDetailView.vue** — 4-section flow | `views/GrammarDetailView.vue` | Hook → Formula (stepper rules) → Practice (3 quiz types) → Real World |
| Audio player per example | `GrammarDetailView.vue` | §8.3 (Grammar audio player) ✅ |
| Prev/Next navigation top + bottom | `GrammarDetailView.vue` | Dùng `prev_topic`/`next_topic` từ API |
| Auto-save quiz khi hoàn thành | `GrammarDetailView.vue` | POST `/grammar/<slug>/quiz/` |
| Route watcher (re-fetch khi slug đổi) | `GrammarDetailView.vue` | Không cần reload trang |

**Tương đương với kế hoạch:** §8.2 + §8.3 ✅, plus UX enhancements ngoài kế hoạch

---

## Tác động đến kế hoạch `chưa triển khai.md`

### Items đã hoàn thành
- **§8.2** P1 — Grammar mini-quiz persistence ✅
- **§8.3** P1 — Grammar audio player ✅

### Thay đổi ảnh hưởng đến kế hoạch P0

**§7.4 — Grammar CRUD admin (P0):**

Field mới `chapter` đã được thêm vào `GrammarTopic` model. Kế hoạch `GrammarTopicAdminSerializer` trong §7.4 cần bổ sung:
```python
# PHẢI thêm vào GrammarTopicAdminSerializer:
fields = ["id", "title", "slug", "level", "chapter", "order", "is_published", ...]
#                                           ↑ NEW
```
→ Admin UI cần có field `chapter` khi tạo/sửa topic (nhập tên chương, VD: "Thì cơ bản", "Modal Verbs").

**GrammarView.vue mới cần chapter được populate:**
Trang `/grammar` sau khi redesign hiển thị topics theo `chapter` field. Nếu `chapter = ""` (blank), tất cả topics của level sẽ hiện vào nhóm "Chưa phân chương". Admin cần nhập đúng chapter khi tạo topic.

**GrammarDetailView.vue mới có prev/next:**
`prev_topic`/`next_topic` được tính dựa theo `order` field trong cùng level. Admin cần chú ý nhập `order` đúng khi tạo topics.

### Items chưa thay đổi (giữ nguyên kế hoạch)
- §7.1 — Chapter + Lesson CRUD: chưa triển khai, kế hoạch không đổi
- §7.2 — Exercise CRUD: chưa triển khai, kế hoạch không đổi
- §7.3 — Exercise → Lesson binding: chưa triển khai, kế hoạch không đổi
- §8.1 — Prerequisite enforcement: chưa triển khai
- §8.4 — Teacher export CSV: chưa triển khai
- §8.5 — CSV bulk import vocabulary: chưa triển khai
- §9.x — P2 UX: chưa triển khai

---

## Phiên 4 — P1/P2 Implementation (29/03/2026)

### §8.1 — Prerequisite Enforcement

**Backend — `apps/curriculum/serializers.py`:**

| Thay đổi | Chi tiết |
|---------|---------|
| Thêm `is_unlocked` field vào `LessonSerializer` | `SerializerMethodField` — 1 query dùng `values_list("lesson_id", "best_score")`, check tất cả `UnlockRule` |
| Fix: `None` score treated as 0 | `(sc if sc is not None else 0) >= min_sc` — không crash khi `best_score=NULL` |

**Frontend — `frontend/src/views/CourseDetailView.vue`:**

| Thay đổi | Chi tiết |
|---------|---------|
| Điều kiện lesson clickable | Đổi từ `progress_status !== 'locked'` → `lesson.is_unlocked !== false` (fix bug: `progress_status='locked'` cho mọi bài chưa bắt đầu) |
| Tooltip locked lessons | Hàm `lessonLockTitle(lesson)` — tránh inline ternary lồng nhau |

---

### §8.4 — Teacher Export Class CSV

**Backend — `apps/teacher/views.py`:**

| Thay đổi | Chi tiết |
|---------|---------|
| Thêm `TeacherExportClassView` | `GET /api/v1/teacher/classes/<pk>/export/` → CSV UTF-8-BOM (họ tên, email, tiến độ %, ngày đăng ký, trạng thái) |
| Import `csv`, `io`, `HttpResponse` | Thêm vào imports |

**Backend — `apps/teacher/urls.py`:**
```python
path("classes/<int:pk>/export/", TeacherExportClassView.as_view(), name="teacher-class-export"),
```

**Frontend — `frontend/src/api/teacher.js`:**
```js
exportClass: (id) => api.get(`/teacher/classes/${id}/export/`, { responseType: 'blob' }),
```

**Frontend — `frontend/src/views/teacher/TeacherClassView.vue`:**
- Nút "📥 Xuất CSV" (disabled khi đang tải)
- `exportCsv()` → blob download với `URL.createObjectURL`

---

### §8.5 — CSV Bulk Import Vocabulary + Vocabulary Admin CRUD (P2 item #20)

**Backend — `apps/admin_portal/views.py`:**

| Class | Endpoint | Chức năng |
|-------|----------|-----------|
| `AdminVocabularyListView` | `GET/POST /admin-portal/vocabulary/` | List + Create, filterable by `cefr_level` + `search` |
| `AdminVocabularyDetailView` | `GET/PATCH/DELETE /admin-portal/vocabulary/<pk>/` | Detail CRUD |
| `AdminVocabularyImportView` | `POST /admin-portal/vocabulary/import/` | Bulk import từ CSV, validate row-by-row, return `{created, duplicates, errors[]}` |

**Backend — `apps/admin_portal/urls.py`:** URL ordering `vocabulary/` → `vocabulary/import/` → `vocabulary/<pk>/` để tránh routing conflict.

**Frontend — `frontend/src/api/admin.js`:**
```js
getVocabulary: (params = {}) => api.get('/admin-portal/vocabulary/', { params }),
createWord: (data) => api.post('/admin-portal/vocabulary/', data),
updateWord: (pk, data) => api.patch(`/admin-portal/vocabulary/${pk}/`, data),
deleteWord: (pk) => api.delete(`/admin-portal/vocabulary/${pk}/`),
importVocabulary: (formData) => api.post('/admin-portal/vocabulary/import/', formData),
```

---

### §9.1 — Unlock Modal Component

**Frontend — `frontend/src/components/UnlockModal.vue` (NEW):**
- `<Teleport to="body">` overlay + `<Transition>` fade+scale
- Props: `show`, `lessonTitle`, `xpGained`
- Auto-dismiss sau 3s với cleanup `clearTimeout` trong `onUnmounted`
- Emit `close` khi click overlay, nút, hoặc timeout

---

### §9.2 — Skill Tree View Component

**Frontend — `frontend/src/components/SkillTreeView.vue` (NEW):**
- Props: `chapters` (array từ CourseDetailView)
- Vertical tree: chapter dividers → lesson nodes + connector lines
- Node states: completed (xanh, RouterLink), available (tím, RouterLink), locked (mờ, div)
- `canNavigate()` dùng `is_unlocked` + `exercise_id`
- Chưa tích hợp vào CourseDetailView.vue (component ready, cần thêm tab/toggle)

---

### §9.3 — Split-Pane Toggle (Listening + Reading)

**Frontend — `ListeningView.vue` + `ReadingView.vue`:**
- `const splitMode = ref(true)` — mặc định ON
- Toggle button `⊞ Split` trong header exercise
- Conditional CSS class thay đổi layout giữa single-column và 60/40 flex-row

---

### §9.4 — Writing Zen Mode

Đã có sẵn trong `WritingView.vue` (không thay đổi).  
`isZenMode`, `enterZen()`/`exitZen()`, `<Teleport to="body">` overlay đã implemented.

---

## Tác động đến kế hoạch `chưa triển khai.md`

### Items đã hoàn thành trong Phiên 4

| Item | Status |
|------|--------|
| **§8.1** P1 — Prerequisite enforcement | ✅ DONE (backend + frontend) |
| **§8.4** P1 — Teacher export class CSV | ✅ DONE (backend + frontend) |
| **§8.5** P1 — CSV bulk import vocabulary | ✅ DONE (backend); ⚠️ UI còn thiếu |
| **#20** P2 — Vocabulary CRUD admin | ✅ DONE (backend + API client); ⚠️ UI còn thiếu |
| **§9.1** P2 — Unlock animation modal | ✅ DONE (component); ⚠️ chưa trigger |
| **§9.2** P2 — Skill tree component | ✅ DONE (component); ⚠️ chưa tích hợp |
| **§9.3** P2 — Split-pane layout | ✅ DONE (Listening + Reading) |
| **§9.4** P2 — Writing Zen Mode | ✅ DONE (đã có sẵn) |

### Items còn lại (chưa triển khai)

| Item | Mức độ | Ghi chú |
|------|--------|---------|
| **#3, #4** Exercise CRUD + Binding UI | ⚠️ | Backend DONE, frontend chỉ có API — chưa có UI form trong admin |
| **#6** Question CRUD standalone | 🟡 P1 | Question chỉ nested trong ExamSet |
| **#10** Progress Check sau chapter | 🟡 P1 | Chưa có backend logic lẫn frontend |
| **#11** Source file upload S3 | 🟡 P1 | Chưa có model SourceFile |
| **#12** CSV import UI | ⚠️ | Backend DONE, chưa có UI upload form |
| **#13** Teacher tạo exam + giao bài | 🟡 P1 | Chưa có |
| **#15** Skill Tree tích hợp | ⚠️ | Component DONE, chưa integrate vào CourseDetailView |
| **#16** Unlock Modal trigger | ⚠️ | Component DONE, chưa trigger khi nộp bài |
| **#18** Speaking dialogue UI | 🟢 P2 | Chưa có |
| **#20** Vocabulary CRUD UI | ⚠️ | Backend DONE, chưa có tab trong admin UI |
