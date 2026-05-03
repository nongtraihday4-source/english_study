"""
Seed pronunciation data: 4 stages, phoneme lessons, full IPA chart, minimal pairs.
Run: python manage.py runscript seed_pronunciation
  or directly: python manage.py shell < scripts/seed_pronunciation.py
"""
import os
import sys
import django

# Allow running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")
django.setup()

from apps.pronunciation.models import (
    MinimalPair, MinimalPairSet, Phoneme, PhonemeLesson, PronunciationStage,
)

# ─── 1. Stages ────────────────────────────────────────────────────────────────
STAGES = [
    {"stage_type": "monophthongs", "title": "Stage 1: Nguyên âm đơn", "description": "Học 12 nguyên âm đơn tiếng Anh cơ bản nhất.", "order": 1, "icon": "🔵"},
    {"stage_type": "consonants",   "title": "Stage 2: Phụ âm",        "description": "Học 24 phụ âm tiếng Anh — từ dễ đến khó.", "order": 2, "icon": "🟢"},
    {"stage_type": "diphthongs",   "title": "Stage 3: Nguyên âm đôi",  "description": "Học 8 nguyên âm đôi (diphthongs) tiếng Anh.", "order": 3, "icon": "🟡"},
    {"stage_type": "advanced",     "title": "Stage 4: Nâng cao",       "description": "Connected speech, linking, reduction và weak forms.", "order": 4, "icon": "🔴"},
]

stages_map = {}
for s in STAGES:
    obj, _ = PronunciationStage.objects.update_or_create(
        stage_type=s["stage_type"],
        defaults={k: v for k, v in s.items() if k != "stage_type"},
    )
    stages_map[s["stage_type"]] = obj

print("✅ Stages seeded:", len(stages_map))

# ─── 2. Phoneme Lessons ────────────────────────────────────────────────────────
LESSONS = [
    # Monophthongs
    {"stage": "monophthongs", "title": "Nguyên âm /æ/ — cat, hat, map",   "slug": "vowel-ae",      "order": 1, "cefr_level": "A1"},
    {"stage": "monophthongs", "title": "Nguyên âm /ɪ/ — sit, bit, fish",  "slug": "vowel-i-short", "order": 2, "cefr_level": "A1"},
    {"stage": "monophthongs", "title": "Nguyên âm /iː/ — see, tree, tea", "slug": "vowel-i-long",  "order": 3, "cefr_level": "A1"},
    {"stage": "monophthongs", "title": "Nguyên âm /ʌ/ — cup, sun, bus",   "slug": "vowel-uh",      "order": 4, "cefr_level": "A1"},
    {"stage": "monophthongs", "title": "Nguyên âm /ɒ/ — hot, top, clock", "slug": "vowel-o-short", "order": 5, "cefr_level": "A1"},
    {"stage": "monophthongs", "title": "Nguyên âm /uː/ — food, moon, blue","slug": "vowel-u-long", "order": 6, "cefr_level": "A2"},
    {"stage": "monophthongs", "title": "Nguyên âm /ə/ — about, sofa (schwa)","slug": "vowel-schwa","order": 7, "cefr_level": "A2"},
    # Consonants
    {"stage": "consonants",   "title": "Phụ âm /θ/ và /ð/ — think, this", "slug": "consonant-th",  "order": 1, "cefr_level": "A1"},
    {"stage": "consonants",   "title": "Phụ âm /v/ và /w/ — van, wine",   "slug": "consonant-v-w", "order": 2, "cefr_level": "A1"},
    {"stage": "consonants",   "title": "Phụ âm /r/ — red, road, right",   "slug": "consonant-r",   "order": 3, "cefr_level": "A1"},
    {"stage": "consonants",   "title": "Phụ âm /l/ — late, fall, well",   "slug": "consonant-l",   "order": 4, "cefr_level": "A1"},
    {"stage": "consonants",   "title": "Phụ âm /ŋ/ — sing, long, ring",   "slug": "consonant-ng",  "order": 5, "cefr_level": "A2"},
    {"stage": "consonants",   "title": "Phụ âm /ʃ/ và /ʒ/ — she, measure","slug": "consonant-sh-zh","order": 6, "cefr_level": "A2"},
    # Diphthongs
    {"stage": "diphthongs",   "title": "Nguyên âm đôi /eɪ/ — day, say",   "slug": "diphthong-ei",  "order": 1, "cefr_level": "A2"},
    {"stage": "diphthongs",   "title": "Nguyên âm đôi /aɪ/ — my, fly",    "slug": "diphthong-ai",  "order": 2, "cefr_level": "A2"},
    {"stage": "diphthongs",   "title": "Nguyên âm đôi /ɔɪ/ — boy, coin",  "slug": "diphthong-oi",  "order": 3, "cefr_level": "B1"},
    {"stage": "diphthongs",   "title": "Nguyên âm đôi /əʊ/ — go, home",   "slug": "diphthong-ou",  "order": 4, "cefr_level": "A2"},
    # Advanced
    {"stage": "advanced",     "title": "Linking Words — Consonant + Vowel", "slug": "linking-cv",    "order": 1, "cefr_level": "B1"},
    {"stage": "advanced",     "title": "Weak Forms — a, the, and, of...",   "slug": "weak-forms",    "order": 2, "cefr_level": "B1"},
    {"stage": "advanced",     "title": "Reduction — gonna, wanna, kinda",   "slug": "reduction",     "order": 3, "cefr_level": "B2"},
]

lessons_map = {}
for l in LESSONS:
    stage = stages_map[l["stage"]]
    obj, _ = PhonemeLesson.objects.update_or_create(
        slug=l["slug"],
        defaults={"stage": stage, "title": l["title"], "order": l["order"], "cefr_level": l["cefr_level"]},
    )
    lessons_map[l["slug"]] = obj

print("✅ Lessons seeded:", len(lessons_map))

# ─── 3. IPA Phoneme Chart ────────────────────────────────────────────────────
# audio_url points to frontend public: /ipa-audio/<file>.mp3
# example_words[0] has before/highlight/after fields for underline rendering
A = "/ipa-audio/"   # base audio path
IPA_PHONEMES = [
    # ── VOWELS ordered for 4-col grid (row-by-row = British phonemic chart) ──
    # Row 1: iː | ɪ | ʊ | uː
    {"symbol": "/iː/", "phoneme_type": "vowel", "order": 1, "audio_url": A+"iː.mp3",
     "description": "Nguyên âm dài — been, feel, see",
     "example_words": [{"word":"been","before":"b","highlight":"ee","after":"n","ipa":"/biːn/","meaning":"đã từng"},
                       {"word":"feel","ipa":"/fiːl/","meaning":"cảm thấy"},{"word":"see","ipa":"/siː/","meaning":"nhìn"}]},
    {"symbol": "/ɪ/",  "phoneme_type": "vowel", "order": 2, "audio_url": A+"ɪ.mp3",
     "description": "Nguyên âm ngắn — tip, sit, bit",
     "example_words": [{"word":"tip","before":"t","highlight":"i","after":"p","ipa":"/tɪp/","meaning":"đầu nhọn"},
                       {"word":"sit","ipa":"/sɪt/","meaning":"ngồi"},{"word":"bit","ipa":"/bɪt/","meaning":"cắn"}]},
    {"symbol": "/ʊ/",  "phoneme_type": "vowel", "order": 3, "audio_url": A+"ʊ.mp3",
     "description": "Nguyên âm ngắn — shook, book, foot",
     "example_words": [{"word":"shook","before":"sh","highlight":"oo","after":"k","ipa":"/ʃʊk/","meaning":"rung chuyển"},
                       {"word":"book","ipa":"/bʊk/","meaning":"sách"},{"word":"foot","ipa":"/fʊt/","meaning":"chân"}]},
    {"symbol": "/uː/", "phoneme_type": "vowel", "order": 4, "audio_url": A+"uː.mp3",
     "description": "Nguyên âm dài — moon, food, blue",
     "example_words": [{"word":"moon","before":"m","highlight":"oo","after":"n","ipa":"/muːn/","meaning":"mặt trăng"},
                       {"word":"food","ipa":"/fuːd/","meaning":"thức ăn"},{"word":"blue","ipa":"/bluː/","meaning":"xanh"}]},
    # Row 2: e | ə | ɜː | ɔː
    {"symbol": "/e/",  "phoneme_type": "vowel", "order": 5, "audio_url": A+"e.mp3",
     "description": "Nguyên âm — met, red, set",
     "example_words": [{"word":"met","before":"m","highlight":"e","after":"t","ipa":"/met/","meaning":"gặp"},
                       {"word":"red","ipa":"/red/","meaning":"đỏ"},{"word":"set","ipa":"/set/","meaning":"đặt"}]},
    {"symbol": "/ə/",  "phoneme_type": "vowel", "order": 6, "audio_url": A+"ə.mp3",
     "description": "Schwa — the, about, sofa",
     "example_words": [{"word":"the","before":"th","highlight":"e","after":"","ipa":"/ðə/","meaning":"(mạo từ)"},
                       {"word":"about","ipa":"/əˈbaʊt/","meaning":"về"},{"word":"sofa","ipa":"/ˈsəʊfə/","meaning":"sofa"}]},
    {"symbol": "/ɜː/", "phoneme_type": "vowel", "order": 7, "audio_url": A+"ɜ.mp3",
     "description": "Nguyên âm dài — sir, word, nurse",
     "example_words": [{"word":"sir","before":"s","highlight":"ir","after":"","ipa":"/sɜː/","meaning":"thưa ngài"},
                       {"word":"word","ipa":"/wɜːd/","meaning":"từ"},{"word":"nurse","ipa":"/nɜːs/","meaning":"y tá"}]},
    {"symbol": "/ɔː/", "phoneme_type": "vowel", "order": 8, "audio_url": A+"ɔː.mp3",
     "description": "Nguyên âm dài — shore, more, law",
     "example_words": [{"word":"shore","before":"sh","highlight":"or","after":"e","ipa":"/ʃɔː/","meaning":"bờ biển"},
                       {"word":"more","ipa":"/mɔː/","meaning":"hơn"},{"word":"law","ipa":"/lɔː/","meaning":"luật"}]},
    # Row 3: æ | ʌ | ɑː | ɒ
    {"symbol": "/æ/",  "phoneme_type": "vowel", "order": 9, "audio_url": A+"æ.mp3",
     "description": "Nguyên âm — pan, hat, map",
     "example_words": [{"word":"pan","before":"p","highlight":"a","after":"n","ipa":"/pæn/","meaning":"chảo"},
                       {"word":"hat","ipa":"/hæt/","meaning":"mũ"},{"word":"map","ipa":"/mæp/","meaning":"bản đồ"}]},
    {"symbol": "/ʌ/",  "phoneme_type": "vowel", "order": 10, "audio_url": A+"ʌ.mp3",
     "description": "Nguyên âm — fun, cup, sun",
     "example_words": [{"word":"fun","before":"f","highlight":"u","after":"n","ipa":"/fʌn/","meaning":"vui vẻ"},
                       {"word":"cup","ipa":"/kʌp/","meaning":"cốc"},{"word":"sun","ipa":"/sʌn/","meaning":"mặt trời"}]},
    {"symbol": "/ɑː/", "phoneme_type": "vowel", "order": 11, "audio_url": A+"ɑː.mp3",
     "description": "Nguyên âm dài — card, car, barn",
     "example_words": [{"word":"card","before":"c","highlight":"ar","after":"d","ipa":"/kɑːd/","meaning":"thẻ"},
                       {"word":"car","ipa":"/kɑː/","meaning":"xe hơi"},{"word":"barn","ipa":"/bɑːn/","meaning":"chuồng"}]},
    {"symbol": "/ɒ/",  "phoneme_type": "vowel", "order": 12, "audio_url": A+"ɒ.mp3",
     "description": "Nguyên âm ngắn — lock, hot, top",
     "example_words": [{"word":"lock","before":"l","highlight":"o","after":"ck","ipa":"/lɒk/","meaning":"khóa"},
                       {"word":"hot","ipa":"/hɒt/","meaning":"nóng"},{"word":"top","ipa":"/tɒp/","meaning":"đỉnh"}]},
    # ── DIPHTHONGS ordered 3-col grid ──────────────────────────────────────
    # Row 1: ɪə | eɪ | eə
    {"symbol": "/ɪə/", "phoneme_type": "diphthong", "order": 1, "audio_url": A+"ɪə.mp3",
     "description": "Nguyên âm đôi — dear, here, ear",
     "example_words": [{"word":"dear","before":"d","highlight":"ear","after":"","ipa":"/dɪə/","meaning":"thân mến"},
                       {"word":"here","ipa":"/hɪə/","meaning":"đây"},{"word":"ear","ipa":"/ɪə/","meaning":"tai"}]},
    {"symbol": "/eɪ/", "phoneme_type": "diphthong", "order": 2, "audio_url": A+"eɪ.mp3",
     "description": "Nguyên âm đôi — day, say, rain",
     "example_words": [{"word":"same","before":"s","highlight":"a","after":"me","ipa":"/seɪm/","meaning":"giống nhau"},
                       {"word":"day","ipa":"/deɪ/","meaning":"ngày"},{"word":"rain","ipa":"/reɪn/","meaning":"mưa"}]},
    {"symbol": "/eə/", "phoneme_type": "diphthong", "order": 3, "audio_url": A+"eə.mp3",
     "description": "Nguyên âm đôi — hair, there, care",
     "example_words": [{"word":"hair","before":"h","highlight":"air","after":"","ipa":"/heə/","meaning":"tóc"},
                       {"word":"there","ipa":"/ðeə/","meaning":"ở đó"},{"word":"care","ipa":"/keə/","meaning":"quan tâm"}]},
    # Row 2: ʊə | əʊ | ɔɪ
    {"symbol": "/ʊə/", "phoneme_type": "diphthong", "order": 4, "audio_url": A+"ʊə.mp3",
     "description": "Nguyên âm đôi — tour, sure, cure",
     "example_words": [{"word":"curious","before":"c","highlight":"u","after":"rious","ipa":"/ˈkjʊəriəs/","meaning":"tò mò"},
                       {"word":"tour","ipa":"/tʊə/","meaning":"du lịch"},{"word":"sure","ipa":"/ʃʊə/","meaning":"chắc chắn"}]},
    {"symbol": "/əʊ/", "phoneme_type": "diphthong", "order": 5, "audio_url": A+"əʊ.mp3",
     "description": "Nguyên âm đôi — go, home, coat",
     "example_words": [{"word":"go","before":"g","highlight":"o","after":"","ipa":"/ɡəʊ/","meaning":"đi"},
                       {"word":"home","ipa":"/həʊm/","meaning":"nhà"},{"word":"coat","ipa":"/kəʊt/","meaning":"áo khoác"}]},
    {"symbol": "/ɔɪ/", "phoneme_type": "diphthong", "order": 6, "audio_url": A+"ɔɪ.mp3",
     "description": "Nguyên âm đôi — boy, coin, voice",
     "example_words": [{"word":"choice","before":"ch","highlight":"oi","after":"ce","ipa":"/tʃɔɪs/","meaning":"lựa chọn"},
                       {"word":"boy","ipa":"/bɔɪ/","meaning":"cậu bé"},{"word":"coin","ipa":"/kɔɪn/","meaning":"đồng xu"}]},
    # Row 3: aɪ | aʊ | əl
    {"symbol": "/aɪ/", "phoneme_type": "diphthong", "order": 7, "audio_url": A+"aɪ.mp3",
     "description": "Nguyên âm đôi — hide, my, fly",
     "example_words": [{"word":"hide","before":"h","highlight":"i","after":"de","ipa":"/haɪd/","meaning":"ẩn"},
                       {"word":"my","ipa":"/maɪ/","meaning":"của tôi"},{"word":"fly","ipa":"/flaɪ/","meaning":"bay"}]},
    {"symbol": "/aʊ/", "phoneme_type": "diphthong", "order": 8, "audio_url": A+"aʊ.mp3",
     "description": "Nguyên âm đôi — loud, now, down",
     "example_words": [{"word":"loud","before":"l","highlight":"ou","after":"d","ipa":"/laʊd/","meaning":"to"},
                       {"word":"now","ipa":"/naʊ/","meaning":"bây giờ"},{"word":"down","ipa":"/daʊn/","meaning":"xuống"}]},
    {"symbol": "/əl/", "phoneme_type": "diphthong", "order": 9, "audio_url": A+"əl.mp3",
     "description": "Nguyên âm đôi — tall, fall, ball",
     "example_words": [{"word":"tall","before":"t","highlight":"all","after":"","ipa":"/tɔːl/","meaning":"cao"},
                       {"word":"fall","ipa":"/fɔːl/","meaning":"ngã"},{"word":"ball","ipa":"/bɔːl/","meaning":"bóng"}]},
    # ── CONSONANTS ordered for 3-row × 8-col grid ──────────────────────────
    # Row 1 voiceless: p | f | t | θ | tʃ | s | ʃ | k
    {"symbol": "/p/",  "phoneme_type": "consonant", "order": 1, "audio_url": A+"p.mp3",
     "description": "Vô thanh — pick, top, cup",
     "example_words": [{"word":"pick","before":"","highlight":"p","after":"ick","ipa":"/pɪk/","meaning":"nhặt"},
                       {"word":"top","ipa":"/tɒp/","meaning":"đỉnh"},{"word":"cup","ipa":"/kʌp/","meaning":"cốc"}]},
    {"symbol": "/f/",  "phoneme_type": "consonant", "order": 2, "audio_url": A+"f.mp3",
     "description": "Vô thanh — first, fish, left",
     "example_words": [{"word":"first","before":"","highlight":"f","after":"irst","ipa":"/fɜːst/","meaning":"đầu tiên"},
                       {"word":"fish","ipa":"/fɪʃ/","meaning":"cá"},{"word":"left","ipa":"/left/","meaning":"trái"}]},
    {"symbol": "/t/",  "phoneme_type": "consonant", "order": 3, "audio_url": A+"t.mp3",
     "description": "Vô thanh — team, cat, sit",
     "example_words": [{"word":"team","before":"","highlight":"t","after":"eam","ipa":"/tiːm/","meaning":"đội"},
                       {"word":"cat","ipa":"/kæt/","meaning":"mèo"},{"word":"sit","ipa":"/sɪt/","meaning":"ngồi"}]},
    {"symbol": "/θ/",  "phoneme_type": "consonant", "order": 4, "audio_url": A+"θ.mp3",
     "description": "Vô thanh th — thick, think, math",
     "example_words": [{"word":"thick","before":"","highlight":"th","after":"ick","ipa":"/θɪk/","meaning":"dày"},
                       {"word":"think","ipa":"/θɪŋk/","meaning":"nghĩ"},{"word":"math","ipa":"/mæθ/","meaning":"toán"}]},
    {"symbol": "/tʃ/", "phoneme_type": "consonant", "order": 5, "audio_url": A+"tʃ.mp3",
     "description": "Vô thanh — choose, chair, beach",
     "example_words": [{"word":"choose","before":"","highlight":"ch","after":"oose","ipa":"/tʃuːz/","meaning":"chọn"},
                       {"word":"chair","ipa":"/tʃeə/","meaning":"ghế"},{"word":"beach","ipa":"/biːtʃ/","meaning":"biển"}]},
    {"symbol": "/s/",  "phoneme_type": "consonant", "order": 6, "audio_url": A+"s.mp3",
     "description": "Vô thanh — saw, see, bus",
     "example_words": [{"word":"saw","before":"","highlight":"s","after":"aw","ipa":"/sɔː/","meaning":"cưa"},
                       {"word":"see","ipa":"/siː/","meaning":"nhìn"},{"word":"bus","ipa":"/bʌs/","meaning":"xe buýt"}]},
    {"symbol": "/ʃ/",  "phoneme_type": "consonant", "order": 7, "audio_url": A+"ʃ.mp3",
     "description": "Vô thanh — she, fish, wash",
     "example_words": [{"word":"she","before":"","highlight":"sh","after":"e","ipa":"/ʃiː/","meaning":"cô ấy"},
                       {"word":"fish","ipa":"/fɪʃ/","meaning":"cá"},{"word":"wash","ipa":"/wɒʃ/","meaning":"rửa"}]},
    {"symbol": "/k/",  "phoneme_type": "consonant", "order": 8, "audio_url": A+"k.mp3",
     "description": "Vô thanh — code, cat, back",
     "example_words": [{"word":"code","before":"","highlight":"c","after":"ode","ipa":"/kəʊd/","meaning":"mã"},
                       {"word":"cat","ipa":"/kæt/","meaning":"mèo"},{"word":"back","ipa":"/bæk/","meaning":"lưng"}]},
    # Row 2 voiced: b | v | d | ð | dʒ | z | ʒ | g
    {"symbol": "/b/",  "phoneme_type": "consonant", "order": 9, "audio_url": A+"b.mp3",
     "description": "Hữu thanh — bed, big, job",
     "example_words": [{"word":"bed","before":"","highlight":"b","after":"ed","ipa":"/bed/","meaning":"giường"},
                       {"word":"big","ipa":"/bɪɡ/","meaning":"to"},{"word":"job","ipa":"/dʒɒb/","meaning":"việc"}]},
    {"symbol": "/v/",  "phoneme_type": "consonant", "order": 10, "audio_url": A+"v.mp3",
     "description": "Hữu thanh — van, live, love",
     "example_words": [{"word":"van","before":"","highlight":"v","after":"an","ipa":"/væn/","meaning":"xe van"},
                       {"word":"live","ipa":"/lɪv/","meaning":"sống"},{"word":"love","ipa":"/lʌv/","meaning":"yêu"}]},
    {"symbol": "/d/",  "phoneme_type": "consonant", "order": 11, "audio_url": A+"d.mp3",
     "description": "Hữu thanh — dine, dog, bad",
     "example_words": [{"word":"dine","before":"","highlight":"d","after":"ine","ipa":"/daɪn/","meaning":"ăn tối"},
                       {"word":"dog","ipa":"/dɒɡ/","meaning":"chó"},{"word":"bad","ipa":"/bæd/","meaning":"xấu"}]},
    {"symbol": "/ð/",  "phoneme_type": "consonant", "order": 12, "audio_url": A+"ð.mp3",
     "description": "Hữu thanh th — these, this, mother",
     "example_words": [{"word":"these","before":"","highlight":"th","after":"ese","ipa":"/ðiːz/","meaning":"những cái này"},
                       {"word":"this","ipa":"/ðɪs/","meaning":"cái này"},{"word":"mother","ipa":"/ˈmʌðə/","meaning":"mẹ"}]},
    {"symbol": "/dʒ/", "phoneme_type": "consonant", "order": 13, "audio_url": A+"dʒ.mp3",
     "description": "Hữu thanh — jet, just, age",
     "example_words": [{"word":"jet","before":"","highlight":"j","after":"et","ipa":"/dʒet/","meaning":"phản lực"},
                       {"word":"just","ipa":"/dʒʌst/","meaning":"chỉ"},{"word":"age","ipa":"/eɪdʒ/","meaning":"tuổi"}]},
    {"symbol": "/z/",  "phoneme_type": "consonant", "order": 14, "audio_url": A+"z.mp3",
     "description": "Hữu thanh — zen, zoo, has",
     "example_words": [{"word":"zen","before":"","highlight":"z","after":"en","ipa":"/zen/","meaning":"thiền"},
                       {"word":"zoo","ipa":"/zuː/","meaning":"sở thú"},{"word":"has","ipa":"/hæz/","meaning":"có"}]},
    {"symbol": "/ʒ/",  "phoneme_type": "consonant", "order": 15, "audio_url": A+"ʒ.mp3",
     "description": "Hữu thanh — casual, measure, vision",
     "example_words": [{"word":"casual","before":"ca","highlight":"su","after":"al","ipa":"/ˈkæʒuəl/","meaning":"thường ngày"},
                       {"word":"measure","ipa":"/ˈmeʒə/","meaning":"đo"},{"word":"vision","ipa":"/ˈvɪʒn/","meaning":"tầm nhìn"}]},
    {"symbol": "/ɡ/",  "phoneme_type": "consonant", "order": 16, "audio_url": A+"g.mp3",
     "description": "Hữu thanh — get, go, big",
     "example_words": [{"word":"get","before":"","highlight":"g","after":"et","ipa":"/ɡet/","meaning":"lấy"},
                       {"word":"go","ipa":"/ɡəʊ/","meaning":"đi"},{"word":"big","ipa":"/bɪɡ/","meaning":"to"}]},
    # Row 3 sonorants: h | m | n | ŋ | r | l | w | j
    {"symbol": "/h/",  "phoneme_type": "consonant", "order": 17, "audio_url": A+"h.mp3",
     "description": "Bán âm — hard, hat, home",
     "example_words": [{"word":"hard","before":"","highlight":"h","after":"ard","ipa":"/hɑːd/","meaning":"khó"},
                       {"word":"hat","ipa":"/hæt/","meaning":"mũ"},{"word":"home","ipa":"/həʊm/","meaning":"nhà"}]},
    {"symbol": "/m/",  "phoneme_type": "consonant", "order": 18, "audio_url": A+"m.mp3",
     "description": "Mũi — mode, map, swim",
     "example_words": [{"word":"mode","before":"","highlight":"m","after":"ode","ipa":"/məʊd/","meaning":"chế độ"},
                       {"word":"map","ipa":"/mæp/","meaning":"bản đồ"},{"word":"swim","ipa":"/swɪm/","meaning":"bơi"}]},
    {"symbol": "/n/",  "phoneme_type": "consonant", "order": 19, "audio_url": A+"n.mp3",
     "description": "Mũi — neck, no, sun",
     "example_words": [{"word":"neck","before":"","highlight":"n","after":"eck","ipa":"/nek/","meaning":"cổ"},
                       {"word":"no","ipa":"/nəʊ/","meaning":"không"},{"word":"sun","ipa":"/sʌn/","meaning":"mặt trời"}]},
    {"symbol": "/ŋ/",  "phoneme_type": "consonant", "order": 20, "audio_url": A+"ŋ.mp3",
     "description": "Mũi — song, sing, ring",
     "example_words": [{"word":"song","before":"s","highlight":"ong","after":"","ipa":"/sɒŋ/","meaning":"bài hát"},
                       {"word":"sing","ipa":"/sɪŋ/","meaning":"hát"},{"word":"ring","ipa":"/rɪŋ/","meaning":"nhẫn"}]},
    {"symbol": "/r/",  "phoneme_type": "consonant", "order": 21, "audio_url": A+"r.mp3",
     "description": "Bán âm — rug, red, road",
     "example_words": [{"word":"rug","before":"","highlight":"r","after":"ug","ipa":"/rʌɡ/","meaning":"thảm"},
                       {"word":"red","ipa":"/red/","meaning":"đỏ"},{"word":"road","ipa":"/rəʊd/","meaning":"đường"}]},
    {"symbol": "/l/",  "phoneme_type": "consonant", "order": 22, "audio_url": A+"l.mp3",
     "description": "Bên — look, late, fall",
     "example_words": [{"word":"look","before":"","highlight":"l","after":"ook","ipa":"/lʊk/","meaning":"nhìn"},
                       {"word":"late","ipa":"/leɪt/","meaning":"muộn"},{"word":"fall","ipa":"/fɔːl/","meaning":"ngã"}]},
    {"symbol": "/w/",  "phoneme_type": "consonant", "order": 23, "audio_url": A+"w.mp3",
     "description": "Bán âm — watch, we, win",
     "example_words": [{"word":"watch","before":"","highlight":"w","after":"atch","ipa":"/wɒtʃ/","meaning":"đồng hồ"},
                       {"word":"we","ipa":"/wiː/","meaning":"chúng ta"},{"word":"win","ipa":"/wɪn/","meaning":"thắng"}]},
    {"symbol": "/j/",  "phoneme_type": "consonant", "order": 24, "audio_url": A+"j.mp3",
     "description": "Bán âm — yet, yes, you",
     "example_words": [{"word":"yet","before":"","highlight":"y","after":"et","ipa":"/jet/","meaning":"vẫn"},
                       {"word":"yes","ipa":"/jes/","meaning":"có"},{"word":"you","ipa":"/juː/","meaning":"bạn"}]},
]

for ph in IPA_PHONEMES:
    Phoneme.objects.update_or_create(
        symbol=ph["symbol"],
        defaults={k: v for k, v in ph.items() if k != "symbol"},
    )

print("✅ Phonemes seeded:", len(IPA_PHONEMES))

# ─── 3b. Link phonemes to their lessons ────────────────────────────────────
PHONEME_LESSON_MAP = {
    "vowel-ae":        ["/æ/"],
    "vowel-i-short":   ["/ɪ/"],
    "vowel-i-long":    ["/iː/"],
    "vowel-uh":        ["/ʌ/"],
    "vowel-o-short":   ["/ɒ/"],
    "vowel-u-long":    ["/uː/"],
    "vowel-schwa":     ["/ə/", "/ɜː/"],
    "consonant-th":    ["/θ/", "/ð/"],
    "consonant-v-w":   ["/v/", "/w/"],
    "consonant-r":     ["/r/"],
    "consonant-l":     ["/l/"],
    "consonant-ng":    ["/ŋ/"],
    "consonant-sh-zh": ["/ʃ/", "/ʒ/"],
    "diphthong-ei":    ["/eɪ/"],
    "diphthong-ai":    ["/aɪ/"],
    "diphthong-oi":    ["/ɔɪ/"],
    "diphthong-ou":    ["/əʊ/"],
}

linked = 0
for slug, symbols in PHONEME_LESSON_MAP.items():
    lesson = lessons_map.get(slug)
    if lesson:
        for sym in symbols:
            updated = Phoneme.objects.filter(symbol=sym).update(lesson=lesson)
            linked += updated

print(f"✅ Phonemes linked to lessons: {linked}")

# ─── 4. Minimal Pair Sets ────────────────────────────────────────────────────
MINIMAL_PAIRS = [
    {
        "title": "/ɪ/ vs /iː/ — ship / sheep",
        "focus_phoneme_1": "/ɪ/", "focus_phoneme_2": "/iː/",
        "description": "Phân biệt nguyên âm ngắn /ɪ/ và nguyên âm dài /iː/.",
        "cefr_level": "A1", "order": 1,
        "pairs": [
            {"word": "ship",  "ipa": "/ʃɪp/",  "meaning": "con tàu",  "order": 1},
            {"word": "sheep", "ipa": "/ʃiːp/", "meaning": "con cừu",  "order": 2},
        ],
    },
    {
        "title": "/æ/ vs /e/ — bad / bed",
        "focus_phoneme_1": "/æ/", "focus_phoneme_2": "/e/",
        "description": "Phân biệt /æ/ như trong 'cat' và /e/ như trong 'bed'.",
        "cefr_level": "A1", "order": 2,
        "pairs": [
            {"word": "bad",  "ipa": "/bæd/", "meaning": "xấu",    "order": 1},
            {"word": "bed",  "ipa": "/bed/", "meaning": "giường", "order": 2},
        ],
    },
    {
        "title": "/θ/ vs /s/ — think / sink",
        "focus_phoneme_1": "/θ/", "focus_phoneme_2": "/s/",
        "description": "Phân biệt phụ âm /θ/ (th) và /s/ dễ bị nhầm lẫn.",
        "cefr_level": "A2", "order": 3,
        "pairs": [
            {"word": "think", "ipa": "/θɪŋk/", "meaning": "nghĩ",    "order": 1},
            {"word": "sink",  "ipa": "/sɪŋk/", "meaning": "bồn rửa", "order": 2},
        ],
    },
    {
        "title": "/ð/ vs /d/ — this / dis",
        "focus_phoneme_1": "/ð/", "focus_phoneme_2": "/d/",
        "description": "Phân biệt /ð/ hữu thanh và /d/ phổ biến.",
        "cefr_level": "A2", "order": 4,
        "pairs": [
            {"word": "then",  "ipa": "/ðen/", "meaning": "sau đó", "order": 1},
            {"word": "den",   "ipa": "/den/", "meaning": "hang",   "order": 2},
        ],
    },
    {
        "title": "/b/ vs /v/ — ban / van",
        "focus_phoneme_1": "/b/", "focus_phoneme_2": "/v/",
        "description": "Phân biệt phụ âm /b/ và /v/ — hai âm dễ nhầm cho người Việt.",
        "cefr_level": "A1", "order": 5,
        "pairs": [
            {"word": "ban",  "ipa": "/bæn/", "meaning": "cấm",    "order": 1},
            {"word": "van",  "ipa": "/væn/", "meaning": "xe van", "order": 2},
        ],
    },
]

for mp in MINIMAL_PAIRS:
    pair_set, _ = MinimalPairSet.objects.update_or_create(
        title=mp["title"],
        defaults={k: v for k, v in mp.items() if k not in ("title", "pairs")},
    )
    for pair in mp["pairs"]:
        MinimalPair.objects.update_or_create(
            pair_set=pair_set, word=pair["word"],
            defaults=pair,
        )

print("✅ Minimal pairs seeded:", len(MINIMAL_PAIRS))
print("🎉 Pronunciation seed complete!")
