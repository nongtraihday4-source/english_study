# 🗺️ CURRICULUM FRONTEND, AI & TEACHER IMPROVEMENT ROADMAP
**Project:** English Study LMS | **Stack:** Django + DRF, Vue 3 `<script setup>`, Pinia, Tailwind, Vite | **AI Core:** `Qwen3.5-9B-Q4_K_M.gguf` | **Timezone:** `Asia/Ho_Chi_Minh` | **Format:** `vi-VN`

## ✅ PHASE CHECKLIST
- [ ] **1. Frontend Integration & SSOT Contract:** `learning_objectives` render, `raw_answers` payload migration, Pinia `useSRSStore`
- [ ] **2. AI Deployment & Async Pipeline:** Qwen3.5-9B serving, Celery + Redis infra, `AIGradingLog` monitoring
- [ ] **3. Teacher Portal & Analytics:** Override UI/API, Stuck-points heatmap, audit trail
- [ ] **4. Final E2E Audit & Architectural Sign-off**

---

## 🎨 1. FRONTEND INTEGRATION & BACKEND SSOT

### 1.1 Render `learning_objectives` in `LessonDetailView.vue`
- **Tại sao thay đổi:** Người học A1/A2 dễ quá tải khi vào bài dài. Hiển thị mục tiêu đầu bài giảm cognitive load, định hướng rõ "học xong làm được gì".
- **Rủi ro nếu giữ nguyên:** Bounce rate cao, người học mất phương hướng, giảm completion rate.
- **Kỹ thuật triển khai:**
  - Đọc từ `content.learning_objectives` (JSON array đã thêm ở Phase 4 Backend).
  - Render dưới dạng bullet list hoặc chips ngay dưới lesson header.
  - Fallback: Ẩn section nếu mảng rỗng hoặc `null`. Không crash UI.
  - File thay đổi: `frontend/src/views/LessonDetailView.vue`
- **TDD/Verify:** 
  - Mock API response chứa `learning_objectives: ["Hiểu thì hiện tại đơn", "Học 10 từ vựng"]`
  - Verify DOM render đúng số lượng item, không crash khi `null`/`[]`.
  - E2E: Navigate lesson → objectives hiển thị → scroll xuống content không bị shift layout.

### 1.2 Migrate to Backend SSOT Payload (`raw_answers`)
- **Tại sao thay đổi:** Client-side `autoScore` drift khỏi backend truth. AI grading cần raw data để chấm định tính. Backend phải là Single Source of Truth.
- **Rủi ro nếu giữ nguyên:** Điểm số không đồng nhất, học sinh có thể manipulate payload, AI grading không thể override chính xác, phá vỡ contract Phase 2.
- **Kỹ thuật triển khai:**
  - Thay đổi payload `markLessonComplete` từ `{score: autoScore}` → `{raw_answers: {...}, time_spent_seconds: number}`
  - `raw_answers` structure khớp contract `ScoringService`:
    ```json
    {
      "reading": [0, 1, 0],
      "grammar": {"Present Simple": [0, 1], "Past Simple": [1]},
      "listening": [0, 1, 1],
      "speaking": {"done": 3, "total": 4},
      "writing": [{"exercise_index": 0, "text": "I go to school."}]
    }
    ```
  - Giữ `autoScore` chỉ để hiển thị progress bar UI, không gửi lên backend.
  - Backend `progress` app gọi `ScoringService.calculate_lesson_score()` → trả về `best_score`, `xp_gained`, `status`.
  - File thay đổi: `frontend/src/views/LessonDetailView.vue`, `frontend/src/api/progress.js`
- **TDD/Verify:**
  - Integration test: Submit payload → verify backend response `score` khớp rubric → verify frontend cập nhật UI từ response, không tự gán score.
  - Network tab audit: Payload không chứa `score`, chỉ chứa `raw_answers` & `time_spent_seconds`.

### 1.3 Pinia `useSRSStore` & Queue UI Integration
- **Tại sao thay đổi:** Từ vựng học xong không ôn → quên nhanh. Model có `srs_review_count` nhưng frontend chưa hiển thị queue.
- **Rủi ro nếu giữ nguyên:** Giảm hiệu quả ghi nhớ dài hạn, SRS logic backend thành vô dụng.
- **Kỹ thuật triển khai:**
  - Tạo `frontend/src/stores/srs.js` dùng `defineStore`
  - Actions: `fetchQueue()`, `markReviewed(cardId, quality)`, `calculateNextInterval()`
  - Component `SRSQueueWidget.vue` render trong `DashboardView` hoặc header `LessonDetailView`
  - Debounce auto-save progress per micro-step (nếu áp dụng)
  - Lazy load queue, không block lesson start.
- **TDD/Verify:**
  - Mock API `/vocabulary/srs/queue/` → verify store state update
  - Test mark reviewed → verify interval calculation & UI refresh
  - E2E: Navigate lesson → widget hiển thị queue → complete review → queue trống, không block navigation.

---

## 🤖 2. AI DEPLOYMENT & ASYNC PIPELINE

### 2.1 Local/Prod Model Serving (Qwen3.5-9B GGUF)
- **Tại sao thay đổi:** Cần AI chấm Speaking/Writing định tính, generate feedback, validate content. Qwen3.5-9B mạnh đa ngôn ngữ, tối ưu VRAM/CPU.
- **Rủi ro nếu giữ nguyên:** Self-rating chủ quan, writing chỉ đếm từ → học sai không biết sai, hiệu suất học tập thấp.
- **Kỹ thuật triển khai:**
  - **Dev:** `ollama run hf.co/unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL` hoặc `llama-cpp-python` load local GGUF.
  - **Prod:** Ollama systemd service hoặc Docker container behind Nginx reverse proxy. Health check: `GET /api/health`
  - Cấu hình `settings.py`:
    ```python
    AI_BASE_URL = "http://localhost:11434/v1"
    AI_MODEL = "qwen3.5-9b"
    AI_GRADING_TIMEOUT = 15
    ```
  - Wrapper `qwen_client.py` đã có: retry, timeout, JSON mode enforcement, circuit breaker.
- **TDD/Verify:**
  - `curl http://localhost:11434/v1/models` → trả về model list
  - Test `qwen_client.py` init & JSON mode response → parse success
  - Load test local: 10 concurrent prompts → latency ≤3s, no OOM.

### 2.2 Celery + Redis Async Grading Infrastructure
- **Tại sao thay đổi:** Sync AI calls block request cycle, gây timeout, trải nghiệm kém.
- **Rủi ro nếu giữ nguyên:** Request cycle treo, DRF timeout 504, worker crash under load.
- **Kỹ thuật triển khai:**
  - Broker/Backend: Redis `redis://localhost:6379/0` (đã config trong `base.py`)
  - Dedicated queue cho AI: `CELERY_TASK_ROUTES = {"apps.ai.tasks.*": {"queue": "ai_grading"}}`
  - Worker command: `celery -A english_study worker -l info -Q ai_grading -c 2`
  - Task config: `max_retries=3`, `soft_time_limit=30`, `time_limit=45`, exponential backoff
  - Circuit breaker: Nếu 5 tasks fail liên tiếp → pause queue, notify admin, fallback toàn bộ sang heuristic
- **TDD/Verify:**
  - Test task routing → verify job vào queue `ai_grading`
  - Test timeout → verify retry & fallback trigger
  - Load test 50 concurrent submissions → queue stable, no memory leak, fallback triggers correctly.

### 2.3 Monitoring & Prompt Tuning via `AIGradingLog`
- **Tại sao thay đổi:** Cần theo dõi latency, fallback rate, score distribution để tune prompt & thresholds.
- **Rủi ro nếu giữ nguyên:** Prompt hallucination không bị phát hiện, fallback rate cao làm giảm chất lượng chấm, log table bloat.
- **Kỹ thuật triển khai:**
  - Model `AIGradingLog` đã có. Thêm Django Admin view hoặc API `/ai/logs/`
  - Metrics track: `latency_ms`, `status` (success/fallback/error), `score`, `prompt_hash`, `model_version`
  - Alert rule: Nếu `fallback_rate > 20%` trong 1 giờ → notify teacher/admin
  - Prompt versioning: Lưu `prompt_version` trong log để A/B test rubric
  - Partition log table theo tháng hoặc archive log >90 ngày để tránh bloat.
- **TDD/Verify:**
  - Test log creation on success/fallback
  - Verify aggregation query zero N+1 (`assertNumQueries`)
  - Dashboard render đúng metrics, filter theo date/status.

---

## 🎓 3. TEACHER PORTAL & ANALYTICS

### 3.1 Teacher Override UI & API Integration
- **Tại sao thay đổi:** AI/heuristic không hoàn hảo. Giáo viên cần can thiệp sư phạm, mở khóa thủ công, ghi chú.
- **Rủi ro nếu giữ nguyên:** Progress cứng nhắc, học sinh bị kẹt do AI fail, giáo viên mất quyền kiểm soát lớp học.
- **Kỹ thuật triển khai:**
  - Endpoint: `POST /api/v1/teacher/override-progress/`
  - Payload: `{student_id, lesson_id, status, score, note}`
  - Backend: `TeacherService.override_lesson_progress()` kiểm tra permission `IsTeacherOrAdmin`, update `LessonProgress`, ghi audit log
  - Frontend: `TeacherGradingView.vue` form override, toast feedback, real-time sync
  - Strict audit trail: Không cho phép xóa override, chỉ append history.
- **TDD/Verify:**
  - Test permission deny student/admin
  - Test override → verify `LessonProgress` update, audit log created
  - Frontend form submit → verify toast & state sync, không reload page.

### 3.2 Stuck Points Heatmap & Analytics Dashboard
- **Tại sao thay đổi:** Xác định bài học gây khó khăn, avg score thấp, nhiều attempts để điều chỉnh nội dung.
- **Rủi ro nếu giữ nguyên:** Content khó không được phát hiện, học sinh bỏ dở, giáo viên không có data để can thiệp.
- **Kỹ thuật triển khai:**
  - Endpoint: `GET /api/v1/teacher/analytics/stuck-points/?course_id=X`
  - Backend: `TeacherService.get_stuck_points()` dùng `annotate(Avg, Count, Min)` → zero N+1
  - Response: `[{lesson_id, title, avg_score, attempts, stuck_rate}]`
  - Frontend: CSS grid heatmap hoặc lightweight chart (Tailwind + SVG). Color scale: 🔴 <50% → 🟡 50-70% → 🟢 >70%
  - Filter: theo chapter, date range, CEFR level. Cache aggregation nếu >10k records.
- **TDD/Verify:**
  - Test aggregation query `assertNumQueries(≤3)`
  - Verify heatmap render đúng color scale, tooltip hiển thị chi tiết
  - Filter change → data update không reload page, latency ≤200ms.

---

## ⚙️ 4. ARCHITECTURAL REVIEW & GUARDRAILS

### 🔍 Review kế hoạch sắp tới & Đảm bảo đi đúng hướng
| Nguyên tắc | Áp dụng thực tế | Cơ chế kiểm chứng |
|------------|----------------|-------------------|
| **Backend SSOT** | Frontend chỉ gửi `raw_answers`, không gửi `score` | Integration test score match backend rubric, Network audit |
| **Async AI Only** | Celery queue `ai_grading`, không sync call trong request | Test task routing, timeout fallback, circuit breaker |
| **Zero N+1** | Analytics/override endpoints dùng `annotate`/`Prefetch` | `assertNumQueries(≤3)` cho mọi list/detail, CI fail nếu vượt |
| **TDD-First** | Test skeleton → Fail → Implement → Pass | Không code khi chưa có test, coverage ≥80% cho logic mới |
| **Surgical Changes** | Chỉ touch file liên quan, không refactor lan man | Git diff review, không format code cũ, không đổi structure |
| **Temporal ICT** | Tất cả timestamp log/analytics dùng `Asia/Ho_Chi_Minh` | Test boundary 23:59 ICT → đúng ngày, streak không reset sai |
| **AI Safety** | Prompt fixed, JSON enforced, input sanitized, fallback manual | Test injection, blank, short, toxic → reject/fallback an toàn |

### ⚖️ First Principles & Tradeoffs
- **Client vs Server Scoring:** Client chỉ tracking UI state. Backend là nguồn chân lý duy nhất cho `best_score`, `xp_gained`, `status`. Tránh drift khi tích hợp AI.
- **Sync vs Async AI Grading:** AI chấm Speaking/Writing không thể sync (timeout risk). Thiết kế async + polling/WebSocket + fallback manual. Không block UX.
- **JSON Flexibility vs Schema Safety:** JSONField tiện nhưng nguy hiểm nếu không validate. Pydantic/JSONSchema là bắt buộc trước khi scale content.
- **Pedagogy First:** Tech phục vụ sư phạm. Micro-steps, objectives, SRS, teacher override ưu tiên hơn feature cosmetic. AI hỗ trợ, không thay thế giáo viên.

### 🚨 Blind Spots cần tránh
1. **Payload Drift:** Frontend vô tình gửi lại `score` trong `raw_answers` → Backend reject hoặc ghi đè sai. Fix: Strict TypeScript/JSDoc contract + backend validator.
2. **Queue Backlog:** Celery worker không scale kịp → grading delay >5 phút. Fix: Monitor queue depth, auto-scale worker, fallback heuristic nếu delay >2 phút.
3. **Heatmap N+1:** Analytics endpoint join nhiều bảng không optimize → timeout. Fix: `annotate` single query, materialized view nếu data >50k rows.
4. **Timezone Leak:** Frontend hiển thị timestamp UTC thay vì ICT → người học nhầm ngày streak. Fix: `fmt_vn` formatter áp dụng ở mọi API response, frontend không tự parse ISO string.

---

## 📅 IMPLEMENTATION SEQUENCE & NEXT ACTIONS

| Step | Module | Action | Verify |
|------|--------|--------|--------|
| **1** | Frontend Payload & Objectives | Đổi `markLessonComplete` payload → render `learning_objectives` | E2E submit raw → backend score đúng, UI hiển thị objectives |
| **2** | Celery/Redis & AI Task | Config queue `ai_grading` → wire `grade_submission_task` | Task routing đúng, retry/fallback hoạt động, log created |
| **3** | Teacher Override API/UI | POST override endpoint → connect `TeacherGradingView.vue` | Permission check pass, progress update, audit log |
| **4** | Analytics Heatmap & SRS | `get_stuck_points` aggregation → `useSRSStore` + widget | Zero N+1 query, heatmap render đúng, SRS queue sync |
| **5** | Final Audit & Sign-off | Cross-check SSOT, async, timezone, N+1, TDD coverage | CI green, latency ≤200ms, fallback ≤10%, docs updated |

---

## 📥 NEXT ACTION
Chọn module ưu tiên để tôi xuất **test skeleton → service/component code → verify script** đúng rule TDD, surgical, zero guesswork:
1. **Frontend Payload Migration + `learning_objectives` render** (Unblock backend scoring SSOT)
2. **Celery/Redis Queue Config + AI Task Wiring** (Unblock async grading pipeline)
3. **Teacher Override API + `TeacherGradingView.vue` integration** (Enable manual intervention)
4. **Analytics Heatmap Endpoint + `useSRSStore` Pinia** (Enhance pedagogy & retention)

Reply số module. Tôi sẽ generate code & test files chính xác, không thừa, không đoán. TDD-first. Surgical only.