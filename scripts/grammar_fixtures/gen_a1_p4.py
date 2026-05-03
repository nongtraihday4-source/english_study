"""Group 4: Articles/nouns second half (19-20) + there/it (21-22) + Adj/Adv (23-25) + rest (26-30)"""

TOPICS = [
  {
    "level": "A1",
    "title": "Lượng từ: Much / Many / A lot / A few / A little",
    "slug": "quantity-expressions",
    "order": 28,
    "chapter": "Articles, nouns, pronouns, and determiners.",
    "description": "Cách dùng các từ chỉ số lượng với danh từ đếm được và không đếm được.",
    "analogy": "Much/Many như hai cái cân khác nhau: much cho chất lỏng, many cho vật rắn có thể đếm.",
    "real_world_use": "Nói về số lượng thức ăn, tiền bạc, thời gian, người trong các tình huống hàng ngày.",
    "memory_hook": "Much + không đếm được. Many + đếm được số nhiều. A lot of = cả hai.",
    "icon": "🔢",
    "rules": [
      {
        "title": "Much / Many / A lot of",
        "formula": "much + uncountable | many + countable plural | a lot of + both",
        "explanation": "Much dùng với danh từ không đếm được (thường trong câu phủ định/hỏi). Many dùng với danh từ đếm được số nhiều. A lot of / lots of dùng với cả hai, phổ biến trong câu khẳng định.",
        "memory_hook": "Much = nhiều (không đếm được). Many = nhiều (đếm được). A lot = nhiều (cả hai, thông dụng hơn).",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Từ", "Dùng với", "Ví dụ"],
          "rows": [
            ["much", "Uncountable (thường phủ định/hỏi)", "I don't have much money. How much time?"],
            ["many", "Countable plural (thường phủ định/hỏi)", "Not many people came. How many books?"],
            ["a lot of / lots of", "Cả hai, câu khẳng định", "She has a lot of friends. I drink a lot of water."],
            ["How much?", "Hỏi số lượng (uncountable)", "How much does it cost?"],
            ["How many?", "Hỏi số lượng (countable)", "How many students are there?"]
          ]
        },
        "examples": [
          {"sentence": "There are many cafes in this street.", "translation": "Trên con phố này có nhiều quán cà phê.", "highlight": "many cafes", "is_correct": True},
          {"sentence": "I don't have much time.", "translation": "Tôi không có nhiều thời gian.", "highlight": "much time", "is_correct": True},
          {"sentence": "She drinks a lot of coffee.", "translation": "Cô ấy uống rất nhiều cà phê.", "highlight": "a lot of coffee", "is_correct": True},
          {"sentence": "How many money do you have?", "translation": "❌ Sai — money không đếm được → much.", "highlight": "many money", "is_correct": False}
        ]
      },
      {
        "title": "A few / A little / Few / Little",
        "formula": "a few + countable | a little + uncountable | few/little = không nhiều (tiêu cực)",
        "explanation": "A few (một vài) và a little (một chút) mang nghĩa tích cực — có đủ. Few (rất ít) và little (rất ít) mang nghĩa tiêu cực — không đủ.",
        "memory_hook": "a few/a little = có một chút (ổn). few/little (không có 'a') = quá ít (vấn đề).",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Từ", "Dùng với", "Ý nghĩa"],
          "rows": [
            ["a few", "Countable plural", "I have a few friends. (một vài, đủ)"],
            ["a little", "Uncountable", "I have a little money. (một chút, đủ)"],
            ["few", "Countable plural", "Few people know this. (rất ít, gần không)"],
            ["little", "Uncountable", "There's little hope. (rất ít, gần không)"]
          ]
        },
        "examples": [
          {"sentence": "Wait a few minutes, please.", "translation": "Vui lòng chờ vài phút.", "highlight": "a few minutes", "is_correct": True},
          {"sentence": "I have a little money left.", "translation": "Tôi còn lại một chút tiền.", "highlight": "a little money", "is_correct": True},
          {"sentence": "Very few students passed the exam.", "translation": "Rất ít học sinh vượt qua kỳ thi. (hầu như không ai)", "highlight": "Very few students", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["much", "many", "a lot", "lots of", "a few", "a little", "how much", "how many"],
    "common_mistakes": [
      {"wrong": "I have many money.", "correct": "I have a lot of money.", "explanation": "'Money' không đếm được → dùng 'much' hoặc 'a lot of'."},
      {"wrong": "She has much friends.", "correct": "She has many friends.", "explanation": "'Friends' đếm được số nhiều → 'many'."},
      {"wrong": "Can I have few water?", "correct": "Can I have a little water?", "explanation": "Câu xin = 'a little', không phải 'few'. 'Few' mang nghĩa tiêu cực."}
    ],
    "notes": [
      {"type": "tip", "text": "Trong văn nói thông thường: 'a lot of' phổ biến hơn 'much/many' trong câu khẳng định. 'Do you have much time?' hơi trang trọng. 'Do you have a lot of time?' tự nhiên hơn."}
    ]
  },
  {
    "level": "A1",
    "title": "Whose? và Possessive 's",
    "slug": "whose-possessive-s",
    "order": 29,
    "chapter": "Articles, nouns, pronouns, and determiners.",
    "description": "Cách hỏi 'của ai?' và cách dùng 's để biểu thị sở hữu.",
    "analogy": "Possessive 's như chiếc nhãn dán tên trên đồ vật — nó kết nối người với đồ vật của họ.",
    "real_world_use": "Hỏi về quyền sở hữu và nói về đồ vật của ai đó.",
    "memory_hook": "Tom's book = cuốn sách của Tom. Whose book? = Của ai?",
    "icon": "🏷️",
    "rules": [
      {
        "title": "Possessive 's và Whose?",
        "formula": "Noun + 's + noun | Whose + noun + is/are + this/that?",
        "explanation": "Thêm 's sau danh từ số ít hoặc tên riêng để biểu thị sở hữu. Số nhiều kết thúc bằng -s: chỉ thêm ' (apostrophe). Whose dùng để hỏi 'của ai?'",
        "memory_hook": "Tom's (của Tom) | the students' (của các sinh viên) | Whose? (của ai?)",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Trường hợp", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Số ít", "Name/'s + noun", "Tom's car. My sister's phone."],
            ["Số nhiều kết thúc -s", "Noun' + noun", "The students' books."],
            ["Số nhiều bất quy tắc", "Noun's + noun", "The children's room."],
            ["Câu hỏi", "Whose + noun + is this?", "Whose bag is this? It's Lisa's."]
          ]
        },
        "examples": [
          {"sentence": "This is my brother's laptop.", "translation": "Đây là máy tính xách tay của anh tôi.", "highlight": "brother's", "is_correct": True},
          {"sentence": "Whose jacket is this? It's John's.", "translation": "Đây là áo khoác của ai? Của John.", "highlight": "Whose / John's", "is_correct": True},
          {"sentence": "The teacher's desk is near the window.", "translation": "Bàn của giáo viên ở gần cửa sổ.", "highlight": "teacher's", "is_correct": True }
        ]
      }
    ],
    "signal_words": ["whose", "'s", "of the..."],
    "common_mistakes": [
      {"wrong": "The book of John is on the table.", "correct": "John's book is on the table.", "explanation": "Trong tiếng Anh, dùng possessive 's thay vì 'of' cho người."},
      {"wrong": "It's John's.", "translation": "Thực ra đây là ĐÚNG khi trả lời 'Whose is it?'", "correct": "It's John's. ✓", "explanation": "Đại từ sở hữu hoặc possessive 's đứng cuối câu là đúng."}
    ],
    "notes": [
      {"type": "info", "text": "Possessive 's vs of: Dùng 's cho người/động vật ('the dog's tail'). Dùng 'of' cho đồ vật ('the door of the car', không phải 'the car's door')."},
      {"type": "warning", "text": "Đừng nhầm: 'Tom's' (sở hữu) vs 'Tom's here' (= Tom is). 's có thể là sở hữu hoặc rút gọn của 'is/has'."}
    ]
  },
  {
    "level": "A1",
    "title": "There is / There are",
    "slug": "there-is-are",
    "order": 30,
    "chapter": "there and it",
    "description": "Dùng 'there is/are' để nói về sự tồn tại của người, vật hoặc địa điểm.",
    "analogy": "There is/are như một biển hiệu thông báo: 'Ở đây có...' — giới thiệu sự tồn tại.",
    "real_world_use": "Mô tả nơi chốn, liệt kê những gì có trong phòng, tòa nhà, thành phố.",
    "memory_hook": "There IS (số ít). There ARE (số nhiều). Chủ ngữ thật đứng SAU 'there is/are'.",
    "icon": "📍",
    "rules": [
      {
        "title": "There is / There are — FORM & USAGE",
        "formula": "There is + singular N | There are + plural N",
        "explanation": "Dùng 'there is/are' để giới thiệu sự tồn tại. Động từ chia theo danh từ đứng sau (số ít hoặc số nhiều). Phủ định: there isn't / there aren't. Câu hỏi: Is there...? / Are there...?",
        "memory_hook": "'There' là chủ ngữ giả. Danh từ thật đứng sau mới quyết định is/are.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Số ít (khẳng định)", "There is + N", "There is a bank near here."],
            ["Số nhiều (khẳng định)", "There are + N", "There are five students."],
            ["Số ít (phủ định)", "There isn't + N", "There isn't a supermarket."],
            ["Số nhiều (phủ định)", "There aren't + N", "There aren't any chairs."],
            ["Câu hỏi", "Is there...? / Are there...?", "Is there a toilet here?"]
          ]
        },
        "examples": [
          {"sentence": "There is a big park in my neighbourhood.", "translation": "Trong khu phố tôi có một công viên lớn.", "highlight": "There is", "is_correct": True},
          {"sentence": "There are two bedrooms in the apartment.", "translation": "Căn hộ có hai phòng ngủ.", "highlight": "There are", "is_correct": True},
          {"sentence": "Is there a gym near the hotel?", "translation": "Gần khách sạn có phòng tập thể dục không?", "highlight": "Is there", "is_correct": True},
          {"sentence": "There are a problem.", "translation": "❌ Sai — problem là số ít → there is.", "highlight": "There are a problem", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["in the room", "on the table", "near here", "in this city", "at the corner"],
    "common_mistakes": [
      {"wrong": "There is many shops here.", "correct": "There are many shops here.", "explanation": "'Many shops' là số nhiều → 'there are'."},
      {"wrong": "Is there any books?", "correct": "Are there any books?", "explanation": "'Books' là số nhiều → 'are there'."},
      {"wrong": "There have a pool.", "correct": "There is a pool.", "explanation": "Dùng 'there is/are', không phải 'there have'."}
    ],
    "notes": [
      {"type": "tip", "text": "There is/are ở thì quá khứ: There was (số ít) / There were (số nhiều). 'There was a beautiful garden here.' / 'There were many people at the party.'"},
      {"type": "info", "text": "Khi có danh sách, chia theo danh từ đầu tiên: 'There is a pen and two books on the desk.' (hoặc 'There are two books and a pen.') — cả hai đều chấp nhận được."}
    ]
  },
  {
    "level": "A1",
    "title": "It — Chủ từ giả",
    "slug": "it-subject",
    "order": 31,
    "chapter": "there and it",
    "description": "Dùng 'it' để nói về thời gian, thời tiết, khoảng cách, nhiệt độ và các chủ đề chung.",
    "analogy": "'It' như người phát ngôn ẩn danh — nói thay cho thứ không có tên cụ thể.",
    "real_world_use": "Nói về thời tiết, thời gian, mô tả ngày, khoảng cách trong cuộc sống hàng ngày.",
    "memory_hook": "It is + thời tiết/thời gian/khoảng cách. Không có chủ ngữ thật.",
    "icon": "🌤️",
    "rules": [
      {
        "title": "It — Nói về thời tiết, thời gian, khoảng cách",
        "formula": "It + is/was + [weather / time / distance / temperature]",
        "explanation": "Dùng 'it' làm chủ ngữ giả (dummy subject) khi không có chủ ngữ thật. Phổ biến nhất cho: thời tiết, thời gian, khoảng cách.",
        "memory_hook": "What time is it? — It's 3 o'clock. What's the weather like? — It's sunny.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Chủ đề", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Thời tiết", "It + is/was + adj", "It is sunny today. / It was cold yesterday."],
            ["Thời gian", "It + is + time", "It's half past two. It's Monday."],
            ["Khoảng cách", "It + is + distance + from...to", "It's 5 km from here to school."],
            ["Nhiệt độ", "It + is + degrees", "It's 35 degrees today."],
            ["Ngày/tháng/năm", "It + is + date", "It's the 15th of April."]
          ]
        },
        "examples": [
          {"sentence": "It's raining heavily.", "translation": "Trời đang mưa to.", "highlight": "It's raining", "is_correct": True},
          {"sentence": "What time is it? It's 7:30.", "translation": "Mấy giờ rồi? Bảy rưỡi.", "highlight": "It's", "is_correct": True},
          {"sentence": "It's about 2 hours from Hanoi to Ha Long Bay.", "translation": "Từ Hà Nội đến Vịnh Hạ Long khoảng 2 tiếng.", "highlight": "It's about 2 hours", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["it's", "what time", "what day", "how far", "how cold/hot", "what's the weather like"],
    "common_mistakes": [
      {"wrong": "Today is sunny.", "correct": "It is sunny today.", "explanation": "Thời tiết dùng 'It is', không phải 'Today is sunny' (mặc dù câu này không sai hoàn toàn, nhưng không tự nhiên)."},
      {"wrong": "Is cold outside.", "correct": "It is cold outside.", "explanation": "Câu tiếng Anh phải có chủ ngữ. Dùng 'it' làm chủ ngữ giả."}
    ],
    "notes": [
      {"type": "info", "text": "'It takes...' = mất bao lâu: 'It takes 20 minutes to walk there.' / 'It took two hours to drive.'"}
    ]
  },
  {
    "level": "A1",
    "title": "Tính từ (Adjectives)",
    "slug": "adjectives",
    "order": 32,
    "chapter": "Adjectives and adverbs",
    "description": "Tính từ mô tả người, vật. Vị trí của tính từ, triệu từ sắp xếp và liên kết tính từ.",
    "analogy": "Tính từ như màu sơn — chúng tô màu và chi tiết hóa các danh từ.",
    "real_world_use": "Mô tả người, địa điểm, cảm xúc — không thể thiếu trong mọi cuộc trò chuyện.",
    "memory_hook": "Tính từ đứng TRƯỚC noun (a tall man) hoặc SAU be (He is tall). Không thêm -s!",
    "icon": "🎨",
    "rules": [
      {
        "title": "Vị trí và hình thức của Tính từ",
        "formula": "Adj + Noun (attributive) | S + be + Adj (predicative)",
        "explanation": "Tính từ tiếng Anh đứng TRƯỚC danh từ (attributive) hoặc sau động từ 'be' và các liên kết động từ (predicative). Tính từ KHÔNG thêm -s cho số nhiều.",
        "memory_hook": "a beautiful flower / The flower is beautiful. — Không bao giờ: a flowers beautiful ❌",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Vị trí", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Trước noun", "adj + noun", "a cold day, an interesting book"],
            ["Sau be", "S + be + adj", "The weather is cold. She seems tired."],
            ["Sau liên kết động từ", "S + look/feel/sound/smell/taste + adj", "This soup smells delicious."],
            ["KHÔNG thêm -s", "adj (same for plural)", "two big cars (not bigs)"]
          ]
        },
        "examples": [
          {"sentence": "It was a wonderful experience.", "translation": "Đó là một trải nghiệm tuyệt vời.", "highlight": "wonderful", "is_correct": True},
          {"sentence": "The soup tastes delicious.", "translation": "Món súp này ngon tuyệt.", "highlight": "tastes delicious", "is_correct": True},
          {"sentence": "She has bigs dreams.", "translation": "❌ Sai — tính từ không thêm -s.", "highlight": "bigs", "is_correct": False}
        ]
      },
      {
        "title": "Thứ tự tính từ (Order of Adjectives)",
        "formula": "Opinion → Size → Age → Shape → Color → Origin → Material → Purpose + Noun",
        "explanation": "Khi dùng nhiều tính từ, có thứ tự chuẩn. Trong giao tiếp A1, thường chỉ dùng 1-2 tính từ.",
        "memory_hook": "OSASCOMP: Opinion, Size, Age, Shape, Color, Origin, Material, Purpose",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Thứ tự", "Loại", "Ví dụ"],
          "rows": [
            ["1", "Opinion (đánh giá)", "beautiful, ugly, nice, wonderful"],
            ["2", "Size (kích cỡ)", "big, small, tall, short, long"],
            ["3", "Age (tuổi)", "old, young, new, ancient"],
            ["4", "Color (màu)", "red, blue, green, black"],
            ["5", "Origin (xuất xứ)", "Vietnamese, French, Italian"],
            ["6", "Material (chất liệu)", "wooden, metal, plastic, silk"]
          ]
        },
        "examples": [
          {"sentence": "She bought a beautiful small red bag.", "translation": "Cô ấy mua một chiếc túi đỏ nhỏ xinh.", "highlight": "beautiful small red", "is_correct": True},
          {"sentence": "He drives a fast Italian sports car.", "translation": "Anh ấy lái một chiếc xe thể thao nhanh của Ý.", "highlight": "fast Italian", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["very", "really", "quite", "so", "too", "extremely"],
    "common_mistakes": [
      {"wrong": "She is a doctor tall.", "correct": "She is a tall doctor.", "explanation": "Tính từ đứng TRƯỚC danh từ."},
      {"wrong": "They are goods students.", "correct": "They are good students.", "explanation": "Tính từ không thêm -s."},
      {"wrong": "He feels tiredly.", "correct": "He feels tired.", "explanation": "Sau linking verbs (feel, look, seem, sound) dùng tính từ, không phải trạng từ."}
    ],
    "notes": [
      {"type": "tip", "text": "Cường độ tính từ: a bit cold → quite cold → very cold → extremely cold → freezing cold."},
      {"type": "info", "text": "Linking verbs (ngoài 'be'): look, feel, seem, sound, smell, taste, appear, become, get. Những động từ này theo sau bởi tính từ: 'You look beautiful today.'"}
    ]
  },
  {
    "level": "A1",
    "title": "Trạng từ cách thức (Adverbs of Manner)",
    "slug": "adverbs-of-manner",
    "order": 33,
    "chapter": "Adjectives and adverbs",
    "description": "Trạng từ mô tả cách thức hành động được thực hiện. Cách tạo trạng từ từ tính từ.",
    "analogy": "Tính từ là màu sắc của danh từ; trạng từ là tốc độ và phong cách của động từ.",
    "real_world_use": "Mô tả cách bạn làm việc, đi lại, nói chuyện — thêm chi tiết cho hành động.",
    "memory_hook": "Adj + -ly = Adverb: slow → slowly, quick → quickly, careful → carefully.",
    "icon": "⚡",
    "rules": [
      {
        "title": "Tạo trạng từ từ tính từ + Vị trí",
        "formula": "adj + -ly | adj-y → -ily | adj-le → -ly | irregular",
        "explanation": "Hầu hết trạng từ cách thức = adj + ly. Vị trí: sau động từ chính hoặc sau tân ngữ. Một số bất quy tắc: good→well, fast→fast, hard→hard.",
        "memory_hook": "quick→quickly. easy→easily (y→ily). gentle→gently (-le→-ly). good→well (ngoại lệ!)",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Tính từ", "Trạng từ", "Ví dụ câu"],
          "rows": [
            ["quick", "quickly", "She runs quickly."],
            ["slow", "slowly", "Please speak slowly."],
            ["careful", "carefully", "Drive carefully!"],
            ["easy", "easily", "He solved it easily."],
            ["good", "well (bất quy tắc)", "She sings well."],
            ["fast", "fast (không thêm -ly)", "He drives fast."],
            ["hard", "hard (không thêm -ly)", "They work hard."]
          ]
        },
        "examples": [
          {"sentence": "She sang beautifully at the concert.", "translation": "Cô ấy đã hát hay tuyệt vời trong buổi hòa nhạc.", "highlight": "beautifully", "is_correct": True},
          {"sentence": "He works very hard.", "translation": "Anh ấy làm việc rất chăm chỉ.", "highlight": "hard", "is_correct": True},
          {"sentence": "Can you speak more slowly, please?", "translation": "Bạn có thể nói chậm hơn không?", "highlight": "more slowly", "is_correct": True},
          {"sentence": "She plays the piano good.", "translation": "❌ Sai — dùng 'well' không phải 'good'.", "highlight": "good", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["slowly", "quickly", "carefully", "well", "fast", "hard", "loudly", "quietly"],
    "common_mistakes": [
      {"wrong": "She sings good.", "correct": "She sings well.", "explanation": "'Good' là tính từ. Trạng từ của 'good' là 'well'."},
      {"wrong": "He runs fastly.", "correct": "He runs fast.", "explanation": "'Fast' là vừa tính từ vừa trạng từ. Không có 'fastly'."},
      {"wrong": "Please drive careful.", "correct": "Please drive carefully.", "explanation": "'Careful' là tính từ → trạng từ phải là 'carefully'."}
    ],
    "notes": [
      {"type": "tip", "text": "Hardly ≠ hard: 'He works hard.' (chăm chỉ) vs 'He hardly works.' (gần như không làm). Đây là hai từ khác nhau hoàn toàn!"},
      {"type": "info", "text": "Trạng từ tần suất (always, usually, often...) khác với trạng từ cách thức. Trạng từ tần suất đứng trước động từ chính, trạng từ cách thức đứng sau."}
    ]
  },
  {
    "level": "A1",
    "title": "So sánh: Comparative & Superlative",
    "slug": "comparative-superlative",
    "order": 34,
    "chapter": "Adjectives and adverbs",
    "description": "Cách so sánh hơn (comparative) và so sánh nhất (superlative) của tính từ và trạng từ.",
    "analogy": "Comparative = bậc thang so sánh hai. Superlative = đỉnh của thang, không ai hơn.",
    "real_world_use": "Chọn lựa, đánh giá, mua sắm, mô tả khác biệt giữa người/vật.",
    "memory_hook": "Short adj: -er than / the -est. Long adj: more... than / the most...",
    "icon": "📊",
    "rules": [
      {
        "title": "Comparative — So sánh hơn",
        "formula": "Short adj + -er + than | more + long adj + than",
        "explanation": "Tính từ ngắn (1-2 âm tiết): thêm -er + than. Tính từ dài (2+ âm tiết): more + adj + than. Bất quy tắc: good→better, bad→worse, far→farther/further.",
        "memory_hook": "old→older, big→bigger (double). easy→easier (y→i). beautiful→more beautiful.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["1-2 âm tiết", "adj + -er + than", "She is taller than me. This is cheaper."],
            ["Kết thúc -e", "adj + r + than", "nice→nicer, large→larger"],
            ["Kết thúc CVC", "double C + er + than", "big→bigger, hot→hotter"],
            ["Kết thúc -y", "adj(i) + er + than", "happy→happier, easy→easier"],
            ["Nhiều âm tiết", "more + adj + than", "more expensive, more comfortable"],
            ["Bất quy tắc", "—", "good→better, bad→worse, far→farther"]
          ]
        },
        "examples": [
          {"sentence": "My new phone is faster than the old one.", "translation": "Điện thoại mới của tôi nhanh hơn cái cũ.", "highlight": "faster than", "is_correct": True},
          {"sentence": "Hanoi is more expensive than my hometown.", "translation": "Hà Nội đắt đỏ hơn quê tôi.", "highlight": "more expensive than", "is_correct": True},
          {"sentence": "He is more taller than his brother.", "translation": "❌ Sai — không dùng 'more' với tính từ ngắn.", "highlight": "more taller", "is_correct": False}
        ]
      },
      {
        "title": "Superlative — So sánh nhất",
        "formula": "the + short adj + -est | the most + long adj",
        "explanation": "So sánh nhất dùng 'the' + -est (tính từ ngắn) hoặc 'the most' + adj (tính từ dài). Bất quy tắc: good→best, bad→worst.",
        "memory_hook": "the tallest person in the room. the most beautiful city in the world.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Ngắn", "the + adj + -est", "the tallest, the cheapest, the biggest"],
            ["Dài", "the most + adj", "the most expensive, the most popular"],
            ["Bất quy tắc", "—", "the best, the worst, the farthest"]
          ]
        },
        "examples": [
          {"sentence": "She is the best student in the class.", "translation": "Cô ấy là học sinh giỏi nhất lớp.", "highlight": "the best", "is_correct": True},
          {"sentence": "It's the most beautiful place I've ever seen.", "translation": "Đó là nơi đẹp nhất tôi từng thấy.", "highlight": "the most beautiful", "is_correct": True},
          {"sentence": "He is the most tall player in the team.", "translation": "❌ Sai — 'tall' là ngắn → 'the tallest'.", "highlight": "the most tall", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["than", "the most", "the least", "as ... as", "not as ... as", "in the world", "in the class"],
    "common_mistakes": [
      {"wrong": "She is more taller than me.", "correct": "She is taller than me.", "explanation": "Không dùng 'more' với tính từ ngắn đã thêm -er."},
      {"wrong": "He is the most good player.", "correct": "He is the best player.", "explanation": "'Good' có superlative bất quy tắc: the best."},
      {"wrong": "This is the more expensive one.", "correct": "This is the most expensive one.", "explanation": "Superlative dùng 'the most', không phải 'the more'."}
    ],
    "notes": [
      {"type": "tip", "text": "As ... as: 'He is as tall as his father.' (bằng nhau). Not as ... as: 'She is not as fast as him.' (kém hơn)."},
      {"type": "info", "text": "Tính từ có 2 âm tiết kết thúc -er, -le, -ow, -y thường dùng -er/-est: clever→cleverer, simple→simpler, narrow→narrower."}
    ]
  },
  {
    "level": "A1",
    "title": "Liên từ: And / But / Or / So / Because",
    "slug": "conjunctions",
    "order": 35,
    "chapter": "Conjunctions",
    "description": "Các liên từ cơ bản để nối câu và ý kiến.",
    "analogy": "Liên từ như cầu nối — kết nối các ý tưởng riêng lẻ thành một câu liền mạch.",
    "real_world_use": "Thêm thông tin, đối lập, lựa chọn, hậu quả và lý do trong giao tiếp.",
    "memory_hook": "AND (thêm). BUT (đối lập). OR (lựa chọn). SO (kết quả). BECAUSE (lý do).",
    "icon": "🔗",
    "rules": [
      {
        "title": "Liên từ phối hợp và bổ sung",
        "formula": "and | but | or | so | because | when | before | after",
        "explanation": "And (thêm thông tin), But (đối lập/tương phản), Or (lựa chọn), So (kết quả), Because (lý do). When/before/after nối hai mệnh đề với thời gian.",
        "memory_hook": "FANBOYS: For, And, Nor, But, Or, Yet, So — các liên từ phối hợp.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Liên từ", "Chức năng", "Ví dụ"],
          "rows": [
            ["and", "Thêm thông tin", "I like coffee and tea."],
            ["but", "Tương phản / đối lập", "He is smart but lazy."],
            ["or", "Lựa chọn", "Tea or coffee?"],
            ["so", "Kết quả / hậu quả", "It was raining, so I took an umbrella."],
            ["because", "Lý do", "I'm tired because I worked late."],
            ["when", "Thời gian", "Call me when you arrive."],
            ["before/after", "Trình tự thời gian", "Wash your hands before eating."]
          ]
        },
        "examples": [
          {"sentence": "She is kind and helpful.", "translation": "Cô ấy tốt bụng và hay giúp đỡ.", "highlight": "and", "is_correct": True},
          {"sentence": "I wanted to go, but I was too tired.", "translation": "Tôi muốn đi, nhưng tôi quá mệt.", "highlight": "but", "is_correct": True},
          {"sentence": "Do you want tea or coffee?", "translation": "Bạn muốn uống trà hay cà phê?", "highlight": "or", "is_correct": True},
          {"sentence": "He missed the bus, so he was late.", "translation": "Anh ấy lỡ xe buýt nên đến muộn.", "highlight": "so", "is_correct": True},
          {"sentence": "I love Vietnamese food because it's delicious.", "translation": "Tôi yêu thức ăn Việt Nam vì nó ngon.", "highlight": "because", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["and", "but", "or", "so", "because", "when", "before", "after", "although", "however"],
    "common_mistakes": [
      {"wrong": "I'm tired, because I worked hard.", "correct": "I'm tired because I worked hard.", "explanation": "Không dùng dấu phẩy trước 'because' trong câu đơn giản."},
      {"wrong": "Although it was cold, but I went out.", "correct": "Although it was cold, I went out. / It was cold, but I went out.", "explanation": "Không dùng cả 'although' và 'but' trong cùng một câu."}
    ],
    "notes": [
      {"type": "tip", "text": "'So' (liên từ) = vì vậy, kết quả. Khác với 'so' (trạng từ) = rất: 'I'm so tired.' (rất mệt)."},
      {"type": "info", "text": "Liên từ phụ 'because' nối mệnh đề nguyên nhân: 'I stayed home because it was raining.' Để hỏi lý do: 'Why did you stay home? Because it was raining.'"}
    ]
  },
  {
    "level": "A1",
    "title": "Giới từ thời gian: At / In / On",
    "slug": "prepositions-time",
    "order": 36,
    "chapter": "Prepositions",
    "description": "Ba giới từ thời gian cơ bản và quy tắc sử dụng.",
    "analogy": "AT = điểm chính xác trên dòng thời gian. IN = khoảng thời gian. ON = bề mặt thời gian (ngày cụ thể).",
    "real_world_use": "Nói về lịch trình, hẹn hò, sự kiện — cần thiết cho mọi cuộc trò chuyện về thời gian.",
    "memory_hook": "AT 3 o'clock / IN the morning / ON Monday. (giờ → khoảng → ngày).",
    "icon": "🕐",
    "rules": [
      {
        "title": "At / In / On — Giới từ thời gian",
        "formula": "at + time/specific point | in + month/year/period | on + day/date",
        "explanation": "AT: giờ cụ thể, thời điểm chính xác. IN: buổi (morning/afternoon), tháng, năm, thập niên, mùa. ON: ngày trong tuần, ngày cụ thể (với date).",
        "memory_hook": "AT a point. IN a period. ON a surface/day.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Giới từ", "Dùng với", "Ví dụ"],
          "rows": [
            ["at", "Giờ cụ thể", "at 9 o'clock, at noon, at midnight"],
            ["at", "Thời điểm cụ thể", "at Christmas, at the weekend (BrE)"],
            ["in", "Buổi (morning/afternoon/evening)", "in the morning, in the evening"],
            ["in", "Tháng / Năm / Mùa", "in April, in 2024, in summer"],
            ["on", "Ngày trong tuần", "on Monday, on Tuesday"],
            ["on", "Ngày/ngày tháng cụ thể", "on 15 April, on my birthday"],
            ["Không dùng giới từ", "this/last/next/every + time", "this morning, last night, next week"]
          ]
        },
        "examples": [
          {"sentence": "The meeting is at 10 o'clock.", "translation": "Cuộc họp lúc 10 giờ.", "highlight": "at 10 o'clock", "is_correct": True},
          {"sentence": "She was born in 1998.", "translation": "Cô ấy sinh năm 1998.", "highlight": "in 1998", "is_correct": True},
          {"sentence": "I have a class on Friday morning.", "translation": "Tôi có lớp học sáng thứ Sáu.", "highlight": "on Friday morning", "is_correct": True},
          {"sentence": "I'll see you in Monday.", "translation": "❌ Sai — dùng 'on Monday'.", "highlight": "in Monday", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["at", "in", "on", "this", "next", "last", "every"],
    "common_mistakes": [
      {"wrong": "I'll see you in Monday.", "correct": "I'll see you on Monday.", "explanation": "Ngày trong tuần dùng 'on'."},
      {"wrong": "She arrived on the morning.", "correct": "She arrived in the morning.", "explanation": "Buổi (morning/afternoon/evening) dùng 'in'."},
      {"wrong": "I go to work at morning.", "correct": "I go to work in the morning.", "explanation": "'In the morning' — buổi sáng dùng 'in', không phải 'at'."},
      {"wrong": "I'll see you on next Monday.", "correct": "I'll see you next Monday.", "explanation": "Không dùng 'on' trước 'next/last/this + ngày'."}
    ],
    "notes": [
      {"type": "tip", "text": "Không dùng giới từ trước 'this, last, next, every': 'I'll see you this Friday.' / 'She called last night.' / 'We meet every Monday.'"},
      {"type": "info", "text": "at night (ban đêm, nói chung) nhưng in the night/morning/afternoon/evening (có mạo từ 'the')."}
    ]
  },
  {
    "level": "A1",
    "title": "Giới từ nơi chốn",
    "slug": "prepositions-place",
    "order": 37,
    "chapter": "Prepositions",
    "description": "Các giới từ chỉ nơi chốn và vị trí: in, on, at, above, below, next to, between, in front of...",
    "analogy": "Giới từ nơi chốn như ứng dụng bản đồ — xác định chính xác vị trí của mọi thứ.",
    "real_world_use": "Mô tả nơi chốn, hướng dẫn đường đi, nói về vị trí trong nhà/văn phòng.",
    "memory_hook": "IN (bên trong). ON (trên bề mặt). AT (tại điểm/địa chỉ).",
    "icon": "📍",
    "rules": [
      {
        "title": "In / On / At — Vị trí cơ bản",
        "formula": "in (enclosed space) | on (surface) | at (point/address)",
        "explanation": "In: bên trong không gian kín (in a room, in a box, in Hanoi). On: trên bề mặt (on the table, on the wall, on the floor). At: tại một điểm/địa chỉ cụ thể (at the door, at 123 Main St, at school).",
        "memory_hook": "IN = bao quanh bạn. ON = dưới chân bạn. AT = điểm cụ thể.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Giới từ", "Dùng cho", "Ví dụ"],
          "rows": [
            ["in", "Không gian kín, thành phố, nước", "in the box, in Hanoi, in Vietnam"],
            ["on", "Bề mặt, sàn, tường", "on the table, on the wall, on the floor"],
            ["at", "Điểm/địa chỉ cụ thể", "at the bus stop, at 10 Downing Street"],
            ["above/below", "Cao hơn/thấp hơn", "above the clouds, below zero"],
            ["next to/beside", "Bên cạnh", "next to the bank, beside the tree"],
            ["between", "Giữa hai thứ", "between the library and the park"],
            ["in front of / behind", "Trước/sau", "in front of the cinema, behind the hotel"],
            ["opposite", "Đối diện", "opposite the station"]
          ]
        },
        "examples": [
          {"sentence": "My keys are on the kitchen table.", "translation": "Chìa khóa của tôi ở trên bàn bếp.", "highlight": "on the kitchen table", "is_correct": True},
          {"sentence": "She lives in Ho Chi Minh City.", "translation": "Cô ấy sống ở Thành phố Hồ Chí Minh.", "highlight": "in Ho Chi Minh City", "is_correct": True},
          {"sentence": "Meet me at the front entrance.", "translation": "Gặp tôi ở lối vào trước.", "highlight": "at the front entrance", "is_correct": True},
          {"sentence": "The dog is in front of the house.", "translation": "Con chó đứng trước nhà.", "highlight": "in front of", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["in", "on", "at", "above", "below", "next to", "between", "in front of", "behind", "opposite", "near"],
    "common_mistakes": [
      {"wrong": "She is at the bed.", "correct": "She is in bed.", "explanation": "'In bed' = đang nằm/ngủ trên giường. 'At the bed' không tự nhiên."},
      {"wrong": "I live in 123 Main Street.", "correct": "I live at 123 Main Street.", "explanation": "Địa chỉ nhà với số nhà → dùng 'at'."},
      {"wrong": "The book is in the table.", "correct": "The book is on the table.", "explanation": "Trên bề mặt → 'on'. 'In' nghĩa là bên trong."}
    ],
    "notes": [
      {"type": "tip", "text": "on the left/right. in the corner. at the top/bottom. in the middle. — Những cụm này vừa là cụm thành ngữ cần nhớ."},
      {"type": "info", "text": "Địa danh quy tắc: at (điểm nhỏ): at the station / at school. in (vùng lớn): in the city / in England. Nhưng: at home, at work, at school (thành ngữ, không có 'the')."}
    ]
  },
  {
    "level": "A1",
    "title": "Câu hỏi và Từ hỏi",
    "slug": "questions-word-order",
    "order": 38,
    "chapter": "Questions",
    "description": "Cách tạo câu hỏi Yes/No và câu hỏi với từ để hỏi (Wh- questions).",
    "analogy": "Yes/No questions = đèn bật/tắt. Wh- questions = ô trống cần điền thông tin.",
    "real_world_use": "Mọi cuộc hội thoại đều cần câu hỏi — đây là kỹ năng giao tiếp thiết yếu.",
    "memory_hook": "Yes/No: đảo to be/modal/do lên đầu. Wh: Wh-word + Yes/No question order.",
    "icon": "❓",
    "rules": [
      {
        "title": "Yes/No Questions",
        "formula": "Am/Is/Are/Was/Were + S...? | Do/Does/Did + S + V-base...? | Modal + S + V...?",
        "explanation": "Để tạo câu hỏi Yes/No: đảo trợ động từ lên trước chủ ngữ. Dùng do/does/did nếu không có trợ động từ.",
        "memory_hook": "Đảo TRƯỚC chủ ngữ: 'She is' → 'Is she?'. 'You like' → 'Do you like?'.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Câu khẳng định", "Câu hỏi Yes/No"],
          "rows": [
            ["She is a teacher.", "Is she a teacher?"],
            ["They were happy.", "Were they happy?"],
            ["You can swim.", "Can you swim?"],
            ["He likes coffee.", "Does he like coffee?"],
            ["They went home.", "Did they go home?"]
          ]
        },
        "examples": [
          {"sentence": "Are you from Vietnam?", "translation": "Bạn có phải người Việt Nam không?", "highlight": "Are you", "is_correct": True},
          {"sentence": "Did she call you?", "translation": "Cô ấy có gọi cho bạn không?", "highlight": "Did she call", "is_correct": True},
          {"sentence": "Do you want to come?", "translation": "Bạn có muốn đến không?", "highlight": "Do you want", "is_correct": True}
        ]
      },
      {
        "title": "Wh- Questions (Câu hỏi với từ để hỏi)",
        "formula": "Wh-word + auxiliary + S + V? | Wh-word + is/are + ...?",
        "explanation": "Từ hỏi Wh- đứng đầu câu, sau đó là cấu trúc câu hỏi Yes/No. What (cái gì), Where (ở đâu), When (khi nào), Who (ai), Why (tại sao), How (thế nào), Which (cái nào).",
        "memory_hook": "What + did/does/do? Where + is/are? When + did? Why + do? How + are?",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Từ hỏi", "Hỏi về", "Ví dụ"],
          "rows": [
            ["What", "Vật/hành động", "What do you do? What is this?"],
            ["Where", "Nơi chốn", "Where do you live?"],
            ["When", "Thời gian", "When does the film start?"],
            ["Who", "Người (chủ ngữ)", "Who called you?"],
            ["Whom/Who", "Người (tân ngữ)", "Who did you call?"],
            ["Why", "Lý do", "Why are you sad?"],
            ["How", "Cách thức", "How do you go to work?"],
            ["How much/many", "Số lượng", "How much does it cost?"]
          ]
        },
        "examples": [
          {"sentence": "Where do you usually have lunch?", "translation": "Bạn thường ăn trưa ở đâu?", "highlight": "Where do you", "is_correct": True},
          {"sentence": "When was she born?", "translation": "Cô ấy sinh năm nào?", "highlight": "When was she", "is_correct": True},
          {"sentence": "Why didn't you call me?", "translation": "Tại sao bạn không gọi cho tôi?", "highlight": "Why didn't you", "is_correct": True },
          {"sentence": "How long does the journey take?", "translation": "Chuyến đi mất bao lâu?", "highlight": "How long does", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["what", "where", "when", "who", "why", "how", "which", "how much", "how many", "how long", "how often"],
    "common_mistakes": [
      {"wrong": "Where you live?", "correct": "Where do you live?", "explanation": "Câu hỏi cần trợ động từ. Dùng 'do' với Present Simple."},
      {"wrong": "What time the film starts?", "correct": "What time does the film start?", "explanation": "Cần 'does' và V-base trong câu hỏi Present Simple."},
      {"wrong": "Why she is crying?", "correct": "Why is she crying?", "explanation": "Trợ động từ đảo trước chủ ngữ."}
    ],
    "notes": [
      {"type": "tip", "text": "Who làm chủ ngữ (subject question): 'Who called you?' — không cần do/did. 'Who did you call?' — 'who' là tân ngữ, cần 'did'."},
      {"type": "info", "text": "Câu hỏi đuôi (Tag questions) ở A1: 'It's cold, isn't it?' / 'She can't drive, can she?' — đảo ngược trợ động từ và thêm not nếu khẳng định."}
    ]
  },
  {
    "level": "A1",
    "title": "Trật tự từ & Trạng từ tần suất",
    "slug": "word-order-frequency",
    "order": 39,
    "chapter": "Word order",
    "description": "Trật tự từ cơ bản trong tiếng Anh (S-V-O) và vị trí của trạng từ tần suất.",
    "analogy": "Câu tiếng Anh như đoàn tàu — đầu máy (S), toa hàng (V), hành khách (O) — phải đúng thứ tự.",
    "real_world_use": "Nền tảng của mọi câu tiếng Anh — hiểu trật tự từ giúp tránh hầu hết lỗi ngữ pháp.",
    "memory_hook": "S + V + O + (place) + (time). 'She eats pizza at home every day.'",
    "icon": "🔀",
    "rules": [
      {
        "title": "Trật tự từ cơ bản S-V-O",
        "formula": "Subject + Verb + Object + (Place) + (Time)",
        "explanation": "Câu tiếng Anh cơ bản: Chủ ngữ → Động từ → Tân ngữ. Trạng ngữ nơi chốn thường đặt trước trạng ngữ thời gian. Không thể đặt tân ngữ trước động từ.",
        "memory_hook": "SVO: She (S) loves (V) pizza (O). Time last, place before time.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Vị trí", "Thành phần", "Ví dụ"],
          "rows": [
            ["1", "Subject (Chủ ngữ)", "She"],
            ["2", "Verb (Động từ)", "eats"],
            ["3", "Object (Tân ngữ)", "lunch"],
            ["4", "Place (Nơi chốn)", "at the office"],
            ["5", "Time (Thời gian)", "every day"],
            ["Câu đầy đủ", "S+V+O+Place+Time", "She eats lunch at the office every day."]
          ]
        },
        "examples": [
          {"sentence": "I drink coffee every morning.", "translation": "Tôi uống cà phê mỗi sáng.", "highlight": "I (S) drink (V) coffee (O) every morning (time)", "is_correct": True},
          {"sentence": "She studies English at the library on weekends.", "translation": "Cô ấy học tiếng Anh ở thư viện vào cuối tuần.", "highlight": "studies (V) English (O) at the library (place) on weekends (time)", "is_correct": True},
          {"sentence": "Every day I coffee drink.", "translation": "❌ Sai — trật tự từ không đúng.", "highlight": "coffee drink", "is_correct": False}
        ]
      },
      {
        "title": "Vị trí của trạng từ tần suất",
        "formula": "Before main verb | After be/modal",
        "explanation": "Trạng từ tần suất (always, usually, often, sometimes, rarely, never): đặt TRƯỚC động từ chính nhưng SAU to be và modal verbs.",
        "memory_hook": "I ALWAYS eat breakfast. She IS always late. I can NEVER remember.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Trạng từ", "Tần suất", "Vị trí & Ví dụ"],
          "rows": [
            ["always", "100%", "I always have breakfast."],
            ["usually", "~80%", "She usually takes the bus."],
            ["often", "~60%", "We often eat out."],
            ["sometimes", "~40%", "He sometimes works late."],
            ["rarely/seldom", "~10%", "They rarely argue."],
            ["never", "0%", "I never miss a class."],
            ["Sau 'be'", "—", "She is always on time."],
            ["Sau modal", "—", "You can always ask me."]
          ]
        },
        "examples": [
          {"sentence": "I usually wake up at 6 AM.", "translation": "Tôi thường thức dậy lúc 6 giờ sáng.", "highlight": "usually wake up", "is_correct": True},
          {"sentence": "He is never late for meetings.", "translation": "Anh ấy không bao giờ đến muộn các cuộc họp.", "highlight": "is never late", "is_correct": True},
          {"sentence": "She always is punctual.", "translation": "❌ Sai — adverb sau 'is', không trước.", "highlight": "always is", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["always", "usually", "often", "sometimes", "rarely", "never", "every day", "once a week"],
    "common_mistakes": [
      {"wrong": "I go always to school by bus.", "correct": "I always go to school by bus.", "explanation": "Trạng từ tần suất đứng trước động từ chính ('go'), không sau nó."},
      {"wrong": "She is always late. → She always is late.", "correct": "She is always late.", "explanation": "Sau 'is/are/am' trạng từ tần suất đặt SAU to be, đúng vậy."},
      {"wrong": "Never I eat junk food.", "correct": "I never eat junk food.", "explanation": "Trạng từ tần suất không thường đứng đầu câu (trừ nhấn mạnh đặc biệt với đảo ngữ)."}
    ],
    "notes": [
      {"type": "tip", "text": "Để nhấn mạnh, có thể đặt trạng từ tần suất đầu câu: 'Sometimes I feel lonely.' / 'Often, the answers are simple.' — chấp nhận được nhưng ít phổ biến hơn."},
      {"type": "info", "text": "Không dùng trạng từ tần suất với Present Continuous (vì Continuous = đang xảy ra tại thời điểm đó, không thường xuyên)."}
    ]
  }
]
