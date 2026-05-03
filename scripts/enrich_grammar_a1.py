"""
Enrich grammar_A1.json — Present tenses chapter (11 topics)
Adds: analogy, memory_hook, real_world_use, signal_words, common_mistakes, notes,
      rule formula/explanation, example translation/highlight/is_correct, grammar_table.

Run: python scripts/enrich_grammar_a1.py
"""
import json
from pathlib import Path

FIXTURE = Path(__file__).parent / "grammar_fixtures" / "grammar_A1.json"

# ─────────────────────────────────────────────────────────────────────────────
# PATCH DATA per slug
# Each entry overrides specific fields on the topic and its rules/examples.
# Keys in "rules_patch" are matched by rule order (1-based).
# ─────────────────────────────────────────────────────────────────────────────
PATCHES = {

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 1: The present simple of be: Form
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-the-present-simple-of-be-form": {
        "description": "Động từ 'be' (am/is/are) là động từ quan trọng nhất trong tiếng Anh. Nó có 3 dạng ở thì hiện tại:\n‣ I am (I'm)\n‣ He/She/It is (He's/She's/It's)\n‣ We/You/They are (We're/You're/They're)",
        "analogy": "Hãy coi động từ 'be' như dấu bằng (=) trong toán học: nó nối chủ từ với thông tin về họ. 'She IS beautiful' = 'She = beautiful'. Ai dùng am/is/are? Nhớ như ABC: A=Am (chỉ I), B-C=Is/Are (he/she/it/we/you/they).",
        "memory_hook": "🎵 I AM, He/She/It IS, còn lại đều ARE — nhớ vần: I-am-1, is-3, are-the-rest!",
        "real_world_use": "Dùng mỗi ngày khi giới thiệu bản thân, mô tả người/vật, nói về nghề nghiệp, tuổi, quốc tịch, cảm xúc. Đây là cấu trúc câu nền tảng nhất của tiếng Anh.",
        "signal_words": ["am", "is", "are", "I'm", "he's", "she's", "it's", "we're", "you're", "they're"],
        "common_mistakes": [
            {
                "wrong": "She are a doctor.",
                "correct": "She is a doctor.",
                "explanation": "He/She/It (số ít) luôn dùng 'is', không dùng 'are'."
            },
            {
                "wrong": "They is my friends.",
                "correct": "They are my friends.",
                "explanation": "They (số nhiều) luôn dùng 'are', không dùng 'is'."
            },
            {
                "wrong": "Is cold today.",
                "correct": "It is cold today.",
                "explanation": "Câu tiếng Anh luôn cần chủ từ. Dùng 'it' cho thời tiết, thời gian, nhiệt độ."
            },
            {
                "wrong": "Yes, I'm.",
                "correct": "Yes, I am.",
                "explanation": "Câu trả lời ngắn khẳng định KHÔNG dùng dạng rút gọn. Chỉ dùng rút gọn trong câu phủ định (No, I'm not)."
            }
        ],
        "notes": [
            {
                "type": "tip",
                "text": "Dạng rút gọn ('m/'s/'re) rất phổ biến trong giao tiếp hàng ngày và văn viết không trang trọng."
            },
            {
                "type": "warning",
                "text": "Không dùng dạng rút gọn trong câu trả lời ngắn khẳng định: 'Are you tired?' → 'Yes, I am.' (KHÔNG phải 'Yes, I'm.')"
            },
            {
                "type": "info",
                "text": "'s có thể là rút gọn của 'is' hoặc dấu sở hữu. Phân biệt qua ngữ cảnh: 'She's beautiful' (is) vs 'Laura's car' (sở hữu)."
            }
        ],
        "rules_patch": {
            1: {
                "formula": "He/She/It (người/vật số ít) + IS | We/You/They (số nhiều) + ARE",
                "explanation": "Dùng 'he' cho nam, 'she' cho nữ, 'it' cho đồ vật/con vật. Dùng 'they' cho cả người lẫn đồ vật số nhiều.",
                "examples": [
                    {"sentence": "We use he for a man, she for a woman, and it for a thing.", "translation": "Dùng 'he' cho nam, 'she' cho nữ, 'it' cho đồ vật.", "highlight": "he, she, it", "is_correct": True},
                    {"sentence": "He's a little boy.", "translation": "Cậu ấy là một cậu bé.", "highlight": "He's", "is_correct": True},
                    {"sentence": "I like this TV. It's very big.", "translation": "Tôi thích chiếc TV này. Nó rất lớn.", "highlight": "It's", "is_correct": True},
                    {"sentence": "We use they for people and for things.", "translation": "Dùng 'they' cho cả người lẫn đồ vật số nhiều.", "highlight": "they", "is_correct": True},
                    {"sentence": "I love Sara and Jonas. They are my friends.", "translation": "Tôi yêu thích Sara và Jonas. Họ là bạn của tôi.", "highlight": "They are", "is_correct": True},
                    {"sentence": "I love these chairs. They are very beautiful.", "translation": "Tôi thích những chiếc ghế này. Chúng rất đẹp.", "highlight": "They are", "is_correct": True},
                ]
            },
            2: {
                "formula": "Subject (I/He/She/It/We/You/They) + am/is/are + ...",
                "explanation": "Tiếng Anh LUÔN cần chủ từ đứng trước động từ. Không được bỏ chủ từ như tiếng Việt.",
                "examples": [
                    {"sentence": "We always need a subject before the verb.", "translation": "Tiếng Anh luôn cần chủ từ đứng trước động từ.", "highlight": "subject", "is_correct": True},
                    {"sentence": "It is cold.", "translation": "Trời lạnh. (dùng 'it' làm chủ từ giả)", "highlight": "It is", "is_correct": True},
                    {"sentence": "Sally is a wonderful woman.", "translation": "Sally là một người phụ nữ tuyệt vời.", "highlight": "Sally is", "is_correct": True},
                    {"sentence": "Is a wonderful woman.", "translation": "❌ SAI — thiếu chủ từ!", "highlight": "", "is_correct": False},
                ]
            },
            3: {
                "formula": "I'm | He's/She's/It's | We're/You're/They're",
                "explanation": "Dùng dạng rút gọn ('m/'s/'re) với đại từ nhân xưng (I, you, he...). Cũng có thể dùng 's với tên riêng.",
                "grammar_table": {
                    "headers": ["Dạng đầy đủ", "Dạng rút gọn", "Ví dụ"],
                    "rows": [
                        ["I am", "I'm", "I'm sad."],
                        ["He/She/It is", "He's / She's / It's", "She's from Scotland."],
                        ["We/You/They are", "We're / You're / They're", "They're students."],
                        ["[Tên riêng] is", "[Tên]'s", "Laura's beautiful."],
                    ]
                },
                "examples": [
                    {"sentence": "I'm sad.", "translation": "Tôi buồn.", "highlight": "I'm", "is_correct": True},
                    {"sentence": "She's from Scotland.", "translation": "Cô ấy đến từ Scotland.", "highlight": "She's", "is_correct": True},
                    {"sentence": "Laura's beautiful.", "translation": "Laura thật xinh đẹp.", "highlight": "Laura's", "is_correct": True},
                    {"sentence": "London's an expensive city.", "translation": "London là một thành phố đắt đỏ.", "highlight": "London's", "is_correct": True},
                ]
            },
            4: {
                "formula": "YES: Yes, I am. / Yes, she is. — NO: No, I'm not. / No, she isn't.",
                "explanation": "Câu trả lời ngắn khẳng định KHÔNG rút gọn. Câu phủ định được rút gọn.",
                "examples": [
                    {"sentence": "We can only use contractions in negative short answers, not in positive short answers.", "translation": "Chỉ dùng dạng rút gọn trong câu trả lời ngắn PHỦ ĐỊNH.", "highlight": "negative", "is_correct": True},
                    {"sentence": "Yes, I am.", "translation": "Vâng, đúng vậy. (KHÔNG viết 'Yes, I'm')", "highlight": "Yes, I am", "is_correct": True},
                    {"sentence": "Yes, she is.", "translation": "Vâng, đúng vậy. (KHÔNG viết 'Yes, she's')", "highlight": "Yes, she is", "is_correct": True},
                    {"sentence": "Yes, they are.", "translation": "Vâng, đúng vậy.", "highlight": "Yes, they are", "is_correct": True},
                    {"sentence": "No, I'm not.", "translation": "Không, không phải.", "highlight": "I'm not", "is_correct": True},
                    {"sentence": "No, she isn't.", "translation": "Không, không phải.", "highlight": "isn't", "is_correct": True},
                ]
            }
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 2: The present simple of be – USE
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-the-present-simple-of-be-use": {
        "description": "Chúng ta dùng động từ 'be' để nói về: danh tính, tuổi tác, nghề nghiệp, quốc tịch, cảm xúc, màu sắc, giá cả, thời tiết, thời gian và mô tả chung.",
        "analogy": "Hãy nghĩ 'be' như chiếc nhãn dán: nó gán nhãn/thông tin cho chủ từ. 'She IS a teacher' = dán nhãn 'teacher' lên 'she'.",
        "memory_hook": "Be = BEschreiben (mô tả). Dùng khi muốn 'dán nhãn' hoặc 'mô tả' ai/cái gì.",
        "real_world_use": "Đây là cấu trúc bạn dùng ngay từ lần đầu nói chuyện với người nước ngoài: 'I'm from Vietnam. I'm 25. I'm a student.'",
        "signal_words": ["job:", "nationality:", "age:", "feelings:", "weather:", "price:", "time:"],
        "notes": [
            {"type": "info", "text": "Động từ 'be' là verbe irrégulier (bất quy tắc) — không thêm -s/-es như các động từ thông thường."},
            {"type": "tip", "text": "Khi mô tả thời tiết, nhiệt độ, thời gian: luôn dùng 'It is...' (it's cold, it's 9 o'clock, it's 30 degrees)."}
        ],
        "rules_patch": {
            1: {
                "title": "Identity & personal info",
                "formula": "S + am/is/are + [tên/tuổi/nghề nghiệp/quốc tịch/...]",
                "explanation": "Dùng 'be' để giới thiệu bản thân, nói về tuổi, nghề nghiệp, quốc tịch.",
                "grammar_table": {
                    "headers": ["Chủ đề", "Công thức", "Ví dụ"],
                    "rows": [
                        ["Danh tính", "I'm + tên", "I'm Steven."],
                        ["Tuổi tác", "I'm + số + years old", "I'm 24 years old."],
                        ["Nghề nghiệp", "I'm a/an + nghề", "She's a doctor."],
                        ["Quốc tịch", "He's from + nơi chốn", "Alex is from Ireland."],
                        ["Cảm xúc", "I'm + adj cảm xúc", "I'm scared."],
                        ["Màu sắc/mô tả", "It's + màu/tính từ", "Our dog is black."],
                        ["Giá cả", "It's + giá", "It's seven pounds."],
                        ["Thời tiết", "It's + adj thời tiết", "It's sunny today."],
                        ["Thời gian", "It's + giờ", "It's ten past four."]
                    ]
                },
                "examples": [
                    {"sentence": "I'm Steven, and this is Isabella.", "translation": "Tôi là Steven, và đây là Isabella.", "highlight": "I'm", "is_correct": True},
                    {"sentence": "I'm 24 years old, and my father is 50.", "translation": "Tôi 24 tuổi, và bố tôi 50 tuổi.", "highlight": "24 years old", "is_correct": True},
                    {"sentence": "I'm a teacher, and my wife is a doctor.", "translation": "Tôi là giáo viên, và vợ tôi là bác sĩ.", "highlight": "a teacher", "is_correct": True},
                    {"sentence": "Alex is from Ireland.", "translation": "Alex đến từ Ireland.", "highlight": "from Ireland", "is_correct": True},
                    {"sentence": "I'm scared. She is very tired.", "translation": "Tôi sợ. Cô ấy rất mệt.", "highlight": "scared", "is_correct": True},
                    {"sentence": "It's seven pounds. This T-shirt is twenty dollars.", "translation": "Nó giá 7 bảng Anh. Chiếc áo này giá 20 đô.", "highlight": "seven pounds", "is_correct": True},
                    {"sentence": "It's sunny today. It is very cold this morning.", "translation": "Hôm nay trời nắng. Sáng nay trời rất lạnh.", "highlight": "It's sunny", "is_correct": True},
                    {"sentence": "What time is it? It's ten past four.", "translation": "Mấy giờ rồi? Bây giờ là bốn giờ mười.", "highlight": "ten past four", "is_correct": True},
                ]
            }
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 3: Present simple form
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-present-simple-form": {
        "description": "Thì hiện tại đơn có 2 dạng chính: khẳng định (I work), phủ định (I don't work), và nghi vấn (Do you work?). Với he/she/it, dùng does/doesn't.",
        "analogy": "Hiện tại đơn như lập lịch hàng ngày — những việc bạn làm theo thói quen, lặp đi lặp lại.",
        "memory_hook": "Do/Does là 'trợ lý' của động từ chính. Do = I/you/we/they, Does = he/she/it. Khi dùng does, động từ chính KHÔNG thêm -s nữa.",
        "real_world_use": "Dùng khi nói về thói quen, sở thích, sự thật hiển nhiên. 'I work from 9 to 5.' 'She likes coffee.' 'The Earth orbits the Sun.'",
        "signal_words": ["every day", "every week", "always", "usually", "often", "sometimes", "never", "on Mondays"],
        "common_mistakes": [
            {
                "wrong": "She don't like coffee.",
                "correct": "She doesn't like coffee.",
                "explanation": "He/She/It dùng 'doesn't' (không phải 'don't') + động từ nguyên mẫu."
            },
            {
                "wrong": "Does she likes coffee?",
                "correct": "Does she like coffee?",
                "explanation": "Khi đã có 'does', động từ chính KHÔNG thêm -s. Does + V (bare infinitive)."
            }
        ],
        "notes": [
            {"type": "tip", "text": "He/She/It: thêm -s vào cuối động từ ở dạng khẳng định. Nhưng 'does' đã mang -s rồi nên câu hỏi/phủ định động từ không thêm -s."},
            {"type": "warning", "text": "Các động từ đặc biệt: go → goes, do → does, have → has, watch → watches, study → studies."}
        ],
        "rules_patch": {
            1: {
                "title": "Full conjugation table — Present Simple",
                "formula": "[I/You/We/They + V] / [He/She/It + V-s/es]",
                "explanation": "Động từ thêm -s/-es ở ngôi thứ 3 số ít (he/she/it). Câu phủ định và nghi vấn dùng do/does + V (nguyên mẫu).",
                "grammar_table": {
                    "headers": ["Dạng câu", "I/You/We/They", "He/She/It"],
                    "rows": [
                        ["Khẳng định (+)", "I work / You play", "He works / She plays"],
                        ["Phủ định (−)", "I don't work", "He doesn't work"],
                        ["Nghi vấn (?)", "Do you work?", "Does she work?"],
                        ["Trả lời ngắn", "Yes, I do. / No, I don't.", "Yes, she does. / No, she doesn't."]
                    ]
                },
                "examples": [
                    {"sentence": "I work in a bank.", "translation": "Tôi làm việc ở ngân hàng.", "highlight": "work", "is_correct": True},
                    {"sentence": "She works in a hospital.", "translation": "Cô ấy làm việc ở bệnh viện.", "highlight": "works", "is_correct": True},
                    {"sentence": "I don't drink coffee.", "translation": "Tôi không uống cà phê.", "highlight": "don't drink", "is_correct": True},
                    {"sentence": "He doesn't like pizza.", "translation": "Anh ấy không thích pizza.", "highlight": "doesn't like", "is_correct": True},
                    {"sentence": "Do you live in Hanoi?", "translation": "Bạn có sống ở Hà Nội không?", "highlight": "Do you live", "is_correct": True},
                    {"sentence": "Does she speak English?", "translation": "Cô ấy có nói tiếng Anh không?", "highlight": "Does she speak", "is_correct": True},
                ]
            },
            2: {
                "title": "Spelling rules for he/she/it (-s/-es/-ies)",
                "formula": "Verb + s | Verb ending in -ch/-sh/-x/-o + es | Consonant + y → -ies",
                "explanation": "Hầu hết động từ chỉ thêm -s. Nhưng một số cần thêm -es hoặc đổi -y thành -ies.",
                "grammar_table": {
                    "headers": ["Quy tắc", "Ví dụ"],
                    "rows": [
                        ["Thêm -s (đa số)", "work → works, play → plays, run → runs"],
                        ["Thêm -es (sau -ch/-sh/-x/-o)", "watch → watches, wash → washes, go → goes, do → does"],
                        ["Consonant + y → -ies", "study → studies, carry → carries, fly → flies"],
                        ["Vowel + y → +s", "play → plays, say → says, buy → buys"],
                        ["Bất quy tắc", "have → has, be → is"]
                    ]
                },
                "examples": [
                    {"sentence": "She watches TV every evening.", "translation": "Tối nào cô ấy cũng xem TV.", "highlight": "watches", "is_correct": True},
                    {"sentence": "He studies English at university.", "translation": "Anh ấy học tiếng Anh tại trường đại học.", "highlight": "studies", "is_correct": True},
                    {"sentence": "The train goes to London.", "translation": "Chuyến tàu đi đến London.", "highlight": "goes", "is_correct": True},
                ]
            }
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 4: Present simple use
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-present-simple-use": {
        "description": "Thì hiện tại đơn dùng để nói về: thói quen hoặc hành động lặp đi lặp lại, tình huống vĩnh cửu hoặc sự thật chung, và các trạng từ tần suất.",
        "analogy": "Hiện tại đơn như 'bản mô tả cuộc sống thường ngày' — những gì bạn làm theo lịch, theo thói quen, hoặc những điều luôn đúng.",
        "memory_hook": "Hỏi: 'Việc này có phải thói quen/sự thật vĩnh cửu không?' → Có = dùng hiện tại đơn!",
        "real_world_use": "Khi kể về cuộc sống hàng ngày: 'I wake up at 7. I take the bus to work. I eat lunch at noon.'",
        "signal_words": ["every day", "every week", "every morning", "always", "usually", "often", "sometimes", "rarely", "never", "on Mondays", "once a week", "twice a month"],
        "common_mistakes": [
            {
                "wrong": "I am going to school every day.",
                "correct": "I go to school every day.",
                "explanation": "Thói quen hàng ngày dùng hiện tại đơn, KHÔNG dùng hiện tại tiếp diễn. Continuous = hành động đang xảy ra ngay lúc nói."
            }
        ],
        "notes": [
            {"type": "tip", "text": "Hiện tại đơn diễn tả THÓI QUEN (habit) và TÌNH TRẠNG VĨNH CỬU (permanent state). Không dùng cho hành động đang diễn ra."},
            {"type": "info", "text": "Sự thật khoa học và quy luật tự nhiên cũng dùng hiện tại đơn: 'The Earth orbits the Sun.' 'Water freezes at 0°C.'"}
        ],
        "rules_patch": {
            1: {
                "formula": "Subject + V(s) + [every day / on Mondays / always / ...]",
                "explanation": "Dùng hiện tại đơn cho thói quen hoặc hành động lặp đi lặp lại thường xuyên.",
                "examples": [
                    {"sentence": "I wash my hair every day.", "translation": "Ngày nào tôi cũng gội đầu.", "highlight": "every day", "is_correct": True},
                    {"sentence": "I never go to the library.", "translation": "Tôi không bao giờ đến thư viện.", "highlight": "never", "is_correct": True},
                    {"sentence": "I go to the library on Saturdays.", "translation": "Thứ Bảy nào tôi cũng đến thư viện.", "highlight": "on Saturdays", "is_correct": True},
                    {"sentence": "She usually drinks coffee in the morning.", "translation": "Thường thì cô ấy uống cà phê vào buổi sáng.", "highlight": "usually", "is_correct": True},
                ]
            },
            2: {
                "formula": "Subject + V(s) [sự thật/tình trạng vĩnh cửu]",
                "explanation": "Dùng hiện tại đơn cho tình huống lâu dài/vĩnh cửu hoặc sự thật luôn đúng (sự thật khoa học, quy luật tự nhiên).",
                "examples": [
                    {"sentence": "I don't drink coffee.", "translation": "Tôi không uống cà phê. (thói quen/sở thích cá nhân)", "highlight": "don't drink", "is_correct": True},
                    {"sentence": "She's very tall.", "translation": "Cô ấy rất cao. (đặc điểm vĩnh viễn)", "highlight": "tall", "is_correct": True},
                    {"sentence": "I have two brothers.", "translation": "Tôi có hai anh/em trai.", "highlight": "have", "is_correct": True},
                    {"sentence": "Water boils at 100 degrees.", "translation": "Nước sôi ở 100 độ C. (sự thật khoa học)", "highlight": "boils at 100 degrees", "is_correct": True},
                    {"sentence": "I like soup.", "translation": "Tôi thích súp. (sở thích cá nhân)", "highlight": "like", "is_correct": True},
                ]
            },
            3: {
                "formula": "Frequency adverb + V [always/usually/often/sometimes/rarely/never]",
                "explanation": "Trạng từ tần suất (always, usually, often, sometimes, rarely, never) đứng TRƯỚC động từ thường nhưng SAU động từ 'be'.",
                "grammar_table": {
                    "headers": ["Trạng từ", "Nghĩa", "Ví dụ"],
                    "rows": [
                        ["always (100%)", "luôn luôn", "I always brush my teeth."],
                        ["usually (80%)", "thường thường", "She usually takes the bus."],
                        ["often (60%)", "thường xuyên", "We often eat pizza on Fridays."],
                        ["sometimes (40%)", "đôi khi", "He sometimes works late."],
                        ["rarely (20%)", "hiếm khi", "I rarely watch TV."],
                        ["never (0%)", "không bao giờ", "They never drink alcohol."]
                    ]
                },
                "examples": [
                    {"sentence": "We usually order a pizza on Fridays.", "translation": "Thứ Sáu nào chúng tôi cũng thường đặt pizza.", "highlight": "usually", "is_correct": True},
                    {"sentence": "I go running twice a week.", "translation": "Tôi đi chạy bộ 2 lần một tuần.", "highlight": "twice a week", "is_correct": True},
                    {"sentence": "She is always late for work.", "translation": "Cô ấy luôn đi làm trễ. (always sau 'is')", "highlight": "always late", "is_correct": True},
                ]
            },
            4: {
                "title": "Stative verbs (NOT used in continuous)",
                "formula": "Stative verb [like/love/hate/know/have/want/need...] + KHÔNG bao giờ dùng -ing",
                "explanation": "Một số động từ mô tả trạng thái (KHÔNG phải hành động) — gọi là stative verbs. Chúng KHÔNG dùng ở thì tiếp diễn.",
                "examples": [
                    {"sentence": "They have a new car.", "translation": "Họ có một chiếc xe mới. ✓", "highlight": "have", "is_correct": True},
                    {"sentence": "They are having a new car.", "translation": "❌ Sai — 'have' (sở hữu) là stative verb", "highlight": "are having", "is_correct": False},
                    {"sentence": "I like chocolate.", "translation": "Tôi thích sô cô la. ✓", "highlight": "like", "is_correct": True},
                    {"sentence": "I'm liking chocolate.", "translation": "❌ Sai — 'like' là stative verb", "highlight": "I'm liking", "is_correct": False},
                ]
            }
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 5: Present continuous: Form
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-present-continuous-form": {
        "description": "Thì hiện tại tiếp diễn được tạo thành bằng am/is/are + V-ing. Dùng để mô tả hành động đang xảy ra ngay lúc nói hoặc đang diễn ra trong thời gian gần đây.",
        "analogy": "Hiện tại tiếp diễn như một 'bức ảnh' chụp lại khoảnh khắc đang xảy ra — giống như bạn đang quay video trực tiếp.",
        "memory_hook": "am/is/are + V-ING = đang làm gì ĐÓ LÀ NGAY BÂY GIỜ! Nhớ -ing là 'đang'.",
        "real_world_use": "Dùng khi mô tả điều đang xảy ra ngay lúc nhắn tin/gọi điện: 'What are you doing?' 'I'm watching Netflix.' 'I'm studying for my exam.'",
        "signal_words": ["now", "right now", "at the moment", "at present", "today", "these days", "this week", "this month", "currently", "Look!", "Listen!"],
        "common_mistakes": [
            {
                "wrong": "I am study English.",
                "correct": "I am studying English.",
                "explanation": "Sau am/is/are PHẢI là V-ing (thêm -ing vào động từ), không dùng động từ nguyên mẫu."
            },
            {
                "wrong": "She is likeing music.",
                "correct": "She likes music. (NOT continuous — stative verb)",
                "explanation": "'like' là stative verb — KHÔNG dùng ở thì tiếp diễn."
            },
            {
                "wrong": "Are you writing a book? Yes, I'm.",
                "correct": "Are you writing a book? Yes, I am.",
                "explanation": "Câu trả lời ngắn khẳng định KHÔNG rút gọn."
            }
        ],
        "notes": [
            {"type": "tip", "text": "Spelling V-ing: Nếu động từ kết thúc bằng consonant đơn + nguyên âm đơn: nhân đôi consonant rồi thêm -ing. VD: run → running, swim → swimming, sit → sitting."},
            {"type": "warning", "text": "Nếu động từ kết thúc -e: bỏ -e rồi thêm -ing. VD: make → making, write → writing, dance → dancing."}
        ],
        "rules_patch": {
            1: {
                "title": "Full form and short forms",
                "formula": "Subject + am/is/are + V-ing",
                "explanation": "Khẳng định: am/is/are + V-ing. Phủ định: am not/isn't/aren't + V-ing. Nghi vấn: Am/Is/Are + subject + V-ing?",
                "grammar_table": {
                    "headers": ["Dạng câu", "Công thức", "Ví dụ"],
                    "rows": [
                        ["Khẳng định", "I am / She is / They are + V-ing", "I am writing. / She's listening. / They're working."],
                        ["Phủ định", "I'm not / She isn't / They aren't + V-ing", "I'm not writing. / She isn't listening."],
                        ["Nghi vấn", "Am I / Is she / Are they + V-ing?", "Are you writing? / Is she listening?"],
                        ["Trả lời (+)", "Yes, I am. / Yes, she is.", "KHÔNG viết 'Yes, I'm.'"],
                        ["Trả lời (−)", "No, I'm not. / No, she isn't.", "Dùng dạng rút gọn được."]
                    ]
                },
                "examples": [
                    {"sentence": "I am writing a book.", "translation": "Tôi đang viết một cuốn sách.", "highlight": "am writing", "is_correct": True},
                    {"sentence": "She is listening to the radio.", "translation": "Cô ấy đang nghe đài.", "highlight": "is listening", "is_correct": True},
                    {"sentence": "They are doing their homework.", "translation": "Họ đang làm bài tập về nhà.", "highlight": "are doing", "is_correct": True},
                    {"sentence": "I'm not writing a book.", "translation": "Tôi không đang viết sách.", "highlight": "I'm not writing", "is_correct": True},
                    {"sentence": "Are you writing a book? No, I'm not.", "translation": "Bạn có đang viết sách không? Không.", "highlight": "Are you writing", "is_correct": True},
                ]
            },
            2: {
                "title": "V-ing spelling rules",
                "formula": "Hầu hết: + ing | Kết thúc -e: bỏ e + ing | Consonant đơn sau nguyên âm đơn: nhân đôi + ing",
                "explanation": "Quy tắc đánh vần khi thêm -ing vào động từ.",
                "grammar_table": {
                    "headers": ["Quy tắc", "Ví dụ"],
                    "rows": [
                        ["Thêm -ing (đa số)", "work → working, play → playing, go → going"],
                        ["Bỏ -e rồi thêm -ing", "write → writing, make → making, dance → dancing"],
                        ["Nhân đôi consonant + ing", "run → running, swim → swimming, sit → sitting, get → getting"],
                        ["Không nhân đôi nếu -w/-x/-y", "show → showing, fix → fixing, play → playing"]
                    ]
                },
                "examples": [
                    {"sentence": "'What are you doing?' 'I'm watching TV.'", "translation": "'Bạn đang làm gì vậy?' 'Tôi đang xem TV.'", "highlight": "I'm watching", "is_correct": True},
                    {"sentence": "She's running in the park.", "translation": "Cô ấy đang chạy bộ trong công viên.", "highlight": "running", "is_correct": True},
                    {"sentence": "He's making dinner right now.", "translation": "Anh ấy đang nấu bữa tối ngay lúc này.", "highlight": "making", "is_correct": True},
                ]
            },
            3: {
                "title": "Signal words for present continuous",
                "formula": "now | right now | at the moment | these days | this week | Look! | Listen!",
                "explanation": "Những từ/cụm từ này thường đi kèm với hiện tại tiếp diễn.",
                "examples": [
                    {"sentence": "She's reading a book at the moment.", "translation": "Hiện tại cô ấy đang đọc sách.", "highlight": "at the moment", "is_correct": True},
                    {"sentence": "What TV series are you watching these days?", "translation": "Dạo này bạn đang xem bộ phim nào vậy?", "highlight": "these days", "is_correct": True},
                    {"sentence": "Listen! Someone is crying.", "translation": "Nghe kìa! Có ai đó đang khóc.", "highlight": "Listen!", "is_correct": True},
                    {"sentence": "I'm reading a very good book this week.", "translation": "Tuần này tôi đang đọc một cuốn sách rất hay.", "highlight": "this week", "is_correct": True},
                ]
            }
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 9: Present simple or continuous?
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-present-simple-or-continuous": {
        "description": "Hiểu sự khác biệt giữa hiện tại đơn (thói quen/vĩnh cửu) và hiện tại tiếp diễn (đang xảy ra/tạm thời) là một trong những điểm ngữ pháp quan trọng nhất ở trình độ A1-B1.",
        "analogy": "Hiện tại đơn = ẢNH CHÂN DUNG (portrait) — mô tả bạn là ai, bạn thường làm gì. Hiện tại tiếp diễn = ẢNH HÀNH ĐỘNG (action shot) — chụp bạn đang làm gì ngay lúc này.",
        "memory_hook": "ĐƠN = THƯỜNG XUYÊN (routine) | TIẾP DIỄN = ĐANG LÀM (right now / temporary)",
        "real_world_use": "'I work at Google.' (công việc thường xuyên — hiện tại đơn) vs 'I'm working from home today.' (tạm thời hôm nay — tiếp diễn)",
        "signal_words": ["[usually/always/often → đơn]", "[now/at the moment/today → tiếp diễn]"],
        "common_mistakes": [
            {
                "wrong": "I'm going to school every day.",
                "correct": "I go to school every day.",
                "explanation": "'Every day' là dấu hiệu thói quen → dùng hiện tại đơn, không dùng tiếp diễn."
            },
            {
                "wrong": "I work now.",
                "correct": "I'm working now.",
                "explanation": "'Now' là dấu hiệu đang xảy ra → dùng hiện tại tiếp diễn."
            }
        ],
        "notes": [
            {"type": "info", "text": "Một số động từ diễn đạt cả hai nghĩa: 'I have a car.' (sở hữu — đơn) vs 'I'm having lunch.' (đang ăn — tiếp diễn). 'Have' khi nghĩa là 'sở hữu' là stative, nhưng khi nghĩa là 'ăn/uống/tổ chức' thì dùng tiếp diễn được."}
        ],
        "rules_patch": {
            1: {
                "formula": "Thói quen/Permanent → Present Simple | Đang xảy ra/Temporary → Present Continuous",
                "explanation": "Hiện tại đơn: hành động lặp đi lặp lại hoặc tình trạng vĩnh cửu. Hiện tại tiếp diễn: hành động đang diễn ra ngay lúc nói.",
                "grammar_table": {
                    "headers": ["Tiêu chí", "Hiện tại Đơn", "Hiện tại Tiếp Diễn"],
                    "rows": [
                        ["Khi nào dùng?", "Thói quen, sự thật vĩnh cửu", "Đang diễn ra, tạm thời"],
                        ["Dấu hiệu", "always, every day, usually, never", "now, at the moment, these days"],
                        ["Công thức", "I work / She works", "I'm working / She's working"],
                        ["Ví dụ thói quen", "I listen to the radio. (= thói quen)", "—"],
                        ["Ví dụ đang làm", "—", "I'm listening to the radio. (= đang nghe)"],
                    ]
                },
                "examples": [
                    {"sentence": "I listen to the radio. (= I usually listen to the radio; it's a habit.)", "translation": "Tôi nghe đài. (= thói quen thường ngày)", "highlight": "listen", "is_correct": True},
                    {"sentence": "I'm listening to the radio. (= I'm doing it now.)", "translation": "Tôi đang nghe đài. (= ngay lúc này)", "highlight": "I'm listening", "is_correct": True},
                    {"sentence": "I don't usually watch documentaries, but I'm watching one now.", "translation": "Thường tôi không xem phim tài liệu, nhưng lúc này tôi đang xem.", "highlight": "watching", "is_correct": True},
                ]
            },
            2: {
                "formula": "Permanent (lâu dài) → Simple | Temporary (tạm thời) → Continuous",
                "explanation": "Hiện tại đơn cho tình huống lâu dài/vĩnh cửu. Hiện tại tiếp diễn cho tình huống tạm thời (trong khoảng thời gian ngắn).",
                "examples": [
                    {"sentence": "I work in an office. (= Permanent — my regular job.)", "translation": "Tôi làm việc ở văn phòng. (công việc thường xuyên)", "highlight": "work", "is_correct": True},
                    {"sentence": "I'm working in an office. (= Temporary — maybe just this week.)", "translation": "Tôi đang làm việc ở văn phòng. (tạm thời, khoảng thời gian ngắn)", "highlight": "I'm working", "is_correct": True},
                    {"sentence": "I live in Hanoi. (= Permanent)", "translation": "Tôi sống ở Hà Nội. (thường trú)", "highlight": "live", "is_correct": True},
                    {"sentence": "I'm living in Hanoi. (= Temporary — just for now)", "translation": "Tôi đang ở Hà Nội. (tạm thời, không phải mãi mãi)", "highlight": "I'm living", "is_correct": True},
                ]
            },
            3: {
                "formula": "What do you do? (= job?) | What are you doing? (= right now?)",
                "explanation": "Hai câu hỏi này có nghĩa HOÀN TOÀN KHÁC NHAU. 'What do you do?' hỏi về nghề nghiệp. 'What are you doing?' hỏi về hành động ngay lúc này.",
                "examples": [
                    {"sentence": "What does Erik do?  → He's a teacher.", "translation": "Erik làm nghề gì?  → Anh ấy là giáo viên.", "highlight": "does Erik do", "is_correct": True},
                    {"sentence": "What is Erik doing? → He's making coffee.", "translation": "Erik đang làm gì vậy? → Anh ấy đang pha cà phê.", "highlight": "is Erik doing", "is_correct": True},
                ]
            }
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 10: Have got: Form
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-have-got-form": {
        "description": "'Have got' là cách diễn đạt phổ biến trong tiếng Anh Anh (British English) để nói về sự sở hữu. Tương đương 'have' trong tiếng Anh Mỹ.",
        "analogy": "'Have got' = 'have' (American). Giống như 'rubbish' (Anh) = 'trash' (Mỹ). Nếu bạn xem phim Anh, bạn sẽ nghe 'have got' rất nhiều.",
        "memory_hook": "Have got = have (sở hữu). 'I've got a car' = 'I have a car'. Nhưng CHỈ dùng ở hiện tại, không có dạng quá khứ 'had got'.",
        "real_world_use": "Trong hội thoại giới thiệu bản thân: 'Have you got any brothers or sisters?' 'Yes, I've got two sisters.'",
        "signal_words": ["I've got", "have you got", "hasn't got", "haven't got"],
        "common_mistakes": [
            {
                "wrong": "I had got a car last year.",
                "correct": "I had a car last year.",
                "explanation": "'Have got' CHỈ có dạng hiện tại. Quá khứ dùng 'had' (không phải 'had got')."
            },
            {
                "wrong": "She have got a dog.",
                "correct": "She has got a dog.",
                "explanation": "He/She/It dùng 'has got' (không phải 'have got')."
            }
        ],
        "notes": [
            {"type": "info", "text": "'Have got' CHỈ có nghĩa sở hữu (NOT eat/drink/take). 'I'm having lunch' = tôi đang ăn trưa (KHÔNG phải have got)."},
            {"type": "warning", "text": "'Have got' không có dạng quá khứ. Quá khứ dùng 'had' — không bao giờ 'had got'."}
        ],
        "rules_patch": {
            1: {
                "title": "Have got vs Have (British vs American English)",
                "formula": "I've got = I have | She's got = She has | Have you got? = Do you have?",
                "explanation": "'Have got' phổ biến trong tiếng Anh Anh (British English). 'Have' phổ biến trong tiếng Anh Mỹ (American English). Cả hai đều đúng và được chấp nhận.",
                "grammar_table": {
                    "headers": ["British English", "American English", "Nghĩa"],
                    "rows": [
                        ["I've got a car.", "I have a car.", "Tôi có xe."],
                        ["She's got a dog.", "She has a dog.", "Cô ấy có chó."],
                        ["I haven't got a car.", "I don't have a car.", "Tôi không có xe."],
                        ["Have you got a car?", "Do you have a car?", "Bạn có xe không?"],
                        ["Yes, I have.", "Yes, I do.", "Có, tôi có."]
                    ]
                },
                "examples": [
                    {"sentence": "I've got a car. = I have a car.", "translation": "Tôi có ô tô.", "highlight": "I've got", "is_correct": True},
                    {"sentence": "I haven't got a car. = I don't have a car.", "translation": "Tôi không có ô tô.", "highlight": "haven't got", "is_correct": True},
                    {"sentence": "Have you got a car? = Do you have a car?", "translation": "Bạn có ô tô không?", "highlight": "Have you got", "is_correct": True},
                ]
            },
            2: {
                "title": "Have got: Present ONLY (no past form!)",
                "formula": "✓ Present: I've got / She's got | ✗ Past: I had (NOT 'I had got')",
                "explanation": "'Have got' chỉ tồn tại ở hiện tại. Ở quá khứ, dùng 'had' (American & British). KHÔNG bao giờ viết 'had got'.",
                "examples": [
                    {"sentence": "I had got a car.", "translation": "❌ SAI — 'had got' không tồn tại", "highlight": "had got", "is_correct": False},
                    {"sentence": "I had a car.", "translation": "✓ Tôi đã có ô tô. (quá khứ dùng 'had')", "highlight": "had", "is_correct": True},
                    {"sentence": "She had got a dog.", "translation": "❌ SAI", "highlight": "had got", "is_correct": False},
                    {"sentence": "She had a dog.", "translation": "✓ Cô ấy đã có chó.", "highlight": "had", "is_correct": True},
                ]
            }
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Topic 11: Have got: Use
    # ═══════════════════════════════════════════════════════════════════════════
    "a1-have-got-use": {
        "description": "'Have got' dùng để nói về sự sở hữu: đồ vật, đặc điểm cơ thể, mối quan hệ gia đình, bệnh tật.",
        "analogy": "'Have got' = 'có'. Bạn dùng nó mỗi khi muốn nói bạn 'có' gì đó — vật chất hoặc đặc điểm.",
        "memory_hook": "Have got = CÓ (sở hữu). Hỏi: 'Tôi CÓ cái này không?' → Dùng 'have got'!",
        "real_world_use": "'Have you got any ID?' 'I've got a headache.' 'She's got blue eyes.' — Rất thông dụng trong hội thoại hàng ngày.",
        "signal_words": ["a/an", "any", "some"],
        "notes": [
            {"type": "tip", "text": "'Have got' dùng για sở hữu — vật chất (car, house), đặc điểm (blue eyes, curly hair), bệnh tật (headache, fever), gia đình (two sisters, a dog)."}
        ],
        "rules_patch": {
            1: {
                "title": "Uses of have got",
                "formula": "S + have/has got + [noun/adjective]",
                "explanation": "'Have got' dùng để nói về sở hữu đồ vật, đặc điểm bên ngoài, bệnh tật, và các mối quan hệ.",
                "grammar_table": {
                    "headers": ["Cách dùng", "Ví dụ", "Tiếng Việt"],
                    "rows": [
                        ["Đồ vật sở hữu", "I've got a new phone.", "Tôi có điện thoại mới."],
                        ["Đặc điểm cơ thể", "She's got brown eyes.", "Cô ấy có mắt màu nâu."],
                        ["Gia đình/bạn bè", "He's got two brothers.", "Anh ấy có hai anh/em."],
                        ["Bệnh tật", "I've got a headache.", "Tôi bị đau đầu."],
                        ["Đồ vật với you/we", "Have you got a pen?", "Bạn có bút không?"]
                    ]
                },
                "examples": [
                    {"sentence": "I've got a new car.", "translation": "Tôi có xe mới.", "highlight": "I've got", "is_correct": True},
                    {"sentence": "She's got long, dark hair.", "translation": "Cô ấy có mái tóc dài đen.", "highlight": "She's got", "is_correct": True},
                    {"sentence": "They've got three children.", "translation": "Họ có ba đứa con.", "highlight": "They've got", "is_correct": True},
                    {"sentence": "He hasn't got a driving licence.", "translation": "Anh ấy không có bằng lái xe.", "highlight": "hasn't got", "is_correct": True},
                    {"sentence": "Have you got any brothers or sisters?", "translation": "Bạn có anh chị em không?", "highlight": "Have you got", "is_correct": True},
                ]
            }
        }
    },
}


def enrich_topic(topic: dict, patch: dict) -> dict:
    """Apply a patch dict to a topic dict."""
    # Top-level fields
    for field in ["description", "analogy", "memory_hook", "real_world_use",
                  "signal_words", "common_mistakes", "notes"]:
        if field in patch:
            topic[field] = patch[field]

    # Rules patch
    rules_patch = patch.get("rules_patch", {})
    if not rules_patch:
        return topic

    for rule in topic.get("rules", []):
        order = rule.get("order", 0)
        rp = rules_patch.get(order)
        if not rp:
            continue
        for field in ["title", "formula", "explanation", "memory_hook", "grammar_table", "is_exception"]:
            if field in rp:
                rule[field] = rp[field]
        # Replace examples entirely if provided
        if "examples" in rp:
            rule["examples"] = rp["examples"]

    return topic


def main():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    patched = 0
    for topic in data["topics"]:
        slug = topic.get("slug", "")
        if slug in PATCHES:
            enrich_topic(topic, PATCHES[slug])
            patched += 1
            print(f"  ✓ Patched: {topic['title']}")

    FIXTURE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone! Patched {patched} topics in {FIXTURE}")


if __name__ == "__main__":
    main()
