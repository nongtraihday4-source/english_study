"""Group 1: Present tenses (topics 1-4)"""

TOPICS = [
{
  "level": "A1",
  "title": "Thì Hiện Tại Đơn (Present Simple)",
  "slug": "present-simple-tense",
  "order": 1,
  "chapter": "Present tenses",
  "description": "Thì dùng để nói về thói quen, sự thật chung, lịch trình cố định và trạng thái.",
  "analogy": "Chiếc đồng hồ bấm giờ — nó ghi lại những điều xảy ra đều đặn, lặp đi lặp lại.",
  "real_world_use": "Dùng để nói về thói quen hằng ngày, sự thật hiển nhiên, và lịch trình.",
  "memory_hook": "Thì đơn = sự kiện đơn giản, có thể xảy ra bất kỳ lúc nào.",
  "icon": "⏰",
  "rules": [
    {
      "title": "FORM — Khẳng định (Affirmative)",
      "formula": "I/You/We/They + V-base | He/She/It + V-s/es",
      "explanation": "Chủ ngữ ngôi thứ nhất, thứ hai và số nhiều dùng động từ nguyên mẫu. Ngôi thứ ba số ít (he/she/it) thêm -s hoặc -es.",
      "memory_hook": "He/She/It → thêm -s vào cuối động từ. Nhớ: HE WORKS hard!",
      "is_exception": False,
      "order": 1,
      "grammar_table": {
        "headers": [
          "Chủ ngữ",
          "Động từ",
          "Ví dụ"
        ],
        "rows": [
          [
            "I",
            "V-base",
            "I work every day."
          ],
          [
            "You",
            "V-base",
            "You speak English."
          ],
          [
            "He / She / It",
            "V+s/es",
            "She works at a hospital."
          ],
          [
            "We / They",
            "V-base",
            "They play football."
          ]
        ]
      },
      "examples": [
        {
          "sentence": "I drink coffee every morning.",
          "translation": "Tôi uống cà phê mỗi sáng.",
          "highlight": "drink",
          "is_correct": True
        },
        {
          "sentence": "She works at a school.",
          "translation": "Cô ấy làm việc ở trường học.",
          "highlight": "works",
          "is_correct": True
        },
        {
          "sentence": "They live in Ha Noi.",
          "translation": "Họ sống ở Hà Nội.",
          "highlight": "live",
          "is_correct": True
        },
        {
          "sentence": "He go to the gym.",
          "translation": "Anh ấy đi tập gym. ❌ (sai)",
          "highlight": "go",
          "is_correct": False
        }
      ]
    },
    {
      "title": "FORM — Phủ định & Câu hỏi",
      "formula": "S + do/does + not + V-base | Do/Does + S + V-base?",
      "explanation": "Dùng do/does để tạo phủ định và câu hỏi. 'Does' dùng cho he/she/it; khi dùng does, động từ chính trở về nguyên mẫu.",
      "memory_hook": "Does đã mang cái -s thay cho động từ rồi → động từ không cần -s nữa.",
      "is_exception": False,
      "order": 2,
      "grammar_table": {
        "headers": [
          "Loại",
          "Cấu trúc",
          "Ví dụ"
        ],
        "rows": [
          [
            "Phủ định (I/You/We/They)",
            "S + don't + V",
            "I don't eat meat."
          ],
          [
            "Phủ định (He/She/It)",
            "S + doesn't + V",
            "He doesn't like coffee."
          ],
          [
            "Câu hỏi (I/You/We/They)",
            "Do + S + V?",
            "Do you speak French?"
          ],
          [
            "Câu hỏi (He/She/It)",
            "Does + S + V?",
            "Does she work here?"
          ]
        ]
      },
      "examples": [
        {
          "sentence": "I don't like spicy food.",
          "translation": "Tôi không thích đồ ăn cay.",
          "highlight": "don't like",
          "is_correct": True
        },
        {
          "sentence": "She doesn't have a car.",
          "translation": "Cô ấy không có xe hơi.",
          "highlight": "doesn't have",
          "is_correct": True
        },
        {
          "sentence": "Do they live near here?",
          "translation": "Họ có sống gần đây không?",
          "highlight": "Do ... live",
          "is_correct": True
        },
        {
          "sentence": "Does he works here?",
          "translation": "Anh ấy có làm việc ở đây không? ❌",
          "highlight": "works",
          "is_correct": False
        }
      ]
    },
    {
      "title": "USAGE — Khi nào dùng Present Simple",
      "formula": "Thói quen | Sự thật | Trạng thái | Lịch trình",
      "explanation": "Dùng Present Simple cho: (1) Thói quen và hành động lặp đi lặp lại. (2) Sự thật và quy luật chung. (3) Trạng thái (cảm xúc, quan hệ). (4) Lịch trình cố định (xe buýt, tàu, phim).",
      "memory_hook": "Nếu bạn có thể thay bằng 'always' hoặc 'every day' → dùng Present Simple.",
      "is_exception": False,
      "order": 3,
      "grammar_table": {
        "headers": [
          "Cách dùng",
          "Ví dụ"
        ],
        "rows": [
          [
            "Thói quen hằng ngày",
            "I wake up at 6 every morning."
          ],
          [
            "Sự thật chung",
            "The Earth goes around the Sun."
          ],
          [
            "Trạng thái / cảm xúc",
            "I love Vietnamese food."
          ],
          [
            "Lịch trình cố định",
            "The train leaves at 8:30."
          ]
        ]
      },
      "examples": [
        {
          "sentence": "The sun rises in the east.",
          "translation": "Mặt trời mọc ở phía đông. (sự thật)",
          "highlight": "rises",
          "is_correct": True
        },
        {
          "sentence": "I usually eat lunch at noon.",
          "translation": "Tôi thường ăn trưa vào buổi trưa. (thói quen)",
          "highlight": "usually eat",
          "is_correct": True
        },
        {
          "sentence": "The flight departs at 9 PM.",
          "translation": "Chuyến bay khởi hành lúc 9 giờ tối. (lịch trình)",
          "highlight": "departs",
          "is_correct": True
        }
      ]
    },
    {
      "title": "Quy tắc thêm -s/-es",
      "formula": "V + s | V(ch/sh/x/o/ss) + es | V-y → V-ies",
      "explanation": "Quy tắc thêm đuôi cho ngôi thứ ba số ít: (1) Đại đa số động từ: thêm -s. (2) Các động từ kết thúc bằng ch, sh, x, o, ss: thêm -es. (3) Động từ kết thúc -y sau phụ âm: bỏ y, thêm -ies.",
      "memory_hook": "y→ies: try→tries, study→studies | -es: watch→watches, go→goes",
      "is_exception": False,
      "order": 6,
      "grammar_table": {
        "headers": [
          "Trường hợp",
          "Quy tắc",
          "Ví dụ"
        ],
        "rows": [
          [
            "Hầu hết động từ",
            "+ s",
            "work→works, eat→eats"
          ],
          [
            "Kết thúc ch/sh/x/o/ss",
            "+ es",
            "watch→watches, go→goes"
          ],
          [
            "Kết thúc phụ âm + y",
            "y → ies",
            "study→studies, try→tries"
          ],
          [
            "Kết thúc nguyên âm + y",
            "+ s",
            "play→plays, say→says"
          ]
        ]
      },
      "examples": [
        {
          "sentence": "She studies English every night.",
          "translation": "Cô ấy học tiếng Anh mỗi tối.",
          "highlight": "studies",
          "is_correct": True
        },
        {
          "sentence": "He watches TV after dinner.",
          "translation": "Anh ấy xem TV sau bữa tối.",
          "highlight": "watches",
          "is_correct": True
        },
        {
          "sentence": "My cat plays with everything.",
          "translation": "Con mèo của tôi chơi với mọi thứ.",
          "highlight": "plays",
          "is_correct": True
        }
      ]
    }
  ],
  "signal_words": [
    "always",
    "usually",
    "often",
    "sometimes",
    "rarely",
    "never",
    "every day",
    "every week",
    "on Mondays",
    "in the morning",
    "at night",
    "once a week"
  ],
  "common_mistakes": [
    {
      "wrong": "She work at a hospital.",
      "correct": "She works at a hospital.",
      "explanation": "Ngôi thứ ba số ít (she/he/it) phải thêm -s vào động từ."
    },
    {
      "wrong": "Does he works here?",
      "correct": "Does he work here?",
      "explanation": "Khi dùng 'does', động từ chính không thêm -s nữa."
    },
    {
      "wrong": "I am go to school every day.",
      "correct": "I go to school every day.",
      "explanation": "Present Simple không dùng 'am/is/are'. Chỉ dùng động từ trực tiếp."
    },
    {
      "wrong": "She don't like coffee.",
      "correct": "She doesn't like coffee.",
      "explanation": "Ngôi thứ ba số ít dùng 'doesn't', không phải 'don't'."
    }
  ],
  "notes": [
    {
      "type": "tip",
      "text": "Trạng từ tần suất (always, usually, often...) được đặt TRƯỚC động từ chính nhưng SAU to be: 'I always eat breakfast' / 'She is always late'."
    },
    {
      "type": "warning",
      "text": "Present Simple KHÔNG dùng cho hành động đang xảy ra ngay lúc nói. Dùng Present Continuous thay thế."
    },
    {
      "type": "info",
      "text": "Một số động từ trạng thái (state verbs) như love, know, want, need, have, see, hear thường KHÔNG dùng ở dạng -ing."
    }
  ],
  "metaphor_title": "Chiếc đồng hồ bấm giờ",
  "narrative_intro": "Thì Hiện tại đơn giống như một chiếc đồng hồ bấm giờ tích tắc đều đặn. Chúng ta sử dụng nó để nói về những sự kiện không ngừng lặp lại, những chân lý luôn đúng, hay những thói quen đã ăn sâu vào cuộc sống thường nhật.",
  "quick_vibe": "Sự thật, thói quen và những điều hiển nhiên.",
  "comparison_with": [
    {
      "title": "Present Continuous",
      "difference": "Hiện tại đơn nói về việc xảy ra thường xuyên. Hiện tại tiếp diễn nói về việc đang xảy ra ngay lúc này.",
      "examples": [
        {
          "sentence": "I live in Hanoi.",
          "explanation": "Sống ở Hà Nội là một sự thật lâu dài (Hiện tại đơn)."
        },
        {
          "sentence": "I am living with my friend these days.",
          "explanation": "Chỉ sống tạm bợ trong thời gian này (Hiện tại tiếp diễn)."
        }
      ]
    }
  ]
},
{
  "level": "A1",
  "title": "Thì Hiện Tại Tiếp Diễn (Present Continuous)",
  "slug": "present-continuous-tense",
  "order": 2,
  "chapter": "Present tenses",
  "description": "Thì dùng để nói về hành động đang xảy ra ngay lúc nói hoặc tình huống tạm thời.",
  "analogy": "Camera quay trực tiếp — ghi lại chính xác những gì đang diễn ra ở thời điểm này.",
  "real_world_use": "Dùng khi livestream, mô tả video, kể chuyện trong tranh, hoặc nói về kế hoạch gần.",
  "memory_hook": "am/is/are + V-ing = đang... ngay bây giờ!",
  "icon": "🎥",
  "rules": [
    {
      "title": "FORM — Cấu trúc",
      "formula": "S + am/is/are + V-ing",
      "explanation": "Động từ 'to be' (am/is/are) thay đổi theo chủ ngữ, sau đó là động từ chính thêm -ing.",
      "memory_hook": "I AM, He/She/It IS, You/We/They ARE → luôn cộng V-ing",
      "is_exception": False,
      "order": 1,
      "grammar_table": {
        "headers": [
          "Chủ ngữ",
          "To be",
          "V-ing",
          "Ví dụ"
        ],
        "rows": [
          [
            "I",
            "am",
            "working",
            "I am working now."
          ],
          [
            "He / She / It",
            "is",
            "eating",
            "She is eating lunch."
          ],
          [
            "You / We / They",
            "are",
            "playing",
            "They are playing football."
          ],
          [
            "Phủ định",
            "am/is/are + not",
            "V-ing",
            "I am not sleeping."
          ],
          [
            "Câu hỏi",
            "Am/Is/Are + S",
            "V-ing?",
            "Are you listening?"
          ]
        ]
      },
      "examples": [
        {
          "sentence": "I am reading a book right now.",
          "translation": "Tôi đang đọc sách ngay lúc này.",
          "highlight": "am reading",
          "is_correct": True
        },
        {
          "sentence": "She is cooking dinner.",
          "translation": "Cô ấy đang nấu bữa tối.",
          "highlight": "is cooking",
          "is_correct": True
        },
        {
          "sentence": "They are not watching TV.",
          "translation": "Họ không đang xem TV.",
          "highlight": "are not watching",
          "is_correct": True
        },
        {
          "sentence": "Is he working from home today?",
          "translation": "Hôm nay anh ấy có đang làm việc tại nhà không?",
          "highlight": "Is ... working",
          "is_correct": True
        }
      ]
    },
    {
      "title": "Quy tắc thêm -ing",
      "formula": "V + ing | V-e → drop e + ing | short V → double consonant + ing",
      "explanation": "(1) Hầu hết: thêm -ing. (2) Kết thúc -e: bỏ e, thêm -ing. (3) Động từ 1 âm tiết kết thúc phụ âm-nguyên âm-phụ âm: nhân đôi phụ âm cuối.",
      "memory_hook": "make→making (bỏ e) | run→running (nhân đôi n) | play→playing (không thay đổi)",
      "is_exception": False,
      "order": 2,
      "grammar_table": {
        "headers": [
          "Trường hợp",
          "Quy tắc",
          "Ví dụ"
        ],
        "rows": [
          [
            "Hầu hết động từ",
            "+ ing",
            "eat→eating, work→working"
          ],
          [
            "Kết thúc -e",
            "bỏ e + ing",
            "make→making, write→writing"
          ],
          [
            "1 âm tiết, kết thúc C-V-C",
            "nhân đôi C + ing",
            "run→running, sit→sitting"
          ],
          [
            "Kết thúc -ie",
            "ie → y + ing",
            "lie→lying, die→dying"
          ]
        ]
      },
      "examples": [
        {
          "sentence": "He is running in the park.",
          "translation": "Anh ấy đang chạy trong công viên.",
          "highlight": "running",
          "is_correct": True
        },
        {
          "sentence": "We are making pizza tonight.",
          "translation": "Chúng tôi đang làm pizza tối nay.",
          "highlight": "making",
          "is_correct": True
        },
        {
          "sentence": "She is lieing on the beach.",
          "translation": "Cô ấy đang nằm trên bãi biển. ❌",
          "highlight": "lieing",
          "is_correct": False
        }
      ]
    },
    {
      "title": "USAGE — Khi nào dùng Present Continuous",
      "formula": "Đang xảy ra | Tạm thời | Kế hoạch tương lai gần",
      "explanation": "(1) Hành động đang xảy ra tại thời điểm nói. (2) Tình huống tạm thời (không phải thường xuyên). (3) Kế hoạch đã sắp xếp trong tương lai gần.",
      "memory_hook": "NOW, AT THE MOMENT, THESE DAYS → Present Continuous",
      "is_exception": False,
      "order": 3,
      "grammar_table": {
        "headers": [
          "Cách dùng",
          "Ví dụ"
        ],
        "rows": [
          [
            "Đang xảy ra lúc nói",
            "Be quiet! The baby is sleeping."
          ],
          [
            "Tạm thời (không thường xuyên)",
            "I'm living with my parents this month."
          ],
          [
            "Kế hoạch tương lai gần",
            "We are meeting Tom tomorrow."
          ]
        ]
      },
      "examples": [
        {
          "sentence": "Be quiet! The baby is sleeping.",
          "translation": "Im lặng! Em bé đang ngủ.",
          "highlight": "is sleeping",
          "is_correct": True
        },
        {
          "sentence": "I'm staying at a hotel this week.",
          "translation": "Tuần này tôi đang ở khách sạn. (tạm thời)",
          "highlight": "am staying",
          "is_correct": True
        },
        {
          "sentence": "She is flying to London next Monday.",
          "translation": "Cô ấy sẽ bay đến London vào thứ Hai tới. (kế hoạch)",
          "highlight": "is flying",
          "is_correct": True
        }
      ]
    }
  ],
  "signal_words": [
    "now",
    "right now",
    "at the moment",
    "currently",
    "at present",
    "today",
    "this week",
    "this month",
    "these days",
    "Look!",
    "Listen!"
  ],
  "common_mistakes": [
    {
      "wrong": "I am know the answer.",
      "correct": "I know the answer.",
      "explanation": "Động từ trạng thái (know, love, want, need, see, hear...) KHÔNG dùng -ing."
    },
    {
      "wrong": "She is work at home.",
      "correct": "She is working at home.",
      "explanation": "Sau am/is/are phải dùng V-ing, không phải V-base."
    },
    {
      "wrong": "They are play football.",
      "correct": "They are playing football.",
      "explanation": "Phải thêm -ing vào động từ trong Present Continuous."
    },
    {
      "wrong": "Are you liking this movie?",
      "correct": "Do you like this movie?",
      "explanation": "'Like' là động từ trạng thái, không dùng Continuous."
    }
  ],
  "notes": [
    {
      "type": "warning",
      "text": "ĐỘNG TỪ TRẠNG THÁI không dùng -ing: know, believe, want, need, love, hate, like, see, hear, smell, taste, have (sở hữu), own, belong."
    },
    {
      "type": "tip",
      "text": "'I'm always losing my keys!' — dùng always với Continuous để diễn tả thói quen gây khó chịu/ngạc nhiên."
    },
    {
      "type": "info",
      "text": "Dạng rút gọn thông dụng: I'm, he's/she's/it's, we're/you're/they're."
    }
  ]
},
{
  "level": "A1",
  "title": "So Sánh: Present Simple vs Continuous",
  "slug": "present-simple-vs-continuous",
  "order": 3,
  "chapter": "Present tenses",
  "description": "Phân biệt khi nào dùng thì Hiện Tại Đơn và khi nào dùng thì Hiện Tại Tiếp Diễn.",
  "analogy": "Simple như ảnh chụp (sự kiện thường xuyên/cố định), Continuous như video quay (đang diễn ra ngay lúc này).",
  "real_world_use": "Tránh nhầm lẫn giữa hai thì — đây là lỗi phổ biến nhất của người học tiếng Anh.",
  "memory_hook": "EVERY DAY = Simple | RIGHT NOW = Continuous",
  "icon": "⚖️",
  "rules": [
    {
      "title": "So Sánh Trực Tiếp",
      "formula": "Simple: thói quen/luôn đúng | Continuous: đang diễn ra/tạm thời",
      "explanation": "Hai thì này thường bị nhầm lẫn. Điểm mấu chốt: Simple nói về điều thường xảy ra hoặc luôn đúng; Continuous nói về điều đang xảy ra tại thời điểm nói hoặc chỉ tạm thời.",
      "memory_hook": "Simple = bức tranh toàn cảnh. Continuous = cảnh quay đặc tả.",
      "is_exception": False,
      "order": 1,
      "grammar_table": {
        "headers": [
          "",
          "Present Simple",
          "Present Continuous"
        ],
        "rows": [
          [
            "Khi dùng",
            "Thói quen, sự thật, trạng thái",
            "Đang xảy ra, tạm thời, kế hoạch"
          ],
          [
            "Ví dụ (làm việc)",
            "She works at a bank.",
            "She is working from home today."
          ],
          [
            "Ví dụ (sống)",
            "They live in Hanoi.",
            "They are living with friends now."
          ],
          [
            "Ví dụ (đọc)",
            "I read books every evening.",
            "I am reading a novel right now."
          ],
          [
            "Tín hiệu",
            "every day, always, usually",
            "now, at the moment, today"
          ]
        ]
      },
      "examples": [
        {
          "sentence": "I work at a hospital. / I am working overtime tonight.",
          "translation": "Tôi làm việc ở bệnh viện. / Tối nay tôi đang làm thêm giờ.",
          "highlight": "work / am working",
          "is_correct": True
        },
        {
          "sentence": "Water boils at 100°C.",
          "translation": "Nước sôi ở 100°C. (sự thật khoa học → Simple)",
          "highlight": "boils",
          "is_correct": True
        },
        {
          "sentence": "Look! It is raining.",
          "translation": "Nhìn kìa! Trời đang mưa. (đang xảy ra → Continuous)",
          "highlight": "is raining",
          "is_correct": True
        }
      ]
    },
    {
      "title": "Động từ trạng thái — Chỉ dùng Simple",
      "formula": "know / understand / believe / want / need / love / hate / see / hear / have (possess)",
      "explanation": "Một số động từ biểu thị trạng thái tinh thần, cảm xúc, hoặc giác quan không dùng được ở dạng Continuous. Chúng luôn ở Present Simple ngay cả khi đang đúng ở thời điểm nói.",
      "memory_hook": "Cảm xúc và nhận thức không 'diễn ra' — chúng tồn tại liên tục.",
      "is_exception": True,
      "order": 2,
      "grammar_table": {
        "headers": [
          "Loại",
          "Động từ"
        ],
        "rows": [
          [
            "Nhận thức",
            "know, understand, remember, forget, believe, think (= believe)"
          ],
          [
            "Cảm xúc",
            "love, hate, like, prefer, want, need, wish"
          ],
          [
            "Giác quan",
            "see, hear, smell, taste, feel (= think)"
          ],
          [
            "Sở hữu",
            "have, own, belong, contain, include"
          ]
        ]
      },
      "examples": [
        {
          "sentence": "I know the answer.",
          "translation": "Tôi biết câu trả lời. ✓",
          "highlight": "know",
          "is_correct": True
        },
        {
          "sentence": "I am knowing the answer.",
          "translation": "❌ Sai — 'know' không dùng -ing",
          "highlight": "am knowing",
          "is_correct": False
        },
        {
          "sentence": "She wants a new phone.",
          "translation": "Cô ấy muốn một chiếc điện thoại mới. ✓",
          "highlight": "wants",
          "is_correct": True
        },
        {
          "sentence": "Do you understand the question?",
          "translation": "Bạn có hiểu câu hỏi không? ✓",
          "highlight": "understand",
          "is_correct": True
        }
      ]
    }
  ],
  "signal_words": [
    "every day (S)",
    "always (S)",
    "usually (S)",
    "now (C)",
    "right now (C)",
    "at the moment (C)",
    "today (C)",
    "this week (C)",
    "currently (C)",
    "these days (C)"
  ],
  "common_mistakes": [
    {
      "wrong": "I am wanting a coffee.",
      "correct": "I want a coffee.",
      "explanation": "'Want' là state verb, không dùng -ing."
    },
    {
      "wrong": "She is knowing how to cook.",
      "correct": "She knows how to cook.",
      "explanation": "'Know' là state verb, luôn dùng Present Simple."
    },
    {
      "wrong": "He work in an office at the moment.",
      "correct": "He is working in an office at the moment.",
      "explanation": "'At the moment' là tín hiệu của Continuous."
    }
  ],
  "notes": [
    {
      "type": "tip",
      "text": "Một số động từ có thể là state verb hoặc action verb tùy ngữ cảnh: 'I think he is right.' (= believe, Simple) vs 'I am thinking about you.' (= đang suy nghĩ, Continuous)."
    },
    {
      "type": "info",
      "text": "'Have' làm state verb = sở hữu (I have a car). 'Have' làm action verb = Continuous được (I am having lunch / I am having a shower)."
    }
  ]
},
{
  "level": "A1",
  "title": "Have Got",
  "slug": "have-got",
  "order": 6,
  "chapter": "Present tenses",
  "description": "Cách dùng 'have got' để nói về sở hữu, đặc điểm và mối quan hệ — phổ biến trong tiếng Anh Anh.",
  "analogy": "Have got = have (British English flavour). Giống nhau về nghĩa, khác nhau về cách dùng.",
  "real_world_use": "Thường được nghe trong tiếng Anh Anh, đặc biệt trong hội thoại hàng ngày.",
  "memory_hook": "I've got = I have. She's got = She has.",
  "icon": "🤝",
  "rules": [
    {
      "title": "FORM — Cấu trúc",
      "formula": "I/You/We/They + have got | He/She/It + has got",
      "explanation": "Have got dùng 'have' hoặc 'has' (ngôi thứ ba số ít) cộng 'got'. Phủ định: haven't got / hasn't got. Câu hỏi: Have you got...? / Has she got...?",
      "memory_hook": "'ve got = have got (dạng rút gọn thông dụng trong giao tiếp)",
      "is_exception": False,
      "order": 1,
      "grammar_table": {
        "headers": [
          "Chủ ngữ",
          "Khẳng định",
          "Phủ định",
          "Câu hỏi"
        ],
        "rows": [
          [
            "I",
            "I have got / I've got",
            "I haven't got",
            "Have I got?"
          ],
          [
            "You",
            "You have got / You've got",
            "You haven't got",
            "Have you got?"
          ],
          [
            "He/She/It",
            "He has got / He's got",
            "He hasn't got",
            "Has he got?"
          ],
          [
            "We/They",
            "We have got / We've got",
            "We haven't got",
            "Have we got?"
          ]
        ]
      },
      "examples": [
        {
          "sentence": "I've got two sisters.",
          "translation": "Tôi có hai chị gái.",
          "highlight": "I've got",
          "is_correct": True
        },
        {
          "sentence": "She has got brown eyes.",
          "translation": "Cô ấy có đôi mắt nâu.",
          "highlight": "has got",
          "is_correct": True
        },
        {
          "sentence": "Have you got a pen?",
          "translation": "Bạn có bút không?",
          "highlight": "Have you got",
          "is_correct": True
        },
        {
          "sentence": "He hasn't got a car.",
          "translation": "Anh ấy không có xe.",
          "highlight": "hasn't got",
          "is_correct": True
        }
      ]
    },
    {
      "title": "USAGE — Have got vs Have",
      "formula": "Have got = Have (sở hữu, đặc điểm, quan hệ)",
      "explanation": "Have got và have có nghĩa tương đương khi nói về sở hữu. Have got phổ biến hơn trong tiếng Anh Anh (British), have phổ biến hơn trong tiếng Anh Mỹ. Have got KHÔNG dùng cho thói quen hoặc trải nghiệm.",
      "memory_hook": "Anh Anh: have got. Mỹ: have. Cả hai đều đúng!",
      "is_exception": False,
      "order": 2,
      "grammar_table": {
        "headers": [
          "Cách dùng",
          "Have got",
          "Have"
        ],
        "rows": [
          [
            "Sở hữu",
            "I've got a new phone.",
            "I have a new phone."
          ],
          [
            "Đặc điểm",
            "She's got long hair.",
            "She has long hair."
          ],
          [
            "Quan hệ gia đình",
            "He's got two brothers.",
            "He has two brothers."
          ],
          [
            "Bệnh/triệu chứng",
            "I've got a headache.",
            "I have a headache."
          ]
        ]
      },
      "examples": [
        {
          "sentence": "We've got a big garden.",
          "translation": "Chúng tôi có một khu vườn rộng.",
          "highlight": "We've got",
          "is_correct": True
        },
        {
          "sentence": "Has she got any brothers or sisters?",
          "translation": "Cô ấy có anh chị em không?",
          "highlight": "Has she got",
          "is_correct": True
        },
        {
          "sentence": "I've got a cold today.",
          "translation": "Hôm nay tôi bị cảm.",
          "highlight": "I've got",
          "is_correct": True
        }
      ]
    }
  ],
  "signal_words": [
    "a car",
    "a house",
    "blue eyes",
    "long hair",
    "two brothers",
    "a headache",
    "any money",
    "some time"
  ],
  "common_mistakes": [
    {
      "wrong": "She have got a cat.",
      "correct": "She has got a cat.",
      "explanation": "Ngôi thứ ba số ít dùng 'has got', không phải 'have got'."
    },
    {
      "wrong": "Do you have got a pen?",
      "correct": "Have you got a pen?",
      "explanation": "Câu hỏi với 'have got' dùng đảo 'have/has' lên đầu, không dùng 'do/does'."
    },
    {
      "wrong": "I have got usually breakfast at 7.",
      "correct": "I usually have breakfast at 7.",
      "explanation": "'Have got' không dùng cho thói quen. Dùng 'have' + Present Simple."
    }
  ],
  "notes": [
    {
      "type": "info",
      "text": "Have got là cấu trúc Present Perfect về hình thức nhưng nghĩa = Present Simple (sở hữu). Không có past tense 'had got' trong văn viết trang trọng."
    },
    {
      "type": "tip",
      "text": "Trong văn nói thân mật: 'I've got a problem.' Trong văn viết trang trọng: 'I have a problem.'"
    }
  ]
},
]
