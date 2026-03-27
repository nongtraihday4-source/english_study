"""
Seed structured lesson content for pronunciation lessons.

Run:
  python manage.py shell < scripts/seed_lesson_content.py
"""
import os
import sys

import django

# Allow running directly from backend/scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")
django.setup()

from apps.pronunciation.models import LessonSection, PhonemeLesson


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
            "Lỗi phổ biến: bỏ âm /l/ cuối từ (fall -> faw), hoặc thay /l/ bằng /n/ (light -> night). "
            "Cách sửa: kéo dài âm cuối 0.3-0.5 giây khi luyện từ có /l/ cuối."
        ),
        "examples": [
            {"word": "light", "ipa": "/laɪt/", "meaning": "ánh sáng", "sentence": "Turn on the light."},
            {"word": "late", "ipa": "/leɪt/", "meaning": "muộn", "sentence": "I am late for class."},
            {"word": "fall", "ipa": "/fɔːl/", "meaning": "ngã", "sentence": "Leaves fall in autumn."},
            {"word": "well", "ipa": "/wel/", "meaning": "tốt", "sentence": "You did very well."},
            {"word": "blue", "ipa": "/bluː/", "meaning": "màu xanh", "sentence": "My bag is blue."},
            {"word": "milk", "ipa": "/mɪlk/", "meaning": "sữa", "sentence": "I drink milk every morning."},
        ],
    },
    "consonant-ng": {
        "explanation": (
            "Âm /ŋ/ là âm mũi ngạc mềm (velar nasal). Phần sau lưỡi nâng lên chạm ngạc mềm, hơi thoát qua mũi. "
            "Trong tiếng Anh, /ŋ/ thường ở giữa hoặc cuối từ, gần như không đứng đầu từ."
        ),
        "tip": (
            "Đừng đọc /ŋ/ thành /n/ + /g/. Ví dụ sing là /sɪŋ/ (1 âm cuối), không phải /sɪn-g/. "
            "Hãy giữ miệng hơi mở và cảm nhận rung mũi ở cuối âm."
        ),
        "common_mistakes": (
            "Lỗi phổ biến: thêm /g/ sau /ŋ/ mọi lúc (song -> /sɒŋg/). Thực tế chỉ một số từ có cụm /ŋg/ thật, "
            "còn nhiều từ chỉ cần /ŋ/ thuần."
        ),
        "examples": [
            {"word": "sing", "ipa": "/sɪŋ/", "meaning": "hát", "sentence": "They sing together."},
            {"word": "song", "ipa": "/sɒŋ/", "meaning": "bài hát", "sentence": "This song is catchy."},
            {"word": "ring", "ipa": "/rɪŋ/", "meaning": "nhẫn", "sentence": "She wears a ring."},
            {"word": "long", "ipa": "/lɒŋ/", "meaning": "dài", "sentence": "It is a long road."},
            {"word": "young", "ipa": "/jʌŋ/", "meaning": "trẻ", "sentence": "He is very young."},
            {"word": "banking", "ipa": "/ˈbæŋkɪŋ/", "meaning": "ngành ngân hàng", "sentence": "She works in banking."},
        ],
    },
    "consonant-sh-zh": {
        "explanation": (
            "Cặp /ʃ/ và /ʒ/ có vị trí lưỡi gần giống nhau: lưỡi nâng nhẹ, môi hơi tròn. "
            "/ʃ/ là vô thanh (she), /ʒ/ là hữu thanh (measure) nên dây thanh quản rung."
        ),
        "tip": (
            "Đặt tay lên cổ họng: đọc /ʃ/ sẽ không rung, đọc /ʒ/ sẽ rung. "
            "Môi tròn nhẹ và giữ luồng hơi đều để âm không bị biến thành /s/ hoặc /z/."
        ),
        "common_mistakes": (
            "Lỗi phổ biến: đọc she thành /siː/ và measure thành /ˈmezə/. "
            "Cách sửa: luyện cặp tối thiểu ship-zip, pressure-pleasure để cảm nhận khác biệt."
        ),
        "examples": [
            {"word": "she", "ipa": "/ʃiː/", "meaning": "cô ấy", "sentence": "She is my friend."},
            {"word": "ship", "ipa": "/ʃɪp/", "meaning": "con tàu", "sentence": "The ship is big."},
            {"word": "wash", "ipa": "/wɒʃ/", "meaning": "rửa", "sentence": "Please wash your hands."},
            {"word": "measure", "ipa": "/ˈmeʒə/", "meaning": "đo lường", "sentence": "We measure the table."},
            {"word": "vision", "ipa": "/ˈvɪʒn/", "meaning": "tầm nhìn", "sentence": "The company has a clear vision."},
            {"word": "usual", "ipa": "/ˈjuːʒuəl/", "meaning": "thường lệ", "sentence": "It is a usual routine."},
        ],
    },
    "diphthong-ai": {
        "explanation": (
            "Âm /aɪ/ là nguyên âm đôi có chuyển động glide: bắt đầu mở ở /a/ rồi trượt lên /ɪ/. "
            "Hàm mở hơn ở đầu âm và khép nhẹ dần ở cuối âm."
        ),
        "tip": "Tránh đọc /aɪ/ thành /a/ đơn. Hãy kéo đường trượt rõ ràng: a...i trong my, fly, time.",
        "common_mistakes": "Lỗi phổ biến: đọc my gần như /ma/. Cách sửa: chia nhịp 2 phần khi luyện: /a/ + /ɪ/ rồi ghép lại.",
        "examples": [
            {"word": "my", "ipa": "/maɪ/", "meaning": "của tôi", "sentence": "This is my book."},
            {"word": "fly", "ipa": "/flaɪ/", "meaning": "bay", "sentence": "Birds fly high."},
            {"word": "time", "ipa": "/taɪm/", "meaning": "thời gian", "sentence": "Time goes fast."},
            {"word": "night", "ipa": "/naɪt/", "meaning": "đêm", "sentence": "Good night, everyone."},
            {"word": "find", "ipa": "/faɪnd/", "meaning": "tìm", "sentence": "I cannot find my keys."},
            {"word": "like", "ipa": "/laɪk/", "meaning": "thích", "sentence": "I like this song."},
        ],
    },
    "diphthong-oi": {
        "explanation": (
            "Âm /ɔɪ/ bắt đầu ở vị trí tròn môi của /ɔ/ rồi trượt lên /ɪ/. "
            "Đây là âm có độ tròn môi rõ ở phần đầu."
        ),
        "tip": "Khi đọc /ɔɪ/, hãy làm môi tròn ở đầu âm (o) rồi mở nhẹ để kết thúc ở (i).",
        "common_mistakes": "Lỗi phổ biến: đọc boy thành /boː/. Cách sửa: luyện theo nhịp /ɔ/ -> /ɪ/ thật rõ.",
        "examples": [
            {"word": "boy", "ipa": "/bɔɪ/", "meaning": "cậu bé", "sentence": "The boy is smiling."},
            {"word": "coin", "ipa": "/kɔɪn/", "meaning": "đồng xu", "sentence": "I found a coin."},
            {"word": "voice", "ipa": "/vɔɪs/", "meaning": "giọng nói", "sentence": "Her voice is clear."},
            {"word": "choice", "ipa": "/tʃɔɪs/", "meaning": "lựa chọn", "sentence": "That is a good choice."},
            {"word": "toy", "ipa": "/tɔɪ/", "meaning": "đồ chơi", "sentence": "This toy is new."},
            {"word": "enjoy", "ipa": "/ɪnˈdʒɔɪ/", "meaning": "thích thú", "sentence": "I enjoy this class."},
        ],
    },
    "diphthong-ou": {
        "explanation": (
            "Âm /əʊ/ bắt đầu ở vị trí trung tính /ə/ rồi trượt về /ʊ/. "
            "Môi từ trạng thái thả lỏng chuyển sang hơi tròn ở cuối âm."
        ),
        "tip": "Đừng đọc /əʊ/ thành /o/ đơn. Hãy cảm nhận chuyển động glide rõ trong go, home, coat.",
        "common_mistakes": "Lỗi phổ biến: đọc go như /gɔː/. Cách sửa: bắt đầu nhẹ ở /ə/ rồi kết thúc gọn ở /ʊ/.",
        "examples": [
            {"word": "go", "ipa": "/ɡəʊ/", "meaning": "đi", "sentence": "We go to school."},
            {"word": "home", "ipa": "/həʊm/", "meaning": "nhà", "sentence": "I am at home."},
            {"word": "coat", "ipa": "/kəʊt/", "meaning": "áo khoác", "sentence": "Put on your coat."},
            {"word": "phone", "ipa": "/fəʊn/", "meaning": "điện thoại", "sentence": "My phone is on the desk."},
            {"word": "road", "ipa": "/rəʊd/", "meaning": "con đường", "sentence": "The road is long."},
            {"word": "close", "ipa": "/kləʊz/", "meaning": "đóng", "sentence": "Please close the door."},
        ],
    },
}

ADVANCED_CONTENT = {
    "linking-cv": {
        "explanation": (
            "Linking (nối âm) xảy ra khi từ trước kết thúc bằng phụ âm và từ sau bắt đầu bằng nguyên âm. "
            "Người bản ngữ nối mượt như một cụm âm liên tục: turn off -> tur-noff, pick it up -> pi-ki-tup."
        ),
        "examples": [
            {"phrase": "turn off", "connected_form": "tur-noff", "explanation": "n nối sang o", "meaning": "tắt"},
            {"phrase": "pick it up", "connected_form": "pi-ki-tup", "explanation": "k nối sang i", "meaning": "nhặt lên"},
            {"phrase": "make it", "connected_form": "mei-kit", "explanation": "k nối sang i", "meaning": "làm được"},
            {"phrase": "leave it", "connected_form": "lea-vit", "explanation": "v nối sang i", "meaning": "để nó lại"},
            {"phrase": "an apple", "connected_form": "a-na-pple", "explanation": "n nối sang a", "meaning": "một quả táo"},
            {"phrase": "take it easy", "connected_form": "tei-ki-deasy", "explanation": "k và t nối tiếp", "meaning": "cứ từ từ"},
            {"phrase": "put on", "connected_form": "pu-ton", "explanation": "t nối sang o", "meaning": "mặc vào"},
        ],
        "practice": [
            {"text": "Turn off the light.", "hint": "Nối turn_off thật mượt"},
            {"text": "Pick it up now.", "hint": "Nối pick_it_up thành 1 cụm"},
            {"text": "Take it easy.", "hint": "Giữ nhịp tự nhiên"},
            {"text": "Leave it on the table.", "hint": "Nối leave_it"},
            {"text": "Put on your coat.", "hint": "Nối put_on"},
        ],
        "quiz": [
            {"audio_text": "turn off", "question": "Nghe và chọn cụm từ đúng", "options": ["turn off", "turn of", "ton off", "turn up"], "answer": "turn off"},
            {"audio_text": "pick it up", "question": "Nghe và chọn cụm từ đúng", "options": ["pick it up", "pick up", "pick it", "pick a cup"], "answer": "pick it up"},
            {"audio_text": "take it easy", "question": "Nghe và chọn cụm từ đúng", "options": ["take it easy", "take easy", "take it", "take this easy"], "answer": "take it easy"},
            {"audio_text": "put on", "question": "Nghe và chọn cụm từ đúng", "options": ["put on", "put in", "put up", "put out"], "answer": "put on"},
        ],
    },
    "weak-forms": {
        "explanation": (
            "Weak forms là dạng phát âm giảm nhẹ của function words trong câu nói tự nhiên. "
            "Ví dụ: and /ənd/ -> /ən/, to /tuː/ -> /tə/, of /ɒv/ -> /əv/. "
            "Dùng strong form khi nhấn mạnh hoặc đứng cuối câu."
        ),
        "examples": [
            {"phrase": "a book", "connected_form": "ə book", "explanation": "a yếu thành /ə/", "meaning": "một quyển sách"},
            {"phrase": "the car", "connected_form": "ðə car", "explanation": "the trước phụ âm", "meaning": "chiếc xe"},
            {"phrase": "the apple", "connected_form": "ði apple", "explanation": "the trước nguyên âm", "meaning": "quả táo"},
            {"phrase": "bread and butter", "connected_form": "bread ən butter", "explanation": "and yếu", "meaning": "bánh mì và bơ"},
            {"phrase": "a cup of tea", "connected_form": "a cup əv tea", "explanation": "of yếu", "meaning": "một tách trà"},
            {"phrase": "want to go", "connected_form": "want tə go", "explanation": "to yếu", "meaning": "muốn đi"},
            {"phrase": "for me", "connected_form": "fə me", "explanation": "for yếu", "meaning": "cho tôi"},
        ],
        "practice": [
            {"text": "I want to go home.", "hint": "to đọc yếu /tə/"},
            {"text": "A cup of tea, please.", "hint": "of đọc yếu /əv/"},
            {"text": "Bread and butter.", "hint": "and đọc yếu /ən/"},
            {"text": "This is for me.", "hint": "for đọc yếu /fə/"},
            {"text": "The apple is red.", "hint": "the đọc /ði/ trước vowel"},
        ],
        "quiz": [
            {"audio_text": "want to go", "question": "Nghe và chọn cụm đúng", "options": ["want to go", "want go", "one to go", "want too go"], "answer": "want to go"},
            {"audio_text": "a cup of tea", "question": "Nghe và chọn cụm đúng", "options": ["a cup of tea", "a cup tea", "cup of tea", "a cap of tea"], "answer": "a cup of tea"},
            {"audio_text": "bread and butter", "question": "Nghe và chọn cụm đúng", "options": ["bread and butter", "bread butter", "bread in butter", "bread an butter"], "answer": "bread and butter"},
            {"audio_text": "for me", "question": "Nghe và chọn cụm đúng", "options": ["for me", "from me", "four me", "for him"], "answer": "for me"},
        ],
    },
    "reduction": {
        "explanation": (
            "Reduction là rút gọn cụm từ thường gặp trong spoken English: going to -> gonna, "
            "want to -> wanna, kind of -> kinda, got to -> gotta. Dùng nhiều trong hội thoại tự nhiên, "
            "nhưng cần phân biệt với văn viết trang trọng."
        ),
        "examples": [
            {"phrase": "going to", "connected_form": "gonna", "explanation": "giảm âm trong nói nhanh", "meaning": "sẽ"},
            {"phrase": "want to", "connected_form": "wanna", "explanation": "giảm âm trong hội thoại", "meaning": "muốn"},
            {"phrase": "kind of", "connected_form": "kinda", "explanation": "giảm âm tự nhiên", "meaning": "kiểu như"},
            {"phrase": "got to", "connected_form": "gotta", "explanation": "giảm âm phổ biến", "meaning": "phải"},
            {"phrase": "let me", "connected_form": "lemme", "explanation": "nói nhanh", "meaning": "để tôi"},
            {"phrase": "give me", "connected_form": "gimme", "explanation": "nói nhanh", "meaning": "đưa tôi"},
            {"phrase": "out of", "connected_form": "outta", "explanation": "nói nhanh", "meaning": "ra khỏi"},
        ],
        "practice": [
            {"text": "I am gonna study tonight.", "hint": "gonna = going to"},
            {"text": "Do you wanna join us?", "hint": "wanna = want to"},
            {"text": "It is kinda hard.", "hint": "kinda = kind of"},
            {"text": "I gotta go now.", "hint": "gotta = got to"},
            {"text": "Gimme a minute.", "hint": "gimme = give me"},
        ],
        "quiz": [
            {"audio_text": "gonna", "question": "Nghe và chọn dạng đầy đủ phù hợp", "options": ["going to", "go to", "gone to", "good to"], "answer": "going to"},
            {"audio_text": "wanna", "question": "Nghe và chọn dạng đầy đủ phù hợp", "options": ["want to", "one to", "went to", "want for"], "answer": "want to"},
            {"audio_text": "kinda", "question": "Nghe và chọn dạng đầy đủ phù hợp", "options": ["kind of", "kind to", "king of", "kind a"], "answer": "kind of"},
            {"audio_text": "gotta", "question": "Nghe và chọn dạng đầy đủ phù hợp", "options": ["got to", "get to", "go to", "got a"], "answer": "got to"},
        ],
    },
}


def uniq_by_word(items):
    seen = set()
    out = []
    for item in items:
        word = (item.get("word") or "").strip().lower()
        if not word or word in seen:
            continue
        seen.add(word)
        out.append(item)
    return out


def extract_examples_from_phonemes(lesson, limit=6):
    items = []
    for ph in lesson.phonemes.order_by("order"):
        for ex in ph.example_words or []:
            word = (ex.get("word") or "").strip()
            if not word:
                continue
            items.append({
                "word": word,
                "ipa": ex.get("ipa", ""),
                "meaning": ex.get("meaning", ""),
                "sentence": f"Say '{word}' clearly in a short sentence.",
            })
    return uniq_by_word(items)[:limit]


def build_quiz(examples, count=4):
    words = [x["word"] for x in examples if x.get("word")]
    if len(words) < 2:
        words = ["cat", "cut", "cot", "coat"]

    quiz = []
    total = min(count, len(words))
    for i in range(total):
        target = words[i]
        # Build 4 options by rotating through list
        pool = [target]
        j = i + 1
        while len(pool) < 4 and words:
            cand = words[j % len(words)]
            if cand not in pool:
                pool.append(cand)
            j += 1
        quiz.append({
            "audio_text": target,
            "question": "Nghe và chọn từ đúng",
            "options": pool,
            "answer": target,
        })
    return quiz


def default_explanation(lesson):
    symbols = [ph.symbol for ph in lesson.phonemes.order_by("order")]
    if symbols:
        return (
            f"Bài học tập trung vào âm {', '.join(symbols)}. "
            "Luyện theo 3 bước: nghe mẫu, quan sát vị trí môi-lưỡi, và lặp lại có kiểm soát tốc độ."
        )
    return (
        "Bài học phát âm theo phương pháp nghe - bắt chước - kiểm tra. "
        "Ưu tiên độ rõ ràng trước, sau đó tăng tốc độ nói tự nhiên."
    )


def default_tip(lesson):
    return (
        "Mẹo cho người Việt: tránh thay âm tiếng Anh bằng âm gần giống tiếng Việt. "
        "Ghi âm giọng đọc của bạn và so sánh với mẫu để sửa sai nhanh hơn."
    )


def default_mistakes(lesson):
    return (
        "Lỗi phổ biến: bỏ âm cuối, rút ngắn nguyên âm dài, hoặc không phân biệt cặp hữu thanh-vô thanh. "
        "Hãy luyện từng từ chậm, sau đó ghép vào câu ngắn."
    )


def create_sections_for_lesson(lesson):
    slug = lesson.slug

    # Clear old sections so content is always fresh and deterministic.
    LessonSection.objects.filter(lesson=lesson).delete()

    if lesson.stage.stage_type == "advanced":
        data = ADVANCED_CONTENT.get(slug)
        if not data:
            data = {
                "explanation": "Bài học nâng cao về connected speech.",
                "examples": [],
                "practice": [],
                "quiz": [],
            }

        sections = [
            {
                "section_type": "explanation",
                "title": "Giải thích quy tắc",
                "body": data["explanation"],
                "items": [],
            },
            {
                "section_type": "examples",
                "title": "Ví dụ trọng tâm",
                "body": "So sánh dạng đầy đủ và dạng nói tự nhiên.",
                "items": data["examples"],
            },
            {
                "section_type": "practice",
                "title": "Luyện tập có hướng dẫn",
                "body": "Bấm phát TTS và lặp lại theo cụm từ.",
                "items": data["practice"],
            },
            {
                "section_type": "quiz",
                "title": "Kiểm tra nghe",
                "body": "Nghe TTS và chọn cụm từ đúng.",
                "items": data["quiz"],
            },
        ]
    else:
        override = PHONEME_OVERRIDES.get(slug, {})
        examples = override.get("examples") or extract_examples_from_phonemes(lesson, limit=6)
        if len(examples) < 5:
            # Pad to 5 examples (minimum requirement)
            base_word = lesson.slug.replace("-", " ")
            while len(examples) < 5:
                n = len(examples) + 1
                examples.append({
                    "word": f"{base_word} {n}",
                    "ipa": "",
                    "meaning": "ví dụ bổ sung",
                    "sentence": f"Practice example {n} for this lesson.",
                })

        quiz_items = build_quiz(examples, count=4)

        sections = [
            {
                "section_type": "explanation",
                "title": "Cách phát âm",
                "body": override.get("explanation") or default_explanation(lesson),
                "items": [],
            },
            {
                "section_type": "tip",
                "title": "Mẹo cho người Việt",
                "body": override.get("tip") or default_tip(lesson),
                "items": [],
            },
            {
                "section_type": "examples",
                "title": "Từ và câu ví dụ",
                "body": "Luyện từng từ rồi đọc cả câu để ổn định phát âm.",
                "items": examples,
            },
            {
                "section_type": "common_mistakes",
                "title": "Lỗi thường gặp",
                "body": override.get("common_mistakes") or default_mistakes(lesson),
                "items": [],
            },
            {
                "section_type": "quiz",
                "title": "Kiểm tra nghe nhanh",
                "body": "Nghe TTS và chọn từ đúng.",
                "items": quiz_items,
            },
        ]

    for i, section in enumerate(sections, start=1):
        LessonSection.objects.create(
            lesson=lesson,
            section_type=section["section_type"],
            title=section["title"],
            body=section.get("body", ""),
            items=section.get("items", []),
            order=i,
        )

    return len(sections)


def main():
    lessons = (
        PhonemeLesson.objects.filter(is_published=True)
        .select_related("stage")
        .prefetch_related("phonemes")
        .order_by("stage__order", "order")
    )

    total_sections = 0
    total_lessons = 0

    for lesson in lessons:
        count = create_sections_for_lesson(lesson)
        total_sections += count
        total_lessons += 1
        print(f"Seeded {count} sections for {lesson.slug}")

    print("-" * 60)
    print(f"Lessons seeded: {total_lessons}")
    print(f"Sections created: {total_sections}")
    print("Done: pronunciation lesson content seeded.")


if __name__ == "__main__":
    main()
