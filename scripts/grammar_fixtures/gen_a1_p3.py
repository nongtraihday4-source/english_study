"""Group 3: -ing/infinitive (12-13) + Articles/nouns first half (14-18)"""

TOPICS = [
  {
    "level": "A1",
    "title": "Verbs + -ing",
    "slug": "verbs-ing",
    "order": 21,
    "chapter": "-ing and the infinitive",
    "description": "Một số động từ luôn theo sau bởi V-ing: like, love, hate, enjoy, finish, stop, mind...",
    "analogy": "Những động từ này 'thích ôm' một gerund (-ing) — chúng không đứng một mình.",
    "real_world_use": "Nói về sở thích, cảm xúc và việc đã hoàn thành.",
    "memory_hook": "enjoy/finish/mind/stop + V-ing (KHÔNG dùng 'to').",
    "icon": "🔄",
    "rules": [
      {
        "title": "Động từ theo sau bởi V-ing (Gerund)",
        "formula": "V1 + V2-ing",
        "explanation": "Một số động từ luôn theo sau bởi gerund (V-ing), không phải to-infinitive.",
        "memory_hook": "enjoy/finish/stop/mind/avoid + V-ing. Không bao giờ dùng 'to' với nhóm này.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Nhóm", "Động từ", "Ví dụ"],
          "rows": [
            ["Sở thích", "like, love, hate, enjoy, prefer", "I enjoy reading. / She hates waiting."],
            ["Hoàn thành/dừng", "finish, stop, give up", "He finished eating. / Stop talking!"],
            ["Né tránh", "avoid, mind", "I don't mind walking. / Avoid eating late."],
            ["Gợi ý", "suggest, recommend", "I suggest taking a taxi."]
          ]
        },
        "examples": [
          {"sentence": "I enjoy cooking Italian food.", "translation": "Tôi thích nấu đồ ăn Ý.", "highlight": "enjoy cooking", "is_correct": True},
          {"sentence": "She finished reading the book.", "translation": "Cô ấy đã đọc xong cuốn sách.", "highlight": "finished reading", "is_correct": True},
          {"sentence": "Do you mind opening the window?", "translation": "Bạn có phiền mở cửa sổ không?", "highlight": "mind opening", "is_correct": True},
          {"sentence": "He stopped to smoke.", "translation": "Anh ấy dừng lại (để hút thuốc = mục đích). ⚠️ nghĩa khác!", "highlight": "stopped to smoke", "is_correct": True},
          {"sentence": "He stopped smoking.", "translation": "Anh ấy bỏ hút thuốc. ✓", "highlight": "stopped smoking", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["enjoy", "finish", "stop", "mind", "avoid", "love", "hate", "like", "prefer"],
    "common_mistakes": [
      {"wrong": "I enjoy to play tennis.", "correct": "I enjoy playing tennis.", "explanation": "'Enjoy' luôn theo sau bởi V-ing."},
      {"wrong": "She finished to eat.", "correct": "She finished eating.", "explanation": "'Finish' theo sau bởi V-ing, không phải to-infinitive."},
      {"wrong": "Do you mind to wait?", "correct": "Do you mind waiting?", "explanation": "'Mind' theo sau bởi V-ing."}
    ],
    "notes": [
      {"type": "warning", "text": "'Stop + V-ing' = bỏ làm gì. 'Stop + to V' = dừng lại để làm gì khác. Nghĩa khác nhau hoàn toàn!"},
      {"type": "tip", "text": "Sau preposition luôn dùng V-ing: 'I'm interested in learning English.' / 'Thank you for helping me.'"}
    ]
  },
  {
    "level": "A1",
    "title": "Verbs + to Infinitive",
    "slug": "verbs-to-infinitive",
    "order": 22,
    "chapter": "-ing and the infinitive",
    "description": "Một số động từ luôn theo sau bởi to + V-base: want, need, decide, plan, hope, would like...",
    "analogy": "Những động từ này 'có mục tiêu' — chúng hướng tới một hành động trong tương lai.",
    "real_world_use": "Nói về kế hoạch, ước muốn, quyết định và mục tiêu.",
    "memory_hook": "want/need/hope/decide/plan + to V (luôn có 'to').",
    "icon": "🎯",
    "rules": [
      {
        "title": "Động từ theo sau bởi to-Infinitive",
        "formula": "V1 + to + V2-base",
        "explanation": "Một số động từ luôn theo sau bởi to-infinitive (to + V-base).",
        "memory_hook": "want/need/hope/decide/plan/learn/try/forget/remember + to V",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Nhóm", "Động từ", "Ví dụ"],
          "rows": [
            ["Mong muốn/kế hoạch", "want, need, hope, wish, plan, decide", "I want to learn French."],
            ["Cố gắng", "try, manage, fail", "She tried to call him."],
            ["Nhớ/quên", "remember, forget, learn", "Don't forget to lock the door."],
            ["Đồng ý/từ chối", "agree, refuse, offer", "He agreed to help us."]
          ]
        },
        "examples": [
          {"sentence": "I want to visit Japan next year.", "translation": "Tôi muốn thăm Nhật Bản năm tới.", "highlight": "want to visit", "is_correct": True},
          {"sentence": "She decided to study abroad.", "translation": "Cô ấy quyết định đi du học.", "highlight": "decided to study", "is_correct": True},
          {"sentence": "Don't forget to call your mother.", "translation": "Đừng quên gọi điện cho mẹ.", "highlight": "forget to call", "is_correct": True},
          {"sentence": "He refused to answer the question.", "translation": "Anh ấy từ chối trả lời câu hỏi.", "highlight": "refused to answer", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["want to", "need to", "hope to", "decide to", "plan to", "try to", "learn to"],
    "common_mistakes": [
      {"wrong": "I want going home.", "correct": "I want to go home.", "explanation": "'Want' theo sau bởi to-infinitive, không phải V-ing."},
      {"wrong": "She needs studying more.", "correct": "She needs to study more.", "explanation": "'Need' (với ý nghĩa bắt buộc) theo sau bởi to-infinitive."},
      {"wrong": "He decided going abroad.", "correct": "He decided to go abroad.", "explanation": "'Decide' luôn theo sau bởi to-infinitive."}
    ],
    "notes": [
      {"type": "tip", "text": "'Remember/forget + to V' = nhớ/quên làm gì (trong tương lai). 'Remember/forget + V-ing' = nhớ/quên đã làm gì (trong quá khứ). Nghĩa khác nhau!"},
      {"type": "info", "text": "Một số động từ có thể theo sau bởi cả V-ing và to V: like, love, hate, begin, start, continue — nghĩa gần giống nhau."}
    ]
  },
  {
    "level": "A1",
    "title": "A / An và Số Nhiều",
    "slug": "a-an-plurals",
    "order": 23,
    "chapter": "Articles, nouns, pronouns, and determiners.",
    "description": "Cách dùng mạo từ không xác định a/an và cách tạo số nhiều cho danh từ.",
    "analogy": "A/an = 'một cái...' (bất kỳ cái nào). Số nhiều = nhiều hơn một.",
    "real_world_use": "Mô tả đồ vật, con người và nơi chốn trong cuộc sống hàng ngày.",
    "memory_hook": "a + phụ âm (a book). an + nguyên âm (an apple, an hour).",
    "icon": "📦",
    "rules": [
      {
        "title": "A vs An",
        "formula": "a + consonant sound | an + vowel sound",
        "explanation": "Dùng 'a' trước âm phụ âm và 'an' trước âm nguyên âm (a, e, i, o, u). Quyết định dựa vào ÂM THANH, không phải chữ.",
        "memory_hook": "an HOUR (h không phát âm → âm nguyên âm /aʊ/). a UNIVERSITY (u phát âm /j/ → âm phụ âm).",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Dùng 'a'", "Dùng 'an'"],
          "rows": [
            ["a book, a car, a dog", "an apple, an egg, an ice cream"],
            ["a university (/j/ sound)", "an hour (/aʊ/ sound)"],
            ["a European (/j/ sound)", "an honest man (/ɒ/ sound)"]
          ]
        },
        "examples": [
          {"sentence": "She is a doctor.", "translation": "Cô ấy là bác sĩ.", "highlight": "a doctor", "is_correct": True},
          {"sentence": "I ate an orange for breakfast.", "translation": "Tôi ăn một quả cam vào bữa sáng.", "highlight": "an orange", "is_correct": True},
          {"sentence": "He is an honest person.", "translation": "Anh ấy là người trung thực.", "highlight": "an honest", "is_correct": True},
          {"sentence": "It was a hour ago.", "translation": "❌ Sai — hour bắt đầu bằng âm nguyên âm.", "highlight": "a hour", "is_correct": False}
        ]
      },
      {
        "title": "Số nhiều của danh từ (Plurals)",
        "formula": "noun + s | noun(ch/sh/x/s/o) + es | noun-y → nouns-ies | irregular",
        "explanation": "Quy tắc thêm -s/-es cho số nhiều. Một số danh từ bất quy tắc: man→men, woman→women, child→children, tooth→teeth, foot→feet.",
        "memory_hook": "Giống quy tắc -s/-es của động từ ngôi 3. Bất quy tắc: man/men, child/children.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Trường hợp", "Quy tắc", "Ví dụ"],
          "rows": [
            ["Hầu hết", "+ s", "book→books, cat→cats"],
            ["ch/sh/x/s/o", "+ es", "bus→buses, box→boxes, watch→watches"],
            ["Phụ âm + y", "y→ies", "baby→babies, city→cities"],
            ["Nguyên âm + y", "+ s", "day→days, boy→boys"],
            ["Bất quy tắc", "đổi hoàn toàn", "man→men, child→children, tooth→teeth"]
          ]
        },
        "examples": [
          {"sentence": "There are three children in the family.", "translation": "Gia đình có ba đứa trẻ.", "highlight": "children", "is_correct": True},
          {"sentence": "Two women are waiting outside.", "translation": "Có hai người phụ nữ đang đợi bên ngoài.", "highlight": "women", "is_correct": True},
          {"sentence": "I brush my teeths every morning.", "translation": "❌ Sai — teeth là số nhiều bất quy tắc.", "highlight": "teeths", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["a/an", "one", "some", "two/three/...", "many", "a few"],
    "common_mistakes": [
      {"wrong": "She is a engineer.", "correct": "She is an engineer.", "explanation": "'Engineer' bắt đầu bằng nguyên âm /e/."},
      {"wrong": "I have two childs.", "correct": "I have two children.", "explanation": "'Child' có số nhiều bất quy tắc: children."},
      {"wrong": "He is a honest man.", "correct": "He is an honest man.", "explanation": "'Honest' bắt đầu bằng âm nguyên âm /ɒ/ (chữ h câm)."}
    ],
    "notes": [
      {"type": "info", "text": "A/an chỉ dùng với danh từ đếm được số ít. Không dùng với danh từ không đếm được: 'a water' ❌ → 'a glass of water' ✓."},
      {"type": "tip", "text": "Các danh từ không đổi ở số nhiều: fish, sheep, deer. 'Two fish' (không phải fishes trong hầu hết trường hợp)."}
    ]
  },
  {
    "level": "A1",
    "title": "Mạo Từ: A/An vs The",
    "slug": "articles-a-an-the",
    "order": 24,
    "chapter": "Articles, nouns, pronouns, and determiners.",
    "description": "Khi dùng mạo từ xác định 'the' và mạo từ không xác định 'a/an'. Khi không dùng mạo từ.",
    "analogy": "A/an = 'tôi không chỉ cái cụ thể nào'. The = 'cái đó, bạn biết cái nào rồi đấy'.",
    "real_world_use": "Sử dụng chính xác mạo từ là một trong những thách thức lớn nhất với người học tiếng Anh.",
    "memory_hook": "Lần đầu nhắc = a/an. Nhắc lại hoặc cả hai biết = the.",
    "icon": "🏷️",
    "rules": [
      {
        "title": "A/An — Mạo từ không xác định",
        "formula": "a/an = một (number) | type/category | first mention",
        "explanation": "Dùng a/an khi: (1) Đề cập lần đầu. (2) Nói về loại/nghề nghiệp. (3) Không chỉ cụ thể cái nào. Chỉ dùng với danh từ đếm được số ít.",
        "memory_hook": "A/an = bất kỳ một cái nào trong loại đó.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Cách dùng", "Ví dụ"],
          "rows": [
            ["Nhắc đến lần đầu", "I saw a dog in the park."],
            ["Nghề nghiệp / danh mục", "She is a teacher. He is an artist."],
            ["Tỉ lệ / tần suất", "60 kilometres an hour. Twice a week."],
            ["Không xác định cụ thể", "Can I have a coffee, please?"]
          ]
        },
        "examples": [
          {"sentence": "I bought a new phone yesterday.", "translation": "Hôm qua tôi mua một chiếc điện thoại mới.", "highlight": "a new phone", "is_correct": True},
          {"sentence": "He is a police officer.", "translation": "Anh ấy là cảnh sát.", "highlight": "a police officer", "is_correct": True},
          {"sentence": "Take an aspirin for your headache.", "translation": "Hãy uống một viên aspirin cho đau đầu.", "highlight": "an aspirin", "is_correct": True}
        ]
      },
      {
        "title": "The — Mạo từ xác định",
        "formula": "the = cả hai đã biết | nhắc lại | duy nhất | địa danh cụ thể",
        "explanation": "Dùng the khi: (1) Cả người nói và người nghe đều biết đang nói về cái nào. (2) Nhắc lại danh từ đã đề cập. (3) Chỉ có một cái (the sun, the moon). (4) Số thứ tự (the first, the last).",
        "memory_hook": "The = 'cái đó', không phải 'một cái'. Người nghe phải biết bạn đang nói cái nào.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Cách dùng", "Ví dụ"],
          "rows": [
            ["Nhắc lại", "I saw a dog. The dog was friendly."],
            ["Cả hai biết", "'Close the door please' (cái cửa trong phòng)"],
            ["Chỉ có một", "The sun, the moon, the Earth, the sky"],
            ["Số thứ tự", "the first time, the second floor, the last bus"],
            ["Địa danh: sông/biển", "the Thames, the Pacific, the Alps"]
          ]
        },
        "examples": [
          {"sentence": "The sun rises in the east.", "translation": "Mặt trời mọc ở phía đông.", "highlight": "The sun / the east", "is_correct": True},
          {"sentence": "I met a girl. The girl was very kind.", "translation": "Tôi gặp một cô gái. Cô gái đó rất tốt bụng.", "highlight": "a girl / The girl", "is_correct": True},
          {"sentence": "Can you pass the salt?", "translation": "Bạn có thể đưa muối giúp tôi không? (cả 2 biết cái lọ muối nào)", "highlight": "the salt", "is_correct": True}
        ]
      },
      {
        "title": "Không dùng mạo từ (Zero Article)",
        "formula": "∅ + plural nouns (chung chung) | ∅ + uncountable nouns | ∅ + proper nouns",
        "explanation": "Không dùng mạo từ khi: (1) Nói chung về danh từ số nhiều hoặc không đếm được. (2) Tên riêng (người, thành phố, nước). (3) Các cụm thông dụng: go to school/work/bed.",
        "memory_hook": "Dogs are friendly. (chó nói chung, không cụ thể) vs The dogs are here. (những con chó cụ thể)",
        "is_exception": False,
        "order": 3,
        "grammar_table": {
          "headers": ["Không dùng the", "Ví dụ"],
          "rows": [
            ["Nói chung (plural)", "Dogs are friendly animals."],
            ["Không đếm được (chung)", "I love music. Sugar is sweet."],
            ["Tên người/thành phố/nước", "Mary lives in Vietnam."],
            ["Cụm quen thuộc", "go to school/work/bed/church"]
          ]
        },
        "examples": [
          {"sentence": "Children need love and attention.", "translation": "Trẻ em cần tình yêu và sự chú ý. (chung chung)", "highlight": "Children", "is_correct": True},
          {"sentence": "She goes to school by bus.", "translation": "Cô ấy đi học bằng xe buýt.", "highlight": "to school", "is_correct": True},
          {"sentence": "The life is beautiful.", "translation": "❌ Sai — life ở nghĩa chung không dùng the.", "highlight": "The life", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["a/an (first mention)", "the (second mention)", "specific", "unique (the sun)", "in general (no article)"],
    "common_mistakes": [
      {"wrong": "The life is short.", "correct": "Life is short.", "explanation": "Khi nói chung về life, không dùng 'the'."},
      {"wrong": "She plays the football.", "correct": "She plays football.", "explanation": "Tên của các môn thể thao không dùng 'the'."},
      {"wrong": "I go to the school every day.", "correct": "I go to school every day.", "explanation": "'Go to school' là cụm thành ngữ, không dùng 'the'."},
      {"wrong": "He is best student in class.", "correct": "He is the best student in class.", "explanation": "Trước tính từ so sánh nhất, phải dùng 'the'."}
    ],
    "notes": [
      {"type": "tip", "text": "Tên nước thường không có 'the': Vietnam, France, Japan. Nhưng tên nước dạng số nhiều hoặc liên bang: the USA, the UK, the Netherlands, the Philippines."},
      {"type": "warning", "text": "The + nhạc cụ: 'She plays the piano / the guitar.' (khác với thể thao không dùng the)."}
    ]
  },
  {
    "level": "A1",
    "title": "This / That / These / Those",
    "slug": "demonstratives",
    "order": 25,
    "chapter": "Articles, nouns, pronouns, and determiners.",
    "description": "Dùng this/that/these/those để chỉ người, vật theo khoảng cách và số lượng.",
    "analogy": "This/these = gần (tay với tới được). That/those = xa (phải chỉ ngón tay).",
    "real_world_use": "Chỉ đồ vật trong cửa hàng, giới thiệu người, nói về điều vừa xảy ra.",
    "memory_hook": "This = gần + số ít. These = gần + số nhiều. That = xa + số ít. Those = xa + số nhiều.",
    "icon": "👆",
    "rules": [
      {
        "title": "This / That / These / Those",
        "formula": "this/these (near) | that/those (far)",
        "explanation": "This (số ít, gần), These (số nhiều, gần), That (số ít, xa), Those (số nhiều, xa). Dùng trước noun (adjective) hoặc một mình (pronoun).",
        "memory_hook": "gần: this/these. xa: that/those. số ít: this/that. số nhiều: these/those.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["", "Gần (near)", "Xa (far)"],
          "rows": [
            ["Số ít (singular)", "this book", "that building"],
            ["Số nhiều (plural)", "these shoes", "those people"]
          ]
        },
        "examples": [
          {"sentence": "This phone is mine.", "translation": "Chiếc điện thoại này là của tôi.", "highlight": "This phone", "is_correct": True},
          {"sentence": "Those mountains are beautiful.", "translation": "Những ngọn núi kia thật đẹp.", "highlight": "Those mountains", "is_correct": True},
          {"sentence": "Is this your bag?", "translation": "Đây có phải túi của bạn không?", "highlight": "this", "is_correct": True},
          {"sentence": "I don't like these shoes.", "translation": "Tôi không thích những đôi giày này.", "highlight": "these shoes", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["here", "there", "near", "far", "over there"],
    "common_mistakes": [
      {"wrong": "These is my brother.", "correct": "This is my brother.", "explanation": "Khi giới thiệu một người, dùng 'this', không phải 'these'."},
      {"wrong": "I like this shoes.", "correct": "I like these shoes.", "explanation": "Shoes là số nhiều → dùng 'these', không phải 'this'."},
      {"wrong": "That are my friends.", "correct": "Those are my friends.", "explanation": "Số nhiều + xa → 'Those'."}
    ],
    "notes": [
      {"type": "tip", "text": "Khi giới thiệu qua điện thoại hoặc trực tiếp: 'This is my colleague, Tom.' (không dùng 'He is my colleague')"}
    ]
  },
  {
    "level": "A1",
    "title": "Đại từ & Tính từ sở hữu",
    "slug": "pronouns-possessives",
    "order": 26,
    "chapter": "Articles, nouns, pronouns, and determiners.",
    "description": "Đại từ nhân xưng (I/me), tính từ sở hữu (my), đại từ sở hữu (mine) và đại từ phản thân (myself).",
    "analogy": "Từng loại có vai trò riêng trong câu như các cầu thủ trong một đội.",
    "real_world_use": "Nói về quyền sở hữu, tránh lặp lại danh từ, và nhấn mạnh.",
    "memory_hook": "my bag (adj), mine (pronoun — dùng một mình). 'It's my bag.' vs 'The bag is mine.'",
    "icon": "👤",
    "rules": [
      {
        "title": "Đại từ nhân xưng chủ ngữ và tân ngữ",
        "formula": "Subject: I/you/he/she/it/we/they | Object: me/you/him/her/it/us/them",
        "explanation": "Chủ ngữ đứng trước động từ. Tân ngữ đứng sau động từ hoặc giới từ.",
        "memory_hook": "I hit him. (I = subject, him = object). He loves her. She misses him.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Chủ ngữ", "Tân ngữ", "Tính từ sở hữu", "Đại từ sở hữu", "Phản thân"],
          "rows": [
            ["I", "me", "my", "mine", "myself"],
            ["you", "you", "your", "yours", "yourself"],
            ["he", "him", "his", "his", "himself"],
            ["she", "her", "her", "hers", "herself"],
            ["it", "it", "its", "its", "-"],
            ["we", "us", "our", "ours", "ourselves"],
            ["they", "them", "their", "theirs", "themselves"]
          ]
        },
        "examples": [
          {"sentence": "She gave him a present.", "translation": "Cô ấy tặng anh ấy một món quà.", "highlight": "She / him", "is_correct": True},
          {"sentence": "Is this your pen? No, it's mine.", "translation": "Đây có phải bút của bạn không? Không, đó là của tôi.", "highlight": "your / mine", "is_correct": True},
          {"sentence": "The cat licked its paw.", "translation": "Con mèo liếm bàn chân của nó.", "highlight": "its", "is_correct": True},
          {"sentence": "Me like pizza.", "translation": "❌ Sai — chủ ngữ phải dùng 'I'.", "highlight": "Me", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["my/mine", "your/yours", "his", "her/hers", "our/ours", "their/theirs"],
    "common_mistakes": [
      {"wrong": "Me and my friend went shopping.", "correct": "My friend and I went shopping.", "explanation": "Chủ ngữ dùng 'I', không phải 'me'. Thêm vào, đặt người khác trước mình."},
      {"wrong": "The dog hurted it's paw.", "correct": "The dog hurt its paw.", "explanation": "'its' (sở hữu) không có dấu phẩy. 'it's' = it is."},
      {"wrong": "This bag is her.", "correct": "This bag is hers.", "explanation": "Đại từ sở hữu đứng một mình = hers (not her)."}
    ],
    "notes": [
      {"type": "warning", "text": "its vs it's: 'its' = sở hữu (The cat lost its tail). 'it's' = it is (It's raining). Đây là lỗi phổ biến ngay cả với người bản ngữ!"},
      {"type": "tip", "text": "Đại từ phản thân nhấn mạnh: 'I did it myself!' (chính tôi làm, không nhờ ai). Hoặc dùng với 'by': 'She lives by herself.' (sống một mình)."}
    ]
  },
  {
    "level": "A1",
    "title": "Danh từ đếm được, không đếm được & Some/Any",
    "slug": "countable-uncountable",
    "order": 27,
    "chapter": "Articles, nouns, pronouns, and determiners.",
    "description": "Phân biệt danh từ đếm được và không đếm được. Cách dùng some/any.",
    "analogy": "Đếm được = riêng lẻ như viên đá quý. Không đếm được = như nước, không thể đếm từng giọt.",
    "real_world_use": "Đặt hàng, nấu ăn, mua sắm — mọi tình huống liên quan đến số lượng.",
    "memory_hook": "Some = có (khẳng định). Any = không có / có không? (phủ định/câu hỏi).",
    "icon": "⚖️",
    "rules": [
      {
        "title": "Danh từ đếm được & không đếm được",
        "formula": "Countable: a book / two books | Uncountable: water / rice / money / information",
        "explanation": "Danh từ đếm được có số ít và số nhiều. Danh từ không đếm được không có số nhiều và không dùng a/an. Để đo lường, dùng 'a piece of / a glass of / a cup of...'",
        "memory_hook": "Bạn có thể đếm: one apple, two apples ✓. Bạn không thể đếm: one water ❌ → a glass of water ✓.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Đếm được (Countable)", "Không đếm được (Uncountable)"],
          "rows": [
            ["a book / books", "water, milk, juice"],
            ["an apple / apples", "rice, bread, sugar, salt"],
            ["a chair / chairs", "money, news, information"],
            ["a job / jobs", "music, advice, homework"],
            ["→ dùng a/an + mạo từ", "→ không dùng a/an; dùng some/any"]
          ]
        },
        "examples": [
          {"sentence": "I need some information about the course.", "translation": "Tôi cần thông tin về khóa học.", "highlight": "some information", "is_correct": True},
          {"sentence": "Can I have a piece of advice?", "translation": "Tôi có thể xin một lời khuyên không?", "highlight": "a piece of advice", "is_correct": True},
          {"sentence": "I need an information.", "translation": "❌ Sai — information không đếm được.", "highlight": "an information", "is_correct": False}
        ]
      },
      {
        "title": "Some / Any",
        "formula": "some (affirmative) | any (negative/question) | some (question = offer/request)",
        "explanation": "Some dùng trong câu khẳng định. Any dùng trong câu phủ định và câu hỏi. Nhưng some cũng dùng trong câu hỏi khi đề nghị hoặc yêu cầu.",
        "memory_hook": "There's some milk. (có) / There isn't any milk. (không) / Is there any milk? (hỏi)",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Tình huống", "Some", "Any"],
          "rows": [
            ["Khẳng định", "I have some money.", "—"],
            ["Phủ định", "—", "I don't have any money."],
            ["Câu hỏi", "Would you like some tea? (offer)", "Do you have any money?"],
            ["Danh từ không đếm được", "some water, some rice", "any water, any rice"],
            ["Danh từ đếm được số nhiều", "some apples, some books", "any apples, any books"]
          ]
        },
        "examples": [
          {"sentence": "There is some milk in the fridge.", "translation": "Trong tủ lạnh có một ít sữa.", "highlight": "some milk", "is_correct": True},
          {"sentence": "Is there any coffee left?", "translation": "Còn cà phê không?", "highlight": "any coffee", "is_correct": True},
          {"sentence": "Would you like some cake?", "translation": "Bạn có muốn ít bánh không?", "highlight": "some cake", "is_correct": True},
          {"sentence": "I don't have some money.", "translation": "❌ Sai — phủ định dùng 'any'.", "highlight": "some", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["some", "any", "no", "a lot of", "much", "many", "a little", "a few"],
    "common_mistakes": [
      {"wrong": "I need an advice.", "correct": "I need some advice.", "explanation": "'Advice' là danh từ không đếm được, không dùng a/an."},
      {"wrong": "Can I have some informations?", "correct": "Can I have some information?", "explanation": "'Information' không có số nhiều."},
      {"wrong": "I don't have some time.", "correct": "I don't have any time.", "explanation": "Câu phủ định dùng 'any', không phải 'some'."}
    ],
    "notes": [
      {"type": "tip", "text": "Danh từ không đếm được thông dụng: advice, news, information, homework, furniture, luggage, money, traffic, weather, music, bread, rice, water, milk, cheese."},
      {"type": "info", "text": "'News' luôn là số ít: 'The news is on at 7.' (không phải 'The news are')."}
    ]
  }
]
