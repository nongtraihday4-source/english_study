# ROLE & CONTEXT
Bạn là một Chuyên gia Dữ liệu AI và một Giáo viên Tiếng Anh xuất sắc. Nhiệm vụ của bạn là tạo ra một bộ dataset chất lượng cao để tinh chỉnh (fine-tune) mô hình ngôn ngữ T5. 
Đối tượng mục tiêu là học viên người Việt Nam thường xuyên mắc lỗi "Vietlish" (dịch word-by-word từ tiếng Việt sang tiếng Anh) và sai trật tự từ (trạng từ, tính từ).

# DATA FORMAT
Bạn phải trả về kết quả dưới dạng JSON Array. Mỗi object gồm 2 trường "input" và "target".
- "input": Bắt buộc bắt đầu bằng tiền tố "tutor: " theo sau là câu sai.
- "target": Cấu trúc bắt buộc là: [Câu đúng] || Lỗi: [Tên lỗi ngắn gọn] || HD: [Giải thích 1 câu duy nhất bằng tiếng Việt].

# EXAMPLES
[
  {
    "input": "tutor: I like very much English.",
    "target": "I like English very much. || Lỗi: Trật tự trạng từ || HD: Trạng từ chỉ mức độ 'very much' thường đứng cuối câu hoặc sau tân ngữ, không đứng trước tân ngữ."
  },
  {
    "input": "tutor: I want to buy a car red.",
    "target": "I want to buy a red car. || Lỗi: Trật tự tính từ và danh từ || HD: Trong tiếng Anh, tính từ (red) phải đứng trước danh từ (car)."
  }
]

# TASK
Hãy tạo 200 mẫu dữ liệu tập trung vào các lỗi: dịch word-by-word, trật tự từ sai, thiếu mạo từ (a/an/the) do thói quen tiếng Việt. Đảm bảo ngữ cảnh đa dạng (công sở, trường học, đời sống). Chỉ trả về mã JSON hợp lệ.

# ROLE & CONTEXT
Bạn là một Chuyên gia Dữ liệu AI và một Giáo viên Tiếng Anh xuất sắc. Nhiệm vụ của bạn là tạo ra bộ dataset để huấn luyện AI khả năng "lọc rác" văn nói (chuyển đổi văn bản Spoken -> Written).
Học viên thường dùng quá nhiều từ đệm (filler words), ngập ngừng, hoặc lặp từ khi nói.

# DATA FORMAT
Bạn phải trả về kết quả dưới dạng JSON Array. Mỗi object gồm 2 trường "input" và "target".
- "input": Bắt buộc bắt đầu bằng "tutor: " theo sau là câu nói chứa từ đệm (uh, um, like, you know, basically, sort of...).
- "target": Cấu trúc bắt buộc là: [Câu đã lọc sạch] || Lỗi: [Tên lỗi] || HD: [Giải thích 1 câu].

# EXAMPLES
[
  {
    "input": "tutor: I, uh, think that, like, the movie is, um, really good.",
    "target": "I think that the movie is really good. || Lỗi: Từ đệm (Filler words) || HD: Hãy loại bỏ các từ đệm như 'uh', 'um', 'like' để câu văn nói trở nên mạch lạc và tự tin hơn."
  },
  {
    "input": "tutor: So basically, he was going to the, the hospital.",
    "target": "He was going to the hospital. || Lỗi: Lặp từ và từ thừa || HD: Cần lược bỏ từ lặp 'the' và từ thừa 'So basically' không mang ý nghĩa thực tế."
  }
]

# TASK
Hãy tạo 300 mẫu dữ liệu chứa các câu ngập ngừng, nói nhịu, nhiều từ đệm phổ biến trong giao tiếp. Câu sửa phải gọn gàng, tự nhiên nhưng giữ nguyên ý nghĩa gốc. Chỉ trả về mã JSON hợp lệ.

# ROLE & CONTEXT
Bạn là một Chuyên gia Dữ liệu AI và Giáo viên Tiếng Anh. Nhiệm vụ của bạn là tạo dataset huấn luyện AI nhận diện lỗi "Nhảy thì" (Tense Shifting) trong đoạn văn.
Học viên thường viết đoạn văn 2-3 câu kể về quá khứ nhưng lại đột ngột dùng hiện tại đơn ở giữa câu chuyện.

# DATA FORMAT
Trả về JSON Array với 2 trường "input" và "target".
- "input": Bắt đầu bằng "tutor: " + [Đoạn văn 2-3 câu có lỗi nhảy thì].
- "target": [Đoạn văn đúng] || Lỗi: [Tên lỗi] || HD: [Giải thích 1-2 câu].

# EXAMPLES
[
  {
    "input": "tutor: Yesterday I went to the park. The sun is shining. I am very happy.",
    "target": "Yesterday I went to the park. The sun was shining. I was very happy. || Lỗi: Sự nhất quán về thì (Tense consistency) || HD: Câu chuyện bắt đầu ở quá khứ (Yesterday I went), nên các câu sau cũng phải dùng quá khứ (was) thay vì hiện tại (is/am)."
  }
]

# TASK
Hãy tạo 300 mẫu dữ liệu là các đoạn văn ngắn (2-3 câu). Ngữ cảnh có thể là: kể về chuyến đi, báo cáo công việc, kể kỷ niệm. Cố tình làm sai thì ở câu thứ 2 hoặc thứ 3. Giải thích phải ngắn gọn, súc tích. Chỉ trả về mã JSON.

# ROLE & CONTEXT
Bạn là một Chuyên gia Dữ liệu AI và Giáo viên Tiếng Anh. Hãy tạo dataset huấn luyện AI nhận diện và sửa lỗi sai Collocations (cụm từ kết hợp) và Prepositions (giới từ) phổ biến của người học tiếng Anh.

# DATA FORMAT
Trả về JSON Array với 2 trường "input" và "target".
- "input": Bắt đầu bằng "tutor: " + [Câu sai cụm từ/giới từ].
- "target": [Câu đúng] || Lỗi: [Tên lỗi] || HD: [Giải thích 1 câu].

# EXAMPLES
[
  {
    "input": "tutor: I need to do a decision right now.",
    "target": "I need to make a decision right now. || Lỗi: Kết hợp từ (Collocation) || HD: Trong tiếng Anh, động từ 'make' đi với 'a decision', không dùng 'do'."
  },
  {
    "input": "tutor: She is totally obsessed on listening to K-pop.",
    "target": "She is totally obsessed with listening to K-pop. || Lỗi: Giới từ sai ngữ cảnh || HD: Tính từ 'obsessed' luôn đi kèm với giới từ 'with', không dùng 'on'."
  }
]

# TASK
Hãy tạo 300 mẫu dữ liệu tập trung vào các bẫy quen thuộc: do/make, take/get/have, say/tell, mạo từ đi kèm, hoặc các giới từ đi sau động từ/tính từ (depend on, interested in...). Chỉ trả về mã JSON.