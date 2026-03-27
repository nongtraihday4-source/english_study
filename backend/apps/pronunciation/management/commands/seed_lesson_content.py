"""
Management command: seed_lesson_content
Populates LessonSection rows for all published PhonemeLesson objects.

Usage:
    python manage.py seed_lesson_content          # skip existing, re-seed all
    python manage.py seed_lesson_content --clear  # delete all sections first, then re-seed
    python manage.py seed_lesson_content --slug vowel-ae  # seed only one lesson
"""

from django.core.management.base import BaseCommand

from apps.pronunciation.models import LessonSection, PhonemeLesson

# ─────────────────────────────────────────────────────────────────────────────
# Content data (identical to scripts/seed_lesson_content.py)
# ─────────────────────────────────────────────────────────────────────────────

PHONEME_OVERRIDES = {
    "consonant-l": {
        "explanation": (
            "Âm /l/ có 2 dạng quan trọng: light L (đầu từ: light, late) và dark L (cuối từ: fall, well). "
            "Đặt đầu lưỡi chạm nhẹ vào lợi trên, giữ luồng hơi đi qua hai bên lưỡi."
        ),
        "tip": (
            "Người Việt thường làm /l/ quá nặng hoặc chuyển thành âm gần /n/. Hãy giữ đầu lưỡi ổn định ở lợi trên "
            "và tách rõ light L (đầu từ) với dark L (cuối từ)."
        ),
        "common_mistakes": (
            "1. Phát âm /l/ như /n/ (nhầm lẫn phụ âm Việt).\n"
            "2. Bỏ dark L ở cuối từ (fall → 'faw').\n"
            "3. Không giữ đầu lưỡi ở đúng vị trí lợi trên."
        ),
        "examples": [
            {"word": "light",  "ipa": "/laɪt/",  "meaning": "ánh sáng",       "sentence": "Turn on the light."},
            {"word": "late",   "ipa": "/leɪt/",  "meaning": "muộn",           "sentence": "Don't be late."},
            {"word": "fall",   "ipa": "/fɔːl/",  "meaning": "mùa thu / ngã",  "sentence": "Leaves fall in autumn."},
            {"word": "well",   "ipa": "/wel/",   "meaning": "tốt / giếng",    "sentence": "She speaks English well."},
            {"word": "blue",   "ipa": "/bluː/",  "meaning": "màu xanh",       "sentence": "The sky is blue."},
            {"word": "glass",  "ipa": "/ɡlɑːs/", "meaning": "cốc thủy tinh", "sentence": "A glass of water."},
        ],
    },
    "consonant-ng": {
        "explanation": (
            "Âm /ŋ/ là âm mũi cổ họng — lưỡi chạm vào vòm mềm (soft palate) phía sau miệng, "
            "KHÔNG mở miệng. Khác với /n/ (đầu lưỡi chạm lợi trên)."
        ),
        "tip": (
            "Thử nói 'singing' — cảm nhận rung ở cổ họng, không phải ở mũi hay môi. "
            "Người Việt thường thêm /g/ ở cuối nghe như /ŋg/."
        ),
        "common_mistakes": (
            "1. Thêm âm /g/ sau /ŋ/: 'sing' → 'sing-g'.\n"
            "2. Thay /ŋ/ bằng /n/: 'long' → 'lon'.\n"
            "3. Bỏ âm cuối hoàn toàn: 'running' → 'runnin'."
        ),
        "examples": [
            {"word": "sing",    "ipa": "/sɪŋ/",     "meaning": "hát",          "sentence": "I love to sing."},
            {"word": "long",    "ipa": "/lɒŋ/",     "meaning": "dài",          "sentence": "It's a long road."},
            {"word": "running", "ipa": "/ˈrʌnɪŋ/", "meaning": "đang chạy",   "sentence": "She is running."},
            {"word": "thing",   "ipa": "/θɪŋ/",     "meaning": "thứ gì đó",   "sentence": "What a strange thing."},
            {"word": "strong",  "ipa": "/strɒŋ/",   "meaning": "mạnh mẽ",     "sentence": "He is very strong."},
            {"word": "English", "ipa": "/ˈɪŋɡlɪʃ/","meaning": "tiếng Anh",  "sentence": "I study English."},
        ],
    },
    "consonant-sh-zh": {
        "explanation": (
            "Âm /ʃ/ (she, shop) — môi tròn, lưỡi tiến gần vòm cứng, hơi thoát ra mạnh.\n"
            "Âm /ʒ/ (measure, vision) — giống /ʃ/ nhưng có rung thanh quản."
        ),
        "tip": (
            "Để phân biệt: đặt tay lên cổ họng. /ʃ/ không rung, /ʒ/ rung nhẹ. "
            "Người Việt thường thay /ʃ/ bằng /s/ và bỏ /ʒ/ hoàn toàn."
        ),
        "common_mistakes": (
            "1. /ʃ/ → /s/: 'ship' nghe như 'sip'.\n"
            "2. /ʒ/ → /z/ hoặc /j/: 'measure' nghe sai.\n"
            "3. Không tròn môi khi phát âm /ʃ/."
        ),
        "examples": [
            {"word": "she",     "ipa": "/ʃiː/",      "meaning": "cô ấy",       "sentence": "She is my friend."},
            {"word": "shop",    "ipa": "/ʃɒp/",      "meaning": "cửa hàng",   "sentence": "Let's go to the shop."},
            {"word": "fish",    "ipa": "/fɪʃ/",      "meaning": "con cá",     "sentence": "I like fish."},
            {"word": "measure", "ipa": "/ˈmeʒə/",   "meaning": "đo lường",    "sentence": "Measure the room."},
            {"word": "vision",  "ipa": "/ˈvɪʒən/",  "meaning": "tầm nhìn",   "sentence": "She has great vision."},
            {"word": "usually", "ipa": "/ˈjuːʒuəli/","meaning":"thường thì",  "sentence": "I usually wake up early."},
        ],
    },
    "diphthong-ai": {
        "explanation": (
            "Âm đôi /aɪ/ bắt đầu từ /a/ (miệng mở rộng) rồi trượt lên /ɪ/ (miệng hẹp lại). "
            "Xuất hiện trong: my, time, night, high, buy."
        ),
        "tip": (
            "Chú ý: /aɪ/ là âm trượt — bắt đầu ở vị trí thấp, kết thúc ở vị trí cao. "
            "Người Việt thường phát âm quá ngắn hoặc như /a/ đơn."
        ),
        "common_mistakes": (
            "1. Phát âm như /a/ thuần: 'time' → 'tam'.\n"
            "2. Không trượt đủ lên /ɪ/: âm nghe thiếu.\n"
            "3. Nhầm với /eɪ/: 'my' → 'may'."
        ),
        "examples": [
            {"word": "my",    "ipa": "/maɪ/",   "meaning": "của tôi",   "sentence": "This is my book."},
            {"word": "time",  "ipa": "/taɪm/",  "meaning": "thời gian", "sentence": "What time is it?"},
            {"word": "night", "ipa": "/naɪt/",  "meaning": "đêm",       "sentence": "Good night."},
            {"word": "high",  "ipa": "/haɪ/",   "meaning": "cao",       "sentence": "The mountain is high."},
            {"word": "buy",   "ipa": "/baɪ/",   "meaning": "mua",       "sentence": "I want to buy this."},
            {"word": "sky",   "ipa": "/skaɪ/",  "meaning": "bầu trời",  "sentence": "The sky is clear."},
        ],
    },
    "diphthong-oi": {
        "explanation": (
            "Âm đôi /ɔɪ/ bắt đầu từ /ɔː/ (miệng tròn, lưỡi thấp) rồi trượt lên /ɪ/. "
            "Xuất hiện trong: boy, coin, voice, enjoy."
        ),
        "tip": (
            "Cảm nhận miệng tròn ở đầu âm rồi mở rộng sang phải khi trượt. "
            "Người Việt thường phát âm quá nhẹ hay như /oi/ Việt."
        ),
        "common_mistakes": (
            "1. Không tròn môi ở phần đầu /ɔ/.\n"
            "2. Âm quá ngắn, không đủ độ trượt.\n"
            "3. Nhầm với /aɪ/: 'boy' → 'buy'."
        ),
        "examples": [
            {"word": "boy",    "ipa": "/bɔɪ/",    "meaning": "cậu bé",     "sentence": "The boy is smart."},
            {"word": "coin",   "ipa": "/kɔɪn/",   "meaning": "đồng tiền",  "sentence": "A gold coin."},
            {"word": "voice",  "ipa": "/vɔɪs/",   "meaning": "giọng nói",  "sentence": "She has a lovely voice."},
            {"word": "enjoy",  "ipa": "/ɪnˈdʒɔɪ/","meaning": "thích thú", "sentence": "Enjoy the music."},
            {"word": "oil",    "ipa": "/ɔɪl/",    "meaning": "dầu",        "sentence": "Add some oil."},
            {"word": "choice", "ipa": "/tʃɔɪs/",  "meaning": "lựa chọn",  "sentence": "Make a choice."},
        ],
    },
    "diphthong-ou": {
        "explanation": (
            "Âm đôi /aʊ/ bắt đầu từ /a/ rồi trượt lên /ʊ/ (môi tròn lại). "
            "Xuất hiện trong: now, out, house, brown, cloud."
        ),
        "tip": (
            "Miệng mở to ở đầu rồi tròn lại như thổi nến ở cuối. "
            "Người Việt hay phát âm /aʊ/ ngắn hoặc nhầm với /oʊ/ (go, home)."
        ),
        "common_mistakes": (
            "1. Không tròn môi đủ ở phần /ʊ/ cuối.\n"
            "2. Nhầm /aʊ/ với /oʊ/: 'out' → 'oat'.\n"
            "3. Phát âm quá ngắn như /a/ đơn."
        ),
        "examples": [
            {"word": "now",   "ipa": "/naʊ/",    "meaning": "bây giờ",   "sentence": "Do it now."},
            {"word": "out",   "ipa": "/aʊt/",    "meaning": "ra ngoài",  "sentence": "Get out."},
            {"word": "house", "ipa": "/haʊs/",   "meaning": "ngôi nhà",  "sentence": "This is my house."},
            {"word": "brown", "ipa": "/braʊn/",  "meaning": "màu nâu",   "sentence": "A brown bear."},
            {"word": "cloud", "ipa": "/klaʊd/",  "meaning": "đám mây",  "sentence": "Look at the cloud."},
            {"word": "loud",  "ipa": "/laʊd/",   "meaning": "to, ồn ào", "sentence": "The music is loud."},
        ],
    },
}

ADVANCED_CONTENT = {
    "linking-cv": {
        "explanation": (
            "Nối âm Consonant → Vowel (C+V Linking): Khi một từ kết thúc bằng phụ âm và từ tiếp theo bắt đầu "
            "bằng nguyên âm, hai âm hợp thành một khối nghe tự nhiên.\n\n"
            "Ví dụ: 'pick it up' → /ˈpɪk.ɪt.ʌp/ → nghe như 'pi-ki-tup'.\n"
            "Quy tắc: Final consonant + initial vowel = merged syllable."
        ),
        "examples": [
            {"phrase": "not at all",     "connected_form": "no-ta-tall",  "ipa": "/nɒ.tə.tɔːl/",    "explanation": "t cuối 'not' nối ngay với 'at'"},
            {"phrase": "pick it up",     "connected_form": "pi-ki-tup",   "ipa": "/ˈpɪ.kɪ.tʌp/",   "explanation": "k nối vào 'it', t nối vào 'up'"},
            {"phrase": "come on",        "connected_form": "co-mon",      "ipa": "/kəˈmɒn/",        "explanation": "m cuối 'come' hòa vào 'on'"},
            {"phrase": "an apple",       "connected_form": "a-napple",    "ipa": "/ə.ˈnæ.pl/",      "explanation": "n của 'an' nối với 'apple'"},
            {"phrase": "sit on it",      "connected_form": "si-to-nit",   "ipa": "/ˈsɪ.tɒ.nɪt/",   "explanation": "3 từ nối thành chuỗi"},
            {"phrase": "get out",        "connected_form": "ge-tout",     "ipa": "/ɡɛ.ˈtaʊt/",      "explanation": "t cuối nối vào 'out'"},
            {"phrase": "hold on",        "connected_form": "hol-don",     "ipa": "/ˈhəʊl.dɒn/",     "explanation": "d cuối 'hold' nối vào 'on'"},
        ],
        "practice": [
            {"text": "turn it off",      "hint": "r → i → t → o"},
            {"text": "look at me",       "hint": "k → a (merge)"},
            {"text": "take off",         "hint": "k → o (merge)"},
            {"text": "wake up",          "hint": "k → u (merge)"},
            {"text": "stand up",         "hint": "d → u (merge)"},
        ],
        "quiz": [
            {"audio_text": "not at all",    "question": "Cách nối âm nào đúng?",
             "options": ["no-tat-all", "no-ta-tall", "not-at-all", "nota-tall"],  "answer": "no-ta-tall"},
            {"audio_text": "pick it up",    "question": "Nghe và chọn cách đọc tự nhiên nhất:",
             "options": ["pick-it-up", "pi-ki-tup", "pickit-up", "pi-kit-up"],   "answer": "pi-ki-tup"},
            {"audio_text": "come on",       "question": "Chuỗi nối âm C+V:",
             "options": ["come-on", "co-mon", "com-eon", "co-me-on"],            "answer": "co-mon"},
            {"audio_text": "an apple",      "question": "Âm /n/ nối vào từ nào?",
             "options": ["an → apple (a-napple)", "an → apple (an-apple)", "a → napple", "none"],
             "answer": "an → apple (a-napple)"},
        ],
    },
    "weak-forms": {
        "explanation": (
            "Weak Forms (dạng yếu): Trong lời nói tự nhiên, các function words (a, an, the, to, for, and, "
            "but, can, have, was, were, do…) thường được nói ở dạng rút gọn với nguyên âm /ə/ (schwa).\n\n"
            "Strong form (khi nhấn mạnh): /fɔːr/ → Weak form (bình thường): /fə/\n"
            "Strong form: /ænd/ → Weak form: /ən/ hoặc /n/"
        ),
        "examples": [
            {"phrase": "for you",     "connected_form": "fə-you",   "ipa": "/fə ˈjuː/",    "explanation": "'for' yếu → /fə/"},
            {"phrase": "and me",      "connected_form": "ən-me",    "ipa": "/ən ˈmiː/",    "explanation": "'and' yếu → /ən/"},
            {"phrase": "to the park", "connected_form": "tə-thə-park","ipa": "/tə ðə ˈpɑːk/","explanation": "'to'→/tə/, 'the'→/ðə/"},
            {"phrase": "can you",     "connected_form": "kən-you",  "ipa": "/kən ˈjuː/",   "explanation": "'can' yếu → /kən/"},
            {"phrase": "I have been", "connected_form": "I-həv-been","ipa": "/aɪ həv ˈbɪn/","explanation": "'have' yếu → /həv/"},
            {"phrase": "was she",     "connected_form": "wəz-she",  "ipa": "/wəz ˈʃiː/",   "explanation": "'was' yếu → /wəz/"},
            {"phrase": "some coffee", "connected_form": "səm-coffee","ipa": "/səm ˈkɒfi/",  "explanation": "'some' yếu → /səm/"},
        ],
        "practice": [
            {"text": "Can you help me?",        "hint": "can → /kən/"},
            {"text": "I'm going to study.",      "hint": "to → /tə/"},
            {"text": "She was at home.",         "hint": "was → /wəz/"},
            {"text": "It's for the class.",      "hint": "for → /fə/, the → /ðə/"},
            {"text": "He has been working.",     "hint": "has → /həz/, been → /bɪn/"},
        ],
        "quiz": [
            {"audio_text": "Can you come?",   "question": "Dạng yếu của 'can' là gì?",
             "options": ["/kæn/", "/kən/", "/kin/", "/keɪn/"],   "answer": "/kən/"},
            {"audio_text": "for the team",    "question": "Chọn cách phát âm tự nhiên:",
             "options": ["for-the-team", "fə-ðə-team", "fo-the-team", "fər-the-team"], "answer": "fə-ðə-team"},
            {"audio_text": "I was there",     "question": "Dạng yếu của 'was' là:",
             "options": ["/wɒz/", "/wəz/", "/wɑːz/", "/wʌz/"],  "answer": "/wəz/"},
            {"audio_text": "and then",        "question": "Dạng yếu của 'and' phổ biến nhất:",
             "options": ["/ænd/", "/ɛnd/", "/ən/", "/ɑːnd/"],    "answer": "/ən/"},
        ],
    },
    "reduction": {
        "explanation": (
            "Reduction (rút gọn âm tiết): Trong connected speech, nhiều từ bị rút gọn hoàn toàn:\n"
            "• gonna = going to\n• wanna = want to\n• gotta = got to\n"
            "• kinda = kind of\n• outta = out of\n• shoulda = should have\n\n"
            "Đây là đặc trưng của tiếng Anh thông tục, hiểu để nghe chuẩn dù không cần lạm dụng khi viết."
        ),
        "examples": [
            {"phrase": "going to",  "connected_form": "gonna",  "ipa": "/ˈɡʌnə/",  "explanation": "going to → gonna (informal)"},
            {"phrase": "want to",   "connected_form": "wanna",  "ipa": "/ˈwɒnə/",  "explanation": "want to → wanna"},
            {"phrase": "got to",    "connected_form": "gotta",  "ipa": "/ˈɡɒtə/",  "explanation": "got to → gotta"},
            {"phrase": "kind of",   "connected_form": "kinda",  "ipa": "/ˈkaɪndə/","explanation": "kind of → kinda"},
            {"phrase": "out of",    "connected_form": "outta",  "ipa": "/ˈaʊtə/",  "explanation": "out of → outta"},
            {"phrase": "should have","connected_form":"shoulda", "ipa": "/ˈʃʊdə/", "explanation": "should have → shoulda"},
            {"phrase": "because",   "connected_form": "'cause",  "ipa": "/kəz/",    "explanation": "because → 'cause (rất phổ biến)"},
        ],
        "practice": [
            {"text": "I'm gonna call you later.",   "hint": "gonna = going to"},
            {"text": "I wanna learn English.",       "hint": "wanna = want to"},
            {"text": "You gotta try this.",          "hint": "gotta = got to"},
            {"text": "It's kinda difficult.",        "hint": "kinda = kind of"},
            {"text": "I shoulda studied more.",      "hint": "shoulda = should have"},
        ],
        "quiz": [
            {"audio_text": "I'm gonna do it",   "question": "'gonna' là dạng rút gọn của:",
             "options": ["go to", "going to", "gone to", "got to"],              "answer": "going to"},
            {"audio_text": "I wanna sleep",     "question": "'wanna' tương đương:",
             "options": ["want to", "wanted to", "wanna to", "wanting"],         "answer": "want to"},
            {"audio_text": "You gotta try",     "question": "'gotta' rút gọn từ:",
             "options": ["got to", "go to", "gotten to", "got a"],               "answer": "got to"},
            {"audio_text": "kinda tired",       "question": "'kinda' nghĩa là:",
             "options": ["kind", "kind of", "kinda to", "kindly"],               "answer": "kind of"},
        ],
    },
}


def _extract_word_from_phoneme(ph):
    """Return the first example word for a Phoneme object (example_words is a JSONField)."""
    words = ph.example_words if isinstance(ph.example_words, list) else []
    if words:
        w = words[0]
        return {"word": w.get("word", ""), "ipa": w.get("ipa", ""),
                "meaning": w.get("meaning", ""), "sentence": w.get("sentence_example", w.get("sentence", ""))}
    return {"word": ph.symbol, "ipa": ph.symbol, "meaning": "", "sentence": ""}


def _build_generic_examples(lesson):
    rows = []
    for ph in lesson.phonemes.all():
        word_data = _extract_word_from_phoneme(ph)
        rows.append({
            "word": word_data["word"] or ph.symbol,
            "ipa": word_data["ipa"],
            "meaning": word_data["meaning"],
            "sentence": word_data["sentence"],
        })
    if not rows:
        rows = [{"word": lesson.slug, "ipa": "", "meaning": "", "sentence": ""}]
    return rows


def _build_quiz(examples, count=4):
    """Build a simple Listen-and-Choose quiz from example data."""
    import random
    words = [e.get("word", "") for e in examples if e.get("word")]
    if not words:
        return []
    questions = []
    for i, ex in enumerate(examples[:count]):
        word = ex.get("word", "")
        ipa = ex.get("ipa", "")
        meaning = ex.get("meaning", "")
        # Build distractors from the other words
        others = [w for w in words if w != word]
        random.shuffle(others)
        options = [word] + others[:3]
        random.shuffle(options)
        questions.append({
            "audio_text": word,
            "question": f"Nghe và chọn từ có âm đúng — nghĩa: '{meaning}'" if meaning else "Nghe và chọn từ đúng",
            "ipa": ipa,
            "options": options,
            "answer": word,
        })
    return questions


def create_sections_for_lesson(lesson):
    """Delete existing sections for a lesson and rebuild from content data."""
    LessonSection.objects.filter(lesson=lesson).delete()

    slug = lesson.slug
    stage_type = getattr(lesson.stage, "stage_type", "") if lesson.stage else ""
    sections = []

    # ── Advanced lessons ────────────────────────────────────────────────────
    if stage_type == "advanced":
        data = ADVANCED_CONTENT.get(slug)
        if not data:
            return 0

        sections.append(LessonSection(
            lesson=lesson, section_type="explanation", order=1,
            title="Giải thích", body=data["explanation"], items=[],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="examples", order=2,
            title="Ví dụ thực tế", body="", items=data["examples"],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="practice", order=3,
            title="Luyện tập", body="", items=data["practice"],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="quiz", order=4,
            title="Kiểm tra nhanh", body="", items=data["quiz"],
        ))

    # ── Priority phoneme overrides ──────────────────────────────────────────
    elif slug in PHONEME_OVERRIDES:
        data = PHONEME_OVERRIDES[slug]
        examples = data["examples"]

        sections.append(LessonSection(
            lesson=lesson, section_type="explanation", order=1,
            title="Cách phát âm", body=data.get("explanation", ""), items=[],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="tip", order=2,
            title="Mẹo ghi nhớ", body=data.get("tip", ""), items=[],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="examples", order=3,
            title="Từ ví dụ", body="", items=examples,
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="common_mistakes", order=4,
            title="Lỗi thường gặp", body=data.get("common_mistakes", ""), items=[],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="quiz", order=5,
            title="Kiểm tra nhanh", body="", items=_build_quiz(examples),
        ))

    # ── Generic phoneme lessons ─────────────────────────────────────────────
    else:
        phoneme_symbols = ", ".join(
            p.symbol for p in lesson.phonemes.all()
        ) or lesson.slug
        explanation = (
            f"Bài học này tập trung vào phát âm {phoneme_symbols}. "
            "Lắng nghe kỹ các ví dụ, chú ý vị trí lưỡi và hình dáng miệng."
        )
        tip = (
            "Lắng nghe từng từ ví dụ nhiều lần rồi đọc theo. "
            "Ghi âm lại giọng của bạn và so sánh với âm chuẩn."
        )
        examples = _build_generic_examples(lesson)

        sections.append(LessonSection(
            lesson=lesson, section_type="explanation", order=1,
            title="Cách phát âm", body=explanation, items=[],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="tip", order=2,
            title="Mẹo luyện tập", body=tip, items=[],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="examples", order=3,
            title="Từ ví dụ", body="", items=examples,
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="common_mistakes", order=4,
            title="Lỗi thường gặp",
            body="Phát âm không rõ vị trí lưỡi, bỏ âm cuối hoặc thay bằng âm Việt tương đương.",
            items=[],
        ))
        sections.append(LessonSection(
            lesson=lesson, section_type="quiz", order=5,
            title="Kiểm tra nhanh", body="", items=_build_quiz(examples),
        ))

    LessonSection.objects.bulk_create(sections)
    return len(sections)


class Command(BaseCommand):
    help = "Seed LessonSection content for all published PhonemeLesson objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete ALL LessonSection rows before re-seeding.",
        )
        parser.add_argument(
            "--slug",
            type=str,
            default=None,
            help="Seed only the lesson with this slug.",
        )

    def handle(self, *args, **options):
        if options["clear"] and not options["slug"]:
            count = LessonSection.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f"Deleted {count} existing sections."))

        queryset = (
            PhonemeLesson.objects.filter(is_published=True)
            .select_related("stage")
            .prefetch_related("phonemes")
            .order_by("stage__order", "order")
        )
        if options["slug"]:
            queryset = queryset.filter(slug=options["slug"])
            if not queryset.exists():
                self.stderr.write(self.style.ERROR(f"No published lesson found with slug '{options['slug']}'."))
                return

        total_sections = 0
        total_lessons = 0

        for lesson in queryset:
            n = create_sections_for_lesson(lesson)
            total_sections += n
            total_lessons += 1
            self.stdout.write(f"  Seeded {n:2d} sections  →  {lesson.slug}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone.  Lessons: {total_lessons}   Sections created: {total_sections}"
        ))
