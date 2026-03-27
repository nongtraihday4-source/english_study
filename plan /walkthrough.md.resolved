# 🔍 Phân Tích Agent Configuration cho English Study

## Tổng quan

Dự án `english_study` là một LMS (Learning Management System) học tiếng Anh từ A1-C1, sử dụng **Django + DRF** (backend), **Vue 3 + Vite** (frontend), và tích hợp **AI grading** (OpenAI GPT-4o + Whisper).

Thư mục `.agent/` hiện tại chứa:
- **2 rules**: `rule-instructions.md`, `vue3-frontend.md`
- **6 skills**: `daily-lottery-ops`, `frontend-design`, `instrument-data-to-allotrope`, `knowledge-synthesis`, `lottery-data-analysis`, `skill-creator`
- **1 workflow**: `analyze-code.md`

---

## ❌ Vấn đề nghiêm trọng: Skills không liên quan

> [!CAUTION]
> **4/6 skills hoàn toàn không liên quan đến project English Study** — chúng được copy từ dự án xổ số cũ hoặc là skill mẫu mặc định.

### Skills cần XÓA ngay

| Skill | Lý do xóa |
|-------|-----------|
| `daily-lottery-ops` | 100% dành cho xổ số (crawl, train MLP, predict) — không liên quan |
| `lottery-data-analysis` | Backtest pattern xổ số, Data Leakage check — không liên quan |
| `instrument-data-to-allotrope` | Chuyển đổi dữ liệu phòng thí nghiệm sang Allotrope format — skill mẫu, không liên quan |
| `knowledge-synthesis` | Tổng hợp kết quả tìm kiếm enterprise — skill chung, không đặc thù cho project |

### Skills GIỮ LẠI (có điều kiện)

| Skill | Đánh giá |
|-------|----------|
| `frontend-design` | ✅ **Giữ**, nhưng cần điều chỉnh: skill nói "Avoid generic fonts like Inter" trong khi PRD yêu cầu Glassmorphism + off-white — cần align với Art Direction của PRD |
| `skill-creator` | ✅ **Giữ**, hữu ích khi cần tạo skill mới cho project |

---

## ⚠️ Rules — Phân tích chi tiết

### 1. `rule-instructions.md` — Cần CẬP NHẬT

> [!WARNING]
> Rule này chứa nội dung **đặc thù xổ số** không phù hợp với English Study.

**Vấn đề cụ thể:**

```diff
- Temporal Consistency: Đặc thù xổ số: Kiểm tra lỗi rò rỉ dữ liệu tương lai (Data Leakage) trong các module ML và Calculation.
+ Temporal Consistency: Kiểm tra tính nhất quán thời gian trong unlock logic (bài học chỉ mở khóa sau khi đạt điểm chuẩn) và AI grading pipeline.

- Backtesting: Các phương pháp soi cầu phải có bài test trên dữ liệu lịch sử ít nhất 30 ngày gần nhất.
+ AI Grading Validation: Các prompt chấm điểm AI (Speaking/Writing) phải được kiểm thử với ít nhất 10 bài mẫu đã chấm tay để đối chiếu độ chính xác.

- Component-based: CSS phải dùng Variables (:root), JavaScript phải viết theo Class-based Modular (VD: PredictionManager).
+ Component-based: CSS phải dùng Variables (:root) hoặc Tailwind tokens, JavaScript phải viết theo Composition API modular (VD: useExercise, useSpeaking composables).
```

**Các điểm tốt cần giữ:**
- ✅ Clean Architecture: Models → Services → Views → Templates/DTOs
- ✅ Service Layer với Transaction & DTO
- ✅ N+1 query prevention
- ✅ TDD Workflow
- ✅ Code Review process (SOLID, DRY)

### 2. `vue3-frontend.md` — Cần CẬP NHẬT

> [!IMPORTANT]
> Rule ghi "KHÔNG SỬ DỤNG TypeScript" nhưng project đang dùng **TailwindCSS** (đã cài trong `package.json`). Rule cũng ghi "Bootstrap 5" trong `rule-instructions.md`, tạo mâu thuẫn.

**Vấn đề:**

| Mâu thuẫn | Trong rule | Trong thực tế |
|-----------|-----------|---------------|
| CSS Framework | `rule-instructions.md` nói "Bootstrap 5" | `package.json` cài TailwindCSS 3.4.3 |
| State Management | Rule chỉ nói `ref`/`reactive` | Project đã dùng **Pinia** (`pinia: ^2.1.7`) |
| Routing | Không đề cập | Project dùng **vue-router** 4 |
| Charts | Không đề cập | Project dùng **chart.js** + **vue-chartjs** cho Radar Chart |

**Cần bổ sung:**
- Quy tắc sử dụng Pinia stores (naming convention, structure)
- Quy tắc API calls (axios interceptors, error handling)
- Quy tắc composables (`use*.js` naming)
- Đề cập TailwindCSS thay vì Bootstrap 5

---

## ⚠️ Workflow — Thiếu nghiêm trọng

### Workflow hiện có: `analyze-code.md`

> [!WARNING]
> Workflow này cũng chứa ngôn ngữ chung chung, không có bước cụ thể cho English Study project. Thiếu hoàn toàn các workflow phát triển cốt lõi.

### Workflows cần BỔ SUNG

| Workflow | Mô tả | Ưu tiên |
|----------|--------|---------|
| `dev-server.md` | Chạy đồng thời backend Django + frontend Vite | 🔴 Cao |
| `run-tests.md` | Chạy test Django + Vue (pytest, vitest) | 🔴 Cao |
| `create-django-app.md` | Tạo app mới trong `backend/apps/` đúng chuẩn Service Layer | 🟡 Trung bình |
| `create-vue-component.md` | Tạo component Vue 3 đúng chuẩn Composition API | 🟡 Trung bình |
| `deploy.md` | Deploy production (build frontend, collectstatic, migrate) | 🟡 Trung bình |
| `import-vocabulary.md` | Import CSV từ vựng Oxford 3000/5000 vào database | 🟡 Trung bình |

---

## ⚠️ File rác tại project root

> [!WARNING]
> Vi phạm Rule #2 "Root Cleanup" — có nhiều file rác tại thư mục gốc.

| File | Đề xuất |
|------|---------|
| `simulate_pronunciation_flow.py` | → Di chuyển vào `scripts/` |
| `simulate_student_flow.py` | → Di chuyển vào `scripts/` |
| `tìm và nạp từ điển.md` | → Di chuyển vào `docs/` |
| `prompts_english_study.md` | → Di chuyển vào `docs/` |
| `backend_backup_20260324_161822/` | → Xóa (đã có Git) |
| `old_system/` | → Xóa hoặc archive |

---

## ✅ Đề xuất bổ sung — Skills mới cho English Study

### Skill 1: `english-lms-development` (Ưu tiên 🔴 Cao)

```
Mục đích: Hướng dẫn phát triển LMS với cấu trúc 5 cấp 
(Level → Course → Chapter → Lesson → Exercise)
Nội dung:
- Database schema conventions (unlock logic, scoring)
- Service layer patterns cho exercise submission
- DTO format cho API responses
- Scoring rules (MC, Gap Fill, Drag & Drop)
```

### Skill 2: `ai-grading-integration` (Ưu tiên 🔴 Cao)

```
Mục đích: Tích hợp AI chấm điểm Speaking/Writing
Nội dung:
- Whisper API integration patterns
- GPT-4o prompt templates cho Speaking/Writing rubric
- Celery async task patterns
- Error handling khi AI API fails
- Response format (score + error_list)
```

### Skill 3: `vue3-exercise-components` (Ưu tiên 🟡 Trung bình)

```
Mục đích: Patterns cho các component bài tập tương tác
Nội dung:
- Split Pane layout (6:4 ratio)
- Audio waveform recorder component
- Karaoke text highlight
- Drag & Drop exercise patterns
- Zen Mode writing editor
```

---

## 📋 Tóm tắt hành động cần thực hiện

| # | Hành động | Loại | Ưu tiên |
|---|-----------|------|---------|
| 1 | Xóa 4 skills không liên quan (lottery × 2, allotrope, knowledge-synthesis) | Xóa | 🔴 |
| 2 | Cập nhật `rule-instructions.md` — loại bỏ nội dung xổ số, thêm context English Study | Sửa | 🔴 |
| 3 | Cập nhật `vue3-frontend.md` — align với thực tế (Tailwind, Pinia, composables) | Sửa | 🔴 |
| 4 | Thêm workflow `dev-server.md` | Tạo mới | 🔴 |
| 5 | Thêm workflow `run-tests.md` | Tạo mới | 🔴 |
| 6 | Cập nhật workflow `analyze-code.md` — thêm bước cụ thể cho English Study | Sửa | 🟡 |
| 7 | Tạo skill `english-lms-development` | Tạo mới | 🟡 |
| 8 | Tạo skill `ai-grading-integration` | Tạo mới | 🟡 |
| 9 | Di chuyển file rác khỏi root | Dọn dẹp | 🟡 |
| 10 | Thêm rule Django REST API conventions | Tạo mới | 🟡 |

---

> [!IMPORTANT]
> **Cần feedback của bạn:**
> 1. Bạn muốn tôi thực hiện tất cả các hành động trên, hay chỉ ưu tiên 🔴 trước?
> 2. Frontend đang dùng TailwindCSS — bạn muốn giữ Tailwind hay chuyển sang Bootstrap 5 như PRD ban đầu?
> 3. Có muốn tôi tạo thêm workflow cho import dữ liệu từ vựng CSV không?
