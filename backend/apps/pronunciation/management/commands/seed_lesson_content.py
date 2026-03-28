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
    # ── Stage 1: Monophthongs ──────────────────────────────────────────────────
    "vowel-ae": {
        "explanation": (
            "Nguyên âm /æ/ — miệng MỞ RỘNG hơn bình thường, lưỡi thấp và tiến ra trước, "
            "khẩu hình giống như đang cười rộng. Xuất hiện trong: cat, hat, map, hand.\n\n"
            "So sánh: /æ/ (cat) vs /ɑː/ (car) — /æ/ căng và tiến ra trước, /ɑː/ thư giãn và lùi ra sau."
        ),
        "tip": (
            "Người Việt thường nói /a/ thuần (ngắn, tự nhiên) thay vì /æ/. "
            "Mẹo: Hít một hơi rồi nói 'aaa' trong khi mỉm cười thật rộng — cảm nhận miệng căng ra hai bên.\n\n"
            "Cặp tập luyện: cat /kæt/ vs cut /kʌt/ — cùng phụ âm, chỉ khác nguyên âm, nghĩa hoàn toàn khác."
        ),
        "common_mistakes": (
            "1. Phát âm /æ/ như /a/ ngắn Việt: 'cat' → /kat/ (quá tự nhiên, không căng miệng).\n"
            "2. Nhầm /æ/ với /ɑː/ dài: 'map' → /mɑːp/ (lưỡi lùi ra sau quá).\n"
            "3. Không mở miệng đủ rộng — /æ/ cần khẩu hình ngang, không tròn.\n"
            "4. Bỏ phụ âm cuối: 'bad' → 'ba', 'hand' → 'han' — lỗi phổ biến người Việt."
        ),
        "examples": [
            {"word": "cat",   "ipa": "/kæt/",   "meaning": "con mèo",    "sentence": "The cat sat on the mat."},
            {"word": "hat",   "ipa": "/hæt/",   "meaning": "cái mũ",     "sentence": "She wears a red hat."},
            {"word": "map",   "ipa": "/mæp/",   "meaning": "bản đồ",     "sentence": "I need a map."},
            {"word": "hand",  "ipa": "/hænd/",  "meaning": "bàn tay",    "sentence": "Raise your hand."},
            {"word": "black", "ipa": "/blæk/",  "meaning": "màu đen",    "sentence": "The bag is black."},
            {"word": "plan",  "ipa": "/plæn/",  "meaning": "kế hoạch",   "sentence": "What's your plan?"},
            {"word": "add",   "ipa": "/æd/",    "meaning": "thêm vào",   "sentence": "Add some salt."},
            {"word": "stand", "ipa": "/stænd/", "meaning": "đứng",       "sentence": "Stand up, please."},
        ],
    },
    "vowel-i-short": {
        "explanation": (
            "Nguyên âm /ɪ/ — ngắn, thư giãn, lưỡi tiến ra trước nhưng KHÔNG căng như /iː/. "
            "Miệng hé mở nhẹ, góc miệng không kéo căng. Xuất hiện trong: sit, bit, fish, big.\n\n"
            "So sánh cặp tối thiểu (minimal pairs):\n"
            "  sit /sɪt/ vs seat /siːt/  |  bit /bɪt/ vs beat /biːt/  |  ship /ʃɪp/ vs sheep /ʃiːp/"
        ),
        "tip": (
            "Người Việt thường kéo dài /ɪ/ thành /iː/ — đây là lỗi gây nhầm nghĩa! "
            "Nhớ: /ɪ/ ngắn và thả lỏng hơn. Thử nói 'it' — đó là /ɪ/ đúng.\n\n"
            "Cảm nhận: /iː/ căng cơ miệng như mỉm cười, /ɪ/ thư giãn, miệng hé nhẹ."
        ),
        "common_mistakes": (
            "1. Kéo dài /ɪ/ thành /iː/: 'sit' → 'seat', 'bit' → 'beat' — gây hiểu nhầm nghĩa!\n"
            "2. Phát âm quá căng, lưỡi ép cao như /iː/.\n"
            "3. Bỏ âm cuối: 'sit' → 'si', 'bit' → 'bi' — lỗi phổ biến của người Việt.\n"
            "4. Nhầm 'ship' /ʃɪp/ → 'sheep' /ʃiːp/ (tàu thuyền thành con cừu) trong giao tiếp."
        ),
        "examples": [
            {"word": "sit",  "ipa": "/sɪt/",  "meaning": "ngồi",          "sentence": "Please sit down."},
            {"word": "bit",  "ipa": "/bɪt/",  "meaning": "một chút",      "sentence": "Just a bit, thanks."},
            {"word": "fish", "ipa": "/fɪʃ/",  "meaning": "con cá",        "sentence": "I love fish and chips."},
            {"word": "big",  "ipa": "/bɪɡ/",  "meaning": "to lớn",        "sentence": "That's a big dog."},
            {"word": "ship", "ipa": "/ʃɪp/",  "meaning": "con tàu",       "sentence": "The ship is in the port."},
            {"word": "him",  "ipa": "/hɪm/",  "meaning": "anh ấy (tân)",  "sentence": "I saw him yesterday."},
            {"word": "trip", "ipa": "/trɪp/", "meaning": "chuyến đi",     "sentence": "Have a safe trip."},
            {"word": "win",  "ipa": "/wɪn/",  "meaning": "chiến thắng",   "sentence": "I hope we win."},
        ],
    },
    "vowel-i-long": {
        "explanation": (
            "Nguyên âm dài /iː/ — lưỡi tiến cao ra trước, miệng gần như mỉm cười, căng góc miệng ra. "
            "Giữ âm DÀI — gần gấp đôi /ɪ/. Xuất hiện trong: see, feel, read, green.\n\n"
            "So sánh cặp: feel /fiːl/ vs fill /fɪl/  |  meal /miːl/ vs mill /mɪl/  |  feet /fiːt/ vs fit /fɪt/"
        ),
        "tip": (
            "Người Việt thường phát âm đúng hình dạng nhưng không đủ dài. "
            "Mẹo: Nói 'eeee' như đang chụp ảnh mỉm cười — đó là /iː/.\n\n"
            "Quy tắc dài-ngắn: Trước phụ âm hữu thanh (d, b, g, z), âm dài thêm: "
            "feed /fiːd/ dài hơn feet /fiːt/."
        ),
        "common_mistakes": (
            "1. Phát âm quá ngắn: 'feel' → /fɪl/ — mất nghĩa hoàn toàn.\n"
            "2. Không căng góc miệng ra đủ.\n"
            "3. Thêm /j/ trước nguyên âm: 'eat' → 'yeat' (gặp ở một số giọng miền Nam VN).\n"
            "4. Bỏ âm cuối: 'read' → 'ree', 'need' → 'nee', 'sleep' → 'slee'."
        ),
        "examples": [
            {"word": "see",   "ipa": "/siː/",   "meaning": "nhìn thấy",   "sentence": "Can you see that?"},
            {"word": "feel",  "ipa": "/fiːl/",  "meaning": "cảm thấy",    "sentence": "I feel great today."},
            {"word": "read",  "ipa": "/riːd/",  "meaning": "đọc",         "sentence": "I like to read books."},
            {"word": "green", "ipa": "/ɡriːn/", "meaning": "màu xanh lá", "sentence": "The grass is green."},
            {"word": "sleep", "ipa": "/sliːp/", "meaning": "ngủ",         "sentence": "I need to sleep."},
            {"word": "need",  "ipa": "/niːd/",  "meaning": "cần",         "sentence": "I need more time."},
            {"word": "key",   "ipa": "/kiː/",   "meaning": "chìa khóa",   "sentence": "Where is the key?"},
            {"word": "team",  "ipa": "/tiːm/",  "meaning": "đội nhóm",    "sentence": "We are a great team."},
        ],
    },
    "vowel-uh": {
        "explanation": (
            "Nguyên âm /ʌ/ — âm giữa thấp, lưỡi ở trung tâm và hơi thấp, miệng mở vừa, "
            "MÔI KHÔNG TRÒN. Tiếng Việt KHÔNG có âm này — đây là một trong những âm khó nhất!\n\n"
            "Cách phát âm: Nói 'uh' như tiếng Anh khi bạn do dự ('uh... I don't know') — đó chính là /ʌ/.\n"
            "So sánh: /ʌ/ (cup) vs /ɑː/ (car) vs /æ/ (cap) — ba chữ 'c_p' khác nhau!"
        ),
        "tip": (
            "Người Việt thường thay /ʌ/ bằng /a/ Việt. Điểm khác biệt: /ʌ/ ở vị trí trung tâm "
            "và ngắn hơn /a/ Việt Nam, cổ họng hơi căng, không tròn, không kéo sang ngang.\n\n"
            "Cặp luyện tập: cup /kʌp/ vs cap /kæp/ vs cop /kɒp/ — chỉ khác nguyên âm, nghĩa hoàn toàn khác."
        ),
        "common_mistakes": (
            "1. Thay bằng /a/ thuần Việt: 'cup' → /kap/ (lưỡi lùi hơn, thư giãn hơn cần thiết).\n"
            "2. Tròn môi thành /o/: 'bun' → 'bone', 'sun' → 'son' (nhầm nghĩa!).\n"
            "3. Kéo dài quá mức thành /ɑː/: 'sun' → 'sarn', 'bus' → 'bars'.\n"
            "4. Nhầm 'come' /kʌm/ với 'calm' /kɑːm/ (thư giãn vs bình tĩnh)."
        ),
        "examples": [
            {"word": "cup",   "ipa": "/kʌp/",   "meaning": "cốc, tách",      "sentence": "A cup of tea, please."},
            {"word": "sun",   "ipa": "/sʌn/",   "meaning": "mặt trời",       "sentence": "The sun is shining."},
            {"word": "bus",   "ipa": "/bʌs/",   "meaning": "xe buýt",        "sentence": "Take the bus home."},
            {"word": "fun",   "ipa": "/fʌn/",   "meaning": "vui vẻ",         "sentence": "That was so much fun!"},
            {"word": "jump",  "ipa": "/dʒʌmp/", "meaning": "nhảy",           "sentence": "Jump over the puddle."},
            {"word": "love",  "ipa": "/lʌv/",   "meaning": "yêu, tình yêu",  "sentence": "I love this song."},
            {"word": "month", "ipa": "/mʌnθ/",  "meaning": "tháng",          "sentence": "Next month is April."},
            {"word": "come",  "ipa": "/kʌm/",   "meaning": "đến",            "sentence": "Come here, please."},
        ],
    },
    "vowel-o-short": {
        "explanation": (
            "Nguyên âm /ɒ/ — miệng mở rộng, môi tròn nhẹ, lưỡi thấp và lùi ra sau. Âm NGẮN. "
            "Xuất hiện trong: hot, top, clock, dog, box.\n\n"
            "Lưu ý: /ɒ/ chỉ xuất hiện trong tiếng Anh-Anh (BrE). "
            "Tiếng Anh-Mỹ (AmE) dùng /ɑː/ không tròn môi: 'hot' = /hɑːt/."
        ),
        "tip": (
            "Người Việt hay phát âm /ɒ/ như /o/ Việt (dài hơn, tròn hơn). "
            "Mẹo cho BrE: Tưởng tượng bác sĩ bảo 'Há miệng ra!' — cái âm bạn phát ra khi há là /ɒ/. "
            "Ngắn và mở hoàn toàn. KHÔNG kéo dài thành /oː/."
        ),
        "common_mistakes": (
            "1. Kéo dài thành /oː/: 'hot' → /hoːt/ (nghe như 'hort' — sai hoàn toàn).\n"
            "2. Tròn môi quá mức như /uː/: 'top' → 'toop'.\n"
            "3. Nhầm /ɒ/ với /ɔː/: 'cot' /kɒt/ vs 'caught' /kɔːt/ — khác nghĩa!\n"
            "4. Bỏ phụ âm cuối: 'clock' → 'cloc', 'stop' → 'sto', 'box' → 'bok'."
        ),
        "examples": [
            {"word": "hot",   "ipa": "/hɒt/",  "meaning": "nóng",        "sentence": "It's very hot today."},
            {"word": "top",   "ipa": "/tɒp/",  "meaning": "đỉnh, trên",  "sentence": "Put it on top."},
            {"word": "clock", "ipa": "/klɒk/", "meaning": "đồng hồ",     "sentence": "Look at the clock."},
            {"word": "stop",  "ipa": "/stɒp/", "meaning": "dừng lại",    "sentence": "Please stop here."},
            {"word": "dog",   "ipa": "/dɒɡ/",  "meaning": "con chó",     "sentence": "The dog is friendly."},
            {"word": "box",   "ipa": "/bɒks/", "meaning": "hộp",         "sentence": "Open the box."},
            {"word": "rock",  "ipa": "/rɒk/",  "meaning": "đá, nhạc rock", "sentence": "I love rock music."},
            {"word": "shop",  "ipa": "/ʃɒp/",  "meaning": "cửa hàng",    "sentence": "The shop is open."},
        ],
    },
    "vowel-u-long": {
        "explanation": (
            "Nguyên âm dài /uː/ — môi tròn chặt và giơ về phía trước, lưỡi cao và lùi ra sau. "
            "Giữ âm DÀI. Xuất hiện trong: food, moon, blue, school.\n\n"
            "So sánh: /ʊ/ ngắn (book, foot, pull) vs /uː/ dài (food, fool, pool).\n"
            "Cặp dễ nhầm: full /fʊl/ vs fool /fuːl/  |  pull /pʊl/ vs pool /puːl/"
        ),
        "tip": (
            "Người Việt phát âm hình dạng đúng nhưng thường KHÔNG đủ DÀI và tròn môi chưa chặt. "
            "Mẹo: Huýt sáo rồi thêm giọng vào — đó là vị trí của /uː/.\n\n"
            "Cẩn thận 'oo' trong từ: đôi khi là /uː/ (food, moon, cool) "
            "đôi khi là /ʊ/ (book, cook, look) — cần học từng trường hợp!"
        ),
        "common_mistakes": (
            "1. Phát âm quá ngắn: 'food' → /fʊd/ (nghe như 'foot' — mất nghĩa).\n"
            "2. Không tròn môi đủ — môi cần tròn như đang hôn.\n"
            "3. Nhầm 'full' /fʊl/ với 'fool' /fuːl/ (no hay sán lại nghĩa khác).\n"
            "4. Nhầm 'good' /ɡʊd/ vs 'food' /fuːd/ — cùng 'oo' nhưng đọc khác nhau!"
        ),
        "examples": [
            {"word": "food",   "ipa": "/fuːd/",   "meaning": "thức ăn",      "sentence": "The food is delicious."},
            {"word": "moon",   "ipa": "/muːn/",   "meaning": "mặt trăng",    "sentence": "The moon is full tonight."},
            {"word": "school", "ipa": "/skuːl/",  "meaning": "trường học",   "sentence": "I go to school daily."},
            {"word": "cool",   "ipa": "/kuːl/",   "meaning": "mát mẻ, ngầu", "sentence": "Stay cool."},
            {"word": "true",   "ipa": "/truː/",   "meaning": "đúng, thật",   "sentence": "Is that true?"},
            {"word": "blue",   "ipa": "/bluː/",   "meaning": "màu xanh",     "sentence": "The sea is blue."},
            {"word": "room",   "ipa": "/ruːm/",   "meaning": "phòng",        "sentence": "This room is huge."},
            {"word": "tool",   "ipa": "/tuːl/",   "meaning": "công cụ",      "sentence": "Use the right tool."},
        ],
    },
    "vowel-schwa": {
        "explanation": (
            "Schwa /ə/ — âm TRUNG TÍNH nhất trong tiếng Anh: miệng hoàn toàn thư giãn, "
            "lưỡi ở trung tâm, không cao không thấp, không trước không sau. "
            "Đây là âm XUẤT HIỆN NHIỀU NHẤT trong tiếng Anh!\n\n"
            "Quy tắc vàng: Hầu hết âm tiết KHÔNG ĐƯỢC NHẤN đều đọc là /ə/.\n"
            "Ví dụ: 'banana' = /bəˈnɑːnə/ (âm tiết 1 và 3 là /ə/)"
        ),
        "tip": (
            "Người Việt thường đọc TỪNG ÂM TIẾT rõ ràng, không giảm âm → nghe rất 'đọc chính tả', thiếu tự nhiên.\n\n"
            "Mẹo: Nói 'uh' (tiếng ừ khi do dự) — đó là /ə/. "
            "Quy tắc: Nếu không chắc nguyên âm không nhấn đọc gì → hãy thử /ə/ trước!"
        ),
        "common_mistakes": (
            "1. Đọc đầy đủ nguyên âm không nhấn: 'banana' → /bæˈnɑːnɑː/ thay vì /bəˈnɑːnə/.\n"
            "2. Đọc 'the' như /ðiː/ trước phụ âm (đúng chỉ dùng /ðiː/ trước nguyên âm: 'the apple').\n"
            "3. Không giảm 'a/an' thành /ə/: 'a book' = /ə bʊk/, không phải /eɪ bʊk/.\n"
            "4. Nhấn âm tiết không nhấn trong từ dài: 'about' → /ˈæbaʊt/ thay vì /əˈbaʊt/."
        ),
        "examples": [
            {"word": "about",   "ipa": "/əˈbaʊt/",   "meaning": "về, khoảng",    "sentence": "Tell me about yourself."},
            {"word": "sofa",    "ipa": "/ˈsəʊfə/",   "meaning": "ghế sofa",      "sentence": "Sit on the sofa."},
            {"word": "banana",  "ipa": "/bəˈnɑːnə/", "meaning": "quả chuối",     "sentence": "I eat a banana every day."},
            {"word": "teacher", "ipa": "/ˈtiːtʃə/",  "meaning": "giáo viên",     "sentence": "My teacher is kind."},
            {"word": "problem", "ipa": "/ˈprɒbləm/", "meaning": "vấn đề",        "sentence": "No problem at all."},
            {"word": "police",  "ipa": "/pəˈliːs/",  "meaning": "cảnh sát",      "sentence": "Call the police!"},
            {"word": "again",   "ipa": "/əˈɡen/",    "meaning": "lại, lần nữa",  "sentence": "Say that again?"},
            {"word": "button",  "ipa": "/ˈbʌtən/",   "meaning": "cái nút",       "sentence": "Press the button."},
        ],
    },
    # ── Stage 2: Consonants ────────────────────────────────────────────────────
    "consonant-th": {
        "explanation": (
            "Hai âm TH — cả hai đều cần THÒNG ĐẦU LƯỠI ra nhẹ giữa hai hàng răng:\n\n"
            "• /θ/ (voiceless — không rung): think, three, thanks, tooth, north\n"
            "  → Thổi hơi nhẹ qua đầu lưỡi, KHÔNG rung thanh quản.\n\n"
            "• /ð/ (voiced — có rung): this, that, the, mother, breathe\n"
            "  → Giống /θ/ nhưng ĐẶT THÊM GIỌNG vào (rung thanh quản).\n\n"
            "Test: Đặt tay lên cổ họng — /θ/ không rung, /ð/ rung nhẹ."
        ),
        "tip": (
            "Đây là cặp âm thách thức nhất với người Việt! Nhiều người SỢ thò lưỡi ra "
            "nhưng đó là cách DUY NHẤT để phát âm đúng.\n\n"
            "Lỗi 3 dạng người Việt hay mắc:\n"
            "• /θ/ → /t/: 'think' → 'tink', 'three' → 'tree' (phổ biến nhất)\n"
            "• /ð/ → /d/: 'this' → 'dis', 'that' → 'dat'\n"
            "• /ð/ → /z/ (một số giọng miền Nam): 'this' → 'zis'\n\n"
            "Mẹo thực hành: Thử 'teeth' /tiːθ/ — kết thúc bằng lưỡi chạm vào mặt sau của răng trên."
        ),
        "common_mistakes": (
            "1. Thay /θ/ bằng /t/: 'think' → 'tink', 'three' → 'tree' (gây nhầm lớn!).\n"
            "2. Thay /ð/ bằng /d/: 'this' → 'dis', 'the' → 'de'.\n"
            "3. Thay /ð/ bằng /z/ (giọng miền Nam): 'that' → 'zat'.\n"
            "4. Không thò lưỡi ra — đây là điều bắt buộc để phát âm đúng!\n"
            "5. Bỏ âm cuối /θ/: 'tooth' → 'too', 'north' → 'nor'."
        ),
        "examples": [
            {"word": "think",   "ipa": "/θɪŋk/",  "meaning": "nghĩ",        "sentence": "I think you're right."},
            {"word": "this",    "ipa": "/ðɪs/",   "meaning": "cái này",     "sentence": "What is this?"},
            {"word": "three",   "ipa": "/θriː/",  "meaning": "số ba",       "sentence": "I have three cats."},
            {"word": "the",     "ipa": "/ðə/",    "meaning": "(mạo từ)",    "sentence": "The sun is shining."},
            {"word": "thanks",  "ipa": "/θæŋks/", "meaning": "cảm ơn",     "sentence": "Thanks for your help."},
            {"word": "mother",  "ipa": "/ˈmʌðə/", "meaning": "mẹ",         "sentence": "My mother is kind."},
            {"word": "tooth",   "ipa": "/tuːθ/",  "meaning": "cái răng",   "sentence": "I have a toothache."},
            {"word": "breathe", "ipa": "/briːð/", "meaning": "thở",        "sentence": "Breathe in slowly."},
        ],
    },
    "consonant-v-w": {
        "explanation": (
            "Hai âm hoàn toàn KHÁC NHAU — người Việt dễ nhầm vì tiếng Việt chỉ có 1 âm gần giống:\n\n"
            "• /v/ (Voiced labiodental fricative): MÔI DƯỚI chạm nhẹ vào RĂNG TRÊN, thổi hơi có rung.\n"
            "  → Cảm nhận rung ở môi dưới khi nói: van /væn/, very /ˈveri/, love /lʌv/\n\n"
            "• /w/ (Voiced labial-velar approximant): TRÒN MÔI như chuẩn bị huýt sáo, "
            "  KHÔNG dùng răng, rồi trượt nhanh sang nguyên âm tiếp theo.\n"
            "  → wine /waɪn/, well /wel/, water /ˈwɔːtə/\n\n"
            "Cặp tối thiểu: van /væn/ vs wan /wɒn/  |  vine /vaɪn/ vs wine /waɪn/  |  vet /vet/ vs wet /wet/"
        ),
        "tip": (
            "Lỗi số 1 người Việt: Phát âm /w/ bằng răng giống /v/ (dùng cách phát âm /v/ Việt cho cả hai)!\n\n"
            "Mẹo phân biệt:\n"
            "• /v/: Cắn nhẹ môi dưới bằng răng trên, thổi hơi + rung → nghe 'vvvvv'\n"
            "• /w/: Tròn môi như hôn, KHÔNG có răng, trượt sang nguyên âm → 'uuuu-wine'\n\n"
            "Test nhanh: Nói 'wine' — nếu cảm thấy răng trên chạm môi dưới → đó là /v/ sai rồi!"
        ),
        "common_mistakes": (
            "1. Phát âm /w/ như /v/ Việt (có răng): 'wine' → 'vine', 'west' → 'vest', 'world' → 'vorld'.\n"
            "2. Phát âm /v/ không đủ rung — nghe như /f/: 'very' → 'fery', 'love' → 'luf'.\n"
            "3. Thêm nguyên âm phụ trước /w/: 'wait' → 'oo-wait', 'wine' → 'oo-wine'.\n"
            "4. Bỏ phụ âm cuối /v/: 'love' → 'lo', 'have' → 'ha', 'live' → 'li'."
        ),
        "examples": [
            {"word": "van",   "ipa": "/væn/",    "meaning": "xe tải nhỏ",  "sentence": "The van is parked outside."},
            {"word": "wine",  "ipa": "/waɪn/",   "meaning": "rượu vang",   "sentence": "A glass of red wine."},
            {"word": "very",  "ipa": "/ˈveri/",  "meaning": "rất",         "sentence": "That's very kind."},
            {"word": "well",  "ipa": "/wel/",    "meaning": "tốt / giếng", "sentence": "She speaks very well."},
            {"word": "voice", "ipa": "/vɔɪs/",   "meaning": "giọng nói",   "sentence": "Lower your voice."},
            {"word": "water", "ipa": "/ˈwɔːtə/", "meaning": "nước",        "sentence": "Drink more water."},
            {"word": "have",  "ipa": "/hæv/",    "meaning": "có",          "sentence": "I have a question."},
            {"word": "world", "ipa": "/wɜːld/",  "meaning": "thế giới",    "sentence": "Travel the world."},
        ],
    },
    "consonant-r": {
        "explanation": (
            "Phụ âm /r/ tiếng Anh — HOÀN TOÀN KHÁC /r/ tiếng Việt:\n\n"
            "• /r/ Anh (đặc biệt AmE): đầu lưỡi CONG LÊN (retroflex) về phía vòm cứng, "
            "  KHÔNG chạm vào vòm miệng, KHÔNG RUNG. Lưỡi căng và cong.\n\n"
            "• /r/ tiếng Việt: đầu lưỡi rung hoặc uốn theo cách hoàn toàn khác.\n\n"
            "Lưu ý: British English thường KHÔNG đọc /r/ cuối từ hoặc trước phụ âm (non-rhotic): "
            "car /kɑː/, first /fɜːst/. American English đọc đầy đủ."
        ),
        "tip": (
            "Cách luyện /r/ Anh từng bước:\n"
            "1. Nói 'uh' thư giãn\n"
            "2. Từ từ cong đầu lưỡi lên và lùi ra sau — cảm nhận căng dưới lưỡi\n"
            "3. Cộng thêm giọng → /rrrr/\n\n"
            "TUYỆT ĐỐI không rung lưỡi! Nếu lưỡi đang rung → đó là /r/ Việt/Tây Ban Nha, không phải /r/ Anh."
        ),
        "common_mistakes": (
            "1. Rung lưỡi như /r/ Việt: 'rice' nghe như tiếng Tây Ban Nha/Việt.\n"
            "2. Thay /r/ bằng /l/: 'right' → 'light', 'road' → 'load' — lỗi nghiêm trọng, gây nhầm nghĩa!\n"
            "3. Thêm nguyên âm phụ: 'green' → 'guh-reen', 'train' → 'tuh-rain'.\n"
            "4. Bỏ /r/ cuối từ (với AmE): 'car' → 'ca', 'work' → 'wok', 'her' → 'huh'."
        ),
        "examples": [
            {"word": "red",   "ipa": "/red/",    "meaning": "màu đỏ",       "sentence": "Red is a bold colour."},
            {"word": "road",  "ipa": "/rəʊd/",  "meaning": "con đường",    "sentence": "Take the road on the left."},
            {"word": "right", "ipa": "/raɪt/",  "meaning": "đúng, phải",   "sentence": "You are absolutely right."},
            {"word": "room",  "ipa": "/ruːm/",  "meaning": "phòng",        "sentence": "The room is spacious."},
            {"word": "try",   "ipa": "/traɪ/",  "meaning": "thử",          "sentence": "Try your best."},
            {"word": "bring", "ipa": "/brɪŋ/",  "meaning": "mang đến",     "sentence": "Bring your ID, please."},
            {"word": "work",  "ipa": "/wɜːk/",  "meaning": "làm việc",     "sentence": "I love my work."},
            {"word": "sorry", "ipa": "/ˈsɒri/", "meaning": "xin lỗi",      "sentence": "I'm sorry for that."},
        ],
    },
    "consonant-l": {
        "explanation": (
            "Âm /l/ có 2 dạng quan trọng:\n"
            "• Light L (đầu từ hoặc trước nguyên âm): light, late, blue — lưỡi chạm lợi trên, âm sáng.\n"
            "• Dark L (cuối từ hoặc trước phụ âm): fall, well, milk — lưỡi cong về sau, âm tối hơn.\n\n"
            "Cả hai dạng đều cần đầu lưỡi chạm lợi trên, luồng hơi qua hai bên lưỡi."
        ),
        "tip": (
            "Người Việt thường làm /l/ quá nặng hoặc chuyển thành âm gần /n/. "
            "Giữ đầu lưỡi ổn định ở lợi trên và tách rõ light L (đầu từ) với dark L (cuối từ).\n\n"
            "Lỗi ÂM CUỐI phổ biến: Người Việt hay BỎ dark /l/ cuối từ: 'fall' → 'faw', 'call' → 'caw'. "
            "Cần giữ lưỡi chạm lợi trên cho đến khi kết thúc từ!\n\n"
            "Cặp cần phân biệt: /l/ vs /r/ — 'light' /laɪt/ vs 'right' /raɪt/ (hoàn toàn khác nghĩa)."
        ),
        "common_mistakes": (
            "1. Phát âm /l/ như /n/ (nhầm lẫn phụ âm Việt).\n"
            "2. Bỏ dark L ở cuối từ: 'fall' → 'faw', 'call' → 'caw', 'well' → 'weh'.\n"
            "3. Không giữ đầu lưỡi ở đúng vị trí lợi trên.\n"
            "4. Nhầm /l/ và /r/: 'light' → 'right', 'road' → 'load' — gây mất nghĩa!"
        ),
        "examples": [
            {"word": "light", "ipa": "/laɪt/",  "meaning": "ánh sáng",      "sentence": "Turn on the light."},
            {"word": "late",  "ipa": "/leɪt/",  "meaning": "muộn",          "sentence": "Don't be late."},
            {"word": "fall",  "ipa": "/fɔːl/",  "meaning": "mùa thu / ngã", "sentence": "Leaves fall in autumn."},
            {"word": "well",  "ipa": "/wel/",   "meaning": "tốt / giếng",   "sentence": "She speaks English well."},
            {"word": "help",  "ipa": "/help/",  "meaning": "giúp đỡ",       "sentence": "Can you help me?"},
            {"word": "girl",  "ipa": "/ɡɜːl/",  "meaning": "cô gái",        "sentence": "She's a smart girl."},
            {"word": "blue",  "ipa": "/bluː/",  "meaning": "màu xanh",      "sentence": "The sky is blue."},
            {"word": "smile", "ipa": "/smaɪl/", "meaning": "nụ cười",       "sentence": "Give me a smile."},
        ],
    },
    "consonant-ng": {
        "explanation": (
            "Âm /ŋ/ là âm mũi cổ họng — lưỡi chạm vào vòm mềm (soft palate) phía sau miệng, "
            "KHÔNG mở miệng. Khác với /n/ (đầu lưỡi chạm lợi trên) và /m/ (môi đóng).\n\n"
            "So sánh 3 âm mũi: /m/ → môi | /n/ → đầu lưỡi + lợi | /ŋ/ → cuối lưỡi + vòm mềm."
        ),
        "tip": (
            "Thử nói 'singing' — cảm nhận rung ở cổ họng, không phải ở mũi hay môi. "
            "Người Việt thường thêm /g/ ở cuối nghe như /ŋg/.\n\n"
            "Kiểm tra: Bịt mũi khi nói /ŋ/ — âm phải thay đổi (tắc lại) mới đúng là âm mũi. "
            "Mẹo nhớ: /ŋ/ = 'ng' cuối từ tiếng Anh, KHÔNG có âm /g/ theo sau (singing ≠ singging)."
        ),
        "common_mistakes": (
            "1. Thêm âm /g/ sau /ŋ/: 'sing' → 'sing-g', 'long' → 'long-g'.\n"
            "2. Thay /ŋ/ bằng /n/: 'long' → 'lon', 'ring' → 'rin'.\n"
            "3. Bỏ âm cuối hoàn toàn: 'running' → 'runnin', 'going' → 'goein'.\n"
            "4. Nhầm '-ng' Việt (nặng hơn, thường kèm /g/) với /ŋ/ Anh (chỉ thuần âm mũi)."
        ),
        "examples": [
            {"word": "sing",    "ipa": "/sɪŋ/",      "meaning": "hát",           "sentence": "I love to sing."},
            {"word": "long",    "ipa": "/lɒŋ/",      "meaning": "dài",           "sentence": "It's a long road."},
            {"word": "running", "ipa": "/ˈrʌnɪŋ/",  "meaning": "đang chạy",    "sentence": "She is running fast."},
            {"word": "thing",   "ipa": "/θɪŋ/",      "meaning": "thứ gì đó",    "sentence": "What a strange thing."},
            {"word": "strong",  "ipa": "/strɒŋ/",    "meaning": "mạnh mẽ",      "sentence": "He is very strong."},
            {"word": "English", "ipa": "/ˈɪŋɡlɪʃ/", "meaning": "tiếng Anh",   "sentence": "I study English."},
            {"word": "morning", "ipa": "/ˈmɔːnɪŋ/",  "meaning": "buổi sáng",   "sentence": "Good morning!"},
            {"word": "wrong",   "ipa": "/rɒŋ/",      "meaning": "sai, không đúng", "sentence": "That's wrong."},
        ],
    },
    "consonant-sh-zh": {
        "explanation": (
            "Hai âm cùng vị trí khớp, chỉ khác rung:\n\n"
            "• /ʃ/ (voiceless): she, shop, fish, push — môi tròn, lưỡi tiến gần vòm cứng, hơi mạnh, không rung.\n"
            "• /ʒ/ (voiced): measure, vision, usually — giống /ʃ/ nhưng có rung thanh quản.\n\n"
            "Test rung: Đặt tay lên cổ — /ʃ/ không rung, /ʒ/ rung nhẹ."
        ),
        "tip": (
            "Người Việt thường thay /ʃ/ bằng /s/ và bỏ /ʒ/ hoàn toàn. "
            "Mẹo nhớ /ʃ/: Tưởng tượng bạn đang nói 'shush!' (im đi!) với ai đó — đó là /ʃ/.\n\n"
            "/ʒ/ rất hiếm đứng đầu từ tiếng Anh — chủ yếu ở GIỮA từ (measure, vision, usual). "
            "Không cần quá lo về /ʒ/ ở đầu từ.\n\n"
            "Cặp cần phân biệt: ship /ʃɪp/ vs sip /sɪp/ — 'tàu' vs 'nhấp chút' — hoàn toàn khác!"
        ),
        "common_mistakes": (
            "1. /ʃ/ → /s/: 'ship' → 'sip', 'she' → 'sea', 'fish' → 'fis' — gây hiểu nhầm.\n"
            "2. /ʒ/ → /z/ hoặc /j/: 'measure' → 'me-zer' hoặc 'me-yer'.\n"
            "3. Không tròn môi khi phát âm /ʃ/ — môi cần hơi tròn về phía trước.\n"
            "4. Bỏ âm cuối: 'fish' → 'fi', 'push' → 'pu', 'fresh' → 'fre'."
        ),
        "examples": [
            {"word": "she",     "ipa": "/ʃiː/",        "meaning": "cô ấy",       "sentence": "She is my friend."},
            {"word": "shop",    "ipa": "/ʃɒp/",        "meaning": "cửa hàng",    "sentence": "Let's go to the shop."},
            {"word": "fish",    "ipa": "/fɪʃ/",        "meaning": "con cá",      "sentence": "I like fish."},
            {"word": "push",    "ipa": "/pʊʃ/",        "meaning": "đẩy",         "sentence": "Push the door open."},
            {"word": "measure", "ipa": "/ˈmeʒə/",      "meaning": "đo lường",    "sentence": "Measure the room."},
            {"word": "vision",  "ipa": "/ˈvɪʒən/",     "meaning": "tầm nhìn",    "sentence": "She has great vision."},
            {"word": "usually", "ipa": "/ˈjuːʒuəli/",  "meaning": "thường thì",  "sentence": "I usually wake up early."},
            {"word": "fresh",   "ipa": "/freʃ/",        "meaning": "tươi mát",    "sentence": "The air is fresh."},
        ],
    },
    # ── Stage 3: Diphthongs ────────────────────────────────────────────────────
    "diphthong-ei": {
        "explanation": (
            "Âm đôi /eɪ/ bắt đầu từ /e/ (miệng mở vừa, lưỡi tiến ra trước) "
            "rồi TRƯỢT LÊN /ɪ/ (miệng hẹp lại). Đây là MỘT âm liền mạch, không tách rời.\n\n"
            "Xuất hiện trong: day, say, rain, name, face, game, wait, they.\n"
            "So sánh 3 âm: /eɪ/ (say) vs /e/ (set) vs /æ/ (sat) — ba khẩu hình và độ dài khác nhau!"
        ),
        "tip": (
            "Người Việt thường phát âm /eɪ/ ngắn như /e/ hoặc như /ê/ Việt — thiếu phần trượt lên.\n\n"
            "Mẹo: Nói 'A-I' nhanh → gần với /eɪ/. Quan trọng: đây không phải hai âm riêng lẻ mà là một âm trượt.\n\n"
            "Cảm nhận: miệng bắt đầu mở rồi hẹp dần — đó là âm đôi đúng chuẩn."
        ),
        "common_mistakes": (
            "1. Không trượt — 'day' nghe như 'deh': thiếu phần /ɪ/ cuối.\n"
            "2. Nhầm với /aɪ/: 'say' → 'sigh', 'late' → 'light' — gây nhầm nghĩa!\n"
            "3. Kéo /e/ dài thay vì trượt sang /ɪ/.\n"
            "4. Bỏ âm cuối phụ âm: 'wait' → 'way', 'face' → 'fay', 'great' → 'grey'."
        ),
        "examples": [
            {"word": "day",   "ipa": "/deɪ/",   "meaning": "ngày",         "sentence": "Have a great day!"},
            {"word": "say",   "ipa": "/seɪ/",   "meaning": "nói",          "sentence": "What did you say?"},
            {"word": "rain",  "ipa": "/reɪn/",  "meaning": "mưa",          "sentence": "It might rain today."},
            {"word": "name",  "ipa": "/neɪm/",  "meaning": "tên",          "sentence": "What's your name?"},
            {"word": "face",  "ipa": "/feɪs/",  "meaning": "khuôn mặt",    "sentence": "Wash your face."},
            {"word": "wait",  "ipa": "/weɪt/",  "meaning": "chờ đợi",      "sentence": "Please wait a moment."},
            {"word": "break", "ipa": "/breɪk/", "meaning": "nghỉ / vỡ",   "sentence": "Let's take a break."},
            {"word": "great", "ipa": "/ɡreɪt/", "meaning": "tuyệt vời",    "sentence": "That's great news!"},
        ],
    },
    "diphthong-ai": {
        "explanation": (
            "Âm đôi /aɪ/ bắt đầu từ /a/ (miệng mở rộng) rồi trượt lên /ɪ/ (miệng hẹp lại). "
            "Xuất hiện trong: my, time, night, high, buy.\n\n"
            "So sánh: /aɪ/ (buy) vs /eɪ/ (bay) vs /ɔɪ/ (boy) — ba âm đôi cần phân biệt rõ."
        ),
        "tip": (
            "/aɪ/ là âm trượt — bắt đầu ở vị trí thấp, kết thúc ở vị trí cao. "
            "Người Việt thường phát âm quá ngắn hoặc như /a/ đơn.\n\n"
            "Thử: Nói 'a' rồi nhanh chóng chuyển sang 'i' — đó là /aɪ/. "
            "So sánh: my /maɪ/ vs may /meɪ/ — /aɪ/ bắt đầu thấp hơn, miệng mở rộng hơn /eɪ/."
        ),
        "common_mistakes": (
            "1. Phát âm như /a/ thuần: 'time' → 'tam' hoặc 'taim' (không đủ trượt).\n"
            "2. Không trượt đủ lên /ɪ/: âm nghe thiếu, không tự nhiên.\n"
            "3. Nhầm với /eɪ/: 'my' → 'may', 'night' → 'nate'.\n"
            "4. Bỏ âm cuối: 'night' → 'nai', 'white' → 'wai', 'right' → 'rai'."
        ),
        "examples": [
            {"word": "my",    "ipa": "/maɪ/",   "meaning": "của tôi",     "sentence": "This is my book."},
            {"word": "time",  "ipa": "/taɪm/",  "meaning": "thời gian",   "sentence": "What time is it?"},
            {"word": "night", "ipa": "/naɪt/",  "meaning": "đêm",         "sentence": "Good night."},
            {"word": "high",  "ipa": "/haɪ/",   "meaning": "cao",         "sentence": "The mountain is high."},
            {"word": "buy",   "ipa": "/baɪ/",   "meaning": "mua",         "sentence": "I want to buy this."},
            {"word": "sky",   "ipa": "/skaɪ/",  "meaning": "bầu trời",    "sentence": "The sky is clear."},
            {"word": "white", "ipa": "/waɪt/",  "meaning": "màu trắng",   "sentence": "A white shirt."},
            {"word": "life",  "ipa": "/laɪf/",  "meaning": "cuộc sống",   "sentence": "Life is beautiful."},
        ],
    },
    "diphthong-oi": {
        "explanation": (
            "Âm đôi /ɔɪ/ bắt đầu từ /ɔː/ (miệng tròn, lưỡi thấp) rồi trượt lên /ɪ/. "
            "Xuất hiện trong: boy, coin, voice, enjoy.\n\n"
            "So sánh cặp 3: boy /bɔɪ/ vs bay /beɪ/ vs buy /baɪ/ — ba âm đôi, ba khẩu hình đầu khác nhau!"
        ),
        "tip": (
            "Cảm nhận miệng tròn ở đầu âm rồi mở rộng sang phải khi trượt lên /ɪ/. "
            "Người Việt thường phát âm quá nhẹ, giống /oi/ Việt không đủ mở.\n\n"
            "/ɔɪ/ Anh có phần /ɔː/ mở và tròn rõ hơn, sau đó trượt rõ lên /ɪ/. "
            "Mẹo: Nói 'or' rồi nhanh chóng chuyển lên 'ee' ngắn — đó là /ɔɪ/."
        ),
        "common_mistakes": (
            "1. Không tròn môi ở phần đầu /ɔ/ — âm nghe giống /a/ lướt hơn.\n"
            "2. Âm quá ngắn, không đủ độ trượt rõ.\n"
            "3. Nhầm với /aɪ/: 'boy' → 'buy', 'coin' → 'kine' — gây nhầm nghĩa!\n"
            "4. Bỏ âm cuối: 'voice' → 'voi', 'point' → 'poi', 'noise' → 'noi'."
        ),
        "examples": [
            {"word": "boy",   "ipa": "/bɔɪ/",      "meaning": "cậu bé",      "sentence": "The boy is smart."},
            {"word": "coin",  "ipa": "/kɔɪn/",     "meaning": "đồng tiền",   "sentence": "A gold coin."},
            {"word": "voice", "ipa": "/vɔɪs/",     "meaning": "giọng nói",   "sentence": "She has a lovely voice."},
            {"word": "enjoy", "ipa": "/ɪnˈdʒɔɪ/",  "meaning": "thích thú",  "sentence": "Enjoy the music."},
            {"word": "oil",   "ipa": "/ɔɪl/",      "meaning": "dầu",         "sentence": "Add some oil."},
            {"word": "choice","ipa": "/tʃɔɪs/",    "meaning": "lựa chọn",   "sentence": "Make a choice."},
            {"word": "point", "ipa": "/pɔɪnt/",    "meaning": "điểm, chỉ",  "sentence": "That's a good point."},
            {"word": "noise", "ipa": "/nɔɪz/",     "meaning": "tiếng ồn",   "sentence": "What's that noise?"},
        ],
    },
    "diphthong-ou": {
        "explanation": (
            "Âm đôi /əʊ/ bắt đầu từ /ə/ (âm trung tính, miệng thư giãn) "
            "rồi tròn môi trượt lên /ʊ/ (môi tròn hơn). Xuất hiện trong: go, home, phone, snow, cold.\n\n"
            "Lưu ý: Tiếng Anh-Anh (BrE) dùng /əʊ/, tiếng Anh-Mỹ (AmE) dùng /oʊ/ (bắt đầu từ /o/).\n"
            "Phân biệt: /əʊ/ (go, home) vs /aʊ/ (now, out, house) — hai âm hoàn toàn khác!"
        ),
        "tip": (
            "Người Việt thường phát âm /əʊ/ như /o/ thuần Việt — không trượt. "
            "Mẹo: Bắt đầu từ 'uh' thư giãn /ə/, rồi tròn dần môi lên /ʊ/ — cảm nhận môi chuyển động.\n\n"
            "Dễ nhầm: 'go' /ɡəʊ/ vs 'cow' /kaʊ/:\n"
            "• /əʊ/: bắt đầu trung tính, không há rộng miệng\n"
            "• /aʊ/: bắt đầu từ 'a' miệng mở, sau đó tròn lại — nghe rõ phần 'ow'."
        ),
        "common_mistakes": (
            "1. Phát âm thẳng /oː/ thay vì trượt: 'go' → /ɡoː/ — thiếu độ trượt.\n"
            "2. Nhầm /əʊ/ với /aʊ/: 'home' → 'howm', 'phone' → 'fown' — miệng mở quá rộng.\n"
            "3. Không tròn môi đủ ở phần cuối /ʊ/.\n"
            "4. Bỏ âm cuối: 'cold' → 'col', 'phone' → 'foh', 'hope' → 'hoh'."
        ),
        "examples": [
            {"word": "go",    "ipa": "/ɡəʊ/",   "meaning": "đi",           "sentence": "Let's go now."},
            {"word": "home",  "ipa": "/həʊm/",  "meaning": "nhà",          "sentence": "I'm going home."},
            {"word": "phone", "ipa": "/fəʊn/",  "meaning": "điện thoại",   "sentence": "My phone is dead."},
            {"word": "snow",  "ipa": "/snəʊ/",  "meaning": "tuyết",        "sentence": "It might snow tonight."},
            {"word": "cold",  "ipa": "/kəʊld/", "meaning": "lạnh",         "sentence": "It's very cold today."},
            {"word": "road",  "ipa": "/rəʊd/",  "meaning": "con đường",    "sentence": "The road is clear."},
            {"word": "hope",  "ipa": "/həʊp/",  "meaning": "hy vọng",      "sentence": "I hope you're well."},
            {"word": "boat",  "ipa": "/bəʊt/",  "meaning": "con thuyền",   "sentence": "We took a boat trip."},
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


def _build_quiz(examples, count=6):
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
