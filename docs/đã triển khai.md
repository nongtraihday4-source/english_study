# Nhật ký triển khai — English Study LMS

> Cập nhật: **28/03/2026**

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
