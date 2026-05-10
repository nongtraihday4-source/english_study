🗺️ CURRICULUM IMPROVEMENT ROADMAP (v2)
Project: English Study LMS | Stack: Django + DRF, Vue 3, Pinia, Tailwind | Timezone: Asia/Ho_Chi_Minh | Format: vi-VN | AI Core: Qwen3.5-9B-Q4_K_M.gguf
## ✅ PHASE CHECKLIST (COMPLETED)
- [x] **Phase 1:** Core Stability & Architecture (URL fix, Service Layer, Zero N+1)
  - [x] 1.1 Fix `urls.py` markdown artifact → DRF `<int:>` syntax
  - [x] 1.2 Create `services/unlock_service.py` & `progress_service.py` + TDD unit tests
  - [x] 1.3 Refactor `LessonListView` batch context + Serializer read-only dict + Integration contract test
- [x] **Phase 2:** Data Integrity & Score Authority (JSON Schema, Backend SSOT, Timezone)
  - [x] 2.1 Pydantic schema cho LessonContent + injection guard + TDD validation tests
  - [x] 2.2 ScoringService SSOT contract + raw_answers payload spec + TDD scoring tests
  - [x] 2.3 Enforce Asia/Ho_Chi_Minh + fmt_vn utility + boundary TDD tests
- [x] **Phase 3:** AI Grading Pipeline & Qwen3.5-9B Integration
  - [x] 3.1 Setup `apps/ai/` + `qwen_client.py` (OpenAI-compatible wrapper, timeout/retry)
  - [x] 3.2 Grading Service + Prompt Guardrails + Sanitizer + Fallback heuristic
  - [x] 3.3 Celery async task stub + `AIGradingLog` audit model + TDD pipeline tests
- [x] **Phase 4:** UX/Pedagogy & Temporal Consistency (SRS, Micro-steps, Teacher Override)
  - [x] 4.1 Add `learning_objectives` to `LessonContent` + Schema update + TDD pedagogy tests
  - [x] 4.2 Teacher Override & Analytics API Stub (`TeacherService`)
  - [x] 4.3 SRS Queue API Stub (`SRSService`)
  - [x] 4.4 Final TDD Verification & Audit
🔍 PART 1: MULTI-PERSPECTIVE ANALYSIS
1. GÓC NHÌN NGƯỜI HỌC (Learner)
✅ Điểm mạnh

    Lộ trình CEFR rõ ràng, unlock tuần tự tạo cảm giác tiến bộ & gamification (XP, streak) duy trì động lực.
    Đa kỹ năng tích hợp trong 1 lesson giảm context-switching.
    UI phản hồi tức thì (MCQ, dictation, word order), TTS điều chỉnh tốc độ, skeleton/toast states mượt.

⚠️ Thiếu sót

    Tải nhận thức (Cognitive Load): Lesson gộp 4–5 section dài → A1/A2 dễ quá tải. Không có micro-breakdown hoặc adaptive pacing.
    Self-rating chủ quan: Speaking chỉ tự chấm (poor/ok/great). Writing free/guided chỉ đếm từ. Không có feedback định tính → học sai không biết sai, giảm hiệu quả dài hạn.
    Thiếu mục tiêu học tập: Không hiển thị learning_objectives hay success_criteria đầu bài → người học không biết "học xong làm được gì".
    SRS chưa ra UI: Model có srs_review_count & vocab_word_ids nhưng frontend không hiển thị queue ôn tập → từ vựng học xong không ôn → quên nhanh.

🛠 Đề xuất

    Thêm learning_objectives (JSON array) vào LessonContent, render đầu lesson.
    Tách lesson dài thành micro_steps (frontend state, không đổi DB). Auto-save progress per step via debounce.
    Hiển thị SRS queue trong DashboardView hoặc VocabFootnote. Trigger review trước khi vào bài mới nếu đến hạn.
    Chuyển Speaking/Writing sang backend grading (AI + rubric) để trả feedback định tính, không chỉ điểm số.

2. GÓC NHÌN GIÁO VIÊN / INSTRUCTIONAL DESIGNER
✅ Điểm mạnh

    Cấu trúc CEFR → Course → Chapter → Lesson chuẩn sư phạm, UnlockRule đảm bảo prerequisite mastery.
    JSONField linh hoạt, cho phép authoring đa dạng bài tập mà không migrate DB.
    Seed scripts (seed_courses, seed_lesson_content) giúp bootstrap nhanh nội dung mẫu.

⚠️ Thiếu sót

    Không có rubric chấm AI: Speaking/Writing không có tiêu chí chấm (fluency, grammar, coherence, lexical resource). Prompt chưa validate → dễ hallucination hoặc chấm sai edge cases (blank, short, inappropriate).
    Authoring rủi ro: Admin nhập JSON thủ công vào LessonContent. Sai key/thiếu field → frontend crash. Không có WYSIWYG hoặc schema validation.
    Không có teacher override: Giáo viên không thể mở khóa thủ công, điều chỉnh min_score, hoặc xem heatmap stuck points của học sinh. Progress hoàn toàn tự động, thiếu flexibility cho lớp học thực tế.

🛠 Đề xuất

    Định nghĩa AI Grading Contract rõ ràng: payload chuẩn, prompt template có guardrails, JSON output enforced, fallback score nếu AI fail.
    Thêm LessonContentSchema (Pydantic/JSONSchema) validate trước save(). Reject malformed JSON ngay ở serializer.
    Stub TeacherGradingView (route đã có trong index.js) kết nối API chấm tay + override progress + xem analytics (stuck points, avg attempts per lesson).
    Thêm teacher_notes & override_unlock fields vào LessonProgress để hỗ trợ can thiệp sư phạm.

3. GÓC NHÌN NHÀ PHÁT TRIỂN (Architect/Dev)
✅ Điểm mạnh

    Stack hiện đại: Django + DRF + Vue 3 Composition API + Vite + Tailwind + Pinia.
    Polymorphic exercise linking (LessonExercise) mở rộng tốt, không tight coupling.
    Frontend modular, lazy-load, skeleton states, toast feedback, routing guard chặt.

⚠️ Critical Gaps (Code vs. Rules)
Vấn đề
	
Vị trí
	
Rủi ro
URL Syntax Blocking
	
urls.py dòng 8-11
	
DRF fail routing ngay ([int:course_pk](int:course_pk) là markdown artifact)
N+1 Query
	
serializers.py get_is_unlocked & get_progress_status
	
List 50 lessons → 50+ queries. Crash under load. Vi phạm rule Zero N+1
Service Layer Missing
	
Logic unlock/progress nằm trong Serializer
	
Vi phạm rule "Logic in Services, HTTP in Views". Khó test, khó reuse
JSON Schema Validation Missing
	
LessonContent model/serializer
	
Frontend crash nếu admin nhập sai. AI grading nhận malformed data
Score Authority Drift
	
LessonDetailView.vue tính autoScore client-side
	
Backend không phải SSOT. AI grading sau này sẽ conflict
Temporal/Timezone
	
Không enforce Asia/Ho_Chi_Minh cho last_activity, streaks, SRS
	
Progress lệch ngày, unlock logic sai, vi phạm rule temporal consistency
Pinia Underutilized
	
State phân tán ở component reactive()
	
Cross-component sync dùng courseProgressRefresh.js marker → fragile, khó debug
🛠 Đề xuất kỹ thuật (Surgical & TDD-First)

    Fix URL routing → path("courses/<int:course_pk>/chapters/", ...)
    Extract Service Layer: apps/curriculum/services/unlock.py & progress.py. Dời logic khỏi serializer. View chỉ gọi service + trả HTTP.
    Batch Progress Resolution: Dùng Prefetch hoặc annotate trong View. Verify bằng assertNumQueries.
    JSON Schema Validation: Pydantic model cho LessonContent. Validate trong LessonContentSerializer.validate(). Test edge cases.
    AI Grading Contract: Backend nhận raw answers → async task → validate prompt → call LLM → store result → emit status. Client không tự tính score.
    Timezone Enforcement: settings.TIME_ZONE = "Asia/Ho_Chi_Minh". Format vi-VN ở serializer response (fmt_vn). Audit auto_now fields.
    Centralize Pinia: Dời readingProgress, writingProgress, autoScore vào useLessonStore. Loại bỏ courseProgressRefresh.js marker.

🤖 PART 2: QWEN3.5-9B AI INTEGRATION STRATEGY
2.1 Model Deployment

    Model: unsloth/Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf
    Dev: llama-cpp-python load GGUF local. Fast iteration, zero infra cost.
    Prod: Ollama hoặc vLLM (nếu có GPU) behind reverse proxy. Auto-scaling, health checks, rate-limit.
    Wrapper: apps/ai/services/qwen_client.py → retry logic, timeout (max 15s), JSON mode enforcement, circuit breaker.

2.2 Grading Pipeline & Guardrails

    Async Only: Celery/RQ task. Không bao giờ gọi sync trong request cycle.
    Prompt Template: Fixed system role (ESL teacher), rubric (fluency, grammar, lexical, coherence, task achievement), JSON output schema enforced.
    Input Sanitization: Reject blank/<min_words, detect toxic/inappropriate, strip HTML/JS, escape prompt injection patterns ({{system}}, <script>, ignore previous instructions).
    Fallback: Nếu AI timeout/fail → mark pending_review, notify teacher, không block progress. Student nhận temporary score dựa trên heuristic (word count, keyword match).
    Audit Log: Lưu ai_grading_log (prompt hash, response, latency, score, model version) để trace & improve prompts.

2.3 TDD/Verify

    Test prompt với edge cases: empty string, 1 word, Vietnamese mixed, injection attempts.
    Verify JSON parse success + score trong range 0-100 + rubric fields present.
    Load test: 50 concurrent submissions → queue stable, no memory leak, fallback triggers correctly.

📅 PART 3: TDD-FIRST IMPLEMENTATION PLAN
Phase
	
Bước
	
Action
	
Verify
1
	
1.1
	
Fix urls.py syntax markdown artifact
	
pytest routing pass, curl 200 OK nested endpoints
	
1.2
	
Tạo services/unlock_service.py & progress_service.py
	
Unit test logic unlock, mock LessonProgress, edge cases pass
	
1.3
	
Dời logic khỏi serializer, thêm Prefetch/annotate ở View
	
self.assertNumQueries(≤3) cho lesson list/detail
2
	
2.1
	
Pydantic schema cho LessonContent (8 JSON fields)
	
Test malformed/blank/injection → ValidationError reject
	
2.2
	
Đổi contract: frontend gửi raw, backend tính score
	
Integration test score match rubric, no client drift
	
2.3
	
Enforce Asia/Ho_Chi_Minh + fmt_vn formatter
	
Timestamp audit 23:59 ICT → đúng ngày, streak không reset sai
3
	
3.1
	
Setup apps/ai/ + qwen_client.py (llama-cpp/Ollama)
	
Local inference test, JSON mode, timeout/circuit breaker
	
3.2
	
Async grading task + prompt guardrails + audit log
	
Test edge cases, fallback flow, log created, parse success
4
	
4.1
	
Thêm learning_objectives, micro-step state, Pinia centralization
	
E2E state persistence, progress sync, no marker hack
	
4.2
	
SRS queue Pinia + UI widget + teacher override stub
	
Queue fetch/review/interval test, override API 200
	
4.3
	
Teacher analytics endpoint (stuck points, avg attempts)
	
Query optimized, returns heatmap data, assertNumQueries pass
⚠️ GUARDRAILS & FIRST PRINCIPLES

    No Blind Coding: Mỗi bước bắt đầu bằng test → fail → implement → pass. Không code khi chưa có test skeleton.
    Surgical Changes: Chỉ touch file liên quan. Không refactor lan man, không format lại code cũ, không đổi structure không cần thiết.
    Backend SSOT: Client chỉ tracking UI state. best_score, xp_gained, status, unlock luôn từ backend. Frontend không tự chấm để lưu.
    AI Safety: Prompt template cố định, JSON output enforced, input sanitized, async only, fallback manual. Không tin LLM output vô điều kiện.
    Zero N+1: Mọi list/detail endpoint phải verify query count. Fail CI nếu vượt ngưỡng. Prefetch/annotate bắt buộc.
    Temporal Accuracy: UTC trong DB, ICT trong app layer. Format vi-VN nhất quán ở response. Streak/SRS/unlock dựa trên ICT date boundary.
    Pedagogy First: Tech phục vụ sư phạm. Micro-steps, objectives, SRS, teacher override ưu tiên hơn feature cosmetic.

📥 NEXT ACTION
Chọn Phase ưu tiên để tôi xuất test skeleton → service code → verify script đúng rule TDD, surgical, zero N+1:

    Phase 1 (URL + Service Layer + N+1) → Unblock backend & performance
    Phase 2 (JSON Validation + Score Contract + Timezone) → Data integrity & AI-ready
    Phase 3 (Qwen3.5 AI Pipeline) → Grading & feedback automation
    Phase 4 (UX + SRS + Teacher Override) → Pedagogy & temporal consistency

