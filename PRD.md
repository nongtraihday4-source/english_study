# PRODUCT REQUIREMENTS DOCUMENT (PRD) 
*(Bản Cập Nhật Dựa Trên Yêu Cầu Chuyên Sâu Của Dự Án)*

## DỰ ÁN: ỨNG DỤNG HỌC LÝ THUYẾT VÀ THỰC HÀNH TIẾNG ANH (ENGLISH STUDY)

### 1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)
- **Mục đích:** Xây dựng một nền tảng Web App quản lý quá trình học tiếng Anh bài bản từ A1 đến C1. Hệ thống nhấn mạnh vào sự liên kết kiến thức, kỹ năng nền tảng và đặc biệt là loại bỏ cách học phát âm từ rời rạc để đưa vào ngữ cảnh, tình huống, hội thoại thực tế.
- **Yêu cầu hệ thống:** Hệ thống LMS (Learning Management System) có tính liên kết chặt chẽ, hệ thống bảo mật 5 lớp vững chắc. Chấm điểm hoàn toàn bằng AI (Trí Tuệ Nhân Tạo) cho cả 4 kỹ năng (Nghe, Nói, Đọc, Viết) với thang điểm 100.
- **Tiêu chuẩn hiển thị bắt buộc:**
  - Múi giờ: Kích hoạt mặc định múi giờ **Việt Nam (Asia/Ho_Chi_Minh)** xuyên suốt từ Database, Backend tới giao diện trình duyệt.
  - Định dạng số: Tuân thủ quy tắc phân cách hàng ngàn của Việt Nam (Ví dụ: `1.234.567` hoặc theo chuẩn `vi-VN` localization).

---

### 2. TECHNOLOGY STACK (TƯ VẤN CÔNG NGHỆ)
- **Backend:** **Django + Django REST Framework (DRF)**. Xử lý logic khóa học, phân quyền, bảo mật.
- **Frontend:** **Vue 3 (Composition API) kết hợp Vite**. Web tương tác cao, linh hoạt và đáp ứng giao diện phức tạp chia đôi màn hình (Split Pane).
- **Database:** **PostgreSQL** kết hợp **Redis** (cache + session + Celery broker).
- **AI Integration:** Tích hợp API AI (OpenAI GPT-4o + Whisper) để chấm điểm tự động bài Nói và Viết, thay thế hoàn toàn chấm tay thủ công.
- **Task Queue:** **Celery + Redis** xử lý tác vụ bất đồng bộ nặng: gọi AI grading, tạo TTS audio, gửi email hàng loạt, tính toán Leaderboard.
- **File Storage:** **AWS S3 / MinIO** lưu trữ toàn bộ file audio, tài liệu source. Kết hợp **CDN (CloudFront / BunnyCDN)** phân phối media tốc độ cao đến học viên.
- **PWA:** Service Worker hỗ trợ **Offline Mode** — học viên có thể xem lại nội dung bài đã tải khi mất kết nối mạng.

---

### 3. HỆ THỐNG BẢO MẬT 5 LỚP & HẠ TẦNG
1. **Lớp Mạng (Network & Infra Level):** Bắt buộc chạy trên HTTPS, tích hợp WAF, cấu hình chặn CORS nghiêm ngặt.
2. **Lớp Xác thực (Authentication):** Sử dụng JWT Token. Cho phép đăng nhập song song đa thiết bị (Ví dụ: Mobile + Laptop cùng lúc).
3. **Lớp Phân quyền (Authorization - RBAC):** 
   - Admin: Quản trị toàn quyền, upload file source nguồn.
   - Teacher: Được tạo khoá học phụ trợ, nhóm lớp riêng và sáng tạo bài tập thuộc quyền cá nhân (không được sửa bài chung của hệ thống tổng).
   - Student: Phân loại tài khoản người dùng Demo (Dùng thử bài học) và Premium (Trả phí học toàn phần).
4. **Lớp Ứng dụng:** Rate Limiting chống spam click API. Code Frontend tự nén audio thu âm trước khi gửi lên server giúp tiết kiệm băng thông.
5. **Lớp Cơ sở dữ liệu (Database Security):** Mật khẩu mã hoá (PBKDF2/Argon2), sao lưu dữ liệu mỗi tuần và sử dụng cờ Soft-Delete bảo vệ dữ liệu Học viên.

---

### 4. CẤU TRÚC LOGIC VÀ CƠ SỞ DỮ LIỆU CỐT LÕI
- **Mô hình Khóa học LMS (Course Hierarchy):**
  Hệ thống đi theo 5 cấp: `Cấp độ (A1-C1)` ➔ `Khóa Học (Course)` ➔ `Chương (Chapter)` ➔ `Bài Học (Lesson)` ➔ `Kỹ năng/Bài tập (Skill/Exercise)`.
- **Ràng buộc Mở khóa (Unlock Logic):** Học viên bắt buộc phải hoàn thành bài tập / chương mục trước đó và **đạt điểm chuẩn tối thiểu** thì mới được hệ thống mở khóa bài học tiếp theo. Ngăn chặn tuyệt đối việc nhảy cóc giai đoạn học. Bản đồ học tập được thiết kế dạng cây kỹ năng (Skill Tree).
- **Quản lý Kho tài liệu (Source Management):** Khu vực Admin/Teacher cung cấp tính năng "Đính kèm file". Upload và liên kết file media (`source`) rõ ràng theo từng cấp độ bài giảng.

---

### 5. BUSINESS LOGIC & THỰC HÀNH 4 KỸ NĂNG

#### 5.1. Module Quản trị Người Dùng & Quá trình Học
- **Học viên:** Đăng ký tài khoản, nâng cấp Premium, mua khóa học đi theo luồng "Tự Cày" (Self-study). Có thể tham gia vào thêm các lớp học riêng biệt do Giáo viên tạo ra.
- **Giáo viên:** Mở thêm các lớp "Củng cố kiến thức" ảo cho học viên bị yếu. Theo dõi được đầy đủ số liệu điểm tập luyện của học viên trong lớp mình.
- **Dashboard Học viên (Analytics):** Giao diện chính quyền lực nhất, hiển thị đồng loạt: 
  1. Biểu đồ lưới Radar đa giác hiển thị sự chênh lệch mạnh/yếu của 4 kỹ năng.
  2. Số ngày học tập liên tục (Streak).
  3. Thanh % tiến độ hoàn thành cho toàn bộ Khóa học.

#### 5.2. Module Thực Hành NGHE & ĐỌC (Listening & Reading)
- **Đa dạng câu hỏi:** Hệ thống tổng hợp toàn bộ các dạng thực hành: Trắc nghiệm (Multiple Choice), Điền từ vào ô trống (Gap Fill), và Kéo thả từ vựng đúng ngữ cảnh (Drag & Drop).
- **Trải nghiệm UX màn hình Đọc/Nghe:** Chia làm 2 cột tỷ lệ 6:4 (Split Pane). Cột trái là nội dung text dài / audio có thanh cuộn độc lập, cột phải là các câu hỏi trắc nghiệm tương ứng, giúp mắt không bao giờ bị mỏi hay phải cuộn lên cuộn xuống liên tục. Hỗ trợ bôi đen từ vựng để dịch ngay trên Tooltip ngữ cảnh.

#### 5.3. Module Thực Hành NÓI (Speaking / Shadowing)
- **Luồng nhập vai (Role-play):** Học viên nghe một đoạn hội thoại gốc đàm thoại hiển thị UI dạng iMessage/Tin nhắn ➔ Tới lượt, Học viên bấm Ghi Âm và nói nhại theo (Shadowing) kịp theo nhịp điệu chữ chạy (Karaoke effect).
- **Tối ưu Băng thông:** Toàn bộ file thu âm được frontend (Vue) dùng bộ codec nén lại giảm dung lượng trước khi upload vào backend Django.
- **Chấm điểm AI:** Backend nhận file ➔ Ném qua API trí tuệ nhân tạo (Whisper/Speech-to-text) ➔ AI tự phân tích độ chênh phô, phát âm, nối âm ➔ Chấm bằng thang 100 và phản hồi danh sách lỗi ngay lập tức.

#### 5.4. Module Thực Hành VIẾT (Writing)
- Hệ thống Editor hiển thị ở dạng Zen Mode (Tập trung tuyệt đối, làm mờ các menu xung quanh).
- Gạch chân thời gian thực (Real-time highlight): Editor tự scan những lỗi chính tả sai cơ bản để học sinh chú ý sửa lại ngay lúc đang viết. Thanh tiến độ số lượng từ thay vì hiện số sẽ hiện thanh bar/vòng tròn tỷ lệ.
- **Chấm bài tự động:** Học sinh nộp bài ➔ Viết được đóng gói đẩy qua Backend ➔ Gọi AI phân tích diễn đạt câu chữ, cấp độ từ vựng (A1/B2/C1), ngữ pháp ➔ Hệ thống trả về Điểm số (Thang 100) và Nhận xét chi tiết ngay lập tức cho học viên.

#### 5.5. Module Bổ sung Kiến thức (Grammar & Vocabulary)
- **Nguồn dữ liệu từ vựng:** Tích hợp Oxford 3000 (A1–B2) và Oxford 5000 (B2–C1) — dữ liệu CSV phân cấp CEFR lưu trong thư mục `dictionary/`. Mỗi từ bao gồm: IPA phiên âm (British & American), nghĩa tiếng Việt, ví dụ ngữ cảnh (EN + VI), collocations, ghi chú mnemonics và etymology hỗ trợ học viên Việt Nam.
- **Phân loại Domain:** Từ vựng được gắn nhãn theo lĩnh vực thực tế — `Business English`, `Casual English`, `Medical English`, `Academic English`, `Travel English` — để học viên lọc nhanh theo mục tiêu học tập cụ thể.
- **UK/US Pronunciation:** Mỗi từ có tệp audio cho cả 2 giọng (British UK và American US). Học viên chọn giọng ưa thích mặc định trong Settings.
- **Interactive Phoneme Learning (cấp A1):** Tại cấp A1, hệ thống cung cấp bản đồ âm vị tương tác (Phoneme Chart) — bấm vào từng âm đơn để nghe phát âm chuẩn, xem minh hoạ khẩu hình (mouth shape diagram). Mục tiêu: xây nền phát âm chính xác trước khi học từ vựng ngữ cảnh.
- **Tìm kiếm & Lọc:** Giao diện tra cứu từ điển tích hợp: tìm kiếm toàn văn, lọc theo CEFR level, domain, part-of-speech, frequency rank.

#### 5.6. Module Bộ Đề Trắc nghiệm & Kiểm Tra (Assessment)
- **Cấu trúc bộ đề:** Mỗi bộ đề (`ExamSet`) có metadata: thời gian làm bài (phút), điểm chuẩn vượt (`passing_score`, mặc định 60/100), số câu hỏi, phân bổ cấu trúc câu (MC / Gap Fill / Drag Drop).
- **Kiểm tra Định kỳ (Progress Check):** Sau mỗi Chapter hoàn thành, hệ thống bắt buộc học viên làm bài Progress Check 20–30 câu. Kết quả tích lũy vào `cumulative_score` — dùng để xác nhận tương đương cấp CEFR (VD: hoàn thành toàn bộ B2 với điểm trung bình tích lũy ≥75 → cấp chứng chỉ B2).
- **Class-based Exam (Giáo viên tạo):** Giáo viên tạo bài thi riêng cho lớp từ Question Bank hoặc soạn mới. Bài thi có `deadline` cứng và **chính sách No Retake** (học viên chỉ được làm đúng 1 lần).
- **Question Bank Trung tâm:** Kho câu hỏi phân loại theo kỹ năng (L/S/R/W), CEFR level, chủ đề, độ khó (easy/medium/hard), dạng câu. Admin và Teacher import câu hỏi hàng loạt từ file CSV.

#### 5.7. Module Phát Âm Chuyên Sâu (Pronunciation Curriculum)
*Hệ thống tích hợp song song hai luồng: (1) Phát âm ngữ cảnh — học trong câu/hội thoại thực tế (xem 5.2/5.3); (2) Phát âm hệ thống — nắm âm vị từ gốc qua 4 giai đoạn có ràng buộc.*
- **Stage 1 – Monophthongs (Nguyên âm đơn):** 12 nguyên âm đơn. Tập trung khẩu hình và vị trí lưỡi.
- **Stage 2 – Consonant Pairs (Phụ âm theo cặp):** Cặp hữu thanh/vô thanh: /p-b/, /t-d/, /k-g/, /f-v/, /s-z/, /ʃ-ʒ/...
- **Stage 3 – Diphthongs (Nguyên âm đôi):** 8 nguyên âm đôi và cách chuyển tiếp âm mượt mà.
- **Stage 4 – Advanced Sounds:** Âm cuối, cụm phụ âm (consonant clusters), lỗi phổ biến của người học Việt Nam.
- **Minimal Pair Discrimination:** Bài tập phân biệt cặp từ gần âm (`ship/sheep`, `bit/beat`, `fan/van`). Hệ thống ghi nhận tỷ lệ chính xác và tự điều chỉnh thứ tự ôn.
- **Prerequisites:** Học viên phải đạt ≥70% Stage N trước khi mở Stage N+1. Liên kết chéo với bài Listening/Speaking ở A1: tự động highlight âm vị đang học trong Stage hiện tại.

#### 5.8. Module Flashcard & Spaced Repetition (SRS)
- **Thuật toán SM-2:** Lập lịch ôn tập tối ưu theo SuperMemo 2. Mỗi flashcard lưu: `ease_factor`, `interval` (ngày), `repetition_count`, `next_review_date`. Học viên đánh giá từng thẻ thang 0–5 (0=không nhớ gì, 5=nhớ hoàn toàn).
- **Deck Management:** Deck mặc định theo level (A1 Core 300, A2 Expansion, B1 Business...) do Admin tạo. Học viên có thể tạo deck cá nhân, gắn tag, đổi tên. Teacher tạo deck chính thức gắn với course.
- **Card Types:** Ba dạng thẻ: `Word → Definition`, `Definition → Word`, `Audio → Word` (nghe → viết).
- **Session Tracking:** Mỗi phiên `StudySession` ghi nhận: số thẻ mới, số thẻ ôn lại, thời gian, accuracy %. Lịch sử `DeckStudyHistory` vẽ biểu đồ tiến độ từ vựng theo ngày.
- **Smart Notification:** Hệ thống tự nhắc học viên khi có thẻ đến hạn ôn (due cards) qua in-app notification và email.

#### 5.9. Module Thanh toán & Gói Premium (Payment & Subscription)
- **Phân loại tài khoản:**
  - **Demo:** Truy cập miễn phí 3 bài đầu mỗi cấp. Không ghi âm Speaking AI, không nộp Writing AI. NavBar hiển thị CTA nâng cấp.
  - **Premium:** Toàn quyền truy cập, AI chấm không giới hạn, tải tài liệu PDF nguồn.
- **Pricing Tiers:** `Gói Tháng` (VD: 199.000 VND/tháng) · `Gói Năm` (VD: 1.490.000 VND/năm, tiết kiệm ~38%) · `Gói Khóa đơn lẻ` (mua riêng 1 khóa).
- **Coupon System:** Mã giảm giá với: % giảm / số tiền cố định, ngày hiệu lực, tổng số lần dùng tối đa, ràng buộc gói áp dụng.
- **Luồng Checkout:** Chọn gói → nhập coupon (tùy chọn) → thanh toán VNPay/Stripe → Backend xác nhận webhook → tự nâng cấp `subscription_status` và set `subscription_end_date`.
- **PaymentTransaction:** Mọi giao dịch lưu đầy đủ: trạng thái (pending/completed/failed/refunded), amount (định dạng vi-VN VND), cổng thanh toán, timestamp chuẩn Asia/Ho_Chi_Minh.

#### 5.10. Module Thông báo & Giao tiếp (Notification System)
- **In-app Notifications:** Bảng `Notification` lưu các loại sự kiện: bài học mới mở khóa, AI chấm xong, thẻ Flashcard đến hạn ôn, streak sắp đứt (nhắc trước 2 giờ), giáo viên giao bài.
- **Email Campaigns:** Admin tạo và gửi email hàng loạt (Celery async). Email tự động (triggered events): chào mừng đăng ký, xác nhận thanh toán, nhắc nhở streak mất, chứng chỉ hoàn thành.
- **Push Notifications (PWA):** Service Worker gửi Web Push khi app chạy nền. Học viên bật/tắt từng loại thông báo trong Settings.
- **Template System:** Email và push dùng template có biến động: `{{ student_name }}`, `{{ course_name }}`, `{{ streak_count }}`, `{{ score }}`.

#### 5.11. Module Gamification & Achievement
- **XP & Điểm Kinh nghiệm:** Hoàn thành bài tập (+10 XP) · Đạt 100/100 (+25 XP bonus) · Streak 7 ngày liên tiếp (+50 XP) · Hoàn thành chapter (+100 XP) · Daily Challenge (+20 XP nhân đôi). XP tích lũy quyết định thứ hạng Leaderboard.
- **Achievement Badges (Huy hiệu):** 30+ huy hiệu phân loại: `Streak` (🔥 7/30/100 ngày) · `Skill Mastery` (đạt ≥90 mỗi kỹ năng L/S/R/W) · `Speed Learner` (hoàn thành chapter trong 24h) · `Night Owl` (học sau 22:00 VN 5+ ngày). Mỗi badge có `condition_type`, `threshold_value`, `icon_url`, `xp_reward`.
- **Leaderboard:** Bảng xếp hạng theo XP, lọc: `Tuần này` · `Tháng này` · `Toàn thời gian` · `Lớp học`. Học viên thấy top 100 + vị trí của chính mình.
- **Certificates (Chứng chỉ):** Hoàn thành toàn bộ khóa 1 cấp với cumulative score ≥60 → tự động phát chứng chỉ PDF có mã xác thực duy nhất. Admin tùy chỉnh template.
- **Daily Challenge:** Hệ thống unlock 1 bài thử thách ngẫu nhiên mỗi 24h (reset 00:00 VN). Hoàn thành trong ngày nhận 2× XP bonus, kéo học viên quay lại mỗi ngày.

---

### 6. ĐẶC TẢ GIAO DIỆN & TRẢI NGHIỆM NGƯỜI DÙNG (UI/UX MOCKUP SPECIFICATIONS)
*Khu vực này dành riêng cho việc thiết kế giao diện (Mockup) hoặc Prompt chuyển giao cho AI Frontend thực hiện thiết kế.*

#### 6.1. Art Direction & Styling (Phong cách & Hệ Màu)
- **Tông Màu Nền (Base Palette):** Sử dụng các dải màu học thuật Off-white (Trắng kem/Ngà) làm nền chính để triệt tiêu sự mỏi mắt. Không dùng trắng tinh (Absolute White).
- **Màu Nhấn (Accent Palette):**
  - **Electric Blue / Gradient Tím Viole:** Dùng cho thanh điều hướng, UI tổng quan thể hiện tính nền tảng công nghệ thông minh.
  - **Xanh Mint (Success Level):** Dành riêng cho Animation mở khóa bài mới, đáp án đúng.
  - **Cam/Đỏ (Streak/Warning Level):** Nổi bật số ngày streak hoặc cảnh báo lỗi sai chính tả.
  - Phải hỗ trợ chế độ **Dark Mode Toggle** mượt mà.
- **Micro-Animations & Components:** Định hướng thiết kế theo phong cách Glassmorphism (Thẻ thông tin bọc kính mờ) kết hợp với bóng đổ cực mềm (Soft Shadows) đánh lừa thị giác tạo độ bấu chạm 3D. Mọi nút gọi hành động (CTA Button) đều phải có hiệu ứng lún cơ học (Cảm giác vật lý lún nhẹ) khi Hover/Click.

#### 6.2. Gamification UI (Trải nghiệm Gây nghiện)
- **Learning Map (Bản Đồ Năng Lực):** UI danh sách lộ trình bài học không thả liệt kê dòng dọc nhàm chán mà thiết kế dưới dạng Sơ đồ cây kỹ năng (Skill tree map) tương đương dòng ứng dụng Duolingo.
- **Visual Unlock Feedback:** Các bài học chưa đáp ứng điều kiện sẽ bị phủ sương xám và sử dụng icon Ổ Khóa. Ngay khi nộp bài và nhận điểm đạt chuẩn qua AI, hệ thống phải chạy một Animation "Phá khóa" và đẩy thanh kinh nghiệm (Progress Bar) nhích lên thực tiếp để tạo Dopamine hứng thú cho học sinh.

#### 6.3. Trải nghiệm Tương tác Bài tập Nghe / Nói Thực Tế
- **Audio Waveform (Sóng âm):** Trình phát Audio tuyệt đối không dùng thanh kéo trượt player truyền thống. Vẽ ra biểu đồ sóng âm chạy Real-time tương tự ghi âm của iPhone/Telegram. Lúc sinh viên thực hiện ghi âm, UI sóng âm cũng dao động nhấp nhô theo tiếng thực.
- **Hồi đáp tức thì (Instant Response):** Mọi thao tác chọn click đáp án trắc nghiệm đều phản hồi flash màu Right/Wrong lập tức. Tại chức năng Role-play/Shadowing, UI chạy chữ highlight giống hệt Karaoke. Quá trình nạp bài đợi AI chấm sẽ biến thành Loading Box có dòng trạng thái "Trí tuệ nhân tạo đang chấm bài...", giúp học viên kiên nhẫn hơn.

#### 6.4. Learning Progression Indicators
- **Thanh Tiến độ Toàn cục:** Hiển thị phần trăm hoàn thành khóa học hiện tại. Bao gồm số chapter đã xong và còn lại. Animation nhích lên mượt mà ngay sau khi nộp bài đạt chuẩn.
- **Radar Chart 4 kỹ năng:** Biểu đồ Radar 4 trục (Listening / Speaking / Reading / Writing) hiển thị điểm trung bình theo thang 0–100, với 5 vạch chia (20-40-60-80-100). Chart cập nhật sau mỗi bài nộp. Hỗ trợ Dark Mode (đổi màu stroke + background).
- **Streak Counter & Fire Badge:** Số ngày học liên tục với icon 🔥, animation pulse khi streak tăng. Streak = 0 nếu qua 24h (timezone Asia/Ho_Chi_Minh) không học bất kỳ bài nào. Ngưỡng 7/30/100 ngày trigger animation đặc biệt + XP bonus.
- **Daily Challenge Countdown:** Đồng hồ đếm ngược đến 00:00 VN time khi Daily Challenge mới mở.

#### 6.5. Modal Dialog & Popup Flow
- **Unlock Trigger Dialog (Điểm không đạt):** Khi điểm < passing_score, hiển thị dialog: `"Bạn cần đạt {passing_score} điểm để mở khóa bài tiếp theo. Điểm của bạn: {score}/100"`. Hai CTA: `"Thử Lại Ngay"` và `"Khám Phá Bài Khác"`. Background blur, không dismiss được khi bấm ra ngoài.
- **Submit Feedback Dialog (Kết quả nộp bài):** Sau nộp bài đạt chuẩn: điểm số (counter animation), nhận xét AI tổng (2–3 câu), danh sách tối đa 3 lỗi ưu tiên. Dialog bắt buộc dừng 2–3 giây trước khi hiện nút "Tiếp tục" để học viên đọc kết quả.
- **Unlock Animation Overlay:** Mở khóa bài mới → full-screen animation: ổ khóa mở → confetti particles → thanh XP nhích lên → text "Bài mới đã được mở khóa!" fade in. Toàn bộ không quá 2.5 giây.
- **XP Gain Toast:** Mỗi lần nhận XP, toast góc phải: `+10 XP ⚡` slide in từ cạnh phải, auto-dismiss sau 2 giây. Tổng hợp nếu nhận nhiều event cùng lúc.

#### 6.6. Admin Panel & Teacher Portal
- **Admin Dashboard:** Tổng quan real-time: tổng học viên (active/demo/premium), số khóa học, số bài tập, số AI grading jobs đang chờ (`pending_ai_jobs`). Biểu đồ doanh thu tháng (VND, định dạng vi-VN). Bảng học viên mới đăng ký hôm nay.
- **Teacher Portal:** (1) Danh sách lớp học, (2) Học viên trong lớp + điểm từng kỹ năng + % tiến độ, (3) Tạo bài kiểm tra lớp từ Question Bank, (4) Giao bài (`AssignExercise`) cho cả lớp hoặc từng học viên, (5) Xem và bổ sung nhận xét Teacher Override cho bài AI đã chấm, (6) Xuất báo cáo CSV tiến độ lớp.
- **Content Management (Admin):** Upload tài liệu nguồn vào `source/` qua Admin UI. Liên kết file với level/chapter/lesson. Preview trước khi publish.
- **Question Bank Manager (Admin + Teacher):** CRUD câu hỏi, import hàng loạt từ CSV, lọc theo skill/level/topic/type. Preview bài tập trong context bộ đề.

---

### 7. AI GRADING RUBRICS & CRITERIA (TIÊU CHÍ CHẤM ĐIỂM AI)

#### 7.1. Speaking Rubric
| Tiêu chí | Mô tả chi tiết | Trọng số |
|---|---|---|
| **Pronunciation Accuracy** | Độ chính xác âm vị từng từ so với chuẩn IPA, phát hiện lỗi thay thế âm (/l/ vs /r/, /b/ vs /v/) | 35% |
| **Fluency & Rhythm** | Nhịp nói tự nhiên, số lần ngắt không tự nhiên, tốc độ phù hợp yêu cầu cấp độ | 25% |
| **Intonation & Stress** | Ngữ điệu câu hỏi/khẳng định/phủ định, nhấn âm đúng từ trọng tâm trong câu | 20% |
| **Vocabulary & Grammar** | Từ vựng và ngữ pháp trong transcript AI so với expected script | 20% |

*Luồng AI: Whisper transcribe audio → GPT-4o so sánh transcript với kịch bản mẫu → chấm điểm theo rubric → trả về JSON `{total_score, pronunciation_score, fluency_score, intonation_score, vocab_score, error_list[]}`.*

#### 7.2. Writing Rubric
| Tiêu chí | Mô tả chi tiết | Trọng số |
|---|---|---|
| **Task Achievement** | Hoàn thành yêu cầu đề bài, đủ số từ quy định, bao quát đầy đủ ý chính | 25% |
| **Grammar Accuracy** | Độ chính xác ngữ pháp: thì động từ, câu điều kiện, mệnh đề quan hệ, subject-verb agreement | 30% |
| **Vocabulary Level** | Đa dạng từ vựng, dùng từ đúng CEFR level, tránh lặp từ. AI phát hiện và gắn nhãn CEFR cho từng từ | 25% |
| **Coherence & Cohesion** | Cấu trúc bài viết, liên kết câu chuyển tiếp, mạch lạc ý tưởng từ đầu đến cuối | 20% |

*AI bổ sung: (1) Danh sách từ sai ngữ cảnh + gợi ý thay thế; (2) Câu cần viết lại + giải thích ngữ pháp; (3) CEFR level từng từ dùng trong bài.*

#### 7.3. Listening & Reading — Auto-graded Scoring
- **Multiple Choice (MC):** Điểm/câu = 100 ÷ tổng_số_câu. Không trừ điểm câu sai.
- **Gap Fill:** So khớp chấp nhận: case-insensitive + trim whitespace + dấu câu không ảnh hưởng. Một số câu có mảng `correct_answers[]` (nhiều đáp án hợp lệ).
- **Drag & Drop:** Tính điểm partial: mỗi vị trí đặt đúng = 100 ÷ (tổng_vị_trí × số_câu). Không cần đúng hoàn toàn toàn bộ câu.
- **Lưu kết quả:** `ExerciseResult.score` (integer 0–100) + `ExerciseResult.detail_json` (chi tiết từng câu: question_id, user_answer, is_correct, correct_answer).

#### 7.4. Score → CEFR Level Mapping
| Điểm tích lũy trung bình | Tương đương CEFR |
|---|---|
| 0–39 | Dưới A1 |
| 40–54 | A1 |
| 55–64 | A2 |
| 65–74 | B1 |
| 75–84 | B2 |
| 85–92 | C1 |
| 93–100 | C2 |

---

### 8. SOURCE FILE STRUCTURE SPECIFICATION (ĐẶC TẢ CẤU TRÚC TỆP NGUỒN)

#### 8.1. Cấu trúc thư mục `source/`
```
source/
├── dict A1-C1/           # Từ vựng CSV phân cấp CEFR (đã có)
│   ├── A1.csv            # ~1.000 từ Oxford 3000 cấp A1
│   ├── A2.csv, B1.csv, B2.csv, C1.csv
├── grammar/              # Tài liệu ngữ pháp PDF/DOCX (đã có)
│   ├── A1-grammar.docx ... C1-grammar.docx
│   └── grammar-topics/   # PDF chủ điểm ngữ pháp đánh số (đã có)
├── pronunciation/        # Tài liệu phát âm (đã có)
│   ├── IPA-guide.pdf
│   └── phoneme-audio/    # Audio từng âm vị chuẩn
├── audio/                # File âm thanh bài học (upload qua Admin)
│   └── {level}/{course_slug}/{lesson_slug}/
│       ├── listening-{n}.mp3
│       └── dialogue-{n}.mp3
└── images/               # Hình ảnh minh họa từ vựng
    └── vocab/{word_slug}.jpg
```

#### 8.2. CSV Vocabulary Format
```csv
word,part_of_speech,cefr_level,ipa_uk,ipa_us,meaning_vi,example_en,example_vi,domain
apple,noun,A1,ˈæp.əl,ˈæp.əl,quả táo,"I eat an apple every day.","Tôi ăn một quả táo mỗi ngày.",Food
```
Cột bắt buộc: `word`, `cefr_level`, `meaning_vi`. Các cột còn lại optional nhưng nên fill đủ để AI grading hoạt động tốt.

#### 8.3. Naming Conventions
- **Audio:** `{skill}-{lesson_order}-{part}.mp3` — VD: `listening-03-part1.mp3`
- **Images:** `{word_slug}.jpg` — VD: `coffee-cup.jpg`
- **Grammar docs:** `{level}-{topic_slug}.pdf` — VD: `b1-conditional-sentences.pdf`
- **Quy tắc chung:** Tất cả lowercase, dấu gạch ngang thay khoảng trắng, không dấu tiếng Việt.

#### 8.4. Upload Flow (Admin)
1. Admin → `Content Management → Upload Source` → chọn loại file
2. Chọn Level + Course liên kết → Upload → Backend validate format → save S3
3. Backend tạo record `SourceFile`: `file_type`, `level`, `course_fk`, `s3_key`, `file_size`, `uploaded_by_fk`, `created_at` (Asia/Ho_Chi_Minh)
4. Admin liên kết `SourceFile` với `Lesson` cụ thể qua giao diện Lesson Editor
