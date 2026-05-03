"""
seed_lesson_content — populate LessonContent for all seeded lessons.

Usage:
    python manage.py seed_lesson_content [--level A1] [--clear]

Uses a hand-crafted CONTENT_MAP keyed by chapter title + lesson order.
For lessons not in the map, auto-generates a minimal placeholder.
"""
from django.core.management.base import BaseCommand
from apps.curriculum.models import Chapter, Course, Lesson, LessonContent
from apps.grammar.models import GrammarTopic

# ---------------------------------------------------------------------------
# CONTENT MAP
# key  = (chapter_title, lesson_order)
# Each entry has all fields of LessonContent.
# ---------------------------------------------------------------------------

CONTENT_MAP = {

    # ════════════════════════════════════════════════════════════════════
    # A1 — Chapter 1: Giới thiệu bản thân
    # ════════════════════════════════════════════════════════════════════
    ("Giới thiệu bản thân", 1): {
        "reading_passage": (
            "<p>Hi! My name is <strong>Linh</strong>. I am 22 years old. "
            "I am a student. I am from Vietnam. I am Vietnamese.</p>"
            "<p>This is my friend <strong>Tom</strong>. He is 25 years old. "
            "He is a teacher. He is from England. He is British.</p>"
            "<p>Nice to meet you!</p>"
        ),
        "reading_questions": [
            {"question": "How old is Linh?", "options": ["20", "22", "25", "30"], "correct": 1, "explanation": "The passage says 'I am 22 years old.'"},
            {"question": "What is Tom's job?", "options": ["student", "doctor", "teacher", "engineer"], "correct": 2, "explanation": "'He is a teacher.'"},
            {"question": "Where is Tom from?", "options": ["Vietnam", "France", "England", "Australia"], "correct": 2, "explanation": "'He is from England.'"},
        ],
        "vocab_items": [
            {"word": "name", "pos": "noun", "ipa": "/neɪm/", "meaning_vi": "tên", "definition_en": "What you are called.", "example_en": "My name is Linh.", "example_vi": "Tên tôi là Linh.", "collocations": ["my name is", "what's your name"], "highlight_in_passage": True},
            {"word": "student", "pos": "noun", "ipa": "/ˈstjuː.dənt/", "meaning_vi": "học sinh / sinh viên", "definition_en": "A person who is studying.", "example_en": "She is a student.", "example_vi": "Cô ấy là sinh viên.", "collocations": ["university student", "a good student"], "highlight_in_passage": True},
            {"word": "teacher", "pos": "noun", "ipa": "/ˈtiː.tʃər/", "meaning_vi": "giáo viên", "definition_en": "A person who teaches.", "example_en": "He is a teacher.", "example_vi": "Anh ấy là giáo viên.", "collocations": ["English teacher", "maths teacher"], "highlight_in_passage": True},
            {"word": "friend", "pos": "noun", "ipa": "/frend/", "meaning_vi": "bạn bè", "definition_en": "A person you like and know well.", "example_en": "She is my friend.", "example_vi": "Cô ấy là bạn tôi.", "collocations": ["best friend", "an old friend"], "highlight_in_passage": True},
            {"word": "old", "pos": "adjective", "ipa": "/əʊld/", "meaning_vi": "tuổi / già", "definition_en": "Used to talk about age.", "example_en": "I am 22 years old.", "example_vi": "Tôi 22 tuổi.", "collocations": ["years old", "how old"], "highlight_in_passage": True},
            {"word": "nationality", "pos": "noun", "ipa": "/ˌnæʃ.ənˈæl.ɪ.ti/", "meaning_vi": "quốc tịch", "definition_en": "The country you belong to.", "example_en": "His nationality is British.", "example_vi": "Quốc tịch anh ấy là Anh.", "collocations": ["Vietnamese nationality", "what nationality"], "highlight_in_passage": False},
            {"word": "meet", "pos": "verb", "ipa": "/miːt/", "meaning_vi": "gặp / làm quen", "definition_en": "To see and talk to someone for the first time.", "example_en": "Nice to meet you.", "example_vi": "Rất vui được gặp bạn.", "collocations": ["nice to meet", "meet someone"], "highlight_in_passage": True},
            {"word": "from", "pos": "preposition", "ipa": "/frɒm/", "meaning_vi": "từ / đến từ", "definition_en": "Used to show where someone was born or lives.", "example_en": "She is from Vietnam.", "example_vi": "Cô ấy đến từ Việt Nam.", "collocations": ["from Vietnam", "where are you from"], "highlight_in_passage": True},
        ],
        "grammar_title": "Present simple of 'be': am / is / are",
        "grammar_note": (
            "We use **am**, **is**, **are** to introduce ourselves and describe people.\n\n"
            "• I **am** (I'm) a student.\n"
            "• He / She / It **is** (He's) a teacher.\n"
            "• You / We / They **are** (You're) from England.\n\n"
            "Notice the contractions: I'm, He's, She's, You're, We're, They're."
        ),
        "grammar_examples": [
            {"en": "I am a student.", "vi": "Tôi là sinh viên.", "highlight": "am"},
            {"en": "She is 22 years old.", "vi": "Cô ấy 22 tuổi.", "highlight": "is"},
            {"en": "We are from Vietnam.", "vi": "Chúng tôi đến từ Việt Nam.", "highlight": "are"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "___ name is Tom. ___ is 25 years old.", "options": ["My / He", "His / He", "My / His", "Her / She"], "correct": 0, "explanation": "'My name is...' and 'He is...' — subject pronoun He takes 'is'."},
            {"type": "gap-fill", "prompt": "Nice to ___ you! Where ___ you from?", "options": ["meet / are", "meeting / is", "met / am", "meet / is"], "correct": 0, "explanation": "'Nice to meet you' is a fixed phrase. 'Where are you from?' uses 'are' with 'you'."},
            {"type": "mc", "prompt": "Choose the correct sentence:", "options": ["I is a teacher.", "He am a student.", "She is from France.", "They is friends."], "correct": 2, "explanation": "'She is' — third person singular uses 'is'."},
            {"type": "error", "prompt": "Find the error: 'My friend he is a doctor.'", "options": ["My friend → My friends", "'he is' is redundant — use only 'My friend is'", "doctor → doctors", "No error"], "correct": 1, "explanation": "In English, don't repeat the subject: 'My friend **is** a doctor.' — not 'My friend he is...'"},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Giới thiệu bản thân", 2): {
        "reading_passage": "",
        "reading_questions": [],
        "vocab_items": [],
        "grammar_title": "Present simple of 'be': Negatives & Questions",
        "grammar_note": (
            "**Negative:** am/is/are + **not**\n"
            "• I **am not** (I'm not) a doctor.\n"
            "• He **is not** (isn't) from France.\n"
            "• They **are not** (aren't) students.\n\n"
            "**Question:** am/is/are + subject\n"
            "• **Are** you a teacher? — Yes, I am. / No, I'm not.\n"
            "• **Is** she from England? — Yes, she is. / No, she isn't."
        ),
        "grammar_examples": [
            {"en": "I am not a doctor.", "vi": "Tôi không phải là bác sĩ.", "highlight": "am not"},
            {"en": "Is he from France?", "vi": "Anh ấy có phải đến từ Pháp không?", "highlight": "Is"},
            {"en": "No, he isn't. He is from England.", "vi": "Không, anh ấy không phải. Anh ấy đến từ Anh.", "highlight": "isn't"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "___ she a student? No, she ___.", "options": ["Is / isn't", "Are / aren't", "Is / is", "Am / isn't"], "correct": 0, "explanation": "'Is she...' — third person singular. Short answer: 'No, she isn't.'"},
            {"type": "rewrite", "prompt": "Rewrite as negative: 'They are from France.'", "options": ["They are not from France.", "They not are from France.", "They aren't from France. ✓ (same as above)", "They isn't from France."], "correct": 2, "explanation": "'They are not' or 'They aren't' — both are correct."},
            {"type": "mc", "prompt": "Which question is correct?", "options": ["Are you from Vietnam?", "Is you a teacher?", "Am he your friend?", "Are he and she students?"], "correct": 0, "explanation": "'Are you' — second person uses 'are'."},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Giới thiệu bản thân", 3): {
        "reading_passage": (
            "<p>Read this profile page:</p>"
            "<blockquote>"
            "<strong>Name:</strong> Anna Smith<br>"
            "<strong>Age:</strong> 28<br>"
            "<strong>Job:</strong> Doctor<br>"
            "<strong>Country:</strong> Canada<br>"
            "<strong>Languages:</strong> English and French<br>"
            "<strong>Hobbies:</strong> reading, cooking, and travelling"
            "</blockquote>"
            "<p>Anna is not a student. She is a doctor. She is from Canada, "
            "not from England. She speaks English and French. "
            "Her hobbies are reading, cooking, and travelling.</p>"
        ),
        "reading_questions": [
            {"question": "Is Anna a student?", "options": ["Yes, she is.", "No, she isn't.", "We don't know.", "Yes, she's a student and a doctor."], "correct": 1, "explanation": "'She is not a student. She is a doctor.'"},
            {"question": "How many languages does Anna speak?", "options": ["one", "two", "three", "four"], "correct": 1, "explanation": "English and French — that's two languages."},
            {"question": "What is one of Anna's hobbies?", "options": ["swimming", "cooking", "singing", "gaming"], "correct": 1, "explanation": "'Her hobbies are reading, cooking, and travelling.'"},
        ],
        "vocab_items": [
            {"word": "doctor", "pos": "noun", "ipa": "/ˈdɒk.tər/", "meaning_vi": "bác sĩ", "definition_en": "A person who treats ill people.", "example_en": "She is a doctor.", "example_vi": "Cô ấy là bác sĩ.", "collocations": ["see a doctor", "family doctor"], "highlight_in_passage": True},
            {"word": "hobby", "pos": "noun", "ipa": "/ˈhɒb.i/", "meaning_vi": "sở thích", "definition_en": "An activity you do for pleasure.", "example_en": "My hobby is reading.", "example_vi": "Sở thích của tôi là đọc sách.", "collocations": ["hobby is", "what's your hobby"], "highlight_in_passage": True},
            {"word": "language", "pos": "noun", "ipa": "/ˈlæŋ.ɡwɪdʒ/", "meaning_vi": "ngôn ngữ", "definition_en": "A system of communication used by people.", "example_en": "English is an international language.", "example_vi": "Tiếng Anh là ngôn ngữ quốc tế.", "collocations": ["speak a language", "foreign language"], "highlight_in_passage": True},
        ],
        "grammar_title": "Possessive adjectives: my, your, his, her, its, our, their",
        "grammar_note": (
            "Possessive adjectives show who something belongs to.\n\n"
            "| Subject | Possessive |\n"
            "|---------|------------|\n"
            "| I | **my** |\n"
            "| you | **your** |\n"
            "| he | **his** |\n"
            "| she | **her** |\n"
            "| it | **its** |\n"
            "| we | **our** |\n"
            "| they | **their** |\n\n"
            "Always followed by a noun: **my** name, **her** hobby, **their** country."
        ),
        "grammar_examples": [
            {"en": "Her name is Anna.", "vi": "Tên cô ấy là Anna.", "highlight": "Her"},
            {"en": "My hobby is cooking.", "vi": "Sở thích của tôi là nấu ăn.", "highlight": "My"},
            {"en": "Their languages are English and French.", "vi": "Ngôn ngữ của họ là tiếng Anh và tiếng Pháp.", "highlight": "Their"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "___ name is Tom and ___ hobby is football.", "options": ["His / his", "He / him", "His / him", "Her / her"], "correct": 0, "explanation": "Both 'his name' and 'his hobby' — Tom is male so use 'his'."},
            {"type": "gap-fill", "prompt": "Anna speaks two languages. ___ languages are English and French.", "options": ["Her", "His", "Their", "Its"], "correct": 0, "explanation": "Anna is female → 'Her languages'."},
            {"type": "error", "prompt": "Find the error: 'What is you name?'", "options": ["What → Which", "is → are", "you → your", "No error"], "correct": 2, "explanation": "'you' cannot come before a noun. Use possessive 'your': 'What is **your** name?'"},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Giới thiệu bản thân", 7): {
        "grammar_note": "This is your chapter review. Use what you've learned to complete the exercises. Questions cover 'be' verb in positive, negative, and question forms, plus possessive adjectives.",
        "grammar_examples": [],
        "exercises": [
            {"type": "gap-fill", "prompt": "Hi! I ___ Minh. I ___ 20 years old.", "options": ["am / am", "is / am", "am / is", "are / am"], "correct": 0, "explanation": "'I am Minh. I am 20 years old.' — use 'am' with 'I'."},
            {"type": "gap-fill", "prompt": "___ you a teacher? No, I ___ not.", "options": ["Are / am", "Is / am", "Are / is", "Am / are"], "correct": 0, "explanation": "'Are you a teacher? No, I am not.' — question with 'you' uses 'are', short answer 'I am not'."},
            {"type": "mc", "prompt": "Complete: '___ name is Linh and ___ is from Hanoi.'", "options": ["Her / she", "She / her", "His / he", "Hers / she"], "correct": 0, "explanation": "'Her name is Linh and **she** is from Hanoi.' — possessive 'Her' before noun, subject pronoun 'she' before verb."},
            {"type": "cloze", "prompt": "Fill in: My [1] is Tom. I'm [2] England. I'm not a student — I'm a [3]. Nice to [4] you!", "options": [["name","age","hobby","job"], ["from","in","at","on"], ["teacher","teaching","teach","teaches"], ["meet","meeting","met","meets"]], "correct": [0, 0, 0, 0], "explanation": "name / from / teacher / meet — all fixed phrases practised in this chapter."},
        ],
        "completion_xp": 15,
        "bonus_xp": 60,
    },

    # ════════════════════════════════════════════════════════════════════
    # A1 — Chapter 2: Gia đình & Bạn bè
    # ════════════════════════════════════════════════════════════════════
    ("Gia đình & Bạn bè", 1): {
        "reading_passage": (
            "<p>This is <strong>Mai's family</strong>.</p>"
            "<p>Her father is <strong>Mr Hung</strong>. He is 52 years old. "
            "He is an engineer. Her mother is <strong>Mrs Lan</strong>. "
            "She is 48 years old. She is a nurse.</p>"
            "<p>Mai has one brother and one sister. "
            "Her brother's name is <strong>Nam</strong>. He is 19 years old. "
            "Her sister's name is <strong>Thao</strong>. She is 15 years old. "
            "They are both students.</p>"
            "<p>Mai loves her family very much.</p>"
        ),
        "reading_questions": [
            {"question": "What is Mai's father's job?", "options": ["doctor", "teacher", "engineer", "nurse"], "correct": 2, "explanation": "'He is an engineer.'"},
            {"question": "How old is Mai's sister Thao?", "options": ["12", "15", "19", "48"], "correct": 1, "explanation": "'She is 15 years old.'"},
            {"question": "What do Nam and Thao have in common?", "options": ["They are both engineers.", "They are both students.", "They are both nurses.", "They are both from Hanoi."], "correct": 1, "explanation": "'They are both students.'"},
        ],
        "vocab_items": [
            {"word": "family", "pos": "noun", "ipa": "/ˈfæm.ɪ.li/", "meaning_vi": "gia đình", "definition_en": "A group of people related to each other.", "example_en": "I have a small family.", "example_vi": "Tôi có một gia đình nhỏ.", "collocations": ["family member", "start a family", "family life"], "highlight_in_passage": True},
            {"word": "father", "pos": "noun", "ipa": "/ˈfɑː.ðər/", "meaning_vi": "bố / cha", "definition_en": "Your male parent.", "example_en": "My father is a doctor.", "example_vi": "Bố tôi là bác sĩ.", "collocations": ["my father", "father and mother"], "highlight_in_passage": True},
            {"word": "mother", "pos": "noun", "ipa": "/ˈmʌð.ər/", "meaning_vi": "mẹ", "definition_en": "Your female parent.", "example_en": "Her mother is a nurse.", "example_vi": "Mẹ cô ấy là y tá.", "collocations": ["my mother", "mother tongue"], "highlight_in_passage": True},
            {"word": "brother", "pos": "noun", "ipa": "/ˈbrʌð.ər/", "meaning_vi": "anh/em trai", "definition_en": "A boy or man who has the same parents as you.", "example_en": "My brother is 19.", "example_vi": "Anh/em trai tôi 19 tuổi.", "collocations": ["older brother", "younger brother"], "highlight_in_passage": True},
            {"word": "sister", "pos": "noun", "ipa": "/ˈsɪs.tər/", "meaning_vi": "chị/em gái", "definition_en": "A girl or woman who has the same parents as you.", "example_en": "I have a younger sister.", "example_vi": "Tôi có một em gái.", "collocations": ["older sister", "younger sister"], "highlight_in_passage": True},
            {"word": "nurse", "pos": "noun", "ipa": "/nɜːs/", "meaning_vi": "y tá", "definition_en": "A person who cares for ill people in a hospital.", "example_en": "My aunt is a nurse.", "example_vi": "Dì tôi là y tá.", "collocations": ["trained nurse", "hospital nurse"], "highlight_in_passage": True},
            {"word": "engineer", "pos": "noun", "ipa": "/ˌen.dʒɪˈnɪər/", "meaning_vi": "kỹ sư", "definition_en": "A person who designs or builds machines and structures.", "example_en": "He works as an engineer.", "example_vi": "Anh ấy làm kỹ sư.", "collocations": ["civil engineer", "software engineer"], "highlight_in_passage": True},
            {"word": "love", "pos": "verb", "ipa": "/lʌv/", "meaning_vi": "yêu thương", "definition_en": "To have a very strong feeling of caring for someone.", "example_en": "I love my family.", "example_vi": "Tôi yêu gia đình mình.", "collocations": ["love your family", "fall in love"], "highlight_in_passage": True},
        ],
        "grammar_title": "This, that, these, those + have/has",
        "grammar_note": (
            "Use **this/these** for things near you, **that/those** for things far away.\n"
            "• **This** is my mother. (singular, near)\n"
            "• **These** are my brothers. (plural, near)\n"
            "• **That** is my sister. (singular, far)\n"
            "• **Those** are my friends. (plural, far)\n\n"
            "**Have/has** to talk about family:\n"
            "• I/You/We/They **have** one brother.\n"
            "• He/She/It **has** two sisters."
        ),
        "grammar_examples": [
            {"en": "This is my father.", "vi": "Đây là bố tôi.", "highlight": "This"},
            {"en": "She has one brother.", "vi": "Cô ấy có một anh trai.", "highlight": "has"},
            {"en": "Those are my friends.", "vi": "Đó là những người bạn của tôi.", "highlight": "Those"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "___ is my mother and ___ are my brothers.", "options": ["This / these", "That / those", "These / this", "Those / that"], "correct": 0, "explanation": "'This' = one person near, 'these' = multiple people near."},
            {"type": "gap-fill", "prompt": "My brother ___ two children. I ___ one child.", "options": ["has / have", "have / has", "has / has", "have / have"], "correct": 0, "explanation": "'He has' (third person singular), 'I have' (first person)."},
            {"type": "mc", "prompt": "Which sentence is correct?", "options": ["She have a brother.", "He has two sister.", "They has one car.", "I have a big family."], "correct": 3, "explanation": "'I have' is correct. 'She has', 'He has' need 'has', 'They have'."},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Gia đình & Bạn bè", 2): {
        "reading_passage": "",
        "reading_questions": [],
        "vocab_items": [
            {"word": "tall", "pos": "adjective", "ipa": "/tɔːl/", "meaning_vi": "cao", "definition_en": "Having a greater than average height.", "example_en": "He is very tall.", "example_vi": "Anh ấy rất cao.", "collocations": ["tall and thin", "tall building"], "highlight_in_passage": False},
            {"word": "short", "pos": "adjective", "ipa": "/ʃɔːt/", "meaning_vi": "thấp / ngắn", "definition_en": "Having less than average height.", "example_en": "She is short with long hair.", "example_vi": "Cô ấy thấp với mái tóc dài.", "collocations": ["short hair", "short and slim"], "highlight_in_passage": False},
            {"word": "young", "pos": "adjective", "ipa": "/jʌŋ/", "meaning_vi": "trẻ", "definition_en": "Not old; having lived for a short time.", "example_en": "My sister is young.", "example_vi": "Em gái tôi còn trẻ.", "collocations": ["young person", "look young"], "highlight_in_passage": False},
            {"word": "kind", "pos": "adjective", "ipa": "/kaɪnd/", "meaning_vi": "tốt bụng / thân thiện", "definition_en": "Friendly and caring about other people.", "example_en": "My teacher is very kind.", "example_vi": "Giáo viên tôi rất tốt bụng.", "collocations": ["very kind", "kind to others"], "highlight_in_passage": False},
        ],
        "grammar_title": "Adjectives to describe people",
        "grammar_note": (
            "Adjectives describe nouns. In English, adjectives come **before** the noun "
            "or after 'be'.\n\n"
            "• He is **tall**. (after 'be')\n"
            "• She is a **kind** teacher. (before noun)\n\n"
            "Adjectives do NOT change for plural:\n"
            "• They are **tall**. (not 'talls')\n\n"
            "Common pairs: tall ↔ short, young ↔ old, kind ↔ unkind, happy ↔ sad"
        ),
        "grammar_examples": [
            {"en": "My mother is kind and tall.", "vi": "Mẹ tôi tốt bụng và cao.", "highlight": "kind"},
            {"en": "He is a young engineer.", "vi": "Anh ấy là một kỹ sư trẻ.", "highlight": "young"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "My brother is very ___. He is 1.85 metres.", "options": ["tall", "short", "young", "kind"], "correct": 0, "explanation": "1.85 metres is tall — 'He is very tall.'"},
            {"type": "error", "prompt": "Find the error: 'She is a talls woman.'", "options": ["She → Her", "talls → tall", "woman → women", "No error"], "correct": 1, "explanation": "Adjectives never take -s in English: 'a **tall** woman'."},
            {"type": "mc", "prompt": "Which sentence correctly uses an adjective?", "options": ["She is a teacher kind.", "Kind she is.", "She is a kind teacher.", "She kindly is a teacher."], "correct": 2, "explanation": "Adjective + noun order in English: 'a **kind** teacher'."},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Gia đình & Bạn bè", 3): {
        "reading_passage": (
            "<p><strong>My best friend</strong></p>"
            "<p>My best friend is <strong>Hoa</strong>. She is 21 years old. "
            "She is a university student. She studies English and French.</p>"
            "<p>Hoa is tall and slim. She has long black hair and brown eyes. "
            "She is very kind and funny. She always makes me laugh.</p>"
            "<p>We are friends because we have the same hobbies. "
            "We both love music and travelling. "
            "We are not from the same city — she is from Hue and I am from Hanoi — "
            "but we are very close friends.</p>"
        ),
        "reading_questions": [
            {"question": "Where is Hoa from?", "options": ["Hanoi", "Ho Chi Minh City", "Hue", "Da Nang"], "correct": 2, "explanation": "'She is from Hue.'"},
            {"question": "What do the writer and Hoa have in common?", "options": ["They are from the same city.", "They both love music and travelling.", "They both study French.", "They are both engineers."], "correct": 1, "explanation": "'We both love music and travelling.'"},
            {"question": "How is Hoa described physically?", "options": ["short and slim", "tall and heavy", "tall and slim", "short and tall"], "correct": 2, "explanation": "'Hoa is tall and slim.'"},
        ],
        "vocab_items": [
            {"word": "slim", "pos": "adjective", "ipa": "/slɪm/", "meaning_vi": "mảnh khảnh / thon gọn", "definition_en": "Thin in a healthy and attractive way.", "example_en": "She is slim and tall.", "example_vi": "Cô ấy mảnh khảnh và cao.", "collocations": ["slim figure", "tall and slim"], "highlight_in_passage": True},
            {"word": "funny", "pos": "adjective", "ipa": "/ˈfʌn.i/", "meaning_vi": "hài hước / buồn cười", "definition_en": "Making you laugh.", "example_en": "He is very funny.", "example_vi": "Anh ấy rất hài hước.", "collocations": ["very funny", "funny story"], "highlight_in_passage": True},
            {"word": "close", "pos": "adjective", "ipa": "/kləʊs/", "meaning_vi": "thân thiết", "definition_en": "Knowing someone very well and liking them a lot.", "example_en": "They are close friends.", "example_vi": "Họ là những người bạn thân.", "collocations": ["close friend", "very close"], "highlight_in_passage": True},
            {"word": "both", "pos": "determiner", "ipa": "/bəʊθ/", "meaning_vi": "cả hai", "definition_en": "Used to talk about two things or people together.", "example_en": "We both love music.", "example_vi": "Chúng tôi cả hai đều yêu âm nhạc.", "collocations": ["both of us", "we both"], "highlight_in_passage": True},
        ],
        "grammar_title": "Subject pronouns + 'be': review in context",
        "grammar_note": (
            "Review of subject pronouns with 'be' through a real description.\n\n"
            "I **am** → She **is** → We **are** → They **are**\n\n"
            "Contraction reminder:\n"
            "I'm | She's | We're | They're\n\n"
            "**Same/different:** We **are** the same age. We **are not** from the same city."
        ),
        "grammar_examples": [
            {"en": "She is tall and slim.", "vi": "Cô ấy cao và mảnh khảnh.", "highlight": "is"},
            {"en": "We are both students.", "vi": "Cả hai chúng tôi đều là sinh viên.", "highlight": "are both"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "My friend and I ___ both students. ___ are from different cities.", "options": ["are / We", "is / We", "are / They", "is / They"], "correct": 0, "explanation": "'My friend and I' = we → 'We **are** both students. **We** are from different cities.'"},
            {"type": "mc", "prompt": "Which sentence means the same as: 'Hoa and I love music'?", "options": ["We both love music.", "She both loves music.", "I both love music.", "They both love music."], "correct": 0, "explanation": "'Hoa and I' = We → 'We both love music.'"},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Gia đình & Bạn bè", 7): {
        "grammar_note": "Chapter review. Complete all exercises to unlock the next chapter.",
        "grammar_examples": [],
        "exercises": [
            {"type": "cloze", "prompt": "This is my [1]. Her name is Anna. She [2] very kind and funny. She [3] a teacher. We [4] close friends.", "options": [["friend","brother","father","son"], ["is","are","am","be"], ["is","are","am","be"], ["are","is","am","be"]], "correct": [0, 0, 0, 0], "explanation": "friend / is / is / are — agreement with subjects."},
            {"type": "gap-fill", "prompt": "___ are my parents. ___ are both doctors.", "options": ["These / They", "This / They", "Those / We", "These / We"], "correct": 0, "explanation": "'These are my parents' (pointing nearby). 'They are both doctors' — subject pronoun they."},
            {"type": "mc", "prompt": "What is the correct question?", "options": ["How many brothers you have?", "How many brothers do you have?", "How many brothers does you have?", "How many brother have you?"], "correct": 1, "explanation": "'How many brothers **do you have**?' — do + you for questions with main verb 'have'."},
        ],
        "completion_xp": 15,
        "bonus_xp": 60,
    },

    # ════════════════════════════════════════════════════════════════════
    # A1 — Chapter 3: Cuộc sống hàng ngày
    # ════════════════════════════════════════════════════════════════════
    ("Cuộc sống hàng ngày", 1): {
        "reading_passage": (
            "<p><strong>A typical day</strong></p>"
            "<p>My name is <strong>Tuan</strong>. I wake up at 6 o'clock every morning. "
            "I have breakfast at 6:30. I usually eat rice and eggs.</p>"
            "<p>I start work at 8 o'clock. I work in an office. "
            "I have lunch at 12:30. I finish work at 5:30 in the afternoon.</p>"
            "<p>In the evening, I cook dinner and watch TV. "
            "I go to bed at 10:30 at night.</p>"
            "<p>At weekends, I don't work. I often meet my friends and we play football.</p>"
        ),
        "reading_questions": [
            {"question": "What time does Tuan wake up?", "options": ["5:00", "6:00", "6:30", "7:00"], "correct": 1, "explanation": "'I wake up at 6 o'clock every morning.'"},
            {"question": "What does Tuan do on weekends?", "options": ["He works.", "He meets friends and plays football.", "He cooks dinner.", "He watches TV all day."], "correct": 1, "explanation": "'At weekends… I often meet my friends and we play football.'"},
            {"question": "What time does Tuan finish work?", "options": ["4:30", "5:00", "5:30", "6:00"], "correct": 2, "explanation": "'I finish work at 5:30 in the afternoon.'"},
        ],
        "vocab_items": [
            {"word": "wake up", "pos": "phrasal verb", "ipa": "/weɪk ʌp/", "meaning_vi": "thức dậy", "definition_en": "To stop sleeping.", "example_en": "I wake up at 6 every day.", "example_vi": "Tôi thức dậy lúc 6 giờ mỗi ngày.", "collocations": ["wake up early", "wake up late"], "highlight_in_passage": True},
            {"word": "breakfast", "pos": "noun", "ipa": "/ˈbrek.fəst/", "meaning_vi": "bữa sáng", "definition_en": "The first meal of the day.", "example_en": "I have breakfast at 7.", "example_vi": "Tôi ăn sáng lúc 7 giờ.", "collocations": ["have breakfast", "eat breakfast", "skip breakfast"], "highlight_in_passage": True},
            {"word": "usually", "pos": "adverb", "ipa": "/ˈjuː.ʒu.ə.li/", "meaning_vi": "thường thường", "definition_en": "In the way that is most common.", "example_en": "I usually go to school by bike.", "example_vi": "Tôi thường đi học bằng xe đạp.", "collocations": ["usually do", "I usually"], "highlight_in_passage": True},
            {"word": "finish", "pos": "verb", "ipa": "/ˈfɪn.ɪʃ/", "meaning_vi": "kết thúc / xong", "definition_en": "To complete something.", "example_en": "I finish work at 5 pm.", "example_vi": "Tôi xong việc lúc 5 giờ chiều.", "collocations": ["finish work", "finish school", "finish early"], "highlight_in_passage": True},
            {"word": "often", "pos": "adverb", "ipa": "/ˈɒf.ən/", "meaning_vi": "thường xuyên", "definition_en": "Many times or frequently.", "example_en": "I often eat lunch at home.", "example_vi": "Tôi thường ăn trưa ở nhà.", "collocations": ["quite often", "very often"], "highlight_in_passage": True},
            {"word": "cook", "pos": "verb", "ipa": "/kʊk/", "meaning_vi": "nấu ăn", "definition_en": "To prepare food by using heat.", "example_en": "I cook dinner every evening.", "example_vi": "Tôi nấu bữa tối mỗi buổi chiều.", "collocations": ["cook dinner", "cook for someone", "learn to cook"], "highlight_in_passage": True},
            {"word": "weekend", "pos": "noun", "ipa": "/ˈwiːk.end/", "meaning_vi": "cuối tuần", "definition_en": "Saturday and Sunday.", "example_en": "I relax at the weekend.", "example_vi": "Tôi nghỉ ngơi vào cuối tuần.", "collocations": ["at the weekend", "weekend plans", "this weekend"], "highlight_in_passage": True},
            {"word": "play", "pos": "verb", "ipa": "/pleɪ/", "meaning_vi": "chơi (thể thao/nhạc)", "definition_en": "To take part in a game or sport.", "example_en": "We play football on Sundays.", "example_vi": "Chúng tôi chơi đá bóng vào Chủ nhật.", "collocations": ["play football", "play tennis", "play music"], "highlight_in_passage": True},
        ],
        "grammar_title": "Present simple: habits and routines",
        "grammar_note": (
            "Use present simple for **regular actions, habits, and facts**.\n\n"
            "**Positive:** I/You/We/They **wake up** | He/She/It **wakes up**\n\n"
            "**Add -s/-es** for he/she/it:\n"
            "• work → work**s** | finish → finish**es** | go → go**es**\n\n"
            "**Negative:** I **don't** work. He **doesn't** work.\n\n"
            "**Adverbs of frequency** (position: before main verb, after 'be'):\n"
            "always (100%) → usually (80%) → often (60%) → sometimes (40%) → rarely (20%) → never (0%)"
        ),
        "grammar_examples": [
            {"en": "I wake up at 6 every morning.", "vi": "Tôi thức dậy lúc 6 giờ mỗi sáng.", "highlight": "wake up"},
            {"en": "He finishes work at 5:30.", "vi": "Anh ấy xong việc lúc 5:30.", "highlight": "finishes"},
            {"en": "They don't work at weekends.", "vi": "Họ không làm việc vào cuối tuần.", "highlight": "don't work"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "She ___ (get up) at 7 o'clock and ___ (have) breakfast.", "options": ["gets up / has", "get up / have", "gets up / have", "get up / has"], "correct": 0, "explanation": "'She' is third person singular → gets up / has."},
            {"type": "gap-fill", "prompt": "Tom ___ eat rice for breakfast. He ___ prefer bread.", "options": ["doesn't / usually", "don't / usually", "doesn't / usual", "isn't / usually"], "correct": 0, "explanation": "'He doesn't eat' (negative present simple) + 'He usually prefers' — 'usually' before main verb."},
            {"type": "error", "prompt": "Find the error: 'She always goes to bed at 10 at night. She don't wake up late.'", "options": ["always → usually", "at night → in the night", "don't → doesn't", "No error"], "correct": 2, "explanation": "'She' = third person singular → 'She **doesn't** wake up late.'"},
            {"type": "mc", "prompt": "I ___ lunch at 12:30. My colleague ___ lunch at 1:00.", "options": ["have / have", "have / has", "has / have", "has / has"], "correct": 1, "explanation": "'I have' (1st person) + 'My colleague has' (3rd person singular)."},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Cuộc sống hàng ngày", 2): {
        "reading_passage": "",
        "reading_questions": [],
        "vocab_items": [
            {"word": "shower", "pos": "noun/verb", "ipa": "/ˈʃaʊ.ər/", "meaning_vi": "vòi hoa sen / tắm vòi sen", "definition_en": "A device for washing your body standing up / the act of using it.", "example_en": "I have a shower every morning.", "example_vi": "Tôi tắm vòi sen mỗi sáng.", "collocations": ["have a shower", "take a shower"], "highlight_in_passage": False},
            {"word": "work", "pos": "verb", "ipa": "/wɜːk/", "meaning_vi": "làm việc", "definition_en": "To do a job or task.", "example_en": "He works in a hospital.", "example_vi": "Anh ấy làm việc ở bệnh viện.", "collocations": ["work hard", "work from home", "start work"], "highlight_in_passage": False},
            {"word": "commute", "pos": "verb", "ipa": "/kəˈmjuːt/", "meaning_vi": "đi lại (làm việc)", "definition_en": "To travel regularly to and from work.", "example_en": "She commutes by bus every day.", "example_vi": "Cô ấy đi xe buýt đi làm mỗi ngày.", "collocations": ["commute to work", "daily commute"], "highlight_in_passage": False},
        ],
        "grammar_title": "Questions in present simple: Do you…? Does he…?",
        "grammar_note": (
            "**Yes/No questions:**\n"
            "• **Do** I/you/we/they + verb? → Yes, I do. / No, I don't.\n"
            "• **Does** he/she/it + verb? → Yes, she does. / No, she doesn't.\n\n"
            "**Wh- questions:**\n"
            "• **What time do** you wake up?\n"
            "• **What does** she do at weekends?\n"
            "• **Where do** they work?\n\n"
            "⚠ In questions, the verb has NO -s: 'Does she **work**?' (not 'works')"
        ),
        "grammar_examples": [
            {"en": "Do you have breakfast every day?", "vi": "Bạn có ăn sáng mỗi ngày không?", "highlight": "Do"},
            {"en": "What time does he start work?", "vi": "Mấy giờ anh ấy bắt đầu làm việc?", "highlight": "does"},
            {"en": "Where do they live?", "vi": "Họ sống ở đâu?", "highlight": "do"},
        ],
        "exercises": [
            {"type": "gap-fill", "prompt": "___ she commute by bus? Yes, she ___.", "options": ["Does / does", "Do / does", "Does / do", "Is / does"], "correct": 0, "explanation": "'Does she…?' for third person singular. Short answer: 'Yes, she **does**.'"},
            {"type": "gap-fill", "prompt": "What time ___ you wake up? I ___ wake up at 6.", "options": ["do / usually", "does / usually", "do / always", "does / always"], "correct": 0, "explanation": "'What time **do** you wake up?' 'I **usually** wake up at 6.' — 'usually' before main verb."},
            {"type": "error", "prompt": "Find the error: 'Does he works in an office?'", "options": ["Does → Do", "works → work", "in → at", "No error"], "correct": 1, "explanation": "In questions with 'does', the main verb has NO -s: 'Does he **work**?'"},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Cuộc sống hàng ngày", 3): {
        "reading_passage": (
            "<p><strong>My weekend routine</strong></p>"
            "<p>I don't work on Saturdays or Sundays. "
            "On Saturday morning, I usually go to the market with my mother. "
            "We buy fresh vegetables, meat and fruit. "
            "In the afternoon, I sometimes play badminton with my friends.</p>"
            "<p>On Sunday, I always sleep late — until 8 or even 9 o'clock! "
            "Then I have a big breakfast and read the newspaper. "
            "In the evening, I cook a special dinner for my family. "
            "My family always eat together on Sunday evenings. "
            "We talk, laugh and enjoy the meal together.</p>"
        ),
        "reading_questions": [
            {"question": "What does the writer do on Saturday morning?", "options": ["plays badminton", "goes to the market", "sleeps late", "cooks dinner"], "correct": 1, "explanation": "'On Saturday morning, I usually go to the market with my mother.'"},
            {"question": "How late does the writer sleep on Sunday?", "options": ["Until 6", "Until 7", "Until 8 or 9", "Until 10"], "correct": 2, "explanation": "'until 8 or even 9 o'clock'"},
            {"question": "When does the family eat together?", "options": ["Saturday morning", "Saturday afternoon", "Sunday morning", "Sunday evening"], "correct": 3, "explanation": "'My family always eat together on Sunday evenings.'"},
        ],
        "vocab_items": [
            {"word": "fresh", "pos": "adjective", "ipa": "/freʃ/", "meaning_vi": "tươi / mới", "definition_en": "Recently made or obtained; not old or canned.", "example_en": "I prefer fresh vegetables.", "example_vi": "Tôi thích rau tươi hơn.", "collocations": ["fresh food", "fresh air", "fresh vegetables"], "highlight_in_passage": True},
            {"word": "market", "pos": "noun", "ipa": "/ˈmɑː.kɪt/", "meaning_vi": "chợ", "definition_en": "A place where people buy and sell food and goods.", "example_en": "We buy food at the market.", "example_vi": "Chúng tôi mua thực phẩm ở chợ.", "collocations": ["go to the market", "local market", "open-air market"], "highlight_in_passage": True},
            {"word": "enjoy", "pos": "verb", "ipa": "/ɪnˈdʒɔɪ/", "meaning_vi": "thích / tận hưởng", "definition_en": "To get pleasure from something.", "example_en": "I enjoy cooking for my family.", "example_vi": "Tôi thích nấu ăn cho gia đình.", "collocations": ["enjoy doing", "enjoy life", "enjoy a meal"], "highlight_in_passage": True},
        ],
        "grammar_title": "Adverbs of frequency: always, usually, often, sometimes, rarely, never",
        "grammar_note": (
            "Adverbs of frequency tell us **how often** something happens.\n\n"
            "**Position:** before the main verb, but **after** 'be':\n"
            "• I **always** wake up early. (before main verb)\n"
            "• I am **never** late. (after 'be')\n\n"
            "**Scale:**\n"
            "always → usually → often → sometimes → rarely/seldom → never"
        ),
        "grammar_examples": [
            {"en": "I always sleep late on Sundays.", "vi": "Tôi luôn ngủ muộn vào Chủ nhật.", "highlight": "always"},
            {"en": "She sometimes plays badminton.", "vi": "Cô ấy đôi khi chơi cầu lông.", "highlight": "sometimes"},
            {"en": "They are never late for school.", "vi": "Họ không bao giờ đến trường muộn.", "highlight": "never"},
        ],
        "exercises": [
            {"type": "rewrite", "prompt": "Rewrite correctly: 'I go always to bed at 10.'", "options": ["I always go to bed at 10.", "Always I go to bed at 10.", "I go to always bed at 10.", "No change needed."], "correct": 0, "explanation": "Frequency adverbs go **before** the main verb: 'I **always go** to bed at 10.'"},
            {"type": "gap-fill", "prompt": "She is ___ on time. She ___ forgets her homework.", "options": ["always / never", "never / always", "sometimes / usually", "often / sometimes"], "correct": 0, "explanation": "'She is **always** on time' (after be) + 'She **never** forgets' (before main verb)."},
        ],
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Cuộc sống hàng ngày", 7): {
        "grammar_note": "Review all present simple forms: positive, negative, question + adverbs of frequency placement.",
        "grammar_examples": [],
        "exercises": [
            {"type": "cloze", "prompt": "Minh [1] up at 6 am. He [2] have coffee for breakfast. He [3] walk to work because he [4] live near his office.", "options": [["gets","get","is getting","got"], ["always","usually","sometimes","never"], ["usually","always","never","often"], ["doesn't","don't","isn't","aren't"]], "correct": [0, 0, 0, 0], "explanation": "gets (3rd person) / always (before verb) / usually (before verb) / doesn't (neg. 3rd person)."},
            {"type": "gap-fill", "prompt": "___ your father cook dinner? Yes, he ___ cook, but not every day.", "options": ["Does / sometimes", "Do / sometimes", "Does / always", "Is / sometimes"], "correct": 0, "explanation": "'Does your father cook?' + 'Yes, he **sometimes** cooks.'"},
            {"type": "error", "prompt": "She don't never eat meat — she is vegetarian.", "options": ["don't → doesn't", "never should be removed (double negative)", "Both A and B are wrong", "No error"], "correct": 2, "explanation": "Both errors: 'She **doesn't** eat meat' (3rd person) + 'she **never** eats meat' (don't + never = double negative, non-standard)."},
        ],
        "completion_xp": 15,
        "bonus_xp": 60,
    },

    # ════════════════════════════════════════════════════════════════════
    # A1 — Chapter 3: Cuộc sống hàng ngày — Assessment (now order 7)
    # ════════════════════════════════════════════════════════════════════
    # (existing entry above, moved from order 4 → 7)

    # ════════════════════════════════════════════════════════════════════
    # A1 — SKILL LESSONS: Giới thiệu bản thân
    # ════════════════════════════════════════════════════════════════════
    ("Giới thiệu bản thân", 4): {
        "listening_content": {
            "audio_text": (
                "Hello! My name is Mai. I am 20 years old. "
                "I am from Hanoi. I am a nurse. I work at a hospital."
            ),
            "translation_vi": (
                "Xin chào! Tên tôi là Mai. Tôi 20 tuổi. "
                "Tôi đến từ Hà Nội. Tôi là y tá. Tôi làm việc ở bệnh viện."
            ),
            "sentences": [
                {"text": "Hello! My name is Mai.", "translation_vi": "Xin chào! Tên tôi là Mai.", "audio_url": ""},
                {"text": "I am 20 years old.", "translation_vi": "Tôi 20 tuổi.", "audio_url": ""},
                {"text": "I am from Hanoi.", "translation_vi": "Tôi đến từ Hà Nội.", "audio_url": ""},
                {"text": "I am a nurse.", "translation_vi": "Tôi là y tá.", "audio_url": ""},
                {"text": "I work at a hospital.", "translation_vi": "Tôi làm việc ở bệnh viện.", "audio_url": ""},
            ],
            "speed": 0.8,
            "comprehension_questions": [
                {
                    "question": "What is Mai's job?",
                    "options": ["teacher", "nurse", "doctor", "student"],
                    "correct": 1,
                    "explanation": "'I am a nurse.'",
                },
                {
                    "question": "Where does Mai work?",
                    "options": ["school", "office", "hospital", "restaurant"],
                    "correct": 2,
                    "explanation": "'I work at a hospital.'",
                },
            ],
            "dictation_sentences": [
                {"text": "My name is Mai.", "hint": "My n____ is M__.", "translation_vi": "Tên tôi là Mai."},
                {"text": "I am a nurse.", "hint": "I __ a n____.", "translation_vi": "Tôi là y tá."},
                {"text": "I work at a hospital.", "hint": "I w____ at a h_______.", "translation_vi": "Tôi làm việc ở bệnh viện."},
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Giới thiệu bản thân", 5): {
        "speaking_content": {
            "mode": "repeat",
            "sentences": [
                {
                    "text": "Hello, my name is...",
                    "translation_vi": "Xin chào, tên tôi là...",
                    "speed": 0.75,
                    "focus_words": ["Hello", "name"],
                },
                {
                    "text": "I am from Vietnam.",
                    "translation_vi": "Tôi đến từ Việt Nam.",
                    "speed": 0.75,
                    "focus_words": ["from"],
                },
                {
                    "text": "I am a student.",
                    "translation_vi": "Tôi là sinh viên.",
                    "speed": 0.8,
                    "focus_words": ["student"],
                },
                {
                    "text": "Nice to meet you!",
                    "translation_vi": "Rất vui được gặp bạn!",
                    "speed": 0.8,
                    "focus_words": ["Nice", "meet"],
                },
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Giới thiệu bản thân", 6): {
        "writing_content": {
            "exercises": [
                {
                    "type": "word_order",
                    "prompt": "Sắp xếp các từ thành câu đúng:",
                    "prompt_vi": None,
                    "grammar_hint": "Chủ ngữ + am/is/are + ...",
                    "items": ["am", "I", "a", "student"],
                    "correct_answer": "I am a student.",
                },
                {
                    "type": "word_order",
                    "prompt": "Sắp xếp các từ thành câu đúng:",
                    "prompt_vi": None,
                    "grammar_hint": "He/She + is + ...",
                    "items": ["is", "She", "from", "Vietnam"],
                    "correct_answer": "She is from Vietnam.",
                },
                {
                    "type": "gap_fill",
                    "prompt": "Điền vào chỗ trống: ___ name is Tom. ___ is 25 years old.",
                    "prompt_vi": "Điền từ còn thiếu vào chỗ trống.",
                    "grammar_hint": "Sở hữu từ: my, his, her, their...",
                    "options": ["His / He", "My / He", "His / Him", "Her / She"],
                    "correct_answer": "His / He",
                    "correct_index": 0,
                },
                {
                    "type": "sentence_completion",
                    "prompt": "Viết 2–3 câu giới thiệu bản thân theo gợi ý:",
                    "prompt_vi": "My name is ____. I am ____ years old. I am from ____.",
                    "grammar_hint": "Dùng 'am' với I. Dùng 'is' với He/She. Dùng 'are' với You/We/They.",
                    "sample_answer": "My name is Linh. I am 22 years old. I am from Hanoi. I am a student.",
                    "min_words": 8,
                    "max_words": 30,
                },
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    # ════════════════════════════════════════════════════════════════════
    # A1 — SKILL LESSONS: Gia đình & Bạn bè
    # ════════════════════════════════════════════════════════════════════
    ("Gia đình & Bạn bè", 4): {
        "listening_content": {
            "audio_text": (
                "This is my family. My father is 52 years old. "
                "He is an engineer. My mother is 48 years old. "
                "She is a nurse. I have one brother and one sister."
            ),
            "translation_vi": (
                "Đây là gia đình tôi. Bố tôi 52 tuổi. "
                "Ông là kỹ sư. Mẹ tôi 48 tuổi. "
                "Bà là y tá. Tôi có một anh trai và một em gái."
            ),
            "sentences": [
                {"text": "This is my family.", "translation_vi": "Đây là gia đình tôi.", "audio_url": ""},
                {"text": "My father is 52 years old.", "translation_vi": "Bố tôi 52 tuổi.", "audio_url": ""},
                {"text": "He is an engineer.", "translation_vi": "Ông là kỹ sư.", "audio_url": ""},
                {"text": "My mother is 48 years old.", "translation_vi": "Mẹ tôi 48 tuổi.", "audio_url": ""},
                {"text": "She is a nurse.", "translation_vi": "Bà là y tá.", "audio_url": ""},
                {"text": "I have one brother and one sister.", "translation_vi": "Tôi có một anh trai và một em gái.", "audio_url": ""},
            ],
            "speed": 0.8,
            "comprehension_questions": [
                {
                    "question": "What is the father's job?",
                    "options": ["doctor", "nurse", "engineer", "teacher"],
                    "correct": 2,
                    "explanation": "'He is an engineer.'",
                },
                {
                    "question": "How many siblings does the speaker have?",
                    "options": ["one", "two", "three", "none"],
                    "correct": 1,
                    "explanation": "'I have one brother and one sister.' = two siblings.",
                },
            ],
            "dictation_sentences": [
                {"text": "This is my family.", "hint": "T___ is my f_____.", "translation_vi": "Đây là gia đình tôi."},
                {"text": "He is an engineer.", "hint": "He is an e________.", "translation_vi": "Ông là kỹ sư."},
                {"text": "I have one brother and one sister.", "hint": "I h___ one b______ and one s_____.", "translation_vi": "Tôi có một anh trai và một em gái."},
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Gia đình & Bạn bè", 5): {
        "speaking_content": {
            "mode": "repeat",
            "sentences": [
                {
                    "text": "This is my father.",
                    "translation_vi": "Đây là bố tôi.",
                    "speed": 0.75,
                    "focus_words": ["This", "father"],
                },
                {
                    "text": "She has long black hair.",
                    "translation_vi": "Cô ấy có mái tóc đen dài.",
                    "speed": 0.75,
                    "focus_words": ["has", "long", "black"],
                },
                {
                    "text": "He is kind and funny.",
                    "translation_vi": "Anh ấy tốt bụng và hài hước.",
                    "speed": 0.8,
                    "focus_words": ["kind", "funny"],
                },
                {
                    "text": "We are close friends.",
                    "translation_vi": "Chúng tôi là những người bạn thân.",
                    "speed": 0.8,
                    "focus_words": ["close", "friends"],
                },
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Gia đình & Bạn bè", 6): {
        "writing_content": {
            "exercises": [
                {
                    "type": "word_order",
                    "prompt": "Sắp xếp các từ thành câu đúng:",
                    "prompt_vi": None,
                    "grammar_hint": "This/These + is/are + ...",
                    "items": ["are", "These", "my", "brothers"],
                    "correct_answer": "These are my brothers.",
                },
                {
                    "type": "word_order",
                    "prompt": "Sắp xếp các từ thành câu đúng:",
                    "prompt_vi": None,
                    "grammar_hint": "He/She + has + ...",
                    "items": ["has", "She", "two", "children"],
                    "correct_answer": "She has two children.",
                },
                {
                    "type": "gap_fill",
                    "prompt": "Điền vào chỗ trống: My sister ___ tall and slim. ___ has long hair.",
                    "prompt_vi": None,
                    "grammar_hint": "Dùng is/are đúng với chủ ngữ. Dùng She/He/They đúng.",
                    "options": ["is / She", "are / She", "is / He", "are / They"],
                    "correct_answer": "is / She",
                    "correct_index": 0,
                },
                {
                    "type": "sentence_completion",
                    "prompt": "Viết 2–3 câu mô tả một người trong gia đình bạn:",
                    "prompt_vi": "Gợi ý: This is my ____. He/She is ____. He/She has ____.",
                    "grammar_hint": "Dùng tính từ: tall/short, kind/funny, old/young.",
                    "sample_answer": "This is my brother. He is 19 years old. He is tall and kind. He has short black hair.",
                    "min_words": 10,
                    "max_words": 35,
                },
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    # ════════════════════════════════════════════════════════════════════
    # A1 — SKILL LESSONS: Cuộc sống hàng ngày
    # ════════════════════════════════════════════════════════════════════
    ("Cuộc sống hàng ngày", 4): {
        "listening_content": {
            "audio_text": (
                "My name is Tuan. I wake up at six o'clock every morning. "
                "I have breakfast at six thirty. I start work at eight o'clock. "
                "I finish work at five thirty. I cook dinner in the evening."
            ),
            "translation_vi": (
                "Tên tôi là Tuan. Tôi thức dậy lúc 6 giờ mỗi sáng. "
                "Tôi ăn sáng lúc 6 giờ 30. Tôi bắt đầu làm việc lúc 8 giờ. "
                "Tôi xong việc lúc 5 giờ 30. Tôi nấu bữa tối vào buổi chiều."
            ),
            "sentences": [
                {"text": "My name is Tuan.", "translation_vi": "Tên tôi là Tuan.", "audio_url": ""},
                {"text": "I wake up at six o'clock every morning.", "translation_vi": "Tôi thức dậy lúc 6 giờ mỗi sáng.", "audio_url": ""},
                {"text": "I have breakfast at six thirty.", "translation_vi": "Tôi ăn sáng lúc 6 giờ 30.", "audio_url": ""},
                {"text": "I start work at eight o'clock.", "translation_vi": "Tôi bắt đầu làm việc lúc 8 giờ.", "audio_url": ""},
                {"text": "I finish work at five thirty.", "translation_vi": "Tôi xong việc lúc 5 giờ 30.", "audio_url": ""},
                {"text": "I cook dinner in the evening.", "translation_vi": "Tôi nấu bữa tối vào buổi chiều.", "audio_url": ""},
            ],
            "speed": 0.85,
            "comprehension_questions": [
                {
                    "question": "What time does Tuan wake up?",
                    "options": ["5:00", "6:00", "6:30", "7:00"],
                    "correct": 1,
                    "explanation": "'I wake up at six o'clock.'",
                },
                {
                    "question": "What does Tuan do in the evening?",
                    "options": ["plays football", "reads", "cooks dinner", "watches TV"],
                    "correct": 2,
                    "explanation": "'I cook dinner in the evening.'",
                },
                {
                    "question": "What time does Tuan finish work?",
                    "options": ["4:00", "5:00", "5:30", "6:00"],
                    "correct": 2,
                    "explanation": "'I finish work at five thirty.'",
                },
            ],
            "dictation_sentences": [
                {"text": "I wake up at six o'clock.", "hint": "I w___ up at s__ o'clock.", "translation_vi": "Tôi thức dậy lúc 6 giờ."},
                {"text": "I start work at eight o'clock.", "hint": "I s____ w___ at e____ o'clock.", "translation_vi": "Tôi bắt đầu làm lúc 8 giờ."},
                {"text": "I cook dinner in the evening.", "hint": "I c___ d_____ in the e_____.", "translation_vi": "Tôi nấu bữa tối vào buổi chiều."},
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Cuộc sống hàng ngày", 5): {
        "speaking_content": {
            "mode": "repeat",
            "sentences": [
                {
                    "text": "I wake up at six o'clock.",
                    "translation_vi": "Tôi thức dậy lúc 6 giờ.",
                    "speed": 0.75,
                    "focus_words": ["wake up", "six"],
                },
                {
                    "text": "I usually have rice for breakfast.",
                    "translation_vi": "Tôi thường ăn cơm cho bữa sáng.",
                    "speed": 0.75,
                    "focus_words": ["usually", "breakfast"],
                },
                {
                    "text": "She always goes to bed at ten.",
                    "translation_vi": "Cô ấy luôn đi ngủ lúc 10 giờ.",
                    "speed": 0.8,
                    "focus_words": ["always", "goes"],
                },
                {
                    "text": "Do you work at weekends?",
                    "translation_vi": "Bạn có làm việc vào cuối tuần không?",
                    "speed": 0.8,
                    "focus_words": ["Do", "weekends"],
                },
                {
                    "text": "No, I don't. I play football with my friends.",
                    "translation_vi": "Không, tôi không. Tôi chơi đá bóng với bạn bè.",
                    "speed": 0.85,
                    "focus_words": ["don't", "play"],
                },
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },

    ("Cuộc sống hàng ngày", 6): {
        "writing_content": {
            "exercises": [
                {
                    "type": "word_order",
                    "prompt": "Sắp xếp các từ thành câu đúng:",
                    "prompt_vi": None,
                    "grammar_hint": "She + verb-s/es + time expression",
                    "items": ["up", "She", "gets", "at", "7", "o'clock"],
                    "correct_answer": "She gets up at 7 o'clock.",
                },
                {
                    "type": "word_order",
                    "prompt": "Sắp xếp các từ thành câu đúng (phủ định):",
                    "prompt_vi": None,
                    "grammar_hint": "He + doesn't + verb (không chia)",
                    "items": ["doesn't", "He", "work", "weekends", "at"],
                    "correct_answer": "He doesn't work at weekends.",
                },
                {
                    "type": "gap_fill",
                    "prompt": "Điền vào chỗ trống: ___ she commute by bus? Yes, she ___.",
                    "prompt_vi": None,
                    "grammar_hint": "Câu hỏi Yes/No với Does cho ngôi thứ 3.",
                    "options": ["Does / does", "Do / does", "Does / do", "Is / does"],
                    "correct_answer": "Does / does",
                    "correct_index": 0,
                },
                {
                    "type": "sentence_completion",
                    "prompt": "Viết 3–4 câu mô tả thói quen hàng ngày của bạn:",
                    "prompt_vi": "Gợi ý: I usually... / I always... / I never... / At weekends, I...",
                    "grammar_hint": "Dùng adverbs of frequency: always, usually, often, sometimes, never.",
                    "sample_answer": "I usually wake up at 6 o'clock. I always have breakfast. I sometimes go to the market at weekends. I never go to bed after midnight.",
                    "min_words": 15,
                    "max_words": 50,
                },
            ],
        },
        "completion_xp": 10,
        "bonus_xp": 50,
    },
}


_SKILL_EXERCISE_TYPES = {"dictation", "shadowing", "guided-writing"}


def _build_skill_sections(data: dict, lesson_title: str, chapter_title: str) -> dict:
    """Build structured skill_sections: {dictation:[3], shadowing:[2], guided_writing:[1]}."""
    grammar_examples = data.get("grammar_examples") or []
    vocab_items = data.get("vocab_items") or []
    grammar_title = data.get("grammar_title", "")

    # Collect candidate (sentence, translation) pairs from grammar + vocab examples
    pairs = []
    for ex in grammar_examples:
        s = ex.get("en", "").strip()
        v = ex.get("vi", "").strip()
        if s:
            pairs.append((s, v))
    for item in vocab_items:
        s = item.get("example_en", "").strip()
        v = item.get("example_vi", "").strip()
        if s and len(pairs) < 8:
            pairs.append((s, v))

    # Fallback sentences
    fallbacks = [
        ("I study English every day.", "Tôi học tiếng Anh mỗi ngày."),
        ("She is a student.", "Cô ấy là sinh viên."),
        ("We are from Vietnam.", "Chúng tôi đến từ Việt Nam."),
        ("He works in an office.", "Anh ấy làm việc trong văn phòng."),
        ("They are close friends.", "Họ là những người bạn thân."),
    ]
    while len(pairs) < 6:
        pairs.append(fallbacks[len(pairs) % len(fallbacks)])

    # ── 3 dictation exercises (increasing difficulty) ─────────────────
    dictation = []
    for i in range(3):
        s, _ = pairs[i % len(pairs)]
        words = s.split()
        hint = f"Bắt đầu bằng '{words[0]}', {len(words)} từ." if words else ""
        dictation.append({"type": "dictation", "audio_text": s, "hint": hint})

    # ── 2 shadowing exercises ──────────────────────────────────────────
    shadowing = []
    for i in range(2):
        s, v = pairs[(i + 1) % len(pairs)]
        shadowing.append({
            "type": "shadowing",
            "audio_text": s,
            "translation_vi": v,
            "speed": 0.75 if i == 0 else 1.0,
        })

    # ── 1 guided-writing exercise ─────────────────────────────────────
    sample = " ".join(s for s, _ in pairs[:3] if s).strip()
    guided_writing = [{
        "type": "guided-writing",
        "prompt": f"Viết 2–3 câu về chủ đề '{chapter_title}' sử dụng từ vựng và ngữ pháp trong bài.",
        "min_words": 15,
        "max_words": 60,
        "structure_hint": grammar_title,
        "sample_answer": sample or "I am a student. I study English every day. I like learning new words.",
    }]

    return {
        "dictation": dictation,
        "shadowing": shadowing,
        "guided_writing": guided_writing,
    }


def _build_grammar_sections(data: dict) -> list:
    """Convert flat grammar_title/note/examples + knowledge exercises → grammar_sections list."""
    grammar_title = data.get("grammar_title", "")
    if not grammar_title:
        return []
    knowledge_exs = [
        e for e in (data.get("exercises") or [])
        if e.get("type") not in _SKILL_EXERCISE_TYPES
    ]
    return [{
        "title": grammar_title,
        "grammar_topic_id": data.get("grammar_topic_id"),
        "note": data.get("grammar_note", ""),
        "examples": data.get("grammar_examples") or [],
        "exercises": knowledge_exs,
    }]


def _get_grammar_topic_id(title: str):
    """Try to find a matching GrammarTopic by title keyword."""
    if not title:
        return None
    qs = GrammarTopic.objects.filter(title__icontains=title.split(":")[0][:30])
    if qs.exists():
        return qs.first().id
    return None


def _build_placeholder(lesson: Lesson) -> dict:
    """Minimal placeholder content for lessons not in CONTENT_MAP."""
    lesson_type_hints = {
        "vocabulary": {
            "grammar_title": f"Vocabulary: {lesson.chapter.title}",
            "grammar_note": f"This lesson covers key vocabulary for the topic '{lesson.chapter.title}'. Complete the exercises to learn and practise the target words.",
        },
        "grammar": {
            "grammar_title": f"Grammar focus: {lesson.chapter.title}",
            "grammar_note": f"This lesson presents the key grammar patterns for '{lesson.chapter.title}'. Study the examples and complete the exercises.",
        },
        "reading": {
            "grammar_title": "Reading comprehension",
            "grammar_note": f"Read the passage about '{lesson.chapter.title}' and answer the comprehension questions.",
        },
        "assessment": {
            "grammar_title": "Chapter review",
            "grammar_note": f"Test your knowledge from the '{lesson.chapter.title}' chapter. Complete all exercises to unlock the next chapter.",
            "completion_xp": 15,
            "bonus_xp": 60,
        },
    }
    return hint if (hint := lesson_type_hints.get(lesson.lesson_type)) else {
        "grammar_title": lesson.title,
        "grammar_note": "Content coming soon.",
    }


class Command(BaseCommand):
    help = "Seed LessonContent for all lessons (uses CONTENT_MAP + auto-placeholder)."

    def add_arguments(self, parser):
        parser.add_argument("--level", type=str, default=None, help="Seed only this CEFR level (e.g. A1)")
        parser.add_argument("--clear", action="store_true", help="Delete existing LessonContent before seeding")
        parser.add_argument("--missing-only", action="store_true", help="Only create content for lessons that have none yet")

    def handle(self, *args, **options):
        level_filter = options["level"]
        clear = options["clear"]
        missing_only = options["missing_only"]

        courses = Course.objects.prefetch_related("chapters__lessons")
        if level_filter:
            courses = courses.filter(level__code=level_filter)

        if clear:
            lesson_ids = Lesson.objects.filter(
                chapter__course__in=courses
            ).values_list("id", flat=True)
            deleted, _ = LessonContent.objects.filter(lesson_id__in=lesson_ids).delete()
            self.stdout.write(f"  Cleared {deleted} existing LessonContent records.")

        total_created = 0
        total_updated = 0
        total_skipped = 0

        for course in courses.order_by("level__order"):
            lvl = course.level.code
            self.stdout.write(f"\n[{lvl}] {course.title}")

            for chapter in course.chapters.order_by("order"):
                for lesson in chapter.lessons.order_by("order"):
                    key = (chapter.title, lesson.order)

                    if missing_only and LessonContent.objects.filter(lesson=lesson).exists():
                        total_skipped += 1
                        continue

                    # Get content data from map or generate placeholder
                    data = CONTENT_MAP.get(key)
                    if data is None:
                        data = _build_placeholder(lesson)

                    # Build structured grammar_sections and skill_sections
                    grammar_sections = _build_grammar_sections(data)
                    skill_sections = _build_skill_sections(data, lesson.title, chapter.title)

                    # Auto-link grammar topic ID
                    grammar_title = data.get("grammar_title", "")
                    if grammar_title and not data.get("grammar_topic_id"):
                        gid = _get_grammar_topic_id(grammar_title)
                        if gid and grammar_sections:
                            grammar_sections[0]["grammar_topic_id"] = gid

                    defaults = {
                        "reading_passage": data.get("reading_passage", ""),
                        "reading_image_url": data.get("reading_image_url", ""),
                        "reading_questions": data.get("reading_questions", []),
                        "vocab_items": data.get("vocab_items", []),
                        "vocab_word_ids": data.get("vocab_word_ids", []),
                        # Legacy flat grammar fields (kept for compat)
                        "grammar_topic_id": data.get("grammar_topic_id"),
                        "grammar_title": grammar_title,
                        "grammar_note": data.get("grammar_note", ""),
                        "grammar_examples": data.get("grammar_examples", []),
                        # New structured fields
                        "grammar_sections": grammar_sections,
                        "skill_sections": skill_sections,
                        # Dedicated skill lesson content
                        "listening_content": data.get("listening_content", {}),
                        "speaking_content": data.get("speaking_content", {}),
                        "writing_content": data.get("writing_content", {}),
                        # Knowledge exercises (flat, for compat)
                        "exercises": [
                            e for e in (data.get("exercises") or [])
                            if e.get("type") not in _SKILL_EXERCISE_TYPES
                        ],
                        "srs_review_count": data.get("srs_review_count", 5),
                        "completion_xp": data.get("completion_xp", 10),
                        "bonus_xp": data.get("bonus_xp", 50),
                    }

                    _, created = LessonContent.objects.update_or_create(
                        lesson=lesson, defaults=defaults
                    )
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1

                    status = "✓ created" if created else "↻ updated"
                    has_reading = "📖" if defaults["reading_passage"] else "  "
                    has_vocab = f"📝{len(defaults['vocab_items'])}" if defaults["vocab_items"] else "  "
                    has_exercises = f"🧩{len(defaults['exercises'])}" if defaults["exercises"] else "  "
                    self.stdout.write(
                        f"  {status} [{chapter.title[:20]:<20}] L{lesson.order} "
                        f"{has_reading} {has_vocab} {has_exercises} — {lesson.title[:40]}"
                    )

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Created: {total_created}  Updated: {total_updated}  Skipped: {total_skipped}")
        self.stdout.write("Done ✓")
