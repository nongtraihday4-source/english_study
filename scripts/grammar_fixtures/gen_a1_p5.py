"""Group 5: 9 missing tense topics (orders 4,5,9,10,13,14,15,16,17)"""

TOPICS = [
  # ─── PRESENT TENSES ─────────────────────────────────────────
  {
    "level": "A1",
    "title": "Thì Hiện Tại Hoàn Thành (Present Perfect)",
    "slug": "present-perfect-tense",
    "order": 4,
    "chapter": "Present tenses",
    "description": "Chiếc cầu nối giữa quá khứ và hiện tại — dùng khi hành động quá khứ vẫn còn liên quan đến lúc này.",
    "analogy": "Ảnh chụp vẫn còn trong ví — chụp hồi nào không quan trọng, quan trọng là bạn VẪN còn giữ nó.",
    "real_world_use": "Thông báo tin tức, kể trải nghiệm, nói về hành động kéo dài tới hiện tại.",
    "memory_hook": "have/has + V3 (past participle). Không cần biết KHI NÀO, chỉ cần biết là ĐÃ (có kết quả).",
    "icon": "🌉",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + have/has + V3 (past participle)",
        "explanation": "I/You/We/They dùng 'have'. He/She/It dùng 'has'. V3 là dạng quá khứ phân từ (cột 3 trong bảng động từ bất quy tắc). Phủ định: haven't/hasn't + V3. Câu hỏi: Have/Has + S + V3?",
        "memory_hook": "I/You/We/They + HAVE. He/She/It + HAS. Sau đó luôn là V3.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Chủ ngữ", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["I / You / We / They", "have + V3", "I have passed the test."],
            ["He / She / It", "has + V3", "She has arrived."],
            ["Phủ định", "haven't / hasn't + V3", "He hasn't called yet."],
            ["Câu hỏi", "Have/Has + S + V3?", "Have you washed the dishes?"],
            ["Rút gọn", "I've, she's, they've...", "I've visited Paris twice."]
          ]
        },
        "examples": [
          {"sentence": "I've passed the test!", "translation": "Tôi vừa qua bài kiểm tra rồi!", "highlight": "I've passed", "is_correct": True},
          {"sentence": "She hasn't arrived yet.", "translation": "Cô ấy vẫn chưa đến.", "highlight": "hasn't arrived", "is_correct": True},
          {"sentence": "Have you ever been to Japan?", "translation": "Bạn đã từng đến Nhật Bản chưa?", "highlight": "Have you ever been", "is_correct": True},
          {"sentence": "He has went to the store.", "translation": "❌ Sai — 'gone' không phải 'went' sau has.", "highlight": "has went", "is_correct": False}
        ]
      },
      {
        "title": "USAGE — 3 Cách dùng cốt lõi",
        "formula": "Trải nghiệm (ever/never) | Tin tức / vừa xảy ra (just/already/yet) | Kéo dài đến nay (for/since)",
        "explanation": "(1) TRẢI NGHIỆM: những điều bạn đã từng / chưa từng làm trong cuộc đời. (2) TIN TỨC / VỪA XẢY RA: hành động vừa hoàn thành, có kết quả ngay lúc này. (3) KÉO DÀI: hành động bắt đầu quá khứ và vẫn tiếp tục đến hiện tại.",
        "memory_hook": "ever/never = trải nghiệm. just/already/yet = tin tức. for/since = kéo dài.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Cách dùng", "Dấu hiệu", "Ví dụ"],
          "rows": [
            ["① Trải nghiệm", "ever, never, before, ...times", "I've never read this book. / She's run a marathon twice."],
            ["② Tin tức / vừa xảy ra", "just, already, yet", "He's just got married. / I haven't called yet."],
            ["③ Kéo dài đến nay", "for (khoảng thời gian), since (mốc thời gian)", "They've been married for 25 years. / I've lived here since 2010."]
          ]
        },
        "examples": [
          {"sentence": "I've never eaten sushi before.", "translation": "Tôi chưa bao giờ ăn sushi. (trải nghiệm)", "highlight": "I've never eaten", "is_correct": True},
          {"sentence": "She's just finished her homework.", "translation": "Cô ấy vừa mới làm xong bài tập. (vừa xảy ra)", "highlight": "has just finished", "is_correct": True},
          {"sentence": "He's lived in Hanoi since 2015.", "translation": "Anh ấy sống ở Hà Nội từ năm 2015 (đến giờ).", "highlight": "has lived ... since", "is_correct": True}
        ]
      },
      {
        "title": "Phân biệt: Present Perfect vs Past Simple",
        "formula": "PP: không có thời gian cụ thể / kết quả vẫn còn | Past Simple: có thời gian cụ thể đã qua",
        "explanation": "Present Perfect KHÔNG dùng với thời gian cụ thể đã qua (yesterday, last year, in 2020, ago). Khi hỏi chi tiết về sự kiện, chuyển sang Past Simple.",
        "memory_hook": "I've seen that film (PP — không biết/không cần biết khi nào). I saw it last Monday (PS — có thời gian cụ thể).",
        "is_exception": False,
        "order": 3,
        "grammar_table": {
          "headers": ["Present Perfect", "Past Simple"],
          "rows": [
            ["I've been to Italy.", "I went to Italy in 2019."],
            ["She's lost her keys.", "She lost her keys yesterday."],
            ["Have you ever tried pho?", "Did you try pho last night?"],
            ["Không có: yesterday/ago/in+year", "Có: yesterday, last week, in 2020, ago"]
          ]
        },
        "examples": [
          {"sentence": "I've been to Paris. — Where did you stay? (PP mở đầu, PS hỏi chi tiết)", "translation": "Tôi đã đến Paris. — Bạn ở đâu?", "highlight": "I've been / did you stay", "is_correct": True},
          {"sentence": "I have seen her yesterday.", "translation": "❌ Sai — 'yesterday' đã qua → dùng Past Simple.", "highlight": "have seen ... yesterday", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["ever", "never", "just", "already", "yet", "recently", "lately", "before", "for", "since", "so far", "up to now", "once", "twice", "...times"],
    "common_mistakes": [
      {"wrong": "I have seen her yesterday.", "correct": "I saw her yesterday.", "explanation": "'Yesterday' là thời gian quá khứ cụ thể → Past Simple."},
      {"wrong": "She has went to the store.", "correct": "She has gone to the store.", "explanation": "'Go' có V3 là 'gone', không phải 'went'."},
      {"wrong": "I didn't eat sushi never.", "correct": "I have never eaten sushi.", "explanation": "'Never' đi với Present Perfect, không dùng double negative."},
      {"wrong": "Since how long have you lived here?", "correct": "How long have you lived here?", "explanation": "'How long' không kết hợp với 'since'."}
    ],
    "notes": [
      {"type": "tip", "text": "been to vs gone to: 'I've been to Ireland' (đã đến và về rồi). 'He's gone to Ireland' (đã đi và VẪN ĐANG ở đó, chưa về)."},
      {"type": "warning", "text": "FOR + khoảng thời gian (for 2 years, for a week). SINCE + mốc thời gian (since 2010, since Monday, since I was born). Không bao giờ dùng 'since 10 years ago' — đổi thành 'for 10 years'."},
      {"type": "info", "text": "Người bản xứ thường dùng PP để mở đầu câu chuyện, rồi dùng Past Simple để kể chi tiết: 'I've been to a great restaurant!' → 'Oh really? Where did you go? What did you eat?'"}
    ]
  },
  {
    "level": "A1",
    "title": "Thì Hiện Tại Hoàn Thành Tiếp Diễn",
    "slug": "present-perfect-continuous",
    "order": 5,
    "chapter": "Present tenses",
    "description": "Nhấn mạnh QUÁ TRÌNH và TÍNH LIÊN TỤC của hành động từ quá khứ đến hiện tại.",
    "analogy": "Bạn về nhà thấy bạn cùng phòng đang có mồ hôi — bạn biết họ vừa tập thể dục (dấu vết của quá trình).",
    "real_world_use": "Giải thích tình trạng hiện tại bằng hành động vừa kéo dài (mệt mỏi, ướt, bẩn...); nói bao lâu rồi.",
    "memory_hook": "have/has + been + V-ing = đã và đang làm liên tục.",
    "icon": "⏳",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + have/has + been + V-ing",
        "explanation": "Kết hợp Present Perfect (have/has been) và Continuous (V-ing). Nhấn mạnh TẦN SUẤT LIÊN TỤC và THỜI GIAN KÉO DÀI.",
        "memory_hook": "have/has BEEN + V-ing. ('been' không bao giờ thiếu!)",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + have/has + been + V-ing", "I have been waiting for hours."],
            ["Phủ định", "S + haven't/hasn't + been + V-ing", "I haven't been feeling well."],
            ["Câu hỏi", "Have/Has + S + been + V-ing?", "Have you been crying?"],
            ["Rút gọn", "I've been, she's been...", "She's been working all day."]
          ]
        },
        "examples": [
          {"sentence": "I have been waiting for hours!", "translation": "Tôi đã đứng đợi suốt mấy tiếng đồng hồ rồi!", "highlight": "have been waiting", "is_correct": True},
          {"sentence": "She's been calling you for days.", "translation": "Cô ấy đã gọi cho bạn liên tục suốt mấy ngày nay.", "highlight": "has been calling", "is_correct": True},
          {"sentence": "Have you been crying?", "translation": "Bạn vừa mới khóc đấy à?", "highlight": "Have you been crying", "is_correct": True}
        ]
      },
      {
        "title": "USAGE — 2 Cách dùng + Phân biệt với Present Perfect",
        "formula": "Liên tục từ QK đến HT | Dấu vết của hành động vừa xảy ra",
        "explanation": "(1) Hành động kéo dài liên tục từ quá khứ đến hiện tại (vẫn đang tiếp tục hoặc vừa dừng). (2) Hành động vừa kết thúc nhưng để lại dấu vết thể chất rõ ràng. PHÂN BIỆT với PP Đơn: PP Continuous = quá trình/thời gian. PP Đơn = kết quả/số lượng.",
        "memory_hook": "How LONG? → PP Continuous. How MANY/MUCH? → PP Simple.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["", "PP Continuous (quá trình)", "PP Simple (kết quả)"],
          "rows": [
            ["Hỏi về", "Thời gian / bao lâu", "Số lượng / kết quả đạt được"],
            ["Ví dụ", "I've been writing emails for hours. (mệt mỏi, vẫn chưa xong)", "I've written 20 emails. (đã viết được 20 cái)"],
            ["Dấu vết bên ngoài", "You've been crying. (mắt đỏ)", "Who has eaten my cookies? (đĩa trống)"],
            ["Signal words", "for, since, how long, all day, lately", "just, already, yet, ...times, ever/never"]
          ]
        },
        "examples": [
          {"sentence": "Sorry I'm so dirty — I've been painting.", "translation": "Xin lỗi trông tôi hơi bẩn — tôi vừa mới sơn nhà xong.", "highlight": "I've been painting", "is_correct": True},
          {"sentence": "I've been studying since you left.", "translation": "Tôi đã học liên tục không nghỉ từ lúc bạn rời đi.", "highlight": "have been studying / since", "is_correct": True},
          {"sentence": "I have been knowing him for 10 years.", "translation": "❌ Sai — 'know' là stative verb, không dùng -ing.", "highlight": "have been knowing", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["for", "since", "how long", "all day", "the whole day", "lately", "recently", "all morning", "for days"],
    "common_mistakes": [
      {"wrong": "I have been knowing him for 10 years.", "correct": "I have known him for 10 years.", "explanation": "'Know' là stative verb — không bao giờ dùng -ing."},
      {"wrong": "She has been written 3 emails.", "correct": "She has written 3 emails.", "explanation": "Số lượng (3 emails) → dùng PP Simple, không phải Continuous."},
      {"wrong": "Have you been cried?", "correct": "Have you been crying?", "explanation": "PP Continuous dùng V-ing, không phải V3."}
    ],
    "notes": [
      {"type": "tip", "text": "Khi hành động còn đang tiếp tục: 'I've been living here for 5 years.' (và tôi vẫn đang sống đây). Khi hành động vừa dừng: 'I've been running.' (vừa chạy xong, đang thở hổn hển)."},
      {"type": "warning", "text": "Stative verbs KHÔNG dùng PP Continuous: know, want, need, love, hate, believe, own, have (sở hữu). Dùng PP Simple: 'I've wanted this for years.' ✓"}
    ]
  },

  # ─── PAST TENSES ────────────────────────────────────────────
  {
    "level": "A1",
    "title": "Thì Quá Khứ Hoàn Thành (Past Perfect)",
    "slug": "past-perfect-tense",
    "order": 9,
    "chapter": "Past tenses",
    "description": "'Quá khứ của quá khứ' — dùng khi cần nói đến hành động xảy ra TRƯỚC một thời điểm quá khứ khác.",
    "analogy": "Đang kể chuyện ngày hôm qua, rồi bạn lùi thêm về trước đó nữa — như flashback trong phim.",
    "real_world_use": "Kể chuyện chi tiết, giải thích nguyên nhân quá khứ, viết tiểu thuyết/truyện.",
    "memory_hook": "had + V3 (dùng cho TẤT CẢ ngôi). Hành động XẢY RA TRƯỚC → Past Perfect.",
    "icon": "⏮️",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + had + V3 (all subjects)",
        "explanation": "'Had' dùng cho tất cả ngôi (I, you, he, she, it, we, they). Phủ định: hadn't + V3. Câu hỏi: Had + S + V3? Rút gọn: 'd (I'd, she'd...)",
        "memory_hook": "had = quá khứ của 'have'. Dùng 'd để rút gọn: 'He'd gone.'",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định (tất cả ngôi)", "S + had + V3", "She had left before I arrived."],
            ["Rút gọn", "S + 'd + V3", "He'd gone to a meeting."],
            ["Phủ định", "S + hadn't + V3", "I hadn't eaten all day."],
            ["Câu hỏi", "Had + S + V3?", "Had she ever been to France?"]
          ]
        },
        "examples": [
          {"sentence": "I called him, but he'd gone to a meeting.", "translation": "Tôi gọi anh ấy nhưng anh ấy đã đi họp mất rồi.", "highlight": "had gone", "is_correct": True},
          {"sentence": "When she opened the door, he had already left.", "translation": "Khi cô ấy mở cửa, anh ta đã rời đi từ trước rồi.", "highlight": "had already left", "is_correct": True},
          {"sentence": "I hadn't eaten all day when I got home.", "translation": "Khi tôi về nhà, tôi đã không ăn gì suốt cả ngày.", "highlight": "hadn't eaten", "is_correct": True}
        ]
      },
      {
        "title": "USAGE — Quy tắc vàng + Từ nối thời gian",
        "formula": "Hai QK xảy ra: hành động TRƯỚC → had V3 | hành động SAU → Past Simple",
        "explanation": "Khi kể hai hành động trong quá khứ: hành động xảy ra TRƯỚC dùng Past Perfect (had V3), hành động SAU dùng Past Simple. Từ nối: when, before, after, by the time, already, just, never, until.",
        "memory_hook": "TRƯỚC = had V3. SAU = V-past. 'When I arrived, she had left.' (cô ấy đi TRƯỚC, tôi đến SAU).",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Từ nối", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["when", "Past Simple, Past Perfect (trước đó)", "When I arrived, she had left."],
            ["before", "Past Perfect, before Past Simple", "She had learned English before she moved abroad."],
            ["after", "After Past Perfect, Past Simple", "After he had finished, Peter went to bed."],
            ["by the time", "By the time + Past Simple, Past Perfect", "By the time I came, he had gone."],
            ["already / just / never", "— đi cùng had —", "She had never worked before."]
          ]
        },
        "examples": [
          {"sentence": "When I arrived, I saw someone had stolen my car.", "translation": "Khi tôi về, tôi thấy ai đó đã lấy cắp xe của tôi.", "highlight": "had stolen", "is_correct": True},
          {"sentence": "By the time I came, she had left.", "translation": "Tính đến lúc tôi đến, cô ấy đã rời đi rồi.", "highlight": "had left", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["by the time", "when", "before", "after", "already", "just", "never", "until", "as soon as"],
    "common_mistakes": [
      {"wrong": "When I arrived, she left.", "correct": "When I arrived, she had already left.", "explanation": "Nếu cô ấy rời đi TRƯỚC khi bạn đến, dùng Past Perfect. Không dùng Past Simple cho cả hai."},
      {"wrong": "He 'd love to go. (=quá khứ?)", "correct": "'d + V-base = would. 'd + V3 = had.", "explanation": "'d có thể là would (+ V-base) HOẶC had (+ V3). Xác định dựa vào động từ theo sau."},
      {"wrong": "I had ate before you came.", "correct": "I had eaten before you came.", "explanation": "'Eat' có V3 là 'eaten', không phải 'ate'."}
    ],
    "notes": [
      {"type": "tip", "text": "'d có thể là would hoặc had: 'I'd love to go.' (would + V-base). 'I'd called him.' (had + V3). Nhìn vào từ tiếp theo để phân biệt."},
      {"type": "info", "text": "Khi thứ tự thời gian đã rõ ràng qua từ nối 'before/after', Past Perfect có thể thay bằng Past Simple: 'I ate before you came.' vẫn chấp nhận được nhưng 'I had eaten' rõ nghĩa hơn."}
    ]
  },
  {
    "level": "A1",
    "title": "Thì Quá Khứ Hoàn Thành Tiếp Diễn",
    "slug": "past-perfect-continuous",
    "order": 10,
    "chapter": "Past tenses",
    "description": "Nhấn mạnh THỜI GIAN KÉO DÀI của hành động xảy ra trước một thời điểm quá khứ khác.",
    "analogy": "Thước phim tua chậm của quá khứ — cho thấy quá trình diễn ra trước khi sự kiện xảy ra.",
    "real_world_use": "Giải thích trạng thái quá khứ (cô ấy mệt vì đã làm suốt ngày), kể chuyện chi tiết.",
    "memory_hook": "had + been + V-ing = đã và đang làm liên tục... trước khi điều gì đó xảy ra.",
    "icon": "🎞️",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + had + been + V-ing (all subjects)",
        "explanation": "Kết hợp Past Perfect (had been) và Continuous (V-ing). Dùng cho tất cả ngôi. Nhấn mạnh THỜI GIAN và TÍNH LIÊN TỤC trước một mốc quá khứ.",
        "memory_hook": "had BEEN + V-ing. (= past perfect của 'have been + V-ing')",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + had + been + V-ing", "She had been working all day."],
            ["Phủ định", "S + hadn't + been + V-ing", "I hadn't been sleeping well."],
            ["Câu hỏi", "Had + S + been + V-ing?", "Had he been drinking?"]
          ]
        },
        "examples": [
          {"sentence": "She was exhausted; she had been working all day.", "translation": "Cô ấy kiệt sức vì đã làm việc liên tục cả ngày.", "highlight": "had been working", "is_correct": True},
          {"sentence": "They were wet because they had been walking in the rain.", "translation": "Họ bị ướt vì đã đi bộ dưới mưa.", "highlight": "had been walking", "is_correct": True},
          {"sentence": "We had been driving for less than an hour when the car broke down.", "translation": "Chúng tôi vừa lái xe được chưa đầy một tiếng thì xe bị hỏng.", "highlight": "had been driving / broke down", "is_correct": True}
        ]
      },
      {
        "title": "Phân biệt QK Hoàn thành Đơn và Tiếp diễn",
        "formula": "QK HT Đơn = KẾT QUẢ / SỐ LƯỢNG | QK HT Tiếp diễn = QUÁ TRÌNH / THỜI GIAN",
        "explanation": "Giống như PP Đơn vs PP Continuous nhưng lùi về quá khứ. Stative verbs KHÔNG dùng tiếp diễn — dùng QK Hoàn thành Đơn thay thế.",
        "memory_hook": "TRƯỚC khi QK → bao lâu/quá trình = had been V-ing. TRƯỚC khi QK → kết quả = had V3.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["", "QK Hoàn thành Đơn", "QK Hoàn thành Tiếp diễn"],
          "rows": [
            ["Nhấn mạnh", "Kết quả / số lượng đạt được", "Quá trình / thời gian kéo dài"],
            ["Ví dụ", "By noon, he had drunk 5 cups. (đã uống được 5 cốc)", "By noon, he had been drinking for 3 hours. (ngồi uống suốt 3 tiếng)"],
            ["Stative verbs", "PHẢI dùng đơn: I had known him for 5 years.", "KHÔNG được: I had been knowing him ❌"]
          ]
        },
        "examples": [
          {"sentence": "When we got married, I had known him for 5 years.", "translation": "Khi chúng tôi kết hôn, tôi đã quen anh ấy được 5 năm.", "highlight": "had known", "is_correct": True},
          {"sentence": "When we got married, I had been knowing him.", "translation": "❌ Sai — 'know' là stative verb.", "highlight": "had been knowing", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["for", "since", "how long", "all day", "when", "before", "until"],
    "common_mistakes": [
      {"wrong": "I had been knowing him for 5 years.", "correct": "I had known him for 5 years.", "explanation": "Stative verbs (know, like, own...) không dùng dạng tiếp diễn."},
      {"wrong": "She was tired. She worked all day.", "correct": "She was tired. She had been working all day.", "explanation": "Để giải thích nguyên nhân của trạng thái quá khứ, dùng Past Perfect Continuous."}
    ],
    "notes": [
      {"type": "tip", "text": "Đây là thì ít dùng nhất trong 8 thì nhưng xuất hiện nhiều trong văn viết học thuật và tiểu thuyết. Gặp ở thi IELTS/TOEFL."},
      {"type": "info", "text": "Khi hành động kéo dài và vẫn đang thực hiện tại điểm mốc quá khứ → had been V-ing. Khi hành động đã hoàn thành tại điểm mốc → had V3."}
    ]
  },

  # ─── FUTURE ─────────────────────────────────────────────────
  {
    "level": "A1",
    "title": "Hiện Tại Tiếp Diễn mang nghĩa Tương lai",
    "slug": "present-continuous-future",
    "order": 13,
    "chapter": "Future",
    "description": "Dùng am/is/are + V-ing để nói về các cuộc hẹn và kế hoạch đã được ĐẶT LỊCH chắc chắn.",
    "analogy": "Lịch hẹn đã viết vào sổ — đã chốt thời gian, địa điểm, người liên quan.",
    "real_world_use": "Nói về các buổi gặp gỡ, chuyến đi, sự kiện đã được xác nhận trong tương lai gần.",
    "memory_hook": "HTTD cho TL = sắp xếp đã chốt (Arrangement). Be Going To = ý định (Intention). Will = quyết định lúc nói.",
    "icon": "📆",
    "rules": [
      {
        "title": "FORM & USAGE — Kế hoạch đã được sắp xếp chắc chắn",
        "formula": "S + am/is/are + V-ing + thời gian tương lai",
        "explanation": "Dùng cấu trúc Present Continuous thông thường nhưng thêm thời gian tương lai để tránh hiểu nhầm. Dùng khi: (1) Đã xác định thời gian và địa điểm. (2) Có người khác liên quan (đã hẹn). (3) Đã có sự chuẩn bị rõ ràng (đặt vé, đặt bàn, gửi lịch).",
        "memory_hook": "Phải có thời gian tương lai trong câu: tonight/tomorrow/next week... Không có → hiểu là đang xảy ra.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Tình huống", "Ví dụ"],
          "rows": [
            ["Đã hẹn gặp", "I'm meeting Sally at 7. (đã nhắn tin, chốt giờ)"],
            ["Đã mua vé", "I'm flying to New York tomorrow morning."],
            ["Đã đặt lịch y tế", "I'm seeing the dentist at 6."],
            ["Sự kiện đã lên kế hoạch", "We're getting married next June."],
            ["PHÂN BIỆT: Lịch trình công cộng", "The train leaves at 4. (HTĐ — không phải HTTD)"]
          ]
        },
        "examples": [
          {"sentence": "I'm meeting Tom for dinner tonight.", "translation": "Tối nay tôi sẽ gặp Tom để ăn tối. (đã hẹn)", "highlight": "am meeting ... tonight", "is_correct": True},
          {"sentence": "She's flying to Singapore next Monday.", "translation": "Thứ Hai tuần tới cô ấy sẽ bay đến Singapore. (đã mua vé)", "highlight": "is flying ... next Monday", "is_correct": True},
          {"sentence": "Are you doing anything on Saturday evening?", "translation": "Tối thứ Bảy bạn có bận không?", "highlight": "Are you doing ... on Saturday", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["tonight", "tomorrow", "next week", "this evening", "on Saturday", "in an hour"],
    "common_mistakes": [
      {"wrong": "The train is leaving at 4.", "correct": "The train leaves at 4.", "explanation": "Lịch trình phương tiện công cộng → Hiện Tại Đơn. HTTD cho kế hoạch cá nhân đã chốt."},
      {"wrong": "I am going to have a drink after work. (intention)", "correct": "I'm having a drink with colleagues after work. (arrangement)", "explanation": "Ý định chưa chốt → be going to. Đã hẹn, chốt lịch → Present Continuous."}
    ],
    "notes": [
      {"type": "tip", "text": "Ba cách nói về tương lai: Will = quyết định tức thì / dự đoán. Be going to = ý định có sẵn / dự đoán có bằng chứng. Present Continuous = đã hẹn, đã đặt lịch."},
      {"type": "warning", "text": "Bắt buộc phải có thời gian tương lai trong câu, nếu không người nghe sẽ hiểu là hành động đang xảy ra: 'She's meeting her boss.' (đang gặp ngay lúc này hay sắp gặp?) → Phải thêm 'She's meeting her boss tomorrow.'"}
    ]
  },
  {
    "level": "A1",
    "title": "Hiện Tại Đơn mang nghĩa Tương lai",
    "slug": "present-simple-future",
    "order": 14,
    "chapter": "Future",
    "description": "3 trường hợp dùng thì Hiện Tại Đơn để nói về tương lai: lịch trình cố định, mệnh đề thời gian, câu điều kiện.",
    "analogy": "Như bảng giờ tàu xe — không ai dùng 'will' vì nó là sự kiện cố định đã được in sẵn.",
    "real_world_use": "Lịch biểu phương tiện, quy tắc 'when/if + thì hiện tại', câu điều kiện loại 1.",
    "memory_hook": "Sau WHEN/IF/BEFORE/AFTER/UNTIL + tương lai → LUÔN dùng Hiện Tại Đơn (KHÔNG will).",
    "icon": "🗓️",
    "rules": [
      {
        "title": "3 Trường hợp dùng Present Simple cho Tương lai",
        "formula": "① Lịch trình cố định | ② Mệnh đề thời gian (when/before/after/until) | ③ Câu ĐK loại 1 (if)",
        "explanation": "(1) Lịch trình tàu/xe/máy bay, giờ mở cửa — những gì in sẵn trong bảng giờ. (2) Mệnh đề phụ với when/before/after/until/as soon as: bắt buộc dùng hiện tại đơn, mệnh đề chính dùng will. (3) If + điều kiện có thể xảy ra: bắt buộc dùng hiện tại đơn trong mệnh đề if.",
        "memory_hook": "When/If/Before/After/Until + FUTURE → PRESENT SIMPLE (tuyệt đối không dùng will sau các từ này).",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Trường hợp", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["① Lịch trình CĐ", "S + V (present simple)", "The train leaves at 4. / Shops close at 6."],
            ["② Mệnh đề thời gian", "When/Before/After/Until + S + V (PS), S + will + V", "When I get home, I'll call you."],
            ["② Mệnh đề thời gian", "—", "I won't leave until she arrives."],
            ["③ Câu ĐK loại 1", "If + S + V (PS), S + will + V", "If you study hard, you will pass."]
          ]
        },
        "examples": [
          {"sentence": "When I get home, I'll call you.", "translation": "Khi tôi về nhà, tôi sẽ gọi cho bạn.", "highlight": "When I get (PS) / will call", "is_correct": True},
          {"sentence": "If it rains, we won't go to the beach.", "translation": "Nếu trời mưa, chúng tôi sẽ không đi biển.", "highlight": "If it rains (PS) / won't go", "is_correct": True},
          {"sentence": "When I will get home, I'll call you.", "translation": "❌ Sai — KHÔNG dùng will sau 'when'.", "highlight": "will get", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["when", "before", "after", "until", "as soon as", "once", "if", "unless"],
    "common_mistakes": [
      {"wrong": "When I will arrive, I'll call you.", "correct": "When I arrive, I'll call you.", "explanation": "Sau 'when' (mệnh đề thời gian tương lai) KHÔNG dùng will — dùng Present Simple."},
      {"wrong": "If she will come, we'll be happy.", "correct": "If she comes, we'll be happy.", "explanation": "Sau 'if' (câu điều kiện loại 1) KHÔNG dùng will — dùng Present Simple."},
      {"wrong": "I'm going to call you when I will finish.", "correct": "I'm going to call you when I finish.", "explanation": "Quy tắc áp dụng cho tất cả dạng tương lai: will/be going to/HTTD — mệnh đề 'when' vẫn dùng Present Simple."}
    ],
    "notes": [
      {"type": "warning", "text": "ĐÂY LÀ LỖI CỰC KỲ PHỔ BIẾN: 'When I will go...' / 'If she will come...' — TUYỆT ĐỐI KHÔNG dùng will ngay sau when/if/before/after/until/as soon as trong câu về tương lai."},
      {"type": "info", "text": "Quy tắc này áp dụng cho cả unless (= if...not): 'Unless you study, you'll fail.' (Nếu bạn không học, bạn sẽ trượt.)"}
    ]
  },
  {
    "level": "A1",
    "title": "Thì Tương Lai Tiếp Diễn (Future Continuous)",
    "slug": "future-continuous",
    "order": 15,
    "chapter": "Future",
    "description": "Dùng để nói về hành động ĐANG DIỄN RA tại một thời điểm cụ thể trong tương lai.",
    "analogy": "Nhắm mắt tưởng tượng và hỏi: 'Lúc 10 giờ sáng mai tôi đang làm gì?' — đó là Future Continuous.",
    "real_world_use": "Mô tả hành động đang xảy ra vào thời điểm tương lai; hỏi về dự định lịch sự.",
    "memory_hook": "will + be + V-ing = sẽ đang... (tại một thời điểm tương lai).",
    "icon": "🔭",
    "rules": [
      {
        "title": "FORM & USAGE",
        "formula": "S + will be + V-ing",
        "explanation": "Kết hợp Will (tương lai) và be + V-ing (tiếp diễn). Dùng: (1) Hành động đang xảy ra tại một thời điểm cụ thể trong TL. (2) Kế hoạch đã lên (giống HTTD). (3) Hỏi về dự định lịch sự hơn 'will you'.",
        "memory_hook": "This time tomorrow, I will be flying to London. (đang bay vào đúng giờ đó)",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + will be + V-ing", "This time next week, we will be travelling."],
            ["Phủ định", "S + won't be + V-ing", "I won't be coming to the party."],
            ["Câu hỏi", "Will + S + be + V-ing?", "Will you be going home this summer?"],
            ["Hỏi lịch sự", "Will you be + V-ing?", "Will you be using the car tonight? (lịch sự hơn 'Can I borrow...')"]
          ]
        },
        "examples": [
          {"sentence": "At 8 PM tomorrow, I will be having dinner with clients.", "translation": "Tối mai lúc 8 giờ tôi sẽ đang ăn tối với khách hàng.", "highlight": "will be having", "is_correct": True},
          {"sentence": "Will you be using the computer later?", "translation": "Lát nữa bạn có dùng máy tính không? (hỏi lịch sự)", "highlight": "Will you be using", "is_correct": True},
          {"sentence": "This time next year, I'll be living in a new city.", "translation": "Giờ này năm sau tôi sẽ đang sống ở một thành phố mới.", "highlight": "will be living", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["at this time tomorrow", "this time next week", "at 10 am tomorrow", "in 2 hours"],
    "common_mistakes": [
      {"wrong": "At 8 tomorrow I will having dinner.", "correct": "At 8 tomorrow I will be having dinner.", "explanation": "Cần 'be' giữa will và V-ing: will BE + V-ing."},
      {"wrong": "This time tomorrow I will be went.", "correct": "This time tomorrow I will be going.", "explanation": "Sau 'will be' dùng V-ing, không phải V3."}
    ],
    "notes": [
      {"type": "tip", "text": "'Will you be going home?' lịch sự hơn 'Will you go home?' — Future Continuous được dùng để hỏi thông tin một cách tế nhị mà không gây áp lực."},
      {"type": "info", "text": "Future Continuous có thể thay thế Present Continuous for Future: 'I'm leaving at 8.' = 'I'll be leaving at 8.' — cả hai đều tự nhiên."}
    ]
  },
  {
    "level": "A1",
    "title": "Thì Tương Lai Hoàn Thành (Future Perfect)",
    "slug": "future-perfect",
    "order": 16,
    "chapter": "Future",
    "description": "Nói về hành động sẽ HOÀN TẤT trước một thời điểm/sự kiện khác trong tương lai.",
    "analogy": "Đặt kỳ hạn (deadline): 'Trước khi bạn đến, tôi sẽ nấu xong cơm.' — biết trước điều gì hoàn thành trước cái gì.",
    "real_world_use": "Nói về mục tiêu, kế hoạch sẽ hoàn thành trước một mốc nhất định.",
    "memory_hook": "will have + V3. Từ khóa: BY (trước lúc/tính đến lúc).",
    "icon": "🏁",
    "rules": [
      {
        "title": "FORM & USAGE",
        "formula": "S + will have + V3",
        "explanation": "Dùng 'will have' + V3 cho tất cả ngôi. Từ khóa quan trọng nhất: BY (by then, by 8 o'clock, by the end of...). LƯU Ý: Trong mệnh đề 'By the time', dùng Present Simple (không dùng will).",
        "memory_hook": "BY = từ khóa của Future Perfect. 'By the time you arrive, I will have cooked dinner.'",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + will have + V3", "By 2030, she will have graduated."],
            ["Phủ định", "S + won't have + V3", "I won't have finished by 8 PM."],
            ["Câu hỏi", "Will + S + have + V3?", "Will you have eaten by 7?"],
            ["By the time (bẫy)", "By the time + S + V (PS), S + will have + V3", "By the time I leave, I'll have lived here for 5 years."]
          ]
        },
        "examples": [
          {"sentence": "By this time next year, I will have graduated.", "translation": "Vào giờ này năm sau, tôi sẽ tốt nghiệp xong rồi.", "highlight": "will have graduated", "is_correct": True},
          {"sentence": "I won't have finished my homework by 8 PM.", "translation": "Tôi sẽ chưa làm xong bài tập trước 8 giờ tối.", "highlight": "won't have finished", "is_correct": True},
          {"sentence": "By the time I will leave, I'll have lived here for 5 years.", "translation": "❌ Sai — dùng 'I leave' sau 'by the time', không phải 'I will leave'.", "highlight": "will leave", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["by then", "by that time", "by the end of", "by 2030", "before", "by the time"],
    "common_mistakes": [
      {"wrong": "By the time she will arrive, I will have left.", "correct": "By the time she arrives, I will have left.", "explanation": "Sau 'by the time' dùng Present Simple, không dưng will."},
      {"wrong": "I will have go home by then.", "correct": "I will have gone home by then.", "explanation": "Sau 'will have' dùng V3, không phải V-base."}
    ],
    "notes": [
      {"type": "warning", "text": "BẪY kinh điển: 'By the time + S + will...' ❌. Bắt buộc: 'By the time + S + V (present simple)'. Lý do: mệnh đề thời gian không dùng will."},
      {"type": "tip", "text": "Future Perfect thường diễn tả mục tiêu hoặc kỳ hạn: 'I will have saved enough money by December.' / 'She will have finished the project before the deadline.'"}
    ]
  },
  {
    "level": "A1",
    "title": "Thì Tương Lai Hoàn Thành Tiếp Diễn",
    "slug": "future-perfect-continuous",
    "order": 17,
    "chapter": "Future",
    "description": "Nhấn mạnh quá trình liên tục sẽ kéo dài đến một thời điểm trong tương lai.",
    "analogy": "Hay nhất khi bạn muốn nói về quá trình (bao lâu), không phải kết quả. Giống như nói: 'Tính đến thứ Bảy, tôi đã tập gym được 3 tháng liên tục.'",
    "real_world_use": "Nói về thời gian kéo dài tính đến một mốc tương lai (kỷ niệm, đánh giá, hoàn thành).",
    "memory_hook": "will have been + V-ing. = Future Perfect + Continuous.",
    "icon": "⏱️",
    "rules": [
      {
        "title": "FORM & USAGE",
        "formula": "S + will have been + V-ing",
        "explanation": "Kết hợp Future Perfect (will have been) và Continuous (V-ing). Nhấn mạnh THỜI GIAN KÉO DÀI đến một mốc tương lai. Thường đi với 'for + khoảng thời gian' và 'by the time/when + PS'. Stative verbs KHÔNG dùng dạng này — dùng Future Perfect thay thế.",
        "memory_hook": "by then + for X years → will have been V-ing. 'When he steps on stage, he will have been training for 18 months.'",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + will have been + V-ing", "By end of year, she will have been working here for 10 years."],
            ["Phủ định", "S + won't have been + V-ing", "I won't have been waiting long."],
            ["Câu hỏi", "Will + S + have been + V-ing?", "How long will you have been studying?"],
            ["Stative verb (ngoại lệ)", "→ dùng Future Perfect Đơn", "In 2030, we will have been married for 25 years. (be = stative → chấp nhận ở đây như thành ngữ cố định)"]
          ]
        },
        "examples": [
          {"sentence": "When he steps into the boxing ring on Saturday, he will have been training for 18 months.", "translation": "Khi anh ấy bước lên võ đài thứ Bảy, anh ấy sẽ đã tập luyện được 18 tháng.", "highlight": "will have been training", "is_correct": True},
          {"sentence": "By the end of the year, she will have been working on this project for over 10 years.", "translation": "Đến cuối năm, cô ấy sẽ làm dự án này được hơn 10 năm.", "highlight": "will have been working", "is_correct": True},
          {"sentence": "In 2 years, we will have been being married for 20 years.", "translation": "❌ Sai — 'be married' là trạng thái → dùng 'will have been married'.", "highlight": "will have been being", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["by then", "by the time", "by the end of", "for (duration)", "when (+ PS)", "how long"],
    "common_mistakes": [
      {"wrong": "By Saturday, I will have been know him for a year.", "correct": "By Saturday, I will have known him for a year.", "explanation": "'Know' là stative verb — dùng Future Perfect Đơn, không phải Continuous."},
      {"wrong": "When he will step on stage, he will have been training.", "correct": "When he steps on stage, he will have been training.", "explanation": "Sau 'when' (mệnh đề thời gian) dùng Present Simple, không dùng will."}
    ],
    "notes": [
      {"type": "info", "text": "Đây là thì phức tạp nhất trong tiếng Anh. Ít dùng trong giao tiếp hàng ngày nhưng hay xuất hiện trong bài thi và văn viết học thuật."},
      {"type": "warning", "text": "Không dùng 'will' sau when/by the time/before/after/until — đây là quy tắc chung cho tất cả mệnh đề thời gian."}
    ]
  }
]
