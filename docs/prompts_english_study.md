# BỘ MẪU PROMPT CHUYÊN BIỆT (SOP) DÀNH CHO DỰ ÁN ENGLISH STUDY

*Tài liệu này là phiên bản tùy chỉnh của `promt_web_app.md`, được tối ưu hóa đặc biệt nhằm hướng dẫn AI (và lập trình viên) trong quá trình phát triển hệ thống học tiếng Anh (LMS). Bạn hãy copy từng đoạn prompt dưới đây vào cửa sổ chat với AI để thực thi từng bước.*

---
## BƯỚC 1: LỘ TRÌNH PHÁT TRIỂN TOÀN DIỆN (MASTER ROADMAP)

> *Đây là sơ đồ toàn cảnh dự án. Dùng như roadmap kiểm tra tiến độ khi bắt đầu mỗi buổi làm việc.*

```
┌───────────────────────────────────────────────────────────────┐
│  ENGLISH STUDY LMS — LỘ TRÌNH PHÁT TRIỂN TOÀN DIỆN           │
├───────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 0 — NỀN TẢNG TÀI LIỆU                              │
│  ☑ PRD.md hoàn chỉnh (8 sections)                            │
│  ☑ Wireframe HTML 10 trang (wireframes/)                       │
│  ☑ docs/database-design.md                                    │
├───────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 1 — DATABASE DESIGN                                  │
│  ☐ Thiết kế schema PostgreSQL (12 Django apps)               │
│  ☐ Viết migrations (Django)                                   │
│  ☐ Seed dữ liệu mẫu (Oxford vocab CSV import)               │
├───────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 2 — BACKEND API (Django + DRF)                        │
│  ☐ Auth module (JWT 5-layer security)                          │
│  ☐ Curriculum API (level/course/chapter/lesson/exercise)      │
│  ☐ Exercise submission + auto-grading (L/R)                   │
│  ☐ AI grading pipeline: Speaking (Whisper+GPT-4o)             │
│  ☐ AI grading pipeline: Writing (GPT-4o Rubrics)              │
│  ☐ Flashcard SRS (SM-2) API                                   │
│  ☐ Gamification API (XP, Streak, Badges, Leaderboard)         │
│  ☐ Payment API (VNPay/Stripe + Coupon)                        │
│  ☐ Notification system (Celery async)                         │
│  ☐ Admin + Teacher Portal API                                 │
│  ☐ docs/api-spec.md                                           │
├───────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 3 — FRONTEND (Vue 3 + Vite + TailwindCSS)             │
│  ☐ Student Dashboard (Radar chart, Streak, XP)                │
│  ☐ Skill Map (Duolingo-style, Unlock animation)               │
│  ☐ Exercise UIs: Listening, Speaking, Reading, Writing        │
│  ☐ Flashcard Study (SM-2 session UI)                          │
│  ☐ Vocabulary Browser (filter by domain/level)                │
│  ☐ Pronunciation Curriculum (Phoneme Chart interactive)       │
│  ☐ Assessment / Exam UI                                       │
│  ☐ Gamification (Leaderboard, Achievements, Certificates)     │
│  ☐ Payment / Pricing / Checkout UI                           │
│  ☐ Teacher Portal UI                                          │
│  ☐ Admin Panel UI                                             │
├───────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 4 — INTEGRATION & TESTING                              │
│  ☐ FE-BE connection (real API, remove mock data)               │
│  ☐ End-to-end flow testing (enroll → learn → submit → grade) │
│  ☐ AI grading QA (accuracy testing)                           │
│  ☐ Payment flow testing (sandbox)                             │
├───────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 5 — SECURITY AUDIT & DEPLOY                           │
│  ☐ Kiểm tra toàn diện 5 lớp bảo mật                           │
│  ☐ docker-compose.yml (4 containers, TZ=Asia/Ho_Chi_Minh)    │
│  ☐ CI/CD pipeline                                             │
│  ☐ Production deployment + monitoring                         │
└───────────────────────────────────────────────────────────────┘
```

---
## BƯỚC 2: LÊN PLAN VÀ CHUẨN BỊ BẢN VẼ (PRD & WIREFRAME)

**1. Prompt khởi tạo và khai thác ý tưởng:**
> "Tôi đang làm dự án Web App học tiếng Anh 'English Study' tập trung vào ứng dụng thực tế (dành cho cấp độ A1-C1). Hệ thống loại bỏ việc học phát âm từ vựng rời rạc, thay vào đó là học ngữ cảnh, nghe/nói/đọc/viết nhập vai thực tế. Hãy soạn cho tôi các câu hỏi chuyên sâu về quy trình vận hành Hệ thống LMS, cách quản lý học viên, giáo viên, cấu trúc khóa học, phân bố bài học từ thư mục 'source', và hệ thống chấm điểm để tôi định hình dự án."

**2. Prompt tối ưu tính năng học thuật & UI/UX:**
> "Dựa trên ý tưởng LMS học tiếng Anh của tôi, hãy tư vấn cách làm các tính năng học tương tác (Nghe trắc nghiệm, Nói đóng vai - role play, Đọc bóc tách, Viết luận đếm từ tự động) sao cho học sinh cảm thấy hứng thú nhất. Bắt buộc luồng học phải chặt chẽ: học sinh phải đạt bài kiểm tra trước mới được qua phần sau. Thiết kế giao diện cần theo phong cách hiện đại, kích thích sự tập trung học tập, màu sắc gợi cảm hứng."

**3. Prompt chốt Tech Stack (Công nghệ):**
> "Dự án học tiếng Anh này đòi hỏi sự ràng buộc cực kỳ chặt chẽ giữa hàng ngàn bài tập, học viên và dữ liệu tiến trình học; đồng thời có hệ thống bảo mật 5 lớp. Theo bạn, tôi nên dùng Django + DRF cho Backend và Vue 3 (Composition API) cho Frontend kết hợp PostgreSQL và Redis cho Database có tối ưu nhất không? Hãy giải thích ngắn gọn lợi ích cho bài toán LMS này."

**4. Prompt xuất file PRD (Product Requirements Document):**
> "Xuất ra bản PRD hoàn chỉnh cho hệ thống Web App English Study (A1-C1). Yêu cầu khắt khe: Sử dụng công nghệ (Django, Vue 3, PostgreSQL, Redis), áp dụng Múi giờ Việt Nam (Asia/Ho_Chi_Minh), định dạng số Việt Nam (phân cách hàng ngàn). Bao quát đủ các Roles (Admin, Teacher, Student) và các module cốt lõi: Quản lý User, Quản lý Bài học dựa trên dữ liệu thư mục 'source', Module bài tập 4 kỹ năng (Nghe, Nói nhập vai, Đọc hiểu, Viết tự luận), Dashboard tiến độ. Viết thật chi tiết."

**5. Prompt yêu cầu thiết kế Wireframe (Giao diện phác thảo):**
> "Dựa vào file PRD thiết kế LMS, hãy tạo UI Wireframe & Mockup dạng HTML tĩnh. Tôi muốn giao diện Dashboard cho Học sinh có sự hiện đại (thống kê tiến độ, biểu đồ radar kỹ năng). Giao diện làm bài tập (Phát âm, Ghi âm, Trắc nghiệm) phải siêu tập trung, thân thiện UX hành vi mắt. Tuân thủ responsive cho di động. Mỗi trang con sinh ra HTML riêng nhưng dùng chung menu bar điều hướng."
**6. Prompt đặc tả Flashcard & SRS (Bổ sung):**
> "Dựa vào PRD phần 5.8, hãy thiết kế Wireframe HTML cho màn hình Flashcard Study Session: hiển thị thẻ 1 mặt, flip animation, nút đánh giá 5 mức (0-5), thanh tiến độ phiên học, thống kê số thẻ mới/ôn lại/hoàn thành. Giao diện Deck Browser: danh sách deck có progress bar, filter theo cefr level và domain. Đảm bảo nhất quán design system với các wireframe đã có."

**7. Prompt đặc tả Payment & Gamification (Bổ sung):**
> "Tiếp tục tạo Wireframe HTML cho: (1) Trang Pricing — 3 gói cước (Demo/Tháng/Năm), nút CTA, bảng so sánh tính năng; (2) Trang Leaderboard — top 10 user, vị trí của mình, filter tuần/tháng; (3) Trang Achievements — lưới huy hiệu đã đạt và chưa đạt (greyscale). Các trang này dùng chung navbar đã xây và tuân thủ design system, dark mode, responsive."
---

## BƯỚC 3: DATABASE (CƠ SỞ DỮ LIỆU CỐT LÕI)

**1. Prompt thiết kế Database toàn diện (Master Schema):**
> "Dựa vào PRD.md (8 sections) và UI Wireframe 6 trang đã có, hãy thiết kế toàn bộ Database PostgreSQL cho LMS tiếng Anh English Study. Yêu cầu chứ: (1) Phân chia rõ thành 12 Django app với bảng chính xác: users (User, UserProfile, UserSettings, Subscription, SessionToken), curriculum (CEFRLevel, Course, Chapter, Lesson, Exercise, UnlockRule), exercises (ListeningExercise, SpeakingExercise, ReadingExercise, WritingExercise, Question, QuestionOption, ExamSet), progress (UserEnrollment, LessonProgress, ExerciseResult, SpeakingSubmission, WritingSubmission, AIGradingJob, DailyStreak, CumulativeScore), vocabulary (Word, Phoneme, FlashcardDeck, Flashcard, UserFlashcardProgress, StudySession), pronunciation (CurriculumStage, PronunciationExercise, MinimalPairSet), assessment (QuestionBank, ClassExam, ExamAttempt), gamification (Achievement, UserAchievement, XPLog, LeaderboardSnapshot, Certificate, DailyChallenge), payments (SubscriptionPlan, UserSubscription, Coupon, CouponRedemption, PaymentTransaction), notifications (Notification, NotificationSetting, EmailTemplate, EmailLog), classes (TeacherClass, ClassEnrollment, AssignedExercise), content (SourceFile, LessonSource). (2) Mọi trường thời gian `created_at`, `updated_at` phải dùng `DateTimeField(auto_now_add=True)` với Django timezone chuẩn Asia/Ho_Chi_Minh. (3) Soft-Delete bằng `is_deleted=BooleanField(default=False)` cho toàn bộ bảng liên quan dữ liệu học viên. (4) Chỉ trả về cấu trúc bảng (field name, field type, constraints, indexes, foreign keys) — chưa cần code."

**2. Prompt kiểm tra luồng tiến trình học (Đối chiếu Wireframe ↔ DB):**
> "Rà soát lại toàn bộ Database theo 6 trang Wireframe: (1) student-dashboard.html cần dữ liệu gì? (Radar chart 4 kỹ năng, XP, streak, course progress) — Bảng nào cung cấp? (2) skill-map.html cần cây kỹ năng với trạng thái locked/active/done — bảng UnlockRule + LessonProgress đã đủ chưa? (3) exercise-speaking.html gửi file audio lên — SpeakingSubmission lưu s3_key chưa? AIGradingJob đẩy kết quả về bảng nào? (4) exercise-writing.html — WritingSubmission có lưu word_count, ai_score, detail_json không? (5) Leaderboard — XPLog + LeaderboardSnapshot đã đủ để tính rank theo tuần/tháng chưa? (6) Payment — sau khi webhook VNPay thành công, bảng nào cập nhật subscription_status? Nếu ổn, hãy nói 'Đã chốt Database' và liệt kê số bảng theo từng app."

**3. Prompt kiểm tra AI Grading Jobs (Celery flow):**
> "Phân tích luồng Celery từ khi học viên nộp bài Speaking đến khi nhận đặc quả: (1) SpeakingSubmission được tạo với `status=pending`. (2) Celery task `grade_speaking_task` được đẩy vào queue. (3) Task gọi Whisper API → nhận transcript. (4) Gọi GPT-4o API với rubric Speaking (35%/25%/20%/20%). (5) Cập nhật AIGradingJob: `status=completed`, lưu `total_score`, `detail_json`. (6) Cập nhật ExerciseResult và CumulativeScore. (7) Push Notification cho học viên. Hãy xác nhận mỗi bước có bảng DB tương ứng, không bước nào bị orphan data."

**4. Prompt xuất tài liệu chuyển giao bước DB:**
> "Tổng hợp toàn bộ kiến trúc Database vừa chốt thành file `docs/database-design.md`. Yêu cầu: (1) Danh sách tất cả bảng chia theo Django app (12 app). (2) ERD dạng text (Markdown) miêu tả các quan hệ FK chính. (3) Giải thích bảng then chốt: ExerciseResult, AIGradingJob, CumulativeScore, UserFlashcardProgress, XPLog. (4) Chú thích rõ bảng nào dùng Soft-Delete, bảng nào có index performance. (5) Ghi rõ chuẩn thời gian (Asia/Ho_Chi_Minh) và định dạng số (vi-VN). Tài liệu này dùng làm mồi cho AI viết Backend Django bước sau."

---

## BƯỚC 4: BACKEND (XÂY DỰNG API/LOGIC)

**1. Prompt yêu cầu code Backend Django:**
> "Kế thừa tài liệu kiến trúc Database LMS tiếng Anh vừa có, hãy xây dựng Backend bằng Django và DRF. Chia nhỏ TO-DO list: 1. Core Config (Múi giờ VN), 2. Auth & bảo mật 5 lớp JWT, 3. Các API Quản trị Khóa học, 4. Luồng xử lý nộp Bài tập (Nghe/Nói/Đọc/Viết). Gắn Debug log cực chi tiết cho từng luồng tính điểm, check đáp án tự động và lưu % tiến độ. Mọi luồng số liên quan đến tiền/thống kê lớn xuất ra API đều phải hỗ trợ định dạng hàng ngàn."

**2. Prompt debug và test luồng Backend LMS:**
> "Hãy chạy quy trình mô phỏng một Học viên nộp bài Listening/Reading, hệ thống sẽ tính điểm tự động và khoá/mở khoá bài tiếp theo. Xem Backend đã kết nối đúng với Database để truy xuất câu hỏi từ thư mục 'source' chưa? Báo cáo output Terminal cho tôi."

**3. Prompt chuẩn bị tài liệu cho Frontend:**
> "Ok tốt rồi. Hãy backup code BE hiện tại. Tạo tài liệu 'api-spec.md' lưu vào 'docs/' liệt kê tất các các endpoints (Đăng nhập, Lấy danh sách bài tập, Nộp file ghi âm Speaking, Nộp bài luận Writing). Tài liệu này phải thật chi tiết tham số (Request/Response) để AI làm Frontend đọc hiểu ngay."

---

## BƯỚC 5: FRONTEND (XÂY DỰNG GIAO DIỆN HỌC TẬP)

**1. Prompt khởi chạy Frontend Vue 3:**
> "Đọc API Specification trong mục 'docs/'. Dựng Frontend dự án bằng Vue 3 + Vite + TailwindCSS. Thiết kế UI cho Student Dashboard kích thích sự chú ý, tông màu hiện đại, tối giản. TO-DO list: 1. Setup, 2. Store dữ liệu (Pinia), 3. Auth Guard (Chặn truy cập bài học nếu chưa login), 4. UI Layout. Đảm bảo hiển thị biểu đồ điểm, hiển thị số liệu ngày tháng chuẩn VN (như 01/12/2026). Hãy ưu tiên code trang Dashboard (Tổng quan tiến độ) trước."

**2. Prompt thẩm định giao diện làm bài (UI Review):**
> "Kiểm tra lại giao diện màn hình Component 'Luyện Nói' (Speaking - Role play) và 'Luyện Nghe' (Listening). Tính năng ghi âm audio và trình phát audio đã có UX gọn gàng chưa? Đã tối ưu không gian hiển thị trên Mobile chưa? Nút Bấm Nộp bài có đủ to và rõ ràng không?"

**3. Prompt xử lý UX bài thi Đọc/Viết (Reading/Writing):**
> "Trang bài Đọc (Reading) giao diện trên máy tính đang bị dài, chữ sát nhau làm người học tiếng Anh mỏi mắt. Hãy xử lý theo kiểu chia 2 pane màn hình (Left pane: Bảng text đoạn văn lớn, Right pane: Bộ câu hỏi trắc nghiệm thanh cuộn độc lập) để tăng trải nghiệm người dùng."

**4. Prompt thiết kế các trang Quản lý (Teacher Dashboard):**
> "Giao diện Sinh viên ổn rồi, xây dựng tiếp '/teacher/dashboard'. Trang này cần lấy dữ liệu từ Backend, hiển thị danh sách Học sinh cần chấm điểm (Speaking/Writing tự luận), và theo dõi biểu đồ tiến độ của Lớp. Thiết kế bảng theo phong cách Data Table có sort và search tiện lợi."

---

## BƯỚC 6: MOCK DATA & KẾT NỐI API (MÓC NỐI FE-BE)

**1. Prompt móc nối luồng thực tế (Real Data):**
> "Xóa bỏ hết Mock Data trên Vue3. Tiến hành móc nối API thực tế luồng: Đăng nhập sinh viên -> Lấy Danh sách Bài học A1 -> Chạy bài thi Listening -> Nộp Bài. Hãy tạo checklist chi tiết quá trình test luồng này. Bật Network Console và xử lý log cẩn thận khi truyền file âm thanh Speaking."

**2. Prompt kiểm tra logic liên kết (Progress Check):**
> "Test lại logic then chốt của LMS: Học viên làm bài thi > Backend báo kết quả 50% < 60% > Giao diện UI lập tức thông báo bạn chưa đủ điểm qua bài và báo đỏ, khóa bài tiếp theo. Luồng này có mượt mà chưa? Ghi log kết quả kiểm tra bằng tiếng Việt ngắn gọn."

---

## BƯỚC 7: DEBUGGING & SỬA LỖI ĐẶC THÙ (LMS BUG FIXING)

**1. Prompt chia nhỏ luồng rà soát lỗi:**
> "Tạo TO-DO list để fix lỗi: Học viên bấm Play Audio nhưng backend báo không tìm thấy đường dẫn trong thư mục 'source'. Và Giáo viên tại sao không save được text nhận xét cho bài Viết của học sinh? Đặt console log chi tiết ở hai FE - BE để rò lỗi."

**2. Prompt xử lý lỗi thao tác (Rate Limiting):**
> "Học sinh có thói quen bấm double-click Nộp Bài, gây lỗi duplicate dữ liệu bài nộp trong Database. Hãy kích hoạt khoá Nút Submit (Disable) ở Vue3 trong lúc gọi API, đồng thời test lại lớp bảo mật Rate Limiting ở Django backend để chặn spam."

---

## BƯỚC 8 & 9: BẢO MẬT 5 LỚP & DEPLOY DỰ ÁN

**1. Prompt rà soát an ninh hệ thống:**
> "Chạy thuật toán kiểm tra toàn diện 5 lớp bảo mật: 1. File Audio/Video có bị truy cập lậu nếu chưa mua khoá học (CORS/URL Token)? 2. Tính toàn vẹn của JWT Auth HttpOnly. 3. Phân quyền Router Vue3 giữa Teacher/Student đã bị bypass chưa? 4. Data submit có bị dính mã độc XSS vào text form môn Viết không? 5. Bảng điểm đã áp dụng Soft Delete chưa?"

**2. Prompt đóng gói Môi trường (Docker):**
> "Viết 'docker-compose.yml' định nghĩ 4 containers: Frontend (Vue3 nginx), Backend (Django), PostgreSQL và Redis. Đồng bộ tuyệt đối biến môi trường 'TZ=Asia/Ho_Chi_Minh' cho tất cả container. Soạn hướng dẫn Deploy siêu tinh gọn."

---

## NGOẠI TRUYỆN: NÂNG CẤP TÍNH NĂNG MỚI (CHẤM ĐIỂM BẰNG A.I)

**1. Prompt định hình tính năng chấm chữa bài tự động:**
> "Hệ thống LMS English đã vận hành trơn tru. Bây giờ tôi muốn thêm Module 'Chấm điểm Speaking và Writing bằng AI (API ngoài)' thay vì giáo viên chấm bằng tay. Hãy tư vấn cho tôi luồng luân chuyển dữ liệu từ người dùng (ghi âm) -> BE -> API ngoài -> BE chấm điểm -> Trả kết quả chi tiết từng lỗi ngữ pháp/phát âm cho FE. LƯU Ý, KHÔNG CODE LÚC NÀY."

**2. Prompt triển khai Module AI:**
> "Dựa trên luồng UX/UI chấm AI vừa thảo luận. Hãy phác thảo Wireframe cho Bảng báo cáo kết quả lỗi chấm Pronunciation/Grammar từ AI. Tiếp đó đóng vai Principal Architect, viết code Backend Django tích hợp logic gọi AI để trả kết quả vào hệ thống đánh giá tiến trình cũ một cách êm ái, đảm bảo giữ nguyên hệ thống cũ không bị phá vỡ."

---
---

# PHẦN 2: HOÀN THIỆN TOÀN DIỆN CÁC TÍNH NĂNG (BƯỚC 10 → 14)

> *Các BƯỚC 10-14 dưới đây kế thừa từ codebase hiện tại đã xây dựng (Backend 9 Django apps, Frontend 14 views, 5 API modules). Mỗi prompt chỉ rõ file, function, pattern cụ thể. **BẮT BUỘC** chạy BƯỚC 10 trước vì đây là bugfix nền tảng — các bước sau phụ thuộc vào kết quả của BƯỚC 10.*

```
┌───────────────────────────────────────────────────────────────────┐
│  ENGLISH STUDY — TIẾN ĐỘ HOÀN THIỆN                                │
├───────────────────────────────────────────────────────────────────┤
│ BƯỚC 10 — SỬA LỖI NỀN TẢNG (PREREQUISITE — LÀM TRƯỚC)           │
│  ☐ 10.1 Xoá double AppLayout khỏi 10 views                     │
│  ☐ 10.2 Fix VNNumberJSONRenderer envelope unwrap                 │
│  ☐ 10.3 Fix submit URLs sai trong curriculum.js                 │
│  ☐ 10.4 Tạo ExerciseResultView hiển thị điểm sau nộp bài       │
├───────────────────────────────────────────────────────────────────┤
│ BƯỚC 11 — HOÀN THIỆN 4 KỸ NĂNG (Nghe/Nói/Đọc/Viết)              │
│  ☐ 11.1 Listening: split-pane, feedback tức thì, timer          │
│  ☐ 11.2 Reading: split-pane 6:4, highlight passage              │
│  ☐ 11.3 Speaking: karaoke, AI grading poll, error UI             │
│  ☐ 11.4 Writing: zen mode, AI grading poll, rubric UI           │
│  ☐ 11.5 ExerciseResult shared component (score + CEFR + errors) │
├───────────────────────────────────────────────────────────────────┤
│ BƯỚC 12 — KHOÁ HỌC & NGỮ PHÁP & TỪ VỰNG                         │
│  ☐ 12.1 CourseDetail: enrollment, chapter tree, unlock logic     │
│  ☐ 12.2 Grammar: detail page, rules, examples, exercises        │
│  ☐ 12.3 Vocabulary: filter, word detail modal, audio playback   │
├───────────────────────────────────────────────────────────────────┤
│ BƯỚC 13 — FLASHCARDS SRS + GAMIFICATION + ASSESSMENT               │
│  ☐ 13.1 Flashcard deck browser + SM-2 study session             │
│  ☐ 13.2 Achievements / Badges / Certificates UI                 │
│  ☐ 13.3 Assessment / Exam UI (timer, auto-submit)               │
│  ☐ 13.4 Pronunciation curriculum (phoneme chart, minimal pairs) │
├───────────────────────────────────────────────────────────────────┤
│ BƯỚC 14 — PAYMENT + TEACHER + ADMIN + E2E TESTING                  │
│  ☐ 14.1 Pricing / Checkout / Coupon (VNPay flow)                │
│  ☐ 14.2 Teacher Portal (grade management, class analytics)      │
│  ☐ 14.3 Admin Panel (user/content management, analytics)        │
│  ☐ 14.4 E2E flow testing (6 luồng chính)                        │
│  ☐ 14.5 UI/UX testing checklist (responsive, dark mode, a11y)   │
└───────────────────────────────────────────────────────────────────┘
```

---
## BƯỚC 10: SỬA LỖI NỀN TẢNG (PREREQUISITE — BẮT BUỘC LÀM TRƯỚC)

> *Codebase hiện tại có 4 bug hệ thống ảnh hưởng tất cả 10 views. PHẢI fix trước khi phát triển tính năng mới.*

**1. Prompt 10.1 — Xoá Double AppLayout (10 views):**
> "Kiểm tra và sửa lỗi cấu trúc layout cho toàn bộ các trang trong hệ thống. **Vấn đề**: Trong `frontend/src/router/index.js`, tất cả route con nằm dưới `path: '/'` đều được render bên trong `components/layout/AppLayout.vue` (chứa Sidebar + Header). Tuy nhiên các views sau đang tự bọc thêm `<AppLayout>` trong template của mình, gây ra **double sidebar + double header**:
> - `views/exercise/ListeningView.vue`
> - `views/exercise/SpeakingView.vue`
> - `views/exercise/ReadingView.vue`
> - `views/exercise/WritingView.vue`
> - `views/GrammarView.vue`
> - `views/CoursesView.vue`
> - `views/CourseDetailView.vue`
> - `views/VocabularyView.vue`
> - `views/FlashcardsView.vue`
> - `views/LeaderboardView.vue`
>
> **Yêu cầu từng file**: (1) Xoá tag `<AppLayout>` wrapper trong `<template>`, thay bằng `<div>` gốc. (2) Xoá dòng `import AppLayout from '@/components/layout/AppLayout.vue'` trong `<script setup>`. (3) Kiểm tra layout không bị vỡ — mỗi view chỉ cần trả về content, AppLayout đã được router xử lý. Sau khi sửa, mở trình duyệt kiểm tra từng trang xác nhận chỉ có 1 sidebar và 1 header."

**2. Prompt 10.2 — Fix VNNumberJSONRenderer Envelope Unwrap:**
> "Backend Django sử dụng `VNNumberJSONRenderer` (`backend/utils/renderers.py`) bọc tất cả response thành công trong envelope: `{ 'success': true, 'data': <actual_payload> }`. Nhưng hầu hết code Frontend đang đọc `res.data` trực tiếp (chỉ nhận được `{ success, data }` thay vì payload thực).
>
> **Pattern sửa chuẩn** (đã áp dụng thành công cho `stores/auth.js`, `stores/dashboard.js`, `stores/notifications.js`):
> ```javascript
> // SAI:
> const res = await api.get('/some/endpoint/')
> myData.value = res.data  // ← nhận { success: true, data: {...} }
>
> // ĐÚNG:
> const res = await api.get('/some/endpoint/')
> myData.value = res.data?.data ?? res.data  // ← unwrap envelope
> ```
>
> **Áp dụng cho 10 views** — Tìm tất cả chỗ gọi API trong các file views sau và thêm unwrap envelope:
> - `ListeningView.vue`: `exercise.value = res.data` → `res.data?.data ?? res.data`
> - `SpeakingView.vue`: tương tự
> - `ReadingView.vue`: tương tự
> - `WritingView.vue`: tương tự
> - `GrammarView.vue`: `topics.value = res.data?.results || res.data || []` → cần unwrap trước: `const d = res.data?.data ?? res.data; topics.value = d?.results || (Array.isArray(d) ? d : [])`
> - `CoursesView.vue`: tương tự pattern cho list response
> - `CourseDetailView.vue`: cả `getCourse` và `getChapters` và `getLessons` đều cần unwrap
> - `VocabularyView.vue`: `words.value = res.data?.results || res.data` → cần unwrap
> - `FlashcardsView.vue`: `cards.value = res.data?.results || res.data` → cần unwrap
> - `LeaderboardView.vue`: `board.value = res.data?.results || res.data` → cần unwrap
>
> **LƯU Ý quan trọng**: Các ListAPI có pagination sẽ KHÔNG bị bọc envelope (vì response chứa key `results` hoặc `count` — renderer skip). Kiểm tra `VNNumberJSONRenderer.render()` để xác nhận: nếu data là dict chứa `results` hoặc `count`, renderer giữ nguyên, không bọc. Cần xử lý cả 2 trường hợp. Sau khi sửa, mở Network DevTools kiểm tra response thực tế từ mỗi endpoint."

**3. Prompt 10.3 — Fix Submit URLs Sai:**
> "File `frontend/src/api/curriculum.js` đang export các hàm submit với URL sai, không khớp backend:
>
> | Hàm trong curriculum.js | URL hiện tại (SAI) | URL đúng trong progress/urls.py |
> |---|---|---|
> | `submitListening` | `/progress/submit-listening/` | `/progress/submit/listening/` |
> | `submitSpeaking` | `/progress/submit-speaking/` | `/progress/submit/speaking/` |
> | `submitReading` | `/progress/submit-reading/` | `/progress/submit/reading/` |
> | `submitWriting` | `/progress/submit-writing/` | `/progress/submit/writing/` |
>
> **Cách sửa**: (1) Trong `frontend/src/api/curriculum.js`, sửa 4 URL trên cho khớp backend. (2) Hoặc tốt hơn: xoá 4 hàm `submitXxx` trong `curriculum.js` (vì `frontend/src/api/progress.js` đã export đúng `progressApi.submitListening/Reading/Speaking/Writing`). (3) Cập nhật tất cả views đang import từ `curriculum.js` sang dùng `progressApi` từ `progress.js`. (4) Kiểm tra bằng cách mở Network tab, thực hiện nộp bài, xác nhận request gửi đúng URL `/progress/submit/listening/` và nhận response 200/201."

**4. Prompt 10.4 — Tạo Màn Hình Kết Quả Bài Tập (ExerciseResultView):**
> "Hiện tại tất cả 4 views bài tập (Listening/Speaking/Reading/Writing) sau khi nộp bài đều `router.push('/dashboard')` — người dùng không biết mình được bao nhiêu điểm, đúng/sai câu nào.
>
> **Yêu cầu**: Tạo route mới `/learn/result/:submissionId` và component `views/exercise/ExerciseResultView.vue` hiển thị:
> - Điểm tổng (score) dạng vòng tròn % lớn, có hiệu ứng count-up animation
> - Trạng thái PASS/FAIL (so với ngưỡng 60%)
> - CEFR tương đương (sử dụng bảng PRD section 7.4: 0-39 Below A1, 40-59 A1, 60-74 A2, 75-84 B1, 85-92 B2, 93-100 C1/C2)
> - Nút 'Xem chi tiết' hiển thị bảng đáp án: câu hỏi — đáp án của bạn — đáp án đúng — đúng/sai (cho Listening/Reading)
> - Với Speaking/Writing: hiển thị rubric 4 tiêu chí (từ PRD section 7.1/7.2) dạng progress bar + feedback text
> - Nút 'Bài tiếp theo' (nếu passed) hoặc 'Làm lại' (nếu failed)
> - Nút 'Về Dashboard'
>
> **Backend cần bổ sung** (nếu chưa có): endpoint `GET /progress/submissions/{type}/{id}/` trả về chi tiết kết quả. File `backend/apps/progress/urls.py` đã có `submissions/speaking/<pk>/` và `submissions/writing/<pk>/` — cần thêm tương tự cho listening và reading.
>
> **Flow cập nhật**: Sau khi nộp bài thành công, `submit()` nhận response chứa `submission_id` → `router.push(\`/learn/result/\${submissionId}\`)`. Với Speaking/Writing (chấm AI async), hiển thị trạng thái 'Đang chấm...' rồi poll mỗi 3 giây tới khi `status === 'completed'`."

---
## BƯỚC 11: HOÀN THIỆN 4 KỸ NĂNG (Nghe / Nói / Đọc / Viết)

> *Nâng cấp 4 views bài tập từ bản prototype thành UI hoàn chỉnh theo PRD sections 5.2, 5.3, 5.4. Chạy từng prompt theo thứ tự.*

**1. Prompt 11.1 — Listening View Hoàn Chỉnh:**
> "Nâng cấp `frontend/src/views/exercise/ListeningView.vue` theo PRD section 5.2. Hiện tại view chỉ có audio player + danh sách câu hỏi trắc nghiệm đơn giản.
>
> **Yêu cầu nâng cấp**:
> 1. **Layout split-pane**: Trên desktop, chia 2 cột — cột trái (40%) chứa audio player + transcript (nếu có), cột phải (60%) chứa câu hỏi. Trên mobile, xếp dọc (audio trên, câu hỏi dưới).
> 2. **Audio player nâng cao**: Thêm nút Play/Pause tròn lớn, thanh progress bar có thể click seek, hiển thị thời gian hiện tại/tổng, nút tốc độ phát (0.75x / 1x / 1.25x) — sử dụng `<audio>` element có ref để control.
> 3. **Số lần nghe**: Backend trả về `max_plays` — hiển thị 'Còn X lần nghe' và disable Play khi hết lượt.
> 4. **Progress bar câu hỏi**: Thanh trên cùng hiển thị 'Câu 3/8 · Đã trả lời 2/8'.
> 5. **Instant feedback sau submit**: Thay vì redirect dashboard, gọi `progressApi.submitListening()` → nhận response score → navigate sang `/learn/result/:id` (đã tạo ở bước 10.4).
> 6. **Hỗ trợ nhiều loại câu hỏi**: PRD nói có 3 loại: trắc nghiệm (multiple choice), điền chỗ trống (gap fill), kéo thả (drag & drop). Script setup cần method `questionComponent(type)` trả về component tương ứng.
> 7. **Timer (tùy chọn)**: Nếu `exercise.time_limit` > 0, hiển thị đồng hồ đếm ngược, tự động submit khi hết giờ.
>
> **API liên quan**: `GET /exercises/listening/:id/` (backend `apps/exercises/urls.py`) trả exercise object chứa `audio_url`, `questions[]`, `max_plays`, `time_limit`. Submit: `POST /progress/submit/listening/` payload `{ lesson_id, exercise_id, answers: { question_id: selected_option_id } }`.
>
> **Kết quả mong đợi**: Trang luyện nghe có UX chuyên nghiệp, audio player mượt mà, progress tracking real-time, feedback trực quan sau nộp bài."

**2. Prompt 11.2 — Reading View Split-Pane:**
> "Nâng cấp `frontend/src/views/exercise/ReadingView.vue` theo PRD section 5.2 — giao diện desktop hiện tại bị dài dọc, chữ sát nhau gây mỏi mắt.
>
> **Yêu cầu nâng cấp**:
> 1. **Split-pane layout 6:4**: Desktop — pane trái (60%) hiển thị passage với typography dễ đọc (font-size 15px, line-height 1.8, padding thoáng), pane phải (40%) chứa câu hỏi với scroll độc lập. Mobile — xếp dọc, passage trên + câu hỏi dưới.
> 2. **Passage highlight**: Khi user click vào câu hỏi, highlight đoạn passage liên quan (nếu question có trường `passage_ref_start/end`). Dùng CSS `background: rgba(99,102,241,0.15)` cho đoạn highlight.
> 3. **Progress sidebar**: Bên phải thanh câu hỏi hiển thị navigation dots — mỗi dot là 1 câu, click nhảy tới câu đó, đổi màu khi đã trả lời.
> 4. **Toolbar trên passage**: Nút tăng/giảm cỡ chữ, nút bật/tắt highlight mode.
> 5. **Submit flow**: Giống 11.1 — gọi `progressApi.submitReading()` → navigate sang ExerciseResultView.
>
> **API**: `GET /exercises/reading/:id/` trả `{ passage, questions[], time_limit }`. `POST /progress/submit/reading/`.
>
> **Kỹ thuật CSS**: Dùng CSS Grid `grid-template-columns: 6fr 4fr` cho desktop, `grid-template-columns: 1fr` cho mobile. Mỗi pane có `overflow-y: auto; max-height: calc(100vh - 120px)` để scroll độc lập."

**3. Prompt 11.3 — Speaking View với Karaoke & AI Grading:**
> "Nâng cấp `frontend/src/views/exercise/SpeakingView.vue` theo PRD section 5.3. Hiện tại chỉ có nút ghi âm và nút nộp. Cần trải nghiệm luyện nói nhập vai chuyên nghiệp.
>
> **Yêu cầu nâng cấp**:
> 1. **Karaoke sentence display**: Backend trả `target_sentence` — hiển thị từng từ trong câu, khi user nói (real-time hoặc sau playback), highlight từ đang nói ở màu xanh, từ đã nói ở màu mờ. Nếu chưa tích hợp real-time recognition, hiển thị static target sentence dạng thẻ lớn + nút audio mẫu.
> 2. **Audio mẫu**: Nếu exercise có `sample_audio_url`, hiển thị nút '🔊 Nghe mẫu' để user nghe trước khi ghi âm.
> 3. **Recorder cải tiến**: Nút ghi âm tròn lớn (80px), hiệu ứng pulse animation khi đang ghi, hiển thị waveform đơn giản (canvas bars animation dùng `AnalyserNode` từ Web Audio API). Hiển thị thời gian ghi `00:15s / 60s`.
> 4. **Playback review**: Sau khi ghi xong, hiển thị player mini để user nghe lại bản ghi, nút 'Ghi lại' và 'Nộp bài'.
> 5. **AI Grading poll loop**: Sau khi nộp (`POST /progress/submit/speaking/` với FormData chứa audio file), backend trả `{ submission_id, status: 'pending' }`. Frontend poll `GET /progress/submissions/speaking/:id/` mỗi 3 giây. Hiển thị animation 'Đang phân tích phát âm...' với spinner. Khi `status === 'completed'`, navigate sang ExerciseResultView.
> 6. **Pronunciation error UI** (trong ExerciseResultView): Backend trả `error_list_json` dạng `[{ word: 'through', user_ipa: '/θruː/', expected_ipa: '/θruː/', score: 45, feedback: 'Chú ý âm th' }]`. Hiển thị bảng từng từ với điểm và feedback.
>
> **Backend FormData**: `exercise_id`, `audio_file` (Blob webm/mp3), `lesson_id`.
>
> **LƯU Ý bảo mật**: Trên component unmount (`onBeforeUnmount`), phải stop `MediaRecorder` và release stream (`stream.getTracks().forEach(t => t.stop())`) để tránh leak microphone. Code hiện tại đã có nhưng kiểm tra lại."

**4. Prompt 11.4 — Writing View Zen Mode & AI Grading:**
> "Nâng cấp `frontend/src/views/exercise/WritingView.vue` theo PRD section 5.4. Hiện tại chỉ có textarea + đếm từ. Cần bổ sung Zen mode và flow chấm AI.
>
> **Yêu cầu nâng cấp**:
> 1. **Zen mode editor**: Nút toggle '☯ Zen mode' — khi bật, ẩn sidebar + header (emit event lên AppLayout hoặc dùng Pinia store), textarea full-screen với background gradient nhẹ, font serif 18px, chỉ hiển thị đề bài + textarea + word count + nút Thoát. Mục đích: giúp tập trung viết.
> 2. **Real-time word count nâng cao**: Hiển thị `42/150 từ` với progress bar. Đổi màu: đỏ khi < min_words, xanh khi đạt min_words, vàng khi vượt max_words.
> 3. **Smart toolbar**: Các nút Bold/Italic/Heading (không cần rich text editor — chỉ là gợi ý formatting). Nút 'Lưu nháp' lưu `localStorage`.
> 4. **Draft auto-save**: Tự động lưu nội dung vào `localStorage` mỗi 30s với key `draft_writing_{exercise_id}`. Khi mở lại bài, hỏi 'Bạn có bản nháp chưa hoàn thành. Tiếp tục?'.
> 5. **AI Grading poll** (giống Speaking): Submit → poll `/progress/submissions/writing/:id/` → khi completed, navigate sang ExerciseResultView.
> 6. **Writing rubric UI** (trong ExerciseResultView): Backend trả `detail_json` chứa 4 tiêu chí theo PRD section 7.2: Task Achievement (25%), Grammar (30%), Vocabulary (25%), Coherence (20%). Mỗi tiêu chí hiển thị progress bar + điểm + feedback text. Hiển thị thêm `feedback_text` tổng quan và `error_list_json` (lỗi ngữ pháp/từ vựng highlight).
>
> **API**: `POST /progress/submit/writing/` payload `{ exercise_id, lesson_id, content_text }`. Response: `{ submission_id, word_count, status: 'pending' }`. Poll: `GET /progress/submissions/writing/:id/`."

**5. Prompt 11.5 — Tạo Shared ExerciseResult Component:**
> "Tạo component dùng chung `frontend/src/components/exercise/ExerciseResult.vue` được sử dụng bởi `ExerciseResultView.vue` (đã tạo ở bước 10.4). Component nhận props:
>
> ```typescript
> props: {
>   type: 'listening' | 'speaking' | 'reading' | 'writing',
>   score: number,            // 0-100
>   passed: boolean,          // score >= 60
>   maxScore: number,         // 100
>   answers?: Array<{ question_id, user_answer, correct_answer, is_correct }>,  // L/R
>   rubric?: Array<{ criterion, weight, score, feedback }>,                      // S/W
>   errorList?: Array<{ word, feedback, score }>,                                  // S
>   feedbackText?: string,    // W
>   cefrEquivalent?: string,  // Mapped from score
>   nextLessonId?: number,
> }
> ```
>
> **UI layout**:
> 1. **Score circle** (trên cùng, giữa): Vòng tròn SVG lớn (200px) hiển thị % với count-up animation từ 0 → score trong 1.5s, màu gradient theo điểm (đỏ → cam → xanh lá). Text lớn bên trong: `78%`. Badge PASS ✓ hoặc FAIL ✗ bên dưới.
> 2. **CEFR badge**: Hiển thị 'Tương đương CEFR: B1' dạng badge pill.
> 3. **Tab chi tiết**: (a) Tab 'Đáp án' (Listening/Reading): bảng câu hỏi + đáp án đúng/sai, icon ✓/✗ mỗi dòng. (b) Tab 'Rubric' (Speaking/Writing): 4 progress bars theo tiêu chí. (c) Tab 'Lỗi phát âm' (Speaking): bảng từ + IPA + feedback.
> 4. **Action buttons**: 'Bài tiếp theo' (primary, nếu passed) | 'Làm lại' (secondary, nếu failed) | 'Về Dashboard' (text link).
>
> Component này dùng `<Transition>` cho animation, dùng CEFR mapping table từ PRD: `{ 0-39: 'Below A1', 40-59: 'A1', 60-74: 'A2', 75-84: 'B1', 85-92: 'B2', 93-100: 'C1-C2' }`."

---
## BƯỚC 12: KHOÁ HỌC & NGỮ PHÁP & TỪ VỰNG

> *Hoàn thiện 3 trang nội dung học thuật chính. Mỗi trang cần kết nối đúng API backend đã có.*

**1. Prompt 12.1 — CourseDetailView Hoàn Chỉnh:**
> "Nâng cấp `frontend/src/views/CourseDetailView.vue` thành trang chi tiết khoá học hoàn chỉnh. View hiện tại đã có cấu trúc cơ bản (header + chapter accordion + lesson list). Cần bổ sung:
>
> 1. **Enrollment flow**: Nút 'Đăng ký học' gọi `progressApi.enrollCourse(courseId)` (`POST /progress/enroll/`). Sau khi enroll thành công: (a) cập nhật `course.is_enrolled = true`, (b) invalidate dashboard store (`dashboard.invalidate()`) để dashboard fetch lại, (c) hiển thị toast '✓ Đăng ký thành công!'.
> 2. **Unlock status trên lesson**: Backend trả `progress_status` cho mỗi lesson: `'locked'` / `'available'` / `'completed'`. Hiển thị icon: 🔒 locked (opacity 50%, không click được), ▶ available (highlight border), ✅ completed (text xanh). Logic: lesson chỉ available khi lesson trước đó đã completed với score >= 60%.
> 3. **Course progress card**: Hiển thị progress bar toàn khoá (% lessons completed), số bài đã hoàn thành / tổng, điểm trung bình toàn khoá.
> 4. **Chapter auto-load lessons**: Khi mở accordion chapter, `watch` trigger API `curriculumApi.getLessons(courseId, chapterId)`. Hiện tại đã có nhưng cần thêm unwrap envelope + cache (không gọi lại nếu đã load).
> 5. **Lesson exercise type icons**: Mỗi lesson hiển thị icon theo `exercise_type`: 🎧 listening, 🎤 speaking, 📄 reading, ✍️ writing. Đã có `lessonIcon()` function — verify nó hoạt động đúng.
>
> **API Backend**: `GET /curriculum/courses/:id/` → course detail. `GET /curriculum/courses/:id/chapters/` → chapters list. `GET /curriculum/courses/:id/chapters/:chapterId/lessons/` → lessons list. Tất cả có thể bị bọc envelope — phải unwrap.
>
> **Responsive**: Trên mobile, chapter accordion chiếm full width, lesson item có padding lớn hơn để dễ tap."

**2. Prompt 12.2 — Grammar Detail Page:**
> "Hoàn thiện tính năng Ngữ pháp. Hiện tại `frontend/src/views/GrammarView.vue` chỉ hiển thị danh sách topic dạng accordion (mở/đóng). Cần:
>
> 1. **GrammarView (danh sách)**: Thêm filter theo CEFR level (A1-C1) dạng pills (giống CoursesView). Thêm ô tìm kiếm debounce. Mỗi topic card hiển thị: tên topic, level badge, số rules, icon trạng thái (đã học/chưa).
> 2. **GrammarDetailView (trang mới)**: Tạo `views/GrammarDetailView.vue` + route `/grammar/:slug`. Gọi `GET /grammar/:slug/` → nhận chi tiết topic gồm:
>    - `summary`: mô tả ngắn chủ điểm
>    - `rules[]`: danh sách quy tắc, mỗi rule có `title`, `explanation`, `examples[]`, `exceptions[]`
>    - `exercises[]`: bài tập ngữ pháp thuộc topic
> 3. **Rule card UI**: Mỗi quy tắc hiển thị trong card đẹp: tiêu đề bold, phần giải thích, bảng ví dụ (câu đúng ✓ xanh / câu sai ✗ đỏ), phần ngoại lệ (collapsible).
> 4. **Practice exercises**: Dưới phần rules, hiển thị mini quiz (trắc nghiệm ngữ pháp) — user chọn đáp án, hiển thị kết quả ngay (instant feedback, không cần submit lên server).
> 5. **Breadcrumb**: `Ngữ pháp > Present Simple` — click quay lại danh sách.
>
> **Router**: Thêm route `{ path: 'grammar/:slug', name: 'grammar-detail', component: () => import('@/views/GrammarDetailView.vue'), meta: { title: 'Chi tiết ngữ pháp' } }` trong `router/index.js` dưới children của AppLayout.
>
> **Backend API**: `GET /grammar/` → list topics (paginated). `GET /grammar/:slug/` → topic detail với rules + exercises. URLs đã có trong `backend/apps/grammar/urls.py`."

**3. Prompt 12.3 — Vocabulary Browser Nâng Cấp:**
> "Nâng cấp `frontend/src/views/VocabularyView.vue` từ grid cơ bản thành Vocabulary Browser đầy đủ theo PRD section 5.5.
>
> 1. **Filter bar**: Bổ sung bộ lọc: (a) CEFR Level pills (A1-C1), (b) Domain/Topic dropdown (Technology, Business, Health...), (c) Part of speech (noun, verb, adj...). Gửi params: `GET /vocabulary/words/?search=xxx&level=A2&domain=technology&pos=noun`.
> 2. **Word card nâng cao**: Mỗi card hiển thị: word (bold), phonetic IPA, part of speech badge, nghĩa tiếng Việt (line-clamp-2).
> 3. **Word Detail Modal**: Click vào word card → mở modal/drawer hiển thị:
>    - Phát âm UK/US: hai nút audio (nếu `pronunciation_uk_url` / `pronunciation_us_url` có sẵn, dùng `new Audio(url).play()`)
>    - IPA transcription
>    - Tất cả definitions (có thể nhiều nghĩa)
>    - Example sentences (highlight từ mục tiêu bằng `<mark>`)
>    - Nút '+ Thêm vào Flashcard' → gọi API tạo flashcard
>    - Synonyms / Antonyms (nếu có)
> 4. **Infinite scroll hoặc Load more**: Thay vì `limit: 30` cố định, dùng pagination — nút 'Xem thêm' load trang tiếp.
> 5. **Audio inline**: Trên card (ngoài modal), nút nhỏ 🔊 bên cạnh phonetic — click phát audio nhanh.
>
> **Backend API**: `GET /vocabulary/words/` (có filter params) → paginated list. `GET /vocabulary/words/:id/` → word detail. Backend `apps/vocabulary/urls.py` đã có cả 2 endpoint."

---
## BƯỚC 13: FLASHCARDS SRS + GAMIFICATION + ASSESSMENT

> *Xây dựng 4 module tính năng nâng cao hoàn toàn mới.*

**1. Prompt 13.1 — Flashcard Deck Browser & SM-2 Study Session:**
> "Nâng cấp hệ thống Flashcard theo PRD section 5.8. Hiện tại `FlashcardsView.vue` chỉ có 1 trang flat load tất cả cards. Cần chia thành 2 views:
>
> **A. FlashcardDecksView (mới)** — Route `/flashcards`:
> - Gọi `GET /vocabulary/flashcard-decks/` → danh sách deck
> - Mỗi deck card hiển thị: tên deck, CEFR level badge, progress bar (số card đã thuộc / tổng), số card cần ôn hôm nay (due_count), nút 'Học ngay'
> - Filter: theo CEFR level, theo domain
> - Nút '+ Tạo deck mới' (nếu có API)
> - Grid layout responsive: 1 cột mobile → 2 cột tablet → 3 cột desktop
>
> **B. FlashcardStudyView (mới)** — Route `/flashcards/:deckId/study`:
> - Gọi `GET /vocabulary/flashcard-decks/:deckId/study/` → lấy danh sách cards cần review (SM-2 algorithm chọn trên backend)
> - **Card flip animation**: Mặt trước: từ tiếng Anh lớn + IPA + audio button. Mặt sau: nghĩa Việt + example sentence + hình ảnh (nếu có). Flip bằng CSS 3D transform (code hiện tại đã có animation cơ bản).
> - **Rating buttons (SM-2)**: 4 nút: 'Quên' (quality=1), 'Khó' (quality=2), 'Nhớ' (quality=4), 'Dễ' (quality=5). Gọi `POST /vocabulary/flashcards/sm2/` payload `{ flashcard_id, quality }`.
> - **Session stats bar**: Thanh trên cùng hiển thị: `Mới: 5 | Ôn lại: 12 | Hoàn thành: 3/17`. Progress bar tổng.
> - **Session complete screen**: Khi hết cards, hiển thị: 'Phiên học hoàn tất! 🎉', thống kê (bao nhiêu card review, accuracy %, time spent), nút 'Quay lại Decks'.
>
> **Router**: Sửa route `/flashcards` trỏ tới FlashcardDecksView. Thêm `/flashcards/:deckId/study` trỏ tới FlashcardStudyView.
>
> **API**: `GET /vocabulary/flashcard-decks/` → list decks. `GET /vocabulary/flashcard-decks/:id/study/` → due cards. `POST /vocabulary/flashcards/sm2/` → update SM-2 record."

**2. Prompt 13.2 — Achievements & Badges UI:**
> "Tạo trang AchievementsView theo PRD section 5.11. Hiện chưa có view — cần tạo mới.
>
> **A. AchievementsView** — Route `/achievements`:
> - Gọi `gamificationApi.getAchievements()` → tất cả achievements (kể cả chưa đạt)
> - Gọi `gamificationApi.getMyAchievements()` → achievements user đã đạt
> - **Layout lưới**: Grid 3×N displaying badge cards. Badge đã đạt: full color, shimmer border animation, ngày đạt. Badge chưa đạt: grayscale, opacity 50%, tooltip mô tả điều kiện.
> - **Categories**: Chia theo nhóm: 'Streak' (streak 7/30/100 ngày), 'Skill' (hoàn thành X bài listening/speaking/...), 'Level' (đạt A2, B1...), 'Social' (top 3 leaderboard)
> - **Progress hint**: Badge chưa đạt hiển thị progress bar nhỏ: 'Streak 7 ngày: 5/7'
>
> **B. CertificatesView** — Route `/certificates`:
> - Gọi `gamificationApi.getCertificates()` → list chứng chỉ user đã đạt
> - Mỗi certificate card: Tên chứng chỉ, cấp độ CEFR, ngày cấp, nút '📥 Tải PDF'
> - Design: Card nền gradient gold/silver, border premium
>
> **Router**: Thêm 2 route con trong AppLayout children.
>
> **Sidebar**: Thêm vào `AppSidebar.vue` navGroups mục 'Thành tựu' với items: `{ to: '/achievements', icon: '🏅', label: 'Thành tựu' }` và `{ to: '/certificates', icon: '📜', label: 'Chứng chỉ' }`.
>
> **API Backend**: `GET /gamification/achievements/` → all. `GET /gamification/my-achievements/` → user achieved. `GET /gamification/certificates/` → user certificates. URLs đã có trong `backend/apps/gamification/urls.py`."

**3. Prompt 13.3 — Assessment / Exam UI:**
> "Tạo module Assessment/Exam hoàn chỉnh theo PRD section 5.6. Hiện Frontend chưa có bất kỳ view nào cho exam. Cần tạo mới hoàn toàn.
>
> **A. Backend API cần kiểm tra/bổ sung**: Xác nhận `backend/apps/exercises/` có models ExamSet, Question, QuestionOption. Endpoint cần có: `GET /exercises/exams/` → list available exams. `GET /exercises/exams/:id/` → exam detail (questions + time_limit). `POST /progress/submit/exam/` → submit all answers. Nếu chưa có, bổ sung endpoint trong `exercises/urls.py` và `progress/urls.py`.
>
> **B. ExamListView** — Route `/assessments`:
> - List exams grouped by type: 'Progress Check' (bắt buộc sau mỗi Chapter), 'Mock Test' (tuỳ chọn), 'Placement Test' (1 lần đầu)
> - Mỗi exam card: Tên, loại, thời gian, số câu, trạng thái (Chưa làm / Đã hoàn thành + score)
> - Badge 'Bắt buộc' cho Progress Check
>
> **C. ExamView** — Route `/assessments/:id`:
> - **Header**: Tên bài thi + timer đếm ngược lớn (mm:ss), tự động submit khi hết giờ
> - **Section navigation**: Nếu exam có sections (Listening → Reading → Grammar), tab bar chuyển section. Mỗi section có trang câu hỏi riêng.
> - **Question navigation**: Panel bên phải hiển thị grid số câu (1-40), click nhảy tới câu đó. Màu: trắng=chưa trả lời, xanh=đã trả lời, đỏ=đã flag.
> - **Flag question**: Nút cờ ⚑ để đánh dấu câu cần xem lại.
> - **Auto-save**: Mỗi 30s lưu đáp án vào `localStorage`, phòng tắt tab. Khi mở lại, hỏi 'Tiếp tục bài thi?'.
> - **Submit confirmation**: Modal 'Bạn đã trả lời 35/40 câu, còn 5 câu chưa trả lời. Nộp bài?'
> - **Result**: Navigate sang ExerciseResultView sau submit.
>
> **Router**: Thêm `/assessments` và `/assessments/:id` trong AppLayout children. Thêm sidebar item."

**4. Prompt 13.4 — Pronunciation Curriculum:**
> "Tạo module Pronunciation theo PRD section 5.7. Đây là tính năng học phát âm 4 giai đoạn.
>
> **A. Backend kiểm tra**: App `pronunciation` không tồn tại trong backend (chưa có folder). Cân nhắc 2 cách: (1) Tạo Django app `pronunciation` mới, (2) Tích hợp vào app `vocabulary` hoặc `exercises`. Khuyến nghị: tạo app mới với models: `PronunciationStage`, `PhonemeLesson`, `MinimalPairSet`. Endpoints: `GET /pronunciation/stages/` → 4 stages. `GET /pronunciation/stages/:id/lessons/` → phoneme lessons. `GET /pronunciation/minimal-pairs/:id/` → minimal pair exercise.
>
> **B. PronunciationView** — Route `/pronunciation`:
> - **Phoneme Chart interactive** (giống bảng IPA): Grid hiển thị tất cả phonemes (vowels + consonants). Click vào phoneme → phát audio mẫu + hiển thị môi hình (mouth diagram image). Dùng dữ liệu từ thư mục `source/`.
> - **4 Stage progression**: Cards hiển thị 4 giai đoạn: Stage 1 Monophthongs, Stage 2 Consonants, Stage 3 Diphthongs, Stage 4 Advanced (Connected Speech). Mỗi stage : progress %, các bài đã/chưa hoàn thành.
> - **Minimal Pair Exercise**: Phát 2 audio: 'ship' vs 'sheep'. User chọn đúng/sai. Instant feedback.
>
> **Router**: Thêm `/pronunciation` route + sidebar item.
>
> **LƯU Ý**: Đây là module phức tạp — có thể làm phiên bản MVP trước (chỉ IPA chart + audio playback) rồi bổ sung exercises sau."

---
## BƯỚC 14: PAYMENT + TEACHER + ADMIN + E2E TESTING

> *Hoàn thiện 3 portal và quy trình kiểm tra toàn diện.*

**1. Prompt 14.1 — Pricing & Checkout & Coupon:**
> "Tạo module Payment theo PRD section 5.9 và luồng VNPay trong `docs/api-spec.md`.
>
> **A. PricingView** — Route `/pricing` (public, không cần login):
> - 3 card so sánh gói: Demo (miễn phí, giới hạn 2 khoá A1), Tháng (199k/tháng, full access), Năm (1.499k/năm, tiết kiệm 37%)
> - Bảng so sánh tính năng: ✓/✗ cho mỗi feature (AI Grading, Flashcards SRS, Certificate, Priority Support)
> - Nút CTA 'Đăng ký ngay' → navigate sang CheckoutView
> - Design: Card gói Năm có badge 'Phổ biến nhất', border gradient gold
>
> **B. CheckoutView** — Route `/checkout/:planId`:
> - Hiển thị chi tiết gói đã chọn (tên, giá, thời hạn)
> - Ô nhập mã giảm giá: `POST /payments/coupons/validate/` → hiển thị giá sau giảm
> - Chọn phương thức thanh toán: VNPay / Stripe cards
> - Nút 'Thanh toán' → `POST /payments/checkout/` payload `{ plan_id, gateway, coupon_code }` → nhận `{ payment_url }` → `window.location.href = payment_url` redirect sang cổng thanh toán
> - Trang 'Đang xử lý...' khi chờ redirect
>
> **C. PaymentSuccessView** — Route `/payment/success`:
> - Kiểm tra `account_type` từ auth store (gọi lại `auth.refreshUser()`)
> - Hiển thị: '🎉 Thanh toán thành công! Tài khoản đã được nâng cấp Premium.'
> - Confetti animation + nút 'Bắt đầu học ngay'
>
> **API Backend**: `GET /payments/plans/` → list plans. `POST /payments/coupons/validate/`. `POST /payments/checkout/`. Webhook VNPay: `POST /payments/webhooks/vnpay/` (server-to-server). URLs trong `apps/payments/urls.py`.
>
> **Router**: Thêm `/pricing`, `/checkout/:planId`, `/payment/success`. Pricing là route public (thêm `meta: { public: true }`)."

**2. Prompt 14.2 — Teacher Portal:**
> "Tạo Teacher Portal theo PRD section 6.6. Đây là portal riêng cho giáo viên quản lý lớp và chấm bài.
>
> **A. Router setup**: Tạo route group `/teacher/*` với guard `meta: { requiresAuth: true, roles: ['teacher', 'admin'] }`. Cập nhật auth guard trong `router/index.js` để kiểm tra `auth.user.role`.
>
> **B. TeacherDashboardView** — Route `/teacher`:
> - Tổng quan: số lớp quản lý, số bài cần chấm (Speaking/Writing pending), số học sinh
> - Biểu đồ: điểm trung bình lớp theo thời gian, phân bố điểm
>
> **C. TeacherGradingView** — Route `/teacher/grading`:
> - Danh sách bài cần chấm: bảng DataTable có sort/search/filter
> - Columns: Học sinh, Bài tập, Loại (Speaking/Writing), Ngày nộp, Trạng thái
> - Click vào → mở panel chấm điểm: nghe audio (Speaking) hoặc đọc text (Writing), form nhập điểm + nhận xét + ghi chú
> - Nút 'Chấm' submit → update ExerciseResult trên backend
>
> **D. TeacherClassView** — Route `/teacher/classes/:id`:
> - Danh sách học sinh trong lớp, tiến độ mỗi người
> - Bảng điểm: học sinh × bài tập, hiển thị điểm
>
> **Backend API cần kiểm tra**: `apps/classes/` (chưa rõ có app không — kiểm tra). Cần endpoints: `GET /teacher/classes/`, `GET /teacher/grading-queue/`, `POST /teacher/grade/:submissionId/`."

**3. Prompt 14.3 — Admin Panel:**
> "Tạo Admin Panel theo PRD section 6.6. Admin quản lý toàn bộ hệ thống.
>
> **A. Router setup**: Route group `/admin/*` với guard `roles: ['admin']`.
>
> **B. AdminDashboardView** — Route `/admin`:
> - KPI cards: Tổng users, Revenue tháng, Bài nộp trong ngày, Active users
> - Charts: User growth (line chart), Revenue (bar chart), Top courses (pie chart)
> - Recent activity log: 10 sự kiện mới nhất (signup, payment, submission)
>
> **C. AdminUsersView** — Route `/admin/users`:
> - DataTable: email, tên, role, account_type, ngày tạo, trạng thái
> - Actions: Edit role, Ban/Unban, View detail
> - Search + filter by role/account_type/level
>
> **D. AdminContentView** — Route `/admin/content`:
> - Quản lý Courses: add/edit/delete
> - Quản lý Lessons: assign exercises, upload audio/images
> - Question Bank: add/edit questions for exams
>
> **Backend**: Sử dụng `AdminUserListSerializer` (đã có trong `users/serializers.py`). Cần endpoints admin-specific. Nhiều view cũ (trong `old_system/admin/`) có thể tham khảo UI.
>
> **LƯU Ý**: Admin Panel phức tạp — có thể dùng Django Admin mặc định cho phase 1, chỉ tạo custom Vue admin cho analytics dashboard."

**4. Prompt 14.4 — E2E Flow Testing (6 luồng chính):**
> "Viết test script hoặc checklist kiểm tra 6 luồng End-to-End chính. Mỗi luồng cần kiểm tra từ click đầu tiên đến kết quả cuối cùng. Sử dụng trình duyệt + Network DevTools để xác nhận.
>
> **Luồng 1 — Đăng ký & Onboarding:**
> ```
> 1. Mở /register → điền form (email, password, first_name, last_name)
> 2. Submit → xác nhận 201 Created + auto-login (JWT cookie set)
> 3. Redirect → /dashboard → kiểm tra tên hiển thị đúng
> 4. Sidebar hiển thị displayName + avatar initials
> 5. Logout → redirect /login → re-login → dashboard hiển thị data
> ```
>
> **Luồng 2 — Enroll & Learn Listening:**
> ```
> 1. /courses → filter A1 → click khoá học → /courses/:id
> 2. Click 'Đăng ký học' → 200 → badge ✓ Đã đăng ký
> 3. Mở Chapter 1 → click Lesson 1 (Listening) → /learn/listening/:id
> 4. Kiểm tra audio player load (Network: GET /exercises/listening/:id ← 200)
> 5. Nghe audio, chọn đáp án → click 'Nộp bài'
> 6. Network: POST /progress/submit/listening/ ← 200, response có score
> 7. Redirect → /learn/result/:id → hiển thị điểm + PASS/FAIL
> 8. Click 'Bài tiếp theo' → verify lesson tiếp available
> ```
>
> **Luồng 3 — Speaking + AI Grading:**
> ```
> 1. /learn/speaking/:id → xác nhận đề bài load
> 2. Click ghi âm → cho phép microphone → nói 10s → stop
> 3. Nghe lại → click 'Nộp bài'
> 4. Network: POST /progress/submit/speaking/ (FormData) ← 200 { submission_id, status: 'pending' }
> 5. Hiển thị 'Đang phân tích...' → poll GET /progress/submissions/speaking/:id
> 6. Khi status=completed → navigate /learn/result/:id → hiển thị rubric
> ```
>
> **Luồng 4 — Writing + AI Grading:**
> ```
> 1. /learn/writing/:id → xác nhận prompt load, word count = 0
> 2. Viết 150 từ → kiểm tra word count cập nhật real-time
> 3. Nộp bài → poll → completed → result page hiển thị 4 tiêu chí
> ```
>
> **Luồng 5 — Flashcard SM-2 Session:**
> ```
> 1. /flashcards → chọn deck → /flashcards/:deckId/study
> 2. Flip card → xem mặt sau → click 'Nhớ' (quality=4)
> 3. Card tiếp theo load → lặp lại → session complete screen
> 4. Quay lại /flashcards → due_count giảm
> ```
>
> **Luồng 6 — Payment VNPay:**
> ```
> 1. /pricing → chọn gói Tháng → /checkout/:planId
> 2. Nhập coupon → validate → giá giảm
> 3. Click Thanh toán → redirect VNPay (sandbox)
> 4. Hoàn thành → redirect /payment/success → account_type = premium
> 5. Kiểm tra: các tính năng premium unlock, giao diện badge Premium hiển thị
> ```
>
> Với **mỗi luồng**: ghi lại Network requests (URL, status code, response body), screenshot trạng thái UI, confirm không có console errors."

**5. Prompt 14.5 — UI/UX Testing Checklist:**
> "Chạy kiểm tra UI/UX toàn diện cho tất cả các trang đã xây dựng. Test trên 3 viewport: Mobile (375px), Tablet (768px), Desktop (1440px). Checklist:
>
> **A. Responsive (mỗi trang)**:
> - [ ] Mobile: sidebar ẩn, hamburger menu mở được, content không overflow
> - [ ] Tablet: sidebar collapsed (chỉ icon), nội dung chiếm full width
> - [ ] Desktop: sidebar expanded, layout 2/3 column nếu có
> - [ ] Text không bị cắt, hình ảnh scale đúng, nút đủ to để tap (min 44px)
>
> **B. Dark Mode consistency**:
> - [ ] Tất cả text dùng CSS variable (`--color-text-base`, `--color-text-muted`, `--color-text-soft`)
> - [ ] Background dùng `--color-surface`, `--color-surface-02`, `--color-surface-03`, `--color-surface-04`
> - [ ] Không có text trắng trên nền trắng hoặc đen trên nền đen
> - [ ] Focus ring visible trên tất cả interactive elements
>
> **C. Loading States**:
> - [ ] Mỗi trang có skeleton loading (đã verify: Dashboard, Courses, Grammar, Vocab, Flashcards, Leaderboard đều có)
> - [ ] Nút submit disabled khi đang loading + hiển thị spinner text
> - [ ] Error state: hiển thị message + nút 'Thử lại'
> - [ ] Empty state: hiển thị icon + message thân thiện (đã verify: 'Không tìm thấy...', 'Chưa có dữ liệu...')
>
> **D. Form Validation**:
> - [ ] Login: email format, password min 6 ký tự, error per-field
> - [ ] Register: email format, password Django strict validation, Vietnamese error messages
> - [ ] Profile edit: field validation, success/error feedback
> - [ ] Writing: min/max word count enforcement
> - [ ] Coupon: validate before checkout
>
> **E. Navigation & Links**:
> - [ ] Sidebar: tất cả link navigate đúng, active state highlight đúng route
> - [ ] Breadcrumb: quay lại trang trước đúng
> - [ ] Back buttons: '← Quay lại' hoạt động đúng
> - [ ] 404: route không tồn tại → redirect /dashboard
> - [ ] Auth guard: truy cập trang protected khi chưa login → redirect /login → sau login → redirect lại trang ban đầu (query `?redirect=`)
>
> **F. Accessibility cơ bản**:
> - [ ] Tất cả `<button>` và `<input>` có thể focus bằng Tab
> - [ ] Radio buttons trong bài tập có label click được
> - [ ] Hình ảnh có alt text
> - [ ] Color contrast ratio >= 4.5:1 cho text chính
>
> Ghi log kết quả mỗi mục: PASS / FAIL + screenshot nếu fail. Liệt kê bug cần fix."

---
---

# PHẦN 3: CÔNG CỤ SINH DỮ LIỆU TỪ VỰNG (VOCABULARY SEED GENERATOR)

> *Dùng khi cần bổ sung từ vựng vào từ điển hệ thống. Fixture đầu ra phải khớp chính xác với Django model `apps/vocabulary/models.Word` và có thể nạp trực tiếp bằng `manage.py loaddata`.*

---

## PROMPT SINH TỪ VỰNG (TEMPLATE CHÍNH)

> **Hướng dẫn sử dụng**: Sao chép prompt bên dưới, điền vào 5 tham số trong `[THAM SỐ]`, gửi cho AI. Kết quả nhận về là file JSON fixture sẵn sàng dùng.

```
Tôi cần sinh [SỐ TỪ] từ vựng tiếng Anh theo các tiêu chí sau:

- Lĩnh vực (domain): [LĨNH VỰC]
- Cấp độ CEFR (cefr_level): [CẤP ĐỘ]
- Từ loại (part_of_speech): [TỪ LOẠI]
- Ngữ cảnh sử dụng (register): [NGỮ CẢNH]

Yêu cầu đầu ra: Django JSON fixture, mỗi từ phải có đầy đủ tất cả các trường dưới đây (không bỏ trống trừ các trường có ghi "nullable"):

Cấu trúc mỗi object:
{
  "model": "vocabulary.word",
  "pk": [SỐ THỨ TỰ TIẾP THEO — bắt đầu từ [PK_START]],
  "fields": {
    "word": "<từ tiếng Anh>",
    "part_of_speech": "<noun | verb | adjective | adverb | phrase | other>",
    "cefr_level": "<A1 | A2 | B1 | B2 | C1>",
    "domain": "<general | everyday | business | technology | academic | medical | health | travel | food | vegetables | animals | nature | art>",
    "ipa_uk": "<IPA UK>",
    "ipa_us": "<IPA US — nếu khác UK, không thì trùng>",
    "audio_uk_s3_key": null,
    "audio_us_s3_key": null,
    "meaning_vi": "<nghĩa tiếng Việt ngắn gọn, 3-8 từ>",
    "definition_en": "<định nghĩa tiếng Anh đầy đủ, 1 câu>",
    "example_en": "<câu ví dụ tiếng Anh tự nhiên, chứa đúng từ đó>",
    "example_vi": "<dịch câu ví dụ sang tiếng Việt>",
    "collocations_json": ["<cụm 1>", "<cụm 2>", "<cụm 3>"],
    "synonyms_json": ["<từ 1>", "<từ 2>", "<từ 3>"],
    "antonyms_json": ["<từ 1>", "<từ 2>"],
    "mnemonic": "<câu gợi nhớ tiếng Việt — nullable nếu không có>",
    "frequency_rank": <số nguyên 100-9999>,
    "register": "<formal | informal | slang | academic | null>",
    "image_key": null,
    "is_oxford_3000": <true hoặc false>,
    "is_oxford_5000": <true hoặc false>,
    "created_at": "2026-01-01T00:00:00Z"
  }
}

Quy tắc chất lượng:
1. Từ phải thực sự phổ biến và hữu ích với người học, không dùng từ quá hiếm.
2. Ví dụ câu phải có ngữ cảnh lĩnh vực [LĨNH VỰC] rõ ràng.
3. Đồng nghĩa / trái nghĩa phải chính xác về nghĩa (không chỉ gần nghĩa).
4. Mnemonic nên sáng tạo, dễ nhớ, ưu tiên liên kết âm thanh hoặc hình ảnh.
5. frequency_rank: từ thông dụng (rank thấp = phổ biến hơn, tương tự Zipf rank).
6. is_oxford_3000 / is_oxford_5000: điền đúng theo danh sách Oxford thực tế.
7. Các từ KHÔNG được trùng lặp với nhau trong lô từ này.
8. Bọc toàn bộ output trong ```json ... ``` để dễ copy.
```

---

## BẢO SỐ THAM SỐ NHANH

### Lĩnh vực (domain) — chọn 1 hoặc nhiều:
| Giá trị | Mô tả |
|---|---|
| `general` | Từ chức năng/cơ bản không thuộc ngữ cảnh cụ thể |
| `everyday` | Đời sống hằng ngày, gia đình, nhà cửa, cảm xúc |
| `business` | Kinh doanh, tài chính, quản lý, marketing |
| `technology` | Công nghệ thông tin, phần mềm, mạng, AI |
| `academic` | Học thuật, nghiên cứu, khoa học, đại học |
| `medical` | Y tế, bệnh viện, dược phẩm, sinh học |
| `health` | Sức khoẻ lối sống, thể dục, dinh dưỡng |
| `travel` | Du lịch, giao thông, khách sạn, địa điểm |
| `food` | Ẩm thực, nấu ăn, thức uống, nhà hàng |
| `vegetables` | Rau xanh, quả, nguyên liệu nấu ăn |
| `animals` | Động vật, côn trùng, sinh vật hoang dã |
| `nature` | Thiên nhiên, địa lý, thời tiết, cảnh quan |
| `art` | Nghệ thuật, âm nhạc, hội hoạ, văn học |

### Cấp độ (cefr_level):
| Giá trị | Mô tả |
|---|---|
| `A1` | Sơ cấp — từ cơ bản nhất, dùng hàng ngày |
| `A2` | Sơ cấp nâng — mở rộng giao tiếp cơ bản |
| `B1` | Trung cấp — hiểu ý chính văn bản quen thuộc |
| `B2` | Trung cấp nâng — làm việc/học thuật tiêu chuẩn |
| `C1` | Nâng cao — văn bản chuyên ngành phức tạp |

### Từ loại (part_of_speech) — chọn 1 hoặc "all":
`noun` · `verb` · `adjective` · `adverb` · `phrase` · `other`

### Ngữ cảnh (register):
`formal` · `informal` · `academic` · `slang` · `null` (trung tính)

---

## VÍ DỤ CÁC LỆNH SẴN DÙNG

### Lệnh A — Lô Business B2, tất cả từ loại (20 từ):
```
Sinh 20 từ vựng tiếng Anh:
- domain: business
- cefr_level: B2
- part_of_speech: noun, verb, adjective (phân bổ đều)
- register: formal
- PK_START: 100

[dán cấu trúc template ở trên]
```

### Lệnh B — Lô Medical A1+A2, danh từ và động từ (15 từ):
```
Sinh 15 từ vựng tiếng Anh:
- domain: medical
- cefr_level: A1 và A2 (mỗi level 7-8 từ)
- part_of_speech: noun, verb
- register: null (neutral)
- PK_START: 200

[dán cấu trúc template ở trên]
```

### Lệnh C — Lô Technology C1, tất cả từ loại (10 từ):
```
Sinh 10 từ vựng tiếng Anh:
- domain: technology
- cefr_level: C1
- part_of_speech: noun, verb, adjective, adverb
- register: formal và academic
- PK_START: 300

[dán cấu trúc template ở trên]
```

### Lệnh D — Lô đa lĩnh vực, trải đều A1→C1 (30 từ):
```
Sinh 30 từ vựng tiếng Anh trải đều:
- domain: business, technology, medical, academic, general (mỗi domain ~6 từ)
- cefr_level: A1, A2, B1, B2, C1 (mỗi level ~6 từ)
- part_of_speech: noun (12 từ), verb (10 từ), adjective (6 từ), adverb (2 từ)
- register: mixed (formal, academic, null)
- PK_START: 400

[dán cấu trúc template ở trên]
```

---

## QUY TRÌNH NẠP DỮ LIỆU VÀO HỆ THỐNG

Sau khi AI trả về JSON, thực hiện 3 bước:

```bash
# Bước 1: Lưu file fixture (chọn tên mô tả)
# Ví dụ: seed_business_b2.json / seed_medical_a1a2.json / seed_batch_002.json
cp /tmp/output.json backend/apps/vocabulary/fixtures/seed_<tên>.json

# Bước 2: Kiểm tra JSON hợp lệ trước khi nạp
python -m json.tool backend/apps/vocabulary/fixtures/seed_<tên>.json > /dev/null && echo "JSON OK"

# Bước 3: Nạp vào database
cd backend
../.venv/bin/python manage.py loaddata apps/vocabulary/fixtures/seed_<tên>.json

# Kiểm tra kết quả
../.venv/bin/python manage.py shell -c "
from apps.vocabulary.models import Word
from django.db.models import Count
print('Tổng từ trong DB:', Word.objects.count())
for r in Word.objects.values('domain').annotate(c=Count('id')).order_by('domain'):
    print(f'  {r[\"domain\"]:<14} {r[\"c\"]} từ')
"
```

---

## LƯU Ý KỸ THUẬT

- **pk liên tục**: Luôn tăng `PK_START` theo batch để tránh conflict. Kiểm tra pk hiện tại cao nhất:
  ```bash
  ../.venv/bin/python manage.py shell -c "from apps.vocabulary.models import Word; print('Max pk:', Word.objects.order_by('-pk').first().pk if Word.objects.exists() else 0)"
  ```
- **Fixture files**: Lưu tại `backend/apps/vocabulary/fixtures/` để Django tự tìm khi dùng `loaddata`.
- **Không duplicate**: Nếu `loaddata` báo IntegrityError, nguyên nhân là pk trùng — tăng `PK_START` và thử lại.
- **Batch size**: Mỗi lô nên 10–30 từ. Lô quá lớn (>50) làm giảm chất lượng AI output.
- **Kiểm tra audio sau**: Trường `audio_uk_s3_key` và `audio_us_s3_key` để `null` — sẽ upload audio riêng sau khi đã có TTS service (Edge TTS hoặc S3).
