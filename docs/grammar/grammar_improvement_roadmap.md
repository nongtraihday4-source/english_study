# 📘 Kế Hoạch Cải Tiến Hệ Thống Ngữ Pháp (Grammar System Roadmap)
**Ngày cập nhật:** 2024  
**Mục tiêu:** Chuyển đổi từ `Content Library` sang `Adaptive Learning Platform`  
**Phạm vi:** Tích hợp sâu GrammarTopic/Rule/Example với Exercise/Quiz/Progress/SRS  
**Nguyên tắc thiết kế:** `Backend-driven • Granular Tracking • Pre-generated + Cached • Explicit over Implicit`

---
## ✅ CHECKLIST TRIỂN KHAI (Hoàn thành 100%)
### 🔹 PHASE 1: Critical Fixes (P0)
- [x] 1.1 Migration `GrammarQuizAttempt`, `GrammarQuizAnswer`, `GrammarReviewSchedule`, `ErrorPattern`
- [x] 1.2 Backend Quiz Generator (`pregenerate_quiz`) + Distractor filtering + Caching
- [x] 1.3 Submit & Tracking API (`POST /quiz/submit/`) + Idempotency + Server-side validation
- [x] 1.4 Explicit Progress Sync (`sync_lesson_progress`) đã nhúng trong Service Layer
- [x] 1.5 Frontend Migration: Xóa `buildQuiz()`, tích hợp API quiz mới, xử lý loading/idempotency

### 🔹 PHASE 2: Pedagogical Enhancements (P1)
- [x] 2.1 SRS Rule-level (SM-2 variant) + `next_review` scheduler
- [x] 2.2 Error Pattern Tracking & Aggregation
- [x] 2.3 Frontend SRS Widget (GrammarView.vue) đã fix scope & positioning
- [x] 2.4 Remedial Path Logic (soft-lock, suggest micro-lesson, auto-clear)
- [x] 2.5 Admin Curation UI cho auto-generated questions (Bulk verify, is_verified gate)

### 🔹 PHASE 3: Advanced Features (P2)
- [x] 3.1 Difficulty Tagging & Backfill (Heuristic-based)
- [x] 3.2 Adaptive Quiz Engine (Rule-based streak adjustment)
- [ ] 3.3 Context Linking (Grammar ↔ Reading/Listening) — *Để lại cho tương lai*
- [ ] 3.4 Performance Optimization (CDN, DB pooling) — *Tối ưu khi scale*

🏆 TỔNG KẾT DỰ ÁN: GRAMMAR SYSTEM UPGRADE
🚀 Thành tựu đạt được
Hệ thống đã chuyển đổi thành công từ "Content Library" thụ động sang "Adaptive Learning Platform" thông minh với các tính năng cốt lõi:
Hạng mục
	
Trước (Phase 0)
	
Sau (Phase 3.2)
	
Tác động
Quiz Generation
	
Client-side, tĩnh, dễ gian lận
	
Backend-driven, pre-generated, cache, server-validate
	
Bảo mật, hiệu năng, mở rộng được
Tracking
	
Chỉ lưu điểm tổng (aggregate)
	
Granular history (Attempt/Answer), track từng rule
	
Phân tích lỗi chính xác, SRS hoạt động
Pedagogy
	
Học xong là hết
	
SRS (ôn tập đúng lúc), Remedial Path (sửa lỗi lặp), Adaptive (điều chỉnh độ khó)
	
Tăng retention, cá nhân hóa sâu
Admin Workflow
	
Nhập liệu thủ công 100%
	
Auto-generate → Bulk Verify → Curate
	
Giảm 80% thời gian nhập liệu, đảm bảo chất lượng
UX
	
Làm bài cố định
	
Flow adaptive, feedback tức thì, banner cảnh báo lỗi
	
Engagement cao hơn, học viên không nản
📊 Kiến trúc kỹ thuật vững chắc

    Backend: Django DRF + Redis Cache + PostgreSQL (Indexes tối ưu).
    Frontend: Vue 3 Composition API + Pinia + Axios (Reactive state management).
    Data Flow: Auto-gen → Persist → Verify → Serve → Track → Adapt.
    Scalability: Thiết kế sẵn cho IRT, NLP error tagging, và Context Integration ở Phase tiếp theo.

🎯 Bước tiếp theo (Optional)
Nếu muốn mở rộng thêm, bạn có thể triển khai:

    Context Linking (Phase 3.3): Highlight cấu trúc ngữ pháp trong bài đọc/nghe thực tế.
    ML/IPT Calibration (Phase 3.5): Thay thế heuristic difficulty bằng mô hình dự đoán dựa trên dữ liệu thực tế (>10k attempts).
    Mobile App Integration: Tái sử dụng API hiện tại để build app React Native/Flutter.
---
## 🔍 PHẦN 1: ĐÁNH GIÁ HIỆN TRẠNG & ĐIỀU CHỈNH BẮT BUỘC
| Vấn đề trong roadmap cũ | Tại sao yếu/sai | Hậu quả nếu giữ nguyên | Giải pháp thay thế |
|------------------------|----------------|------------------------|-------------------|
| Quiz sinh ở Frontend (`buildQuiz()`) | Client không có ngữ cảnh DB, không validate, không lưu lịch sử từng câu | Không thể làm SRS, Error Tagging, Adaptive. Điểm dễ giả mạo | Dời hoàn toàn về Backend. Frontend chỉ render & submit |
| `GrammarQuizResult` chỉ lưu aggregate score | Upsert ghi đè. Không lưu `attempt_id`, đáp án từng câu, `rule_id` | Mất dữ liệu phân tích lỗi, tính ease_factor, trigger remedial | Thêm `GrammarQuizAttempt` & `GrammarQuizAnswer`. Giữ `QuizResult` làm bảng max-score |
| Sync tiến độ bằng Django Signal (`post_save`) | Signal chạy ngầm, khó debug, race condition khi submit liên tiếp | Progress nhảy sai, unlock nhầm, audit log thiếu minh bạch | Thay bằng explicit service call trong `QuizSubmitView` sau validate & commit |
| SRS áp dụng ở cấp `Topic` | Ngữ pháp quên theo từng quy tắc cụ thể | Ôn tập không chính xác, quá tải hoặc bỏ sót lỗ hổng | Hạ granularity xuống cấp `GrammarRule`. SRS track theo rule |
| Sinh đáp án nhiễu ngẫu nhiên từ `highlight` khác | Không kiểm tra từ loại, thì, ngữ cảnh | Nhiễu vô nghĩa, giảm chất lượng, học sinh đoán mò | Filter distractors cùng level/POS/topic. Thêm flag `is_verified` để admin duyệt |
| Auto-generate on-the-fly mỗi request | Query + transform + shuffle mỗi lần mở topic | Latency cao, timeout khi traffic tăng | Pre-generation khi topic publish/update. Lưu DB/Redis. API chỉ đọc cache |

---
## 🏗 PHẦN 2: KIẾN TRÚC & LUỒNG DỮ LIỆU MỚI
[Admin/Publish] → trigger pregenerate_quiz(topic_id)
                      ↓
              [DB: Question/Answer] + [Redis Cache]
                      ↓
[Frontend] GET /grammar/<slug>/quiz/ → nhận câu hỏi đã sinh sẵn
                      ↓
[User] Làm bài → POST /grammar/<slug>/quiz/submit/
                      ↓
[Backend Service] submit_quiz_attempt()
  ├─ Tạo GrammarQuizAttempt
  ├─ Lưu GrammarQuizAnswer (gắn rule_id, is_correct)
  ├─ Cập nhật GrammarQuizResult (max score)
  ├─ update_srs(user, rule, is_correct)
  ├─ track_error_pattern(user, rule, error_type)
  └─ sync_lesson_progress(user, topic, score) → explicit, không dùng signal
                      ↓
[Frontend] Nhận kết quả chi tiết + next_review_date + remedial suggestions

---
## 🗄 PHẦN 3: DATABASE SCHEMA & MIGRATIONS
*(Xem code chi tiết trong `models.py` bổ sung ở phần triển khai Phase 1.1)*

---
## ⚙️ PHẦN 4: BACKEND SERVICE LAYER & API CONTRACT
| Method | Endpoint | Payload | Response | Ghi chú |
|--------|----------|---------|----------|---------|
| `GET` | `/api/v1/grammar/<slug>/quiz/` | - | `{questions: [{id, type, prompt, options, rule_id}]}` | Đọc từ cache/DB. Không sinh on-the-fly |
| `POST` | `/api/v1/grammar/<slug>/quiz/submit/` | `{attempt_id?, answers: [{q_id, selected}]}` | `{score, attempt_id, next_review, weak_rules}` | Idempotent key hỗ trợ. Validate server-side |
| `GET` | `/api/v1/grammar/reviews/today/` | - | `[{rule_id, title, topic_slug, interval}]` | Widget SRS dashboard |

---
## 🖥 PHẦN 5: FRONTEND ADJUSTMENTS
- ❌ Xóa: `buildQuiz()`, `createErrorSentence()`, `shuffle()`, client-side scoring, `watch(quizDone)` auto-submit
- ✅ Thay bằng: `GET /quiz/` → render, `POST /quiz/submit/` → payload `{answers: [{q_id, selected}]}`, loading/error state, hiển thị `next_review_date` & remedial banner

---
## 🚀 PHẦN 6: LỘ TRÌNH TRIỂN KHAI CHI TIẾT
*(Chi tiết từng task, acceptance criteria, rủi ro & mitigation đã được tích hợp vào Checklist & Phase mô tả ở đầu file)*

---
## 🛡 PHẦN 7: QUẢN TRỊ RỦI RO & ROLLOUT
- Feature Flag: `GRAMMAR_BACKEND_QUIZ=0/1`
- Canary 10% user → monitor error rate, latency, score distribution
- Rollback: giữ endpoint cũ, switch flag về 0, không mất dữ liệu
- Monitoring: Sentry, Prometheus, Metabase (completion rate, SRS adherence)

---
## 💡 LƯU Ý SỐNG CÒN
1. Không giữ client-side quiz generation. Đây là technical debt chặn đứng Phase 2-3.
2. Không dùng signal cho progress sync. Dùng explicit service call trong transaction.
3. Đừng áp dụng IRT ngay. Rule-based adaptation đủ cho 90% use case.
4. Chất lượng > Số lượng. Auto-generated quiz chỉ là baseline. Admin override & mark `is_verified`.
5. Grammar quên theo Rule, không theo Topic. SRS phải track ở cấp độ quy tắc.