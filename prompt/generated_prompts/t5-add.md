# ROLE
Bạn là một chuyên gia thiết kế dữ liệu cho LLM và là giáo viên tiếng Anh chuyên dạy người Việt. Nhiệm vụ của bạn là tạo ra một bộ Dataset chất lượng cao theo định dạng JSON để tinh chỉnh (fine-tune) mô hình Qwen2.5-7B (hoặc Qwen3.5-2B).

# CONTEXT
Học viên là người Việt Nam, thường xuyên mắc lỗi "Vietlish" (dịch word-by-word từ tiếng Việt sang tiếng Anh) và sai trật tự từ (tính từ đứng sau danh từ, trạng từ đặt sai vị trí). AI cần phản hồi bằng tiếng Việt với giọng văn sư phạm, khích lệ và giải thích sâu sắc.

# DATASET STRUCTURE (JSON)
Mỗi mẫu dữ liệu phải tuân thủ cấu trúc sau:
{
  "instruction": "Sửa lỗi tiếng Anh trong câu sau và giải thích bằng tiếng Việt.",
  "input": "Câu sai của học viên",
  "output": "Phản hồi chi tiết của giáo viên"
}

# CHUYÊN ĐỀ CẦN TẠO: Ngữ pháp – Lỗi dịch word-by-word, trật tự tính từ/trạng từ và thiếu mạo từ.
# KỊCH BẢN: Học viên viết một câu sai do tư duy tiếng Việt.

# YÊU CẦU CHI TIẾT CHO OUTPUT:
1. Corrected Sentence: Đưa ra câu đúng hoàn chỉnh.
2. Error Identification: Chỉ rõ tên loại lỗi (Word-by-word translation, Adjective/Noun order, Adverb placement, Missing article...).
3. Vietnamese Explanation: Giải thích tại sao người Việt hay sai (ví dụ: tiếng Việt tính từ đứng sau danh từ, không có mạo từ...) và mẹo ghi nhớ.
4. Giọng văn: Thân thiện, chuyên nghiệp, sử dụng emoji phù hợp.

# NHIỆM VỤ:
Hãy tạo 200 mẫu dữ liệu khác nhau cho chuyên đề trên. Đảm bảo các lỗi sai cực kỳ thực tế với người Việt. Ngữ cảnh đa dạng: công sở, trường học, đời sống. Trả về kết quả dưới dạng một mảng JSON duy nhất.
2
# ROLE
Bạn là một chuyên gia thiết kế dữ liệu cho LLM và là giáo viên tiếng Anh chuyên dạy người Việt. Nhiệm vụ của bạn là tạo ra một bộ Dataset chất lượng cao theo định dạng JSON để tinh chỉnh (fine-tune) mô hình Qwen2.5-7B (hoặc Qwen3.5-2B).

# CONTEXT
Học viên là người Việt Nam, trong văn nói thường dùng quá nhiều từ đệm (filler words), ngập ngừng, lặp từ, hoặc nói nhịu. AI cần giúp họ chuyển đổi văn bản nói sang văn bản viết gọn gàng, tự nhiên, giữ nguyên ý nghĩa gốc. AI phản hồi bằng tiếng Việt với giọng văn sư phạm, khích lệ.

# DATASET STRUCTURE (JSON)
Mỗi mẫu dữ liệu phải tuân thủ cấu trúc sau:
{
  "instruction": "Lọc bỏ từ đệm và lặp từ trong câu nói sau để có câu văn viết mạch lạc, tự nhiên. Giải thích ngắn gọn bằng tiếng Việt.",
  "input": "Câu nói chứa từ đệm",
  "output": "Phản hồi chi tiết của giáo viên"
}

# CHUYÊN ĐỀ CẦN TẠO: Kỹ năng Viết – Loại bỏ từ đệm (filler words), lặp từ và từ thừa trong văn nói.
# KỊCH BẢN: Học viên nói một câu ngập ngừng, lặp từ, nhiều filler (uh, um, like, you know, basically, sort of...).

# YÊU CẦU CHI TIẾT CHO OUTPUT:
1. Cleaned Sentence: Đưa ra câu đã lọc sạch, mượt mà.
2. Error Identification: Chỉ rõ tên lỗi (Filler words, Repetition, Redundant words).
3. Vietnamese Explanation: Giải thích tại sao cần lược bỏ những từ đó trong văn viết và mẹo để nói tự tin hơn.
4. Giọng văn: Thân thiện, chuyên nghiệp, sử dụng emoji phù hợp.

# NHIỆM VỤ:
Hãy tạo 300 mẫu dữ liệu khác nhau cho chuyên đề trên. Câu nói phải đa dạng ngữ cảnh giao tiếp hàng ngày, công sở, trường học. Trả về kết quả dưới dạng một mảng JSON duy nhất.
3
# ROLE
Bạn là một chuyên gia thiết kế dữ liệu cho LLM và là giáo viên tiếng Anh chuyên dạy người Việt. Nhiệm vụ của bạn là tạo ra một bộ Dataset chất lượng cao theo định dạng JSON để tinh chỉnh (fine-tune) mô hình Qwen2.5-7B (hoặc Qwen3.5-2B).

# CONTEXT
Học viên là người Việt Nam, thường viết đoạn văn kể chuyện về quá khứ nhưng đột ngột nhảy thì hiện tại do thói quen từ tiếng Việt (tiếng Việt không chia thì). AI cần giúp họ giữ nhất quán thì trong đoạn. AI phản hồi bằng tiếng Việt với giọng văn sư phạm, khích lệ.

# DATASET STRUCTURE (JSON)
Mỗi mẫu dữ liệu phải tuân thủ cấu trúc sau:
{
  "instruction": "Sửa lỗi nhảy thì trong đoạn văn sau và giải thích bằng tiếng Việt.",
  "input": "Đoạn văn 2-3 câu chứa lỗi nhảy thì",
  "output": "Phản hồi chi tiết của giáo viên"
}

# CHUYÊN ĐỀ CẦN TẠO: Ngữ pháp – Sự nhất quán về thì (Tense consistency) trong đoạn văn ngắn (2-3 câu).
# KỊCH BẢN: Học viên viết đoạn kể về quá khứ nhưng câu thứ 2 hoặc thứ 3 lại dùng hiện tại đơn.

# YÊU CẦU CHI TIẾT CHO OUTPUT:
1. Corrected Paragraph: Đưa ra toàn bộ đoạn đúng thì.
2. Error Identification: Chỉ rõ tên lỗi (Tense shift, Inconsistent tense).
3. Vietnamese Explanation: Giải thích tại sao người Việt hay mắc lỗi này (do tiếng Việt ghép từ chỉ thời gian chứ không chia động từ) và mẹo ghi nhớ: chọn một mốc thời gian chính và giữ nguyên thì cho các hành động xung quanh mốc đó.
4. Giọng văn: Thân thiện, chuyên nghiệp, sử dụng emoji phù hợp.

# NHIỆM VỤ:
Hãy tạo 300 mẫu dữ liệu khác nhau cho chuyên đề trên. Đoạn văn nên đa dạng ngữ cảnh: kể chuyến đi, báo cáo công việc, kỷ niệm. Trả về kết quả dưới dạng một mảng JSON duy nhất.
4
# ROLE
Bạn là một chuyên gia thiết kế dữ liệu cho LLM và là giáo viên tiếng Anh chuyên dạy người Việt. Nhiệm vụ của bạn là tạo ra một bộ Dataset chất lượng cao theo định dạng JSON để tinh chỉnh (fine-tune) mô hình Qwen2.5-7B (hoặc Qwen3.5-2B).

# CONTEXT
Học viên là người Việt Nam, thường xuyên sai các cụm từ kết hợp cố định (collocations) và giới từ đi kèm động từ/tính từ do dịch từ tiếng Việt. AI cần phản hồi bằng tiếng Việt với giọng văn sư phạm, khích lệ và giải thích sâu sắc.

# DATASET STRUCTURE (JSON)
Mỗi mẫu dữ liệu phải tuân thủ cấu trúc sau:
{
  "instruction": "Sửa lỗi dùng từ hoặc giới từ trong câu sau và giải thích bằng tiếng Việt.",
  "input": "Câu sai collocation/giới từ",
  "output": "Phản hồi chi tiết của giáo viên"
}

# CHUYÊN ĐỀ CẦN TẠO: Từ vựng/Ngữ pháp – Kết hợp từ (Collocations) và Giới từ (Dependent prepositions).
# KỊCH BẢN: Học viên viết một câu dùng sai collocation (do/make, take/get/have, say/tell) hoặc giới từ sau tính từ/động từ (depend on, interested in, married to...).

# YÊU CẦU CHI TIẾT CHO OUTPUT:
1. Corrected Sentence: Đưa ra câu đúng hoàn chỉnh.
2. Error Identification: Chỉ rõ tên lỗi (Collocation error, Wrong preposition).
3. Vietnamese Explanation: Giải thích tại sao tiếng Việt hay gây nhầm lẫn (ví dụ: "làm" có thể là do/make, "nói" là say/tell...) và mẹo ghi nhớ (Make = tạo ra cái mới, Do = hành động; Interested + in; Married + to…).
4. Giọng văn: Thân thiện, chuyên nghiệp, sử dụng emoji phù hợp.

# NHIỆM VỤ:
Hãy tạo 300 mẫu dữ liệu khác nhau cho chuyên đề trên. Tập trung vào các bẫy quen thuộc: do/make, take/get, say/tell, depend on, interested in, afraid of, married to, discuss something (không có about)… Trả về kết quả dưới dạng một mảng JSON duy nhất.