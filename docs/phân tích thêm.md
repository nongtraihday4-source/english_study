Dựa trên tài liệu cấu trúc ngữ pháp từ A1-C1 và bản phân tích yêu cầu dự án (PRD) của bạn, hệ thống của bạn có một nền tảng rất vững chắc. Để đáp ứng yêu cầu **"người dùng nắm vững ngữ pháp trước, sau đó mới tham gia các khóa học chủ đề tương ứng"**, chúng ta sẽ áp dụng **Ràng buộc Mở khóa (Unlock Logic)** theo mô hình cây kỹ năng (Skill Tree) đã được định nghĩa trong PRD.

Dưới đây là đề xuất thiết kế khung khóa học minh bạch, chia làm 2 giai đoạn cho mỗi cấp độ (Phase 1: Làm chủ Ngữ pháp ➔ Phase 2: Ứng dụng theo Chủ đề).

### I. CẤU TRÚC LOGIC TRÊN HỆ THỐNG WEB APP

Theo PRD, hệ thống đi theo 5 cấp: **Cấp độ ➔ Khóa Học ➔ Chương ➔ Bài Học ➔ Bài tập**. 
Để ép buộc người học đi theo đúng lộ trình, bạn cần cấu hình tính năng `UnlockRule` (hiện đang được đánh giá là cần bổ sung frontend enforcement trong kế hoạch P1).

Lộ trình của một học viên tại một cấp độ (ví dụ B1) sẽ diễn ra như sau:
1. **Khóa 1: B1 Grammar Masterclass** (Bắt buộc học trước).
2. **Progress Check (Kiểm tra định kỳ):** Học viên phải vượt qua bài test ngữ pháp tổng hợp với điểm chuẩn (passing score).
3. **Khóa 2: B1-B2 Practical Topics** (Khóa chủ đề): Chỉ tự động mở khóa (hiệu ứng Unlock Animation) khi Khóa 1 đã hoàn thành.

---

### II. ĐỀ XUẤT KHUNG CHƯƠNG TRÌNH CHI TIẾT TỪ A1 ĐẾN C1

Dưới đây là khung phân bổ bài học được trích xuất minh bạch từ các nguồn tài liệu của bạn.

#### 1. Cấp độ A1 (Foundation)
**Giai đoạn 1: A1 Grammar Masterclass**
Học viên cần xây dựng móng ngữ pháp cơ bản nhất để hình thành câu đơn.
*   **Chương 1: Các thì cơ bản (Present & Past):** Động từ 'to be' (am/is/are), Thì hiện tại đơn, Hiện tại tiếp diễn, Thì quá khứ đơn với động từ có quy tắc/bất quy tắc.
*   **Chương 2: Tương lai & Động từ khuyết thiếu:** Will/Shall, Be going to, Can/Can't, và câu mệnh lệnh (Imperative).
*   **Chương 3: Từ loại & Số lượng:** Mạo từ (A/an/the), danh từ đếm được/không đếm được, There is/There are, This/That/These/Those.
*   **Chương 4: Giới từ & Cấu trúc câu:** Giới từ chỉ thời gian/nơi chốn (In/On/At), từ để hỏi (What, Where, How...), và trật tự từ cơ bản (Word order).

**Giai đoạn 2: Khóa chủ đề A1-A2 (Ứng dụng)**
(Do bạn chưa cung cấp file `topics_a1.txt`, hệ thống có thể tái sử dụng các chủ đề giao tiếp nền tảng nhất từ A2-B1 như *Personal Care, Household Chores, Directions*).

#### 2. Cấp độ A2 (Pre-Intermediate)
**Giai đoạn 1: A2 Grammar Masterclass**
*   **Chương 1: Mở rộng các thì:** Phân biệt Hiện tại đơn vs Hiện tại tiếp diễn, Hiện tại hoàn thành (Just, yet, already), Quá khứ tiếp diễn.
*   **Chương 2: Động từ khuyết thiếu mở rộng:** Have to/Don't have to, Must/Mustn't, Should/Shouldn't, Used to (thói quen trong quá khứ).
*   **Chương 3: Câu điều kiện & Bị động:** Câu điều kiện loại 1 & 2 (First & Second Conditional), Câu bị động thì hiện tại & quá khứ đơn.
*   **Chương 4: Mệnh đề & So sánh:** Mệnh đề quan hệ xác định (Who, which, that, where), So sánh hơn/nhất của tính từ và trạng từ.

**Giai đoạn 2: A2-B1 Practical Topics (Khóa chủ đề ứng dụng)**
Sau khi nắm vững ngữ pháp, học viên luyện 4 kỹ năng (Nghe/Nói/Đọc/Viết) qua các từ vựng và ngữ cảnh thực tế:
*   **Daily Life & Travel:** Thói quen hàng ngày, Mua sắm siêu thị, Quản lý tài chính cá nhân, Đặt vé máy bay & Khách sạn, Cấp cứu cơ bản.
*   **Food & Health:** Phương pháp nấu ăn, Gọi món tại nhà hàng, Triệu chứng bệnh & Thuốc.

#### 3. Cấp độ B1 (Intermediate)
**Giai đoạn 1: B1 Grammar Masterclass**
*   **Chương 1: Các thì nâng cao (Narrative Tenses):** Quá khứ hoàn thành, Hiện tại hoàn thành tiếp diễn, Tương lai tiếp diễn/hoàn thành.
*   **Chương 2: Modal Verbs nâng cao:** Động từ khuyết thiếu chỉ sự suy luận (Modal verbs of deduction: Must/might/can't), Had better, Would rather.
*   **Chương 3: Cấu trúc phức hợp:** Câu điều kiện loại 3 & Câu điều kiện hỗn hợp, Câu bị động với 2 tân ngữ (Passive verbs with two objects), Câu tường thuật (Reported speech).
*   **Chương 4: Gerunds & Infinitives:** Cấu trúc Động từ + Tân ngữ + To-infinitive/Gerund.

**Giai đoạn 2: B1-B2 Practical Topics (Khóa chủ đề ứng dụng)**
Áp dụng ngữ pháp cấu trúc phức tạp vào môi trường chuyên nghiệp và xu hướng xã hội:
*   **Modern Career & TOEIC:** Phỏng vấn xin việc, Làm việc từ xa (Remote work), Quản lý nhân sự, Bán hàng & Marketing, Hợp đồng kinh tế.
*   **Digital Life & Trends:** Mạng xã hội, Thương mại điện tử, Tiền điện tử (Cryptocurrencies), Lối sống tối giản (Minimalism).
*   **Industry & Society:** Đa dạng văn hóa, Bình đẳng giới, Bất động sản, Nông nghiệp, Kỹ thuật ô tô.

#### 4. Cấp độ B2 (Upper-Intermediate)
**Giai đoạn 1: B2 Grammar Masterclass**
*   **Chương 1: Ngữ pháp tự sự & Giả định:** Phân biệt rõ Ràng buộc Narrative tenses, Unreal uses of past tenses (Wish, if only, it's time).
*   **Chương 2: Mệnh đề & Phức từ:** Mệnh đề phân từ (Participle clauses), Tính từ ghép (Compound adjectives), Discourse markers (Linking words).
*   **Chương 3: Cấu trúc nhấn mạnh (Emphasis):** Câu chẻ (Cleft sentences - "It was...", "What..."), Đảo ngữ với trạng từ phủ định (Inversion with negative adverbials).

**Giai đoạn 2: Khóa chủ đề B2 (Luyện thi & Học thuật)**
Tiếp tục sử dụng nguồn `topics_b1_b2.txt` nhưng yêu cầu độ khó bài tập (Listening gap-fill, Writing) cao hơn, tập trung vào kỹ năng phân tích và phản biện trong các chủ đề: Quản lý khủng hoảng, Khởi nghiệp, Tranh luận & Bày tỏ quan điểm.

#### 5. Cấp độ C1 (Advanced)
**Giai đoạn 1: C1 Grammar Masterclass**
Ở cấp độ này, ngữ pháp tập trung vào sự tinh tế (nuances) và văn phong học thuật/báo chí:
*   **Chương 1: Sử dụng thì nâng cao (Advanced Tenses):** Narrative present (dùng hiện tại đơn/tiếp diễn kể chuyện/báo chí), Present continuous cho thói quen gây khó chịu (với always/constantly), Quá khứ hoàn thành chỉ sự hối tiếc/suy luận.
*   **Chương 2: Đảo ngữ & Nhấn mạnh (Inversion & Emphasis):** Thành thạo Negative Adverbial Inversion (Never have I...), Conditional Inversion (Had I known, Should you need, Were he...), Emphasis với "Do", Fronting.
*   **Chương 3: Cấu trúc Bị động học thuật (Advanced Passives):** Impersonal passive (It is believed that... / Millions are estimated to...), The passive with 'get'.
*   **Chương 4: Tránh lặp từ & Viết súc tích (Avoiding Repetition & Ellipsis):** Lược bỏ chủ ngữ/trợ động từ (Ellipsis), Thay thế mệnh đề (Substitution: do so, ones, if so).

**Giai đoạn 2: C1-C2 Academic & Global Contexts (Khóa chủ đề chuyên sâu)**
Chủ đề mang tính vĩ mô, chuẩn bị cho IELTS và môi trường nghiên cứu/kinh doanh cấp cao:
*   **IELTS & Academic:** Toàn cầu hóa, Tội phạm & Luật pháp, Báo chí, Lịch sử, Triết học, Tâm lý học, Cơ học lượng tử, Nghiên cứu khoa học.
*   **Advanced Business & Law:** M&A (Sáp nhập & Mua lại), Trách nhiệm xã hội (CSR), Sở hữu trí tuệ, Đầu tư mạo hiểm (Venture Capital), Ngoại giao, Hệ thống bầu cử.
*   **Global Issues & Science:** Biến đổi khí hậu, Năng lượng tái tạo, Dịch bệnh & Y tế công cộng, AI & Dữ liệu lớn (Big Data), Kỹ thuật hàng không vũ trụ.

---

### III. TRIỂN KHAI TRÊN HỆ THỐNG WEB APP

Để thiết kế theo đúng nguồn tài liệu và luồng PRD của bạn:

1.  **Quản lý Nội dung (Admin Panel):** Bạn cần một tính năng (hiện đang thiếu trong hệ thống theo file phân tích) để gán `Exercise -> Lesson Binding`. Hệ thống cần cho phép Admin tạo Bài tập ngữ pháp (Multiple Choice, Gap Fill) và gắn chặt vào Bài học Ngữ pháp.
2.  **Chấm điểm AI cho các Khóa Chủ đề (Speaking/Writing):** Khi học viên sang Giai đoạn 2 (Học chủ đề), các bài Speaking Role-play và Writing Zen Mode sẽ được chấm bằng AI (OpenAI + Whisper). Thang điểm AI rubric đã có (Grammar Accuracy chiếm 30% điểm Writing và 20% điểm Speaking). Nếu học viên làm sai ngữ pháp, AI sẽ **tham chiếu lại chính xác các bài học ngữ pháp (ví dụ: Lỗi Mixed Conditional)** để yêu cầu học viên ôn lại.
3.  **Hệ thống Flashcard SRS:** Từ vựng học trong các khóa Chủ đề sẽ được đẩy tự động vào hệ thống Spaced Repetition (Flashcard) để ôn tập mỗi ngày.

Bằng cách tách bạch rõ **Khóa Ngữ Pháp** và **Khóa Chủ Đề** song song với tính năng `UnlockRule`, hệ thống của bạn sẽ đảm bảo đúng triết lý: *Xây móng ngữ pháp chắc chắn trước khi xây tầng giao tiếp và từ vựng chuyên sâu.*