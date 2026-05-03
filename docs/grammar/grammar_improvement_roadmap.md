📘 Kế Hoạch Cải Tiến Hệ Thống Ngữ Pháp (Grammar System Roadmap)
Ngày cập nhật: 2024
Mục tiêu: Chuyển đổi từ Content Library sang Adaptive Learning Platform
Phạm vi: Tích hợp sâu GrammarTopic/Rule/Example với Exercise/Quiz/Progress/SRS
Nguyên tắc thiết kế: Backend-driven • Granular Tracking • Pre-generated + Cached • Explicit over Implicit
🔍 PHẦN 1: ĐÁNH GIÁ HIỆN TRẠNG & ĐIỀU CHỈNH BẮT BUỘC
✅ Điểm mạnh cần giữ nguyên

    Cấu trúc phân tầng Chapter → Topic → Rule → Example sạch, chuẩn sư phạm.
    Metadata giàu ngữ cảnh: analogy, memory_hook, signal_words, common_mistakes, context.
    UX frontend mạch lạc: grouping CEFR, tab Lesson/Practice, immediate feedback, progress tracking cơ bản.

⚠️ Lỗ hổng logic & Rủi ro kỹ thuật (Cần sửa trước khi code)
Vấn đề trong roadmap cũ
	
Tại sao yếu/sai
	
Hậu quả nếu giữ nguyên
	
Giải pháp thay thế
Quiz sinh ở Frontend (buildQuiz())
	
Client không có ngữ cảnh DB, không validate đáp án, không lưu lịch sử từng câu.
	
Không thể làm SRS, Error Tagging, Adaptive. Điểm số dễ bị giả mạo.
	
Dời hoàn toàn về Backend. Frontend chỉ render & submit.
GrammarQuizResult chỉ lưu aggregate score
	
Upsert ghi đè kết quả cũ. Không lưu attempt_id, đáp án từng câu, hay rule_id.
	
Mất dữ liệu để phân tích lỗi, tính ease_factor, trigger remedial path.
	
Thêm GrammarQuizAttempt & GrammarQuizAnswer. Giữ QuizResult làm bảng tổng hợp max-score.
Sync tiến độ bằng Django Signal (post_save)
	
Signal chạy ngầm, khó debug, dễ race condition khi submit liên tiếp. Khó kiểm soát "chỉ tính điểm cao nhất".
	
Progress bar nhảy sai, unlock lesson nhầm, audit log thiếu minh bạch.
	
Thay bằng explicit service call trong QuizSubmitView sau khi validate & commit transaction.
SRS áp dụng ở cấp Topic
	
Ngữ pháp quên theo từng quy tắc cụ thể (VD: quên does/doesn't nhưng nhớ công thức tổng quát).
	
Ôn tập không chính xác, gây quá tải hoặc bỏ sót lỗ hổng kiến thức.
	
Hạ granularity xuống cấp GrammarRule. SRS track theo rule, không theo topic.
Sinh đáp án nhiễu bằng cách lấy ngẫu nhiên highlight khác
	
Không kiểm tra từ loại, thì, ngữ cảnh. VD: trộn "goes" với "yesterday" → nhiễu vô nghĩa.
	
Giảm chất lượng bài tập, phá vỡ tính sư phạm, học sinh đoán mò.
	
Filter distractors cùng level, cùng POS (nếu có), ưu tiên cùng topic. Thêm flag is_verified để admin duyệt.
Auto-generate on-the-fly mỗi lần request
	
Query + transform + shuffle mỗi lần mở topic → tải DB/CPU tăng tuyến tính.
	
Latency cao, timeout khi traffic tăng, trải nghiệm giật lag.
	
Pre-generation khi topic publish/update. Lưu vào DB/Redis. API chỉ đọc cache.
🏗 PHẦN 2: KIẾN TRÚC & LUỒNG DỮ LIỆU MỚI
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

Nguyên tắc cốt lõi:

    Frontend = Presenter. Không sinh câu hỏi, không chấm điểm, không quyết định tiến độ.
    Backend = Source of Truth. Validate, chấm, lưu granular data, trigger business logic.
    Explicit > Implicit. Không dùng signal cho luồng nghiệp vụ quan trọng. Dùng service call trong transaction.
    Pre-compute > On-the-fly. Sinh quiz 1 lần, cache nhiều lần đọc.

🗄 PHẦN 3: DATABASE SCHEMA & MIGRATIONS
3.1 Model bổ sung (apps/grammar/models.py)
class GrammarQuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    class Meta:
        db_table = "grammar_quiz_attempt"
        indexes = [models.Index(fields=["user", "topic", "-started_at"])]

class GrammarQuizAnswer(models.Model):
    attempt = models.ForeignKey(GrammarQuizAttempt, on_delete=models.CASCADE, related_name="answers")
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE, null=True, blank=True)
    question_source_id = models.PositiveIntegerField()  # ID của GrammarExample hoặc Question
    selected_option = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    class Meta:
        db_table = "grammar_quiz_answer"
        indexes = [models.Index(fields=["attempt", "rule", "is_correct"])]

class GrammarReviewSchedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE)
    next_review = models.DateField(db_index=True)
    interval_days = models.PositiveIntegerField(default=1)
    ease_factor = models.FloatField(default=2.5)
    class Meta:
        db_table = "grammar_review_schedule"
        unique_together = ("user", "rule")

class ErrorPattern(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE)
    error_type = models.CharField(max_length=50, default="general")
    count = models.PositiveIntegerField(default=1)
    last_seen = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "grammar_error_pattern"
        unique_together = ("user", "rule", "error_type")

3.2 Chiến lược Migration

    Thêm FK với null=True, blank=True → chạy migration an toàn.
    Backfill rule_id cho câu hỏi auto-generated dựa trên source_id.
    Không migrate dữ liệu quiz cũ (chỉ track từ Phase 1). Ghi log legacy_score_migrated=True nếu cần.
    Index tối ưu cho query SRS (next_review <= today) & Error analytics (user, rule, count).

⚙️ PHẦN 4: BACKEND SERVICE LAYER & API CONTRACT
4.1 grammar/services.py (Core Logic)
def pregenerate_quiz(topic_id: int) -> List[dict]:
    """
    Duyệt GrammarExample → sinh câu hỏi Gap-fill/MC/Error.
    Filter distractors cùng level, ưu tiên cùng topic.
    Gán tests_rule_id = rule.id.
    Lưu vào bảng Question (hoặc JSON cache) với flag is_auto_generated=True.
    Trả về danh sách câu hỏi đã shuffle.
    """

def submit_quiz_attempt(user, topic, answers: List[dict]) -> dict:
    """
    answers = [{question_id, selected_option, rule_id}]
    1. Tạo GrammarQuizAttempt
    2. Duyệt answers → tạo GrammarQuizAnswer, chấm is_correct
    3. Tính score, upsert GrammarQuizResult (giữ max)
    4. Gọi update_srs() & track_error_pattern()
    5. Gọi sync_lesson_progress()
    6. Trả về {attempt_id, score, next_review_dates, weak_rules}
    """

def update_srs(user, rule, is_correct: bool):
    """
    SM-2 biến thể cho ngữ pháp:
    - Đúng: interval = max(1, interval * ease_factor)
    - Sai: interval = 1, ease_factor = max(1.3, ease_factor - 0.2)
    - Cập nhật next_review = today + interval
    """

def sync_lesson_progress(user, topic, score: float):
    """
    Tìm LessonExercise(grammar_topic=topic)
    Nếu score >= 80% → mark completed
    Kiểm tra prerequisite → unlock lesson tiếp theo
    KHÔNG dùng signal. Gọi explicit trong transaction.
    """

4.2 API Endpoints
Method	Endpoint	Payload	Response	Ghi chú
GET	/api/v1/grammar/<slug>/quiz/	-	{questions: [{id, type, prompt, options, rule_id}]}	Đọc từ cache/DB. Không sinh on-the-fly.
POST	/api/v1/grammar/<slug>/quiz/submit/	{attempt_id?, answers: [{q_id, selected}]}	{score, attempt_id, next_review, weak_rules}	Idempotent key hỗ trợ. Validate server-side.
GET	/api/v1/grammar/reviews/today/	-	[{rule_id, title, topic_slug, interval}]	Widget SRS dashboard.

🖥 PHẦN 5: FRONTEND ADJUSTMENTS
5.1 Loại bỏ

    ❌ buildQuiz(), createErrorSentence(), shuffle(), client-side scoring.
    ❌ watch(quizDone) auto-submit không idempotent.
    ❌ Logic tính progress/unlock ở client.

5.2 Thay thế

    ✅ GET /grammar/<slug>/quiz/ → render câu hỏi từ backend.
    ✅ Submit payload: { answers: [{ q_id, selected }] }
    ✅ Disable nút submit sau khi click, hiển thị loading, xử lý retry an toàn.
    ✅ Hiển thị next_review_date, weak_rules, remedial banner từ response.
    ✅ Giữ nguyên UX: tab Lesson/Practice, immediate feedback, progress bar, sidebar navigator.

🚀 PHẦN 6: LỘ TRÌNH TRIỂN KHAI CHI TIẾT
🔹 PHASE 1: Critical Fixes (P0) — Tuần 1-2
Mục tiêu: Đóng vòng lặp Học → Luyện → Chấm → Sync tiến độ. Chuyển quiz generation về backend.
Task
	
Technical Spec
	
Acceptance Criteria
	
Rủi ro & Mitigation
1.1 Migration Attempt & Answer
	
Tạo 2 model, index tối ưu, null=True cho FK
	
DB có bảng mới, query < 50ms, không lock table
	
Dữ liệu cũ không migrate → chấp nhận, chỉ track từ Phase 1
1.2 Backend Quiz Generator
	
pregenerate_quiz(), filter distractors cùng level/POS, lưu DB + Redis
	
API trả về 5-8 câu, có rule_id, type, options
	
Distractor kém chất lượng → thêm needs_review, admin override
1.3 Submit & Tracking API
	
POST /quiz/submit/: tạo Attempt, lưu Answer, upsert Result (max score)
	
Trả về {score, attempt_id, next_review}. DB lưu đầy đủ
	
Race condition → dùng select_for_update() hoặc idempotency key
1.4 Sync LessonProgress
	
Service sync_lesson_progress(): tìm LessonExercise(grammar_topic=topic), update nếu score ≥ 80%
	
Progress bar nhảy đúng, unlock lesson tiếp theo
	
FK grammar_topic chưa có → migration an toàn, backfill sau
1.5 Frontend Migration
	
Xóa buildQuiz(), gọi API quiz, submit payload mới, loading/error state
	
UX không đổi, quiz load < 500ms, submit thành công hiện ✓
	
Fallback nếu API fail → hiển thị "Chưa có bài tập", không crash
🔹 PHASE 2: Pedagogical Enhancements (P1) — Tuần 3-4
Mục tiêu: SRS rule-level, Error Tagging, Remedial Path.
Task
	
Technical Spec
	
Acceptance Criteria
2.1 SRS Model & Algorithm
	
GrammarReviewSchedule(user, rule, next_review, interval, ease_factor). SM-2 biến thể.
	
Dashboard hiện widget "Ôn tập hôm nay". Quiz result hiện "Lần ôn tiếp: X ngày"
2.2 Error Pattern Tracking
	
Trigger khi is_correct=False. Upsert ErrorPattern(user, rule, error_type, count)
	
Profile hiện biểu đồ "Lỗi thường gặp". Rule có count ≥ 3 hiện cảnh báo
2.3 Remedial Path Logic
	
Nếu count ≥ 3: gợi ý micro-lesson/video, khóa bài tập nâng cao đến khi pass remedial quiz
	
UI hiện banner "Bạn hay sai [Rule]. Ôn lại tại đây". Exercise bị lock đến khi pass
2.4 Admin Curation UI
	
Django Admin: inline edit auto-generated questions, gán difficulty, fix distractors, mark is_verified
	
Admin duyệt/chỉnh câu hỏi auto-gen. Frontend ưu tiên câu is_verified=True
🔹 PHASE 3: Advanced Features (P2) — Tuần 5+
Mục tiêu: Adaptive Quiz, Context Integration, Performance.
Task
	
Technical Spec
	
Acceptance Criteria
3.1 Difficulty Tagging
	
Thêm difficulty (1-3) vào GrammarExample & Question. Gán tự động dựa trên độ dài câu, số ngoại lệ
	
Quiz engine filter được theo difficulty. Admin override được
3.2 Adaptive Engine
	
Rule-based: 3 đúng liên tiếp → tăng difficulty. 2 sai liên tiếp → giảm. Không dùng IRT giai đoạn đầu
	
Quiz flow điều chỉnh độ khó real-time. UI hiện "Đang điều chỉnh..."
3.3 Context Linking
	
M2M GrammarTopic.related_readings, related_listenings. Highlight câu chứa cấu trúc trong bài đọc/nghe
	
Hover vào câu trong Reading → tooltip hiện rule + link về grammar detail
3.4 Performance Optimize
	
Cache quiz JSON, background task pre-generate khi topic publish, CDN cho audio, DB connection pooling
	
P95 latency < 300ms, CPU < 40% ở 1k concurrent users
🛡 PHẦN 7: QUẢN TRỊ RỦI RO & CHIẾN LƯỢC ROLLOUT
Rủi ro
	
Mức độ
	
Biện pháp giảm thiểu
Distractor auto-gen vô nghĩa
	
Cao
	
Filter POS/level, fallback cùng topic, flag needs_review, admin curation UI
Race condition khi submit nhanh
	
Trung bình
	
Idempotency key (X-Idempotency-Key), select_for_update(), debounce frontend
Migration FK gây lock table
	
Cao
	
null=True, chạy off-peak, batch backfill, monitor pg_stat_activity
SRS gây quá tải notification
	
Trung bình
	
Group review theo ngày, cap max 5 rules/ngày, opt-out setting
IRT quá phức tạp giai đoạn đầu
	
Cao
	
Hoãn IRT. Dùng rule-based adaptation + difficulty tagging. IRT chỉ khi có >10k attempts
Rollout Strategy:

    Feature Flag: GRAMMAR_BACKEND_QUIZ=0/1
    Canary 10% user → monitor error rate, latency, score distribution
    Rollback plan: giữ endpoint cũ, switch flag về 0, không mất dữ liệu
    Monitoring: Sentry (FE/BE), Prometheus (latency, DB queries), Metabase (quiz completion rate, SRS adherence)

📋 PHẦN 8: CHECKLIST TRIỂN KHAI & DEFINITION OF DONE
Giai đoạn 1 (Tuần 1-2)

    Migration GrammarQuizAttempt, GrammarQuizAnswer chạy thành công
    pregenerate_quiz() sinh được 5-8 câu/topic, lưu DB/Redis
    API GET /quiz/ & POST /quiz/submit/ hoạt động, idempotent
    sync_lesson_progress() thay thế signal, test được unlock logic
    Frontend xóa buildQuiz(), tích hợp API mới, xử lý loading/error
    E2E test: Học → Làm quiz → Lưu kết quả → Progress bar nhảy đúng

Giai đoạn 2 (Tuần 3-4)

    Model GrammarReviewSchedule & ErrorPattern deploy
    SM-2 variant tính next_review chính xác, reset khi sai
    Dashboard widget "Ôn tập hôm nay" hiển thị đúng
    Error count ≥ 3 trigger remedial banner & lock advanced exercises
    Admin inline duyệt/chỉnh câu hỏi auto-gen, mark is_verified

Giai đoạn 3 (Tuần 5+)

    difficulty field backfill & admin override
    Adaptive rule-based hoạt động ổn định (3 đúng ↑, 2 sai ↓)
    M2M linking Grammar ↔ Reading/Listening, tooltip context hoạt động
    P95 latency < 300ms, cache hit rate > 85%, CPU ổn định

Definition of Done (Mỗi Phase):

    Code review ≥ 2 người, unit test coverage ≥ 80% cho service layer
    E2E test pass trên staging, không regression progress/unlock
    Document API contract, migration guide, rollback procedure
    Metric baseline được ghi nhận (completion rate, avg score, latency)

💡 LƯU Ý CHO DEVELOPER & PRODUCT TEAM

    Không giữ client-side quiz generation. Đây là technical debt chặn đứng SRS, Error Tracking, Adaptive.
    Không dùng signal cho progress sync. Dùng explicit service call trong transaction để dễ test, debug, rollback.
    Đừng áp dụng IRT ngay. Rule-based adaptation đủ cho 90% use case. IRT cần dataset lớn & calibration phức tạp.
    Chất lượng > Số lượng. Auto-generated quiz chỉ là baseline. Cho phép admin override & mark is_verified. Frontend ưu tiên câu đã duyệt.
    Grammar quên theo Rule, không theo Topic. SRS phải track ở cấp độ quy tắc cụ thể để ôn tập chính xác.

📎 Tài liệu liên quan:  

    grammar_current_implementation.md — Hiện trạng Phase 0  
    models.py, views.py, serializers.py — Backend hiện tại  
    GrammarDetailView.vue — Frontend hiện tại (cần refactor buildQuiz)  
    curriculum.js — API client (cần thêm endpoint quiz mới)