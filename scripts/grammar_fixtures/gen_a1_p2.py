"""Group 2: Past tenses (5-6) + Future (7-8) + Modals (9-11)"""

TOPICS = [
  {
    "level": "A1",
    "title": "Thì Quá Khứ Đơn (Past Simple)",
    "slug": "past-simple-tense",
    "order": 7,
    "chapter": "Past tenses",
    "description": "Thì dùng để nói về hành động đã hoàn thành trong quá khứ tại một thời điểm cụ thể.",
    "analogy": "Ảnh chụp trong album — khoảnh khắc đã xảy ra xong, đóng khung lại trong quá khứ.",
    "real_world_use": "Kể chuyện, nói về ngày hôm qua, mô tả các sự kiện đã qua.",
    "memory_hook": "YESTERDAY / AGO → Past Simple. Động từ đều đổi sang dạng quá khứ.",
    "icon": "📷",
    "rules": [
      {
        "title": "FORM — Động từ có quy tắc (Regular Verbs)",
        "formula": "S + V-ed | S + did not + V-base | Did + S + V-base?",
        "explanation": "Động từ có quy tắc thêm -ed. Câu phủ định và câu hỏi dùng 'did' + động từ nguyên mẫu (không thêm -ed).",
        "memory_hook": "Khẳng định: V-ed. Phủ định/câu hỏi: did/didn't + V-base (không -ed).",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + V-ed", "I worked yesterday."],
            ["Phủ định", "S + didn't + V-base", "She didn't work yesterday."],
            ["Câu hỏi", "Did + S + V-base?", "Did they work?"],
            ["Quy tắc -ed: + ed", "V + ed", "work→worked, play→played"],
            ["Quy tắc -ed: bỏ e + d", "Ve + d", "love→loved, use→used"],
            ["Quy tắc -ed: y→ied", "-y → -ied", "study→studied, try→tried"],
            ["Quy tắc -ed: nhân đôi", "CVC → + ed", "stop→stopped, plan→planned"]
          ]
        },
        "examples": [
          {"sentence": "I played football yesterday.", "translation": "Hôm qua tôi đã chơi bóng đá.", "highlight": "played", "is_correct": True},
          {"sentence": "She didn't go to school last week.", "translation": "Tuần trước cô ấy không đến trường.", "highlight": "didn't go", "is_correct": True},
          {"sentence": "Did you watch the game last night?", "translation": "Tối qua bạn có xem trận đấu không?", "highlight": "Did ... watch", "is_correct": True},
          {"sentence": "He didn't worked yesterday.", "translation": "❌ Sai — sau didn't không dùng V-ed", "highlight": "didn't worked", "is_correct": False}
        ]
      },
      {
        "title": "FORM — Động từ bất quy tắc (Irregular Verbs)",
        "formula": "go→went | have→had | be→was/were | see→saw | eat→ate | come→came",
        "explanation": "Nhiều động từ thông dụng có quá khứ bất quy tắc. Cần học thuộc. Câu phủ định và câu hỏi vẫn dùng 'didn't/did' + V-base.",
        "memory_hook": "Học theo nhóm: go-went, come-came, see-saw, eat-ate, take-took, make-made...",
        "is_exception": True,
        "order": 2,
        "grammar_table": {
          "headers": ["V-base", "V-past", "Nghĩa"],
          "rows": [
            ["go", "went", "đi"],
            ["come", "came", "đến"],
            ["see", "saw", "nhìn thấy"],
            ["eat", "ate", "ăn"],
            ["have", "had", "có/ăn"],
            ["take", "took", "lấy/cầm"],
            ["make", "made", "làm"],
            ["know", "knew", "biết"],
            ["think", "thought", "nghĩ"],
            ["say", "said", "nói"]
          ]
        },
        "examples": [
          {"sentence": "We went to the beach last summer.", "translation": "Mùa hè vừa rồi chúng tôi đã đi biển.", "highlight": "went", "is_correct": True},
          {"sentence": "She saw an amazing film yesterday.", "translation": "Hôm qua cô ấy đã xem một bộ phim tuyệt vời.", "highlight": "saw", "is_correct": True},
          {"sentence": "I didn't see the accident.", "translation": "Tôi không thấy vụ tai nạn.", "highlight": "didn't see", "is_correct": True}
        ]
      },
      {
        "title": "Was / Were — To be ở quá khứ",
        "formula": "I/He/She/It → was | You/We/They → were",
        "explanation": "Động từ 'to be' có dạng quá khứ đặc biệt: was (I/He/She/It) và were (You/We/They). Câu phủ định: wasn't / weren't. Câu hỏi: Was/Were + S?",
        "memory_hook": "was = 1 người/vật (I, he, she, it). were = nhiều (you, we, they).",
        "is_exception": False,
        "order": 3,
        "grammar_table": {
          "headers": ["Chủ ngữ", "Khẳng định", "Phủ định"],
          "rows": [
            ["I / He / She / It", "was", "wasn't"],
            ["You / We / They", "were", "weren't"]
          ]
        },
        "examples": [
          {"sentence": "I was tired after work.", "translation": "Tôi đã mệt sau khi làm việc.", "highlight": "was", "is_correct": True},
          {"sentence": "They were at the party last night.", "translation": "Tối qua họ đã ở buổi tiệc.", "highlight": "were", "is_correct": True},
          {"sentence": "Was the film good?", "translation": "Bộ phim có hay không?", "highlight": "Was", "is_correct": True},
          {"sentence": "We wasn't ready.", "translation": "❌ Sai — 'we' dùng 'weren't'", "highlight": "wasn't", "is_correct": False}
        ]
      }
    ],
    "signal_words": ["yesterday", "last night", "last week", "last year", "ago", "in 2020", "when I was young", "at that time", "in the morning (của ngày hôm qua)"],
    "common_mistakes": [
      {"wrong": "I goed to school yesterday.", "correct": "I went to school yesterday.", "explanation": "'Go' là động từ bất quy tắc: go → went."},
      {"wrong": "Did she went home?", "correct": "Did she go home?", "explanation": "Sau 'did' dùng V-base, không dùng V-past."},
      {"wrong": "He didn't came yesterday.", "correct": "He didn't come yesterday.", "explanation": "Sau 'didn't' dùng V-base."},
      {"wrong": "They was happy.", "correct": "They were happy.", "explanation": "'They' dùng 'were', không dùng 'was'."}
    ],
    "notes": [
      {"type": "warning", "text": "Có 100+ động từ bất quy tắc phổ biến cần học thuộc. Bắt đầu với 20 động từ thông dụng nhất: go, come, see, have, take, make, know, get, give, think, say, eat, drink, sleep, wake, sit, stand, run, buy, tell."},
      {"type": "tip", "text": "Quy tắc phát âm -ed: /t/ sau âm vô thanh (worked, stopped), /d/ sau âm hữu thanh (played, loved), /ɪd/ sau âm /t/ hoặc /d/ (wanted, needed)."}
    ]
  },
  {
    "level": "A1",
    "title": "Thì Quá Khứ Tiếp Diễn (Past Continuous)",
    "slug": "past-continuous-tense",
    "order": 8,
    "chapter": "Past tenses",
    "description": "Thì dùng để nói về hành động đang diễn ra tại một thời điểm cụ thể trong quá khứ.",
    "analogy": "Video đang phát lại dừng ở một khung hình — bạn thấy hành động đang xảy ra tại khoảnh khắc đó.",
    "real_world_use": "Kể chuyện khi bạn muốn mô tả bối cảnh: 'At 8 PM, I was studying...'",
    "memory_hook": "was/were + V-ing = đang làm gì đó vào thời điểm trong quá khứ.",
    "icon": "🎬",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + was/were + V-ing",
        "explanation": "Cấu trúc giống Present Continuous nhưng dùng was/were thay vì am/is/are.",
        "memory_hook": "was (I/he/she/it) + V-ing | were (you/we/they) + V-ing",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Chủ ngữ", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["I / He / She / It", "was + V-ing", "I was sleeping at 10 PM."],
            ["You / We / They", "were + V-ing", "They were watching TV."],
            ["Phủ định", "wasn't/weren't + V-ing", "She wasn't working at that time."],
            ["Câu hỏi", "Was/Were + S + V-ing?", "Were you sleeping?"]
          ]
        },
        "examples": [
          {"sentence": "I was studying when you called.", "translation": "Tôi đang học bài khi bạn gọi điện.", "highlight": "was studying", "is_correct": True},
          {"sentence": "They were having dinner at 7 PM.", "translation": "Lúc 7 giờ tối họ đang ăn tối.", "highlight": "were having", "is_correct": True},
          {"sentence": "What were you doing last night?", "translation": "Tối qua bạn đang làm gì?", "highlight": "were you doing", "is_correct": True}
        ]
      },
      {
        "title": "USAGE — Kết hợp Past Simple và Past Continuous",
        "formula": "S was/were V-ing (bối cảnh) + when + S V-past (sự kiện xảy ra)",
        "explanation": "Past Continuous thường dùng để mô tả bối cảnh (hành động đang xảy ra), trong khi Past Simple mô tả sự kiện ngắn xảy ra xen vào. Dùng 'when' + Past Simple, 'while' + Past Continuous.",
        "memory_hook": "while + đang làm (Continuous) | when + đã xảy ra (Simple)",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Cấu trúc", "Ví dụ"],
          "rows": [
            ["Past Cont. + when + Past Simple", "I was sleeping when the phone rang."],
            ["while + Past Cont., Past Simple", "While I was cooking, she arrived."],
            ["Hai hành động song song", "He was reading while she was watching TV."]
          ]
        },
        "examples": [
          {"sentence": "I was walking home when it started to rain.", "translation": "Tôi đang đi bộ về nhà thì trời bắt đầu mưa.", "highlight": "was walking / started", "is_correct": True},
          {"sentence": "While they were sleeping, the thief came in.", "translation": "Trong khi họ đang ngủ, tên trộm đã vào.", "highlight": "were sleeping / came", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["while", "when", "at that time", "at 8 PM last night", "all day yesterday", "this time yesterday"],
    "common_mistakes": [
      {"wrong": "I was sleep when you called.", "correct": "I was sleeping when you called.", "explanation": "Sau was/were phải dùng V-ing."},
      {"wrong": "While I cooked, she arrived.", "correct": "While I was cooking, she arrived.", "explanation": "'While' thường kết hợp với Past Continuous để chỉ hành động đang diễn ra."}
    ],
    "notes": [
      {"type": "tip", "text": "Past Continuous thường đi với Past Simple: 'I was watching TV when my friend called.' (was watching = đang xảy ra, called = xen vào)."}
    ]
  },
  {
    "level": "A1",
    "title": "Will / Shall — Tương lai đơn",
    "slug": "will-shall",
    "order": 11,
    "chapter": "Future",
    "description": "Dùng will/shall để nói về tương lai, quyết định tức thời, dự đoán và lời hứa.",
    "analogy": "Đèn bật lên trong đầu — bạn chợt quyết định ngay lúc đó.",
    "real_world_use": "Hứa hẹn, đề nghị giúp đỡ, dự đoán, quyết định tức thì.",
    "memory_hook": "Will = quyết định TỨC THỜI ngay khi nói. Be going to = kế hoạch ĐÃ CÓ từ trước.",
    "icon": "🔮",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + will + V-base | S + will not (won't) + V-base | Will + S + V-base?",
        "explanation": "Will không thay đổi theo chủ ngữ. Dạng rút gọn: I'll, you'll, he'll, she'll, it'll, we'll, they'll. Phủ định: won't (= will not).",
        "memory_hook": "'ll = will (rút gọn). won't = will not.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + will + V-base", "I will help you."],
            ["Rút gọn", "S + 'll + V-base", "I'll help you."],
            ["Phủ định", "S + won't + V-base", "She won't be late."],
            ["Câu hỏi", "Will + S + V-base?", "Will you come?"]
          ]
        },
        "examples": [
          {"sentence": "I'll open the window.", "translation": "Tôi sẽ mở cửa sổ. (quyết định tức thì)", "highlight": "I'll open", "is_correct": True},
          {"sentence": "Don't worry. I won't tell anyone.", "translation": "Đừng lo. Tôi sẽ không nói với ai.", "highlight": "won't tell", "is_correct": True},
          {"sentence": "Will you marry me?", "translation": "Em có lấy anh không?", "highlight": "Will you", "is_correct": True}
        ]
      },
      {
        "title": "USAGE — Khi nào dùng Will",
        "formula": "Quyết định tức thì | Dự đoán | Hứa hẹn | Đề nghị",
        "explanation": "(1) Quyết định tức thì khi nói. (2) Dự đoán về tương lai (thường với think/believe/probably). (3) Lời hứa. (4) Đề nghị hoặc xin phép.",
        "memory_hook": "Will = I decide NOW, as I'm speaking.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Cách dùng", "Ví dụ"],
          "rows": [
            ["Quyết định tức thì", "The phone is ringing. I'll get it!"],
            ["Dự đoán", "I think it will rain tomorrow."],
            ["Lời hứa", "I promise I'll call you tonight."],
            ["Đề nghị giúp", "Shall I carry that for you?"],
            ["Gợi ý (shall I/we)", "Shall we go now?"]
          ]
        },
        "examples": [
          {"sentence": "I think she'll pass the exam.", "translation": "Tôi nghĩ cô ấy sẽ vượt qua kỳ thi.", "highlight": "I think ... will pass", "is_correct": True},
          {"sentence": "I'll call you later, I promise.", "translation": "Tôi hứa sẽ gọi cho bạn sau.", "highlight": "I'll call", "is_correct": True},
          {"sentence": "Shall I help you with that?", "translation": "Tôi có thể giúp bạn với việc đó không?", "highlight": "Shall I", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["tomorrow", "next week", "next year", "soon", "one day", "in the future", "I think...", "probably", "I promise", "I'm sure"],
    "common_mistakes": [
      {"wrong": "I will to go home.", "correct": "I will go home.", "explanation": "Sau will dùng V-base, không cần 'to'."},
      {"wrong": "She wills come.", "correct": "She will come.", "explanation": "Will không thêm -s cho ngôi thứ ba số ít."},
      {"wrong": "I'm going to a coffee. I'll decide right now.", "correct": "I'll have a coffee. (quyết định tức thì)", "explanation": "Quyết định ngay lúc nói = will, không phải be going to."}
    ],
    "notes": [
      {"type": "info", "text": "Shall thường dùng trong câu hỏi với I/we để đề nghị hoặc gợi ý: 'Shall I open the window?' / 'Shall we start?' Ít dùng hơn will trong tiếng Anh Mỹ."},
      {"type": "tip", "text": "Will vs Be going to: Will = quyết định tức thì. Be going to = kế hoạch đã có trước. 'I'll have the pizza.' (vừa quyết định) vs 'I'm going to have pizza tonight.' (đã định từ trước)."}
    ]
  },
  {
    "level": "A1",
    "title": "Be Going To",
    "slug": "be-going-to",
    "order": 12,
    "chapter": "Future",
    "description": "Dùng 'be going to' để nói về kế hoạch đã có sẵn và dự đoán có bằng chứng rõ ràng.",
    "analogy": "Lịch trình đã đặt sẵn — bạn đã lên kế hoạch, đọc lịch và nói về nó.",
    "real_world_use": "Khi nói về kế hoạch du lịch, sinh nhật, cuối tuần — mọi thứ bạn đã quyết định từ trước.",
    "memory_hook": "PLAN = Be going to. Decision now = Will.",
    "icon": "📅",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + am/is/are + going to + V-base",
        "explanation": "Dùng am/is/are phù hợp với chủ ngữ, sau đó 'going to', cuối cùng là động từ nguyên mẫu.",
        "memory_hook": "am/is/are + going to + V (không thêm -s hay -ed)",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Chủ ngữ", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["I", "am going to + V", "I am going to study tonight."],
            ["He/She/It", "is going to + V", "She is going to visit her parents."],
            ["You/We/They", "are going to + V", "They are going to get married."],
            ["Phủ định", "am/is/are NOT going to + V", "I'm not going to eat fast food."],
            ["Câu hỏi", "Am/Is/Are + S + going to + V?", "Are you going to come?"]
          ]
        },
        "examples": [
          {"sentence": "I'm going to visit my grandparents next week.", "translation": "Tuần tới tôi sẽ thăm ông bà.", "highlight": "am going to visit", "is_correct": True},
          {"sentence": "She is going to study medicine.", "translation": "Cô ấy sẽ học y khoa.", "highlight": "is going to study", "is_correct": True},
          {"sentence": "Is he going to join us for dinner?", "translation": "Anh ấy có tham gia bữa tối với chúng ta không?", "highlight": "Is he going to join", "is_correct": True}
        ]
      },
      {
        "title": "USAGE — Kế hoạch và Dự đoán có bằng chứng",
        "formula": "Kế hoạch đã có | Dự đoán có bằng chứng rõ ràng",
        "explanation": "(1) Kế hoạch đã được quyết định trước khi nói. (2) Dự đoán về tương lai dựa trên bằng chứng quan sát được ngay lúc đó.",
        "memory_hook": "Nhìn thấy bằng chứng (mây đen) → 'It's going to rain!' (dự đoán chắc chắn).",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Cách dùng", "Ví dụ"],
          "rows": [
            ["Kế hoạch đã định", "We're going to have a party on Friday."],
            ["Dự đoán có bằng chứng", "Look at those clouds! It's going to rain."],
            ["Quyết định đã có", "She's going to quit her job next month."]
          ]
        },
        "examples": [
          {"sentence": "Look at those dark clouds. It's going to rain.", "translation": "Nhìn những đám mây đen kia. Trời sắp mưa.", "highlight": "is going to rain", "is_correct": True},
          {"sentence": "They're going to get married in June.", "translation": "Họ sẽ kết hôn vào tháng Sáu.", "highlight": "are going to get", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["tomorrow", "next week", "next month", "soon", "this evening", "at the weekend", "in the future"],
    "common_mistakes": [
      {"wrong": "I am going to studied tonight.", "correct": "I am going to study tonight.", "explanation": "Sau 'going to' dùng V-base, không -ed."},
      {"wrong": "She is going to goes to Paris.", "correct": "She is going to go to Paris.", "explanation": "Sau 'going to' dùng V-base, không -s."}
    ],
    "notes": [
      {"type": "tip", "text": "Trong văn nói, 'going to' thường được phát âm là 'gonna': 'I'm gonna study.' (không nên dùng trong văn viết trang trọng)."}
    ]
  },
  {
    "level": "A1",
    "title": "Can / Can't — Khả năng và Cho phép",
    "slug": "can-cant",
    "order": 18,
    "chapter": "Modals, the imperative, etc .",
    "description": "Dùng can/can't để nói về khả năng, kỹ năng, xin phép và đề nghị.",
    "analogy": "Chiếc chìa khóa — can mở ra cánh cửa của khả năng và sự cho phép.",
    "real_world_use": "Nói về kỹ năng bản thân, xin phép, đề nghị giúp đỡ, và những điều được/không được làm.",
    "memory_hook": "CAN = có thể làm. CAN'T = không thể làm. Sau CAN luôn dùng V-base.",
    "icon": "🔑",
    "rules": [
      {
        "title": "FORM — Cấu trúc",
        "formula": "S + can + V-base | S + cannot (can't) + V-base | Can + S + V-base?",
        "explanation": "Can là modal verb: không thêm -s/-es, không dùng do/does, luôn theo sau bởi V-base.",
        "memory_hook": "Can không bao giờ thêm -s. She can (không phải she cans).",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "S + can + V-base", "I can swim."],
            ["Phủ định", "S + can't + V-base", "He can't drive."],
            ["Câu hỏi", "Can + S + V-base?", "Can you help me?"],
            ["Trả lời ngắn", "Yes, I can. / No, I can't.", "Can you cook? Yes, I can."]
          ]
        },
        "examples": [
          {"sentence": "She can speak three languages.", "translation": "Cô ấy có thể nói ba ngôn ngữ.", "highlight": "can speak", "is_correct": True},
          {"sentence": "I can't find my keys.", "translation": "Tôi không thể tìm thấy chìa khóa.", "highlight": "can't find", "is_correct": True},
          {"sentence": "Can I use your phone?", "translation": "Tôi có thể dùng điện thoại của bạn không?", "highlight": "Can I use", "is_correct": True},
          {"sentence": "She cans play the piano.", "translation": "❌ Sai — can không thêm -s.", "highlight": "cans", "is_correct": False}
        ]
      },
      {
        "title": "USAGE — Các cách dùng Can",
        "formula": "Khả năng/kỹ năng | Cho phép | Đề nghị | Yêu cầu",
        "explanation": "(1) Khả năng hoặc kỹ năng (có thể làm). (2) Xin phép hoặc cho phép. (3) Đề nghị giúp đỡ. (4) Yêu cầu ai đó làm gì.",
        "memory_hook": "Can I...? = xin phép. Can you...? = nhờ ai đó.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Cách dùng", "Ví dụ"],
          "rows": [
            ["Khả năng / kỹ năng", "Dogs can hear very well."],
            ["Xin phép (Can I...?)", "Can I open the window?"],
            ["Cho phép (You can...)", "You can leave early today."],
            ["Đề nghị (Can you...?)", "Can you pass the salt, please?"]
          ]
        },
        "examples": [
          {"sentence": "Can you explain that again?", "translation": "Bạn có thể giải thích lại không?", "highlight": "Can you explain", "is_correct": True},
          {"sentence": "You can park here for free.", "translation": "Bạn có thể đỗ xe ở đây miễn phí.", "highlight": "can park", "is_correct": True},
          {"sentence": "I can't swim, but I can run fast.", "translation": "Tôi không biết bơi nhưng tôi có thể chạy nhanh.", "highlight": "can't swim / can run", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["well", "fluently", "fast", "easily", "at all", "without help"],
    "common_mistakes": [
      {"wrong": "She can to swim.", "correct": "She can swim.", "explanation": "Sau modal verb (can) dùng V-base, không dùng 'to'."},
      {"wrong": "Can you to help me?", "correct": "Can you help me?", "explanation": "Không dùng 'to' sau can trong câu hỏi."},
      {"wrong": "He cans play guitar.", "correct": "He can play guitar.", "explanation": "Can không bao giờ thêm -s."}
    ],
    "notes": [
      {"type": "info", "text": "Could là dạng quá khứ của can: 'When I was 5, I couldn't read.' Cũng dùng could để xin phép lịch sự hơn: 'Could I borrow your pen?'"},
      {"type": "tip", "text": "Can I? vs May I? — Cả hai dùng để xin phép. 'May I?' trang trọng hơn. Trong giao tiếp hàng ngày, 'Can I?' phổ biến hơn."}
    ]
  },
  {
    "level": "A1",
    "title": "The Imperative — Câu mệnh lệnh",
    "slug": "the-imperative",
    "order": 19,
    "chapter": "Modals, the imperative, etc .",
    "description": "Dùng câu mệnh lệnh để ra lệnh, hướng dẫn, đề nghị và cảnh báo.",
    "analogy": "Biển báo giao thông — truyền đạt ý nghĩa trực tiếp, ngắn gọn, không cần chủ ngữ.",
    "real_world_use": "Hướng dẫn nấu ăn, quy tắc, hướng đường, biển cảnh báo, lời khuyên.",
    "memory_hook": "Imperative = V-base, không có chủ ngữ 'you'. Phủ định = Don't + V-base.",
    "icon": "📢",
    "rules": [
      {
        "title": "FORM — Khẳng định và Phủ định",
        "formula": "V-base (affirmative) | Don't + V-base (negative)",
        "explanation": "Câu mệnh lệnh khẳng định dùng động từ nguyên mẫu không có chủ ngữ. Câu mệnh lệnh phủ định dùng 'Don't' + V-base. Chủ ngữ 'you' ẩn.",
        "memory_hook": "Không có 'you' trước động từ. Chỉ cần V-base!",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Loại", "Cấu trúc", "Ví dụ"],
          "rows": [
            ["Khẳng định", "V-base", "Open the door. / Come in!"],
            ["Phủ định", "Don't + V-base", "Don't be late. / Don't touch that!"],
            ["Lịch sự hơn", "Please + V-base", "Please sit down."],
            ["Cảnh báo", "Be careful! / Watch out!", "Be careful with that knife!"]
          ]
        },
        "examples": [
          {"sentence": "Turn left at the traffic lights.", "translation": "Rẽ trái tại đèn giao thông.", "highlight": "Turn left", "is_correct": True},
          {"sentence": "Don't run in the corridor!", "translation": "Đừng chạy trong hành lang!", "highlight": "Don't run", "is_correct": True},
          {"sentence": "Please be quiet.", "translation": "Vui lòng giữ trật tự.", "highlight": "Please be quiet", "is_correct": True},
          {"sentence": "Have a nice day!", "translation": "Chúc một ngày tốt lành!", "highlight": "Have", "is_correct": True}
        ]
      },
      {
        "title": "USAGE — Các tình huống dùng Imperative",
        "formula": "Lệnh | Hướng dẫn | Lời khuyên | Đề nghị | Cảnh báo",
        "explanation": "Imperative được dùng rộng rãi trong: ra lệnh/yêu cầu, hướng dẫn/công thức, lời khuyên, lời mời/đề nghị, và cảnh báo.",
        "memory_hook": "Ngữ điệu thay đổi ý nghĩa: nhẹ nhàng = lời mời; mạnh = lệnh; sợ hãi = cảnh báo.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Tình huống", "Ví dụ"],
          "rows": [
            ["Ra lệnh", "Sit down and be quiet!"],
            ["Hướng dẫn nấu ăn", "Add two eggs and mix well."],
            ["Lời khuyên", "Take an umbrella — it might rain."],
            ["Lời mời", "Help yourself to some cake!"],
            ["Cảnh báo", "Watch out! There's a car!"]
          ]
        },
        "examples": [
          {"sentence": "Add salt and pepper to taste.", "translation": "Thêm muối và tiêu vừa miệng.", "highlight": "Add", "is_correct": True},
          {"sentence": "Don't forget to bring your passport.", "translation": "Đừng quên mang theo hộ chiếu.", "highlight": "Don't forget", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["please", "don't", "always", "never", "be careful", "remember to", "make sure to"],
    "common_mistakes": [
      {"wrong": "You don't to run here.", "correct": "Don't run here.", "explanation": "Câu mệnh lệnh không có chủ ngữ 'you' và không dùng 'to'."},
      {"wrong": "Please to sit down.", "correct": "Please sit down.", "explanation": "Sau 'please' dùng V-base trực tiếp, không có 'to'."}
    ],
    "notes": [
      {"type": "tip", "text": "Để làm câu mệnh lệnh mềm mại hơn: thêm 'please' đầu hoặc cuối câu. 'Please come in.' / 'Sit down, please.'"},
      {"type": "info", "text": "Let's + V-base = mệnh lệnh số nhiều, bao gồm cả người nói: 'Let's go!' (= Let us go!)"}
    ]
  },
  {
    "level": "A1",
    "title": "Like vs Would Like",
    "slug": "like-vs-would-like",
    "order": 20,
    "chapter": "Modals, the imperative, etc .",
    "description": "Phân biệt 'like' (sở thích chung) và 'would like' (mong muốn cụ thể ở thời điểm nói).",
    "analogy": "'Like' là album sở thích của bạn. 'Would like' là đơn đặt hàng bạn viết ngay lúc này.",
    "real_world_use": "Gọi món ăn, đặt vé, bày tỏ mong muốn lịch sự trong các tình huống giao tiếp.",
    "memory_hook": "Like + V-ing = sở thích chung. Would like + to V = muốn ngay bây giờ.",
    "icon": "💝",
    "rules": [
      {
        "title": "Like + V-ing — Sở thích chung",
        "formula": "S + like/likes + V-ing (general preference)",
        "explanation": "'Like' + V-ing diễn tả sở thích, điều bạn thích làm nói chung (không phải ngay lúc này). Theo sau 'like' là V-ing hoặc N.",
        "memory_hook": "Like coffee = bạn thích cà phê nói chung (mọi lúc). Would like a coffee = muốn uống ngay bây giờ.",
        "is_exception": False,
        "order": 1,
        "grammar_table": {
          "headers": ["Cấu trúc", "Ví dụ"],
          "rows": [
            ["S + like + V-ing", "I like reading books."],
            ["S + like + noun", "She likes coffee."],
            ["S + don't/doesn't like + V-ing", "He doesn't like cooking."],
            ["Do/Does + S + like + V-ing?", "Do you like swimming?"]
          ]
        },
        "examples": [
          {"sentence": "I like swimming in the sea.", "translation": "Tôi thích bơi ở biển.", "highlight": "like swimming", "is_correct": True},
          {"sentence": "She likes listening to music.", "translation": "Cô ấy thích nghe nhạc.", "highlight": "likes listening", "is_correct": True},
          {"sentence": "Do you like cooking?", "translation": "Bạn có thích nấu ăn không?", "highlight": "like cooking", "is_correct": True}
        ]
      },
      {
        "title": "Would Like + to Infinitive — Muốn cụ thể",
        "formula": "S + would like + to + V-base (specific desire right now)",
        "explanation": "'Would like' = want (lịch sự hơn). Diễn tả mong muốn cụ thể vào lúc nói. Theo sau 'would like' là 'to + V' (infinitive) hoặc noun.",
        "memory_hook": "Would like = polite want. 'd like = rút gọn thông dụng.",
        "is_exception": False,
        "order": 2,
        "grammar_table": {
          "headers": ["Cấu trúc", "Ví dụ"],
          "rows": [
            ["S + would like + to + V", "I'd like to order a pizza."],
            ["S + would like + noun", "She'd like a glass of water."],
            ["Would + S + like + to + V?", "Would you like to dance?"],
            ["Trả lời: Yes, I'd love to.", "Yes, please! / No, thank you."]
          ]
        },
        "examples": [
          {"sentence": "I'd like to book a table for two.", "translation": "Tôi muốn đặt bàn cho hai người.", "highlight": "I'd like to book", "is_correct": True},
          {"sentence": "Would you like a cup of tea?", "translation": "Bạn có muốn một tách trà không?", "highlight": "Would you like", "is_correct": True},
          {"sentence": "She'd like to visit Japan one day.", "translation": "Cô ấy muốn thăm Nhật Bản một ngày nào đó.", "highlight": "She'd like to visit", "is_correct": True}
        ]
      }
    ],
    "signal_words": ["in general", "usually", "often (like)", "now", "right now", "please", "one day (would like)"],
    "common_mistakes": [
      {"wrong": "I would like swimming.", "correct": "I would like to swim. / I like swimming.", "explanation": "'Would like' theo sau bởi 'to + V', không phải V-ing."},
      {"wrong": "I'd like go home.", "correct": "I'd like to go home.", "explanation": "Sau 'would like' cần 'to' trước động từ."},
      {"wrong": "Do you would like some coffee?", "correct": "Would you like some coffee?", "explanation": "Câu hỏi với 'would like' đảo 'would' lên đầu, không dùng 'do'."}
    ],
    "notes": [
      {"type": "tip", "text": "'Would love to' = rất muốn (mạnh hơn would like): 'I'd love to visit Paris someday!'"},
      {"type": "info", "text": "Trong nhà hàng: 'I'd like the chicken, please.' / 'Would you like anything else?' — đây là cách nói lịch sự và tự nhiên nhất."}
    ]
  }
]
