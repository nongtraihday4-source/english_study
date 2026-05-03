"""
Management command: seed_courses
Creates CEFRLevel, Course, Chapter, and skeleton Lesson records for A1-C1.

Usage:
    python manage.py seed_courses                    # create (skip if exists)
    python manage.py seed_courses --level A2         # only one level
    python manage.py seed_courses --clear            # delete + recreate

Each Chapter gets 7 skeleton Lessons:
  1. vocabulary   (~10 min)
  2. grammar      (~15 min)
  3. reading      (~15 min)
  4. listening    (~10 min)
  5. speaking     (~8 min)
  6. writing      (~10 min)
  7. assessment   (~10 min)
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.curriculum.models import CEFRLevel, Chapter, Course, Lesson

# ─── CEFR level catalogue ────────────────────────────────────────────────────
CEFR_LEVELS = [
    {"code": "A1", "name": "Beginner",      "name_vi": "Sơ cấp",          "order": 1},
    {"code": "A2", "name": "Elementary",    "name_vi": "Tiền trung cấp",  "order": 2},
    {"code": "B1", "name": "Intermediate",  "name_vi": "Trung cấp",       "order": 3},
    {"code": "B2", "name": "Upper-Intermediate", "name_vi": "Cao trung cấp", "order": 4},
    {"code": "C1", "name": "Advanced",      "name_vi": "Nâng cao",        "order": 5},
]

# ─── Course + Chapter definitions ────────────────────────────────────────────
# Each chapter: { title, description, vocab_topics (list of Word.topic strings) }
# vocab_topics are used later by seed_vocab_lessons to link Lesson→Word

COURSES = {
    "A1": {
        "title": "Nền tảng tiếng Anh",
        "title_en": "English Foundations",
        "description": (
            "Khoá học A1 xây dựng nền tảng vững chắc với ngữ pháp cơ bản, "
            "từ vựng hàng ngày và các tình huống giao tiếp thiết yếu."
        ),
        "is_premium": False,
        "chapters": [
            {
                "title": "Giới thiệu bản thân",
                "description": "Học cách giới thiệu bản thân, hỏi & trả lời về tên, quốc tịch, nghề nghiệp.",
                "vocab_topics": [],  # A1 vocab files don't exist yet
                "grammar_hint": "Present simple of 'be' (am/is/are), Subject pronouns",
            },
            {
                "title": "Gia đình & Bạn bè",
                "description": "Mô tả gia đình và bạn bè, dùng tính từ sở hữu và đại từ chỉ định.",
                "vocab_topics": [],
                "grammar_hint": "Possessive adjectives (my/your/his…), This/That/These/Those",
            },
            {
                "title": "Cuộc sống hàng ngày",
                "description": "Nói về thói quen và lịch trình hàng ngày.",
                "vocab_topics": [],
                "grammar_hint": "Present simple (I do, I don't, Do I?), Adverbs of frequency",
            },
            {
                "title": "Nhà ở & Đồ vật",
                "description": "Mô tả ngôi nhà, phòng ốc và đồ đạc.",
                "vocab_topics": [],
                "grammar_hint": "Articles (a/an/the), There is/There are, Prepositions of place",
            },
            {
                "title": "Mua sắm & Số lượng",
                "description": "Hỏi giá, mô tả số lượng khi mua sắm.",
                "vocab_topics": [],
                "grammar_hint": "Much/Many, Countable/Uncountable nouns, How much/How many",
            },
            {
                "title": "Thời tiết & Quần áo",
                "description": "Mô tả thời tiết và quần áo đang mặc.",
                "vocab_topics": [],
                "grammar_hint": "Present continuous (I'm doing), Adjectives",
            },
            {
                "title": "Đồ ăn & Uống",
                "description": "Đặt món, nói về sở thích ăn uống.",
                "vocab_topics": [],
                "grammar_hint": "Some/Any, Would like, I'd like…",
            },
            {
                "title": "Kế hoạch & Tương lai",
                "description": "Nói về kế hoạch sắp tới và dự đoán tương lai.",
                "vocab_topics": [],
                "grammar_hint": "Be going to, Will/Shall for future",
            },
            {
                "title": "Sở thích & Giải trí",
                "description": "Nói về sở thích và hoạt động giải trí.",
                "vocab_topics": [],
                "grammar_hint": "Like/Love/Hate + -ing, Adverbs of frequency",
            },
            {
                "title": "Chỉ đường & Di chuyển",
                "description": "Hỏi và chỉ đường, dùng giới từ chỉ vị trí.",
                "vocab_topics": [],
                "grammar_hint": "Imperative, Prepositions of place (on/in/at/next to…)",
            },
            {
                "title": "Kinh nghiệm quá khứ",
                "description": "Kể về các sự kiện và trải nghiệm trong quá khứ.",
                "vocab_topics": [],
                "grammar_hint": "Past simple (was/were, regular + irregular verbs)",
            },
            {
                "title": "Ôn tập tổng hợp A1",
                "description": "Tổng ôn toàn bộ kiến thức A1 qua các bài tập đa dạng.",
                "vocab_topics": [],
                "grammar_hint": "Mixed tenses and structures review",
            },
        ],
    },

    "A2": {
        "title": "Tiếng Anh cho cuộc sống",
        "title_en": "Everyday English",
        "description": (
            "Khoá A2 đưa người học vào các tình huống thực tế hàng ngày: "
            "du lịch, mua sắm, sức khoẻ và giao tiếp xã hội."
        ),
        "is_premium": False,
        "chapters": [
            {
                "title": "Thói quen & Lịch trình",
                "description": "Mô tả thói quen hàng ngày và lịch trình cá nhân.",
                "vocab_topics": ["Daily Life - Daily Routines & Habits", "Daily Life - Personal Care & Hygiene"],
                "grammar_hint": "Present simple vs continuous, Adverbs of frequency",
            },
            {
                "title": "Nhà cửa & Việc nhà",
                "description": "Nói về nhà ở và phân công công việc nhà.",
                "vocab_topics": ["Daily Life - Housing & Accommodation", "Daily Life - Household Chores & Cleaning"],
                "grammar_hint": "Have to / Must / Mustn't, Imperatives",
            },
            {
                "title": "Gia đình & Cảm xúc",
                "description": "Mô tả gia đình, mối quan hệ và cảm xúc.",
                "vocab_topics": ["Daily Life - Family & Relationships", "Daily Life - Emotions & Feelings"],
                "grammar_hint": "Comparative adjectives, Used to",
            },
            {
                "title": "Thời tiết & Khí hậu",
                "description": "Nói về thời tiết, dự báo và khí hậu.",
                "vocab_topics": ["Daily Life - Weather & Climate"],
                "grammar_hint": "Will for predictions, Might/May for possibility",
            },
            {
                "title": "Đi mua sắm",
                "description": "Mua sắm, so sánh giá cả và lựa chọn sản phẩm.",
                "vocab_topics": ["Daily Life - Shopping & Supermarket", "Daily Life - Supermarket Aisles & Groceries"],
                "grammar_hint": "Too/Enough, Quantifiers (a lot of/a few/a little)",
            },
            {
                "title": "Tài chính cá nhân",
                "description": "Quản lý tiền bạc, giao dịch ngân hàng và tiết kiệm.",
                "vocab_topics": ["Daily Life - Personal Finance, Taxes & Mortgages", "Daily Life - Banking & Personal Finance"],
                "grammar_hint": "First conditional (If + present simple, will)",
            },
            {
                "title": "Đặt vé & Khách sạn",
                "description": "Đặt vé máy bay, khách sạn và lên kế hoạch chuyến đi.",
                "vocab_topics": ["Travel - Booking Flights & Hotels"],
                "grammar_hint": "Going to vs Will, Future plans and arrangements",
            },
            {
                "title": "Ở sân bay",
                "description": "Làm thủ tục sân bay, quá cảnh và quản lý hành lý.",
                "vocab_topics": ["Travel - At the Airport & Immigration", "Travel - Luggage & Packing"],
                "grammar_hint": "Past simple regular/irregular verbs, Time expressions",
            },
            {
                "title": "Tham quan & Chỉ đường",
                "description": "Khám phá địa điểm du lịch và hỏi đường.",
                "vocab_topics": ["Travel - Sightseeing & Attractions", "Travel - Directions & Navigation"],
                "grammar_hint": "Present perfect (ever/never/just/already/yet)",
            },
            {
                "title": "Giao thông & Sự cố",
                "description": "Sử dụng phương tiện công cộng và xử lý sự cố khi đi lại.",
                "vocab_topics": ["Travel - Public Transportation", "Travel - Travel Emergencies & Problems"],
                "grammar_hint": "Comparative and Superlative adjectives",
            },
            {
                "title": "Nấu ăn & Nhà hàng",
                "description": "Đặt món, đánh giá nhà hàng và nói về ẩm thực.",
                "vocab_topics": ["Food - Cooking Methods & Recipes", "Food - At the Restaurant & Ordering"],
                "grammar_hint": "Countable/Uncountable nouns, Some/Any/No",
            },
            {
                "title": "Dinh dưỡng & Đồ uống",
                "description": "Nói về chế độ ăn uống lành mạnh và các loại đồ uống.",
                "vocab_topics": ["Food - Ingredients & Spices", "Food - Diets & Nutrition", "Food - Beverages & Drinks"],
                "grammar_hint": "Should/Shouldn't for advice, Modal review",
            },
            {
                "title": "Sức khoẻ & Bệnh viện",
                "description": "Mô tả triệu chứng, đi khám bác sĩ và mua thuốc.",
                "vocab_topics": ["Health - At the Hospital & Clinic", "Health - Symptoms & Illnesses", "Health - Medicines & Treatments"],
                "grammar_hint": "Need to / Had better, Past continuous",
            },
            {
                "title": "Thể dục & Lối sống",
                "description": "Duy trì sức khoẻ qua tập luyện và chăm sóc bản thân.",
                "vocab_topics": ["Health - Fitness & Workout", "Daily Life - Cosmetics, Skincare & Grooming"],
                "grammar_hint": "Gerund vs Infinitive (like doing / want to do)",
            },
            {
                "title": "Sự kiện đời sống",
                "description": "Nói về các dịp đặc biệt: đám cưới, tốt nghiệp, chuyển nhà.",
                "vocab_topics": ["Life Events - Weddings & Marriage", "Life Events - Graduation & Anniversaries", "Life Events - Moving House & Relocation"],
                "grammar_hint": "Past simple narrative, Time linkers (first/then/after/finally)",
            },
            {
                "title": "Giao tiếp xã hội",
                "description": "Bắt chuyện, xin lỗi và dùng ngôn ngữ lịch sự.",
                "vocab_topics": ["Communication - Small Talk & Icebreakers", "Communication - Complaining & Apologizing"],
                "grammar_hint": "Polite requests with Would/Could, Offers and suggestions",
            },
        ],
    },

    "B1": {
        "title": "Mở rộng tiếng Anh",
        "title_en": "Expanding English",
        "description": (
            "Khoá B1 đưa người học vào thế giới nghề nghiệp, công nghệ và văn hoá "
            "với ngữ pháp trung cấp và từ vựng thực dụng."
        ),
        "is_premium": True,
        "chapters": [
            {
                "title": "Phỏng vấn & CV",
                "description": "Chuẩn bị hồ sơ và phỏng vấn xin việc bằng tiếng Anh.",
                "vocab_topics": ["Modern Career - Job Interviews & CVs"],
                "grammar_hint": "Present perfect vs Past simple, Interview verb patterns",
            },
            {
                "title": "Làm từ xa & Freelance",
                "description": "Thảo luận về xu hướng làm việc từ xa và tự do.",
                "vocab_topics": ["Modern Career - Remote Work & Telecommuting", "Modern Career - Freelancing & Gig Economy"],
                "grammar_hint": "Second conditional (If + past, would), Hypothetical situations",
            },
            {
                "title": "Lãnh đạo & Thuyết trình",
                "description": "Kỹ năng lãnh đạo và trình bày ý kiến trước đám đông.",
                "vocab_topics": ["Modern Career - Leadership & Management", "Modern Career - Business Presentations & Public Speaking"],
                "grammar_hint": "Passive voice (present/past), Reported speech",
            },
            {
                "title": "Khởi nghiệp & Networking",
                "description": "Xây dựng mạng lưới quan hệ và hiểu về startup.",
                "vocab_topics": ["Modern Career - Startup & Entrepreneurship", "Modern Career - Networking & Professional Relationships"],
                "grammar_hint": "Relative clauses (who/which/that/where)",
            },
            {
                "title": "Thương mại điện tử & Mạng xã hội",
                "description": "Mua sắm trực tuyến, marketing số và mạng xã hội.",
                "vocab_topics": ["Digital Life - E-commerce & Online Shopping", "Digital Life - Social Media & Networking"],
                "grammar_hint": "Third conditional, Wish + past perfect",
            },
            {
                "title": "Công nghệ & Quyền riêng tư",
                "description": "Lập trình, phần mềm và bảo mật thông tin.",
                "vocab_topics": ["Digital Life - Software Development & Coding", "Digital Life - Data Privacy & Cyber Ethics"],
                "grammar_hint": "Passive voice (past), Modal perfect (should have/could have)",
            },
            {
                "title": "Phim & Âm nhạc",
                "description": "Nói về phim ảnh, âm nhạc và văn hoá đại chúng.",
                "vocab_topics": ["Entertainment - Movies, Cinema & Oscars", "Entertainment - Music Genres & Concerts"],
                "grammar_hint": "Used to vs Would for past habits, Narrative tenses",
            },
            {
                "title": "Sách & Thời trang",
                "description": "Thảo luận về văn học và xu hướng thời trang.",
                "vocab_topics": ["Entertainment - Books, Literature & Publishing", "Entertainment - Fashion, Beauty & Trends"],
                "grammar_hint": "Reported speech advanced, Say vs Tell",
            },
            {
                "title": "Hoạt động ngoài trời",
                "description": "Nói về cắm trại, thể thao và hoạt động ngoài trời.",
                "vocab_topics": ["Leisure - Outdoor Activities & Camping", "Leisure - Sports Competitions & Olympics"],
                "grammar_hint": "Future continuous, Future perfect",
            },
            {
                "title": "Sức khoẻ tinh thần",
                "description": "Thảo luận về wellbeing, mindfulness và phát triển bản thân.",
                "vocab_topics": ["Social Trends - Mental Well-being & Self-care", "Social Trends - Personal Development & Productivity"],
                "grammar_hint": "Should/Ought to/Had better review, Causative (have/get something done)",
            },
            {
                "title": "Ẩm thực & Văn hoá ăn uống",
                "description": "Xu hướng ăn uống, ẩm thực nghệ thuật và vegan.",
                "vocab_topics": ["Social Trends - Veganism & Plant-based Diets", "Industry - Culinary Arts & Fine Dining"],
                "grammar_hint": "As...as comparison, Much/a lot + comparative",
            },
            {
                "title": "Giao tiếp công sở",
                "description": "Viết email chuyên nghiệp và đàm phán trong công việc.",
                "vocab_topics": ["Communication - Email Writing & Etiquette", "Communication - Negotiating & Persuading"],
                "grammar_hint": "Formal register, Discourse markers (however/furthermore/nevertheless)",
            },
            {
                "title": "Xã hội & Đa dạng văn hoá",
                "description": "Bàn về bình đẳng, đa dạng và thay đổi xã hội.",
                "vocab_topics": ["Society - Cultural Diversity & Inclusion", "Society - Gender Equality & Feminism"],
                "grammar_hint": "Advanced articles (the/zero), Abstract nouns",
            },
            {
                "title": "Môi trường & Bền vững",
                "description": "Thảo luận về biến đổi khí hậu và lối sống xanh.",
                "vocab_topics": ["Social Trends - Sustainability & Eco-friendly Living", "Trends - Eco-friendly Living & Zero Waste"],
                "grammar_hint": "Non-defining relative clauses, Passive review",
            },
            {
                "title": "Ôn tập tổng hợp B1",
                "description": "Tổng ôn B1 qua bài đọc, từ vựng và ngữ pháp tích hợp.",
                "vocab_topics": [],
                "grammar_hint": "Mixed B1 grammar, Timed exercises",
            },
        ],
    },

    "B2": {
        "title": "Tiếng Anh chuyên sâu",
        "title_en": "Advanced English",
        "description": (
            "Khoá B2 tập trung vào tiếng Anh thương mại, chuyên ngành và "
            "các cấu trúc ngữ pháp phức tạp hướng đến TOEIC/IELTS."
        ),
        "is_premium": True,
        "chapters": [
            {
                "title": "Mua hàng & Hợp đồng",
                "description": "Quy trình mua sắm doanh nghiệp và điều khoản hợp đồng.",
                "vocab_topics": ["TOEIC - Purchasing & Procurement", "TOEIC - Contracts & Legal Agreements"],
                "grammar_hint": "Mixed conditionals, Formal expressions of obligation",
            },
            {
                "title": "Họp & Chiến lược",
                "description": "Dẫn dắt cuộc họp và thảo luận chiến lược công ty.",
                "vocab_topics": ["TOEIC - Board Meetings & Committees", "TOEIC - Corporate Planning & Strategy"],
                "grammar_hint": "Reported speech advanced, Passive causative",
            },
            {
                "title": "Marketing & Bán hàng",
                "description": "Chiến lược marketing, kênh bán hàng và dịch vụ khách hàng.",
                "vocab_topics": ["TOEIC - Sales & Marketing", "TOEIC - Customer Service & Support"],
                "grammar_hint": "Emphasis structures (do/does/did + verb), Cleft sentences",
            },
            {
                "title": "Nhân sự & Tài chính",
                "description": "Quản trị nhân sự, tuyển dụng và kế toán.",
                "vocab_topics": ["TOEIC - Human Resources & Recruiting", "TOEIC - Accounting & Finance"],
                "grammar_hint": "Inversion (Not only...but also, Rarely/Hardly ever...)",
            },
            {
                "title": "Sản xuất & Kiểm tra chất lượng",
                "description": "Quy trình sản xuất và tiêu chuẩn chất lượng.",
                "vocab_topics": ["TOEIC - Manufacturing & Production", "TOEIC - Quality Control & Inspections"],
                "grammar_hint": "Participle clauses (-ing/-ed phrases)",
            },
            {
                "title": "Logistics & Vận chuyển",
                "description": "Chuỗi cung ứng, giao nhận hàng hoá và cảng biển.",
                "vocab_topics": ["TOEIC - Shipping & Logistics", "Industry - Logistics & Warehousing"],
                "grammar_hint": "Nominal clauses (the fact that/what/whether)",
            },
            {
                "title": "Bất động sản & Ngân hàng",
                "description": "Giao dịch bất động sản và dịch vụ ngân hàng đầu tư.",
                "vocab_topics": ["TOEIC - Property & Real Estate", "TOEIC - Banking & Investments"],
                "grammar_hint": "Subjunctive (I suggest that he be...), Wish/If only",
            },
            {
                "title": "Crypto & Metaverse",
                "description": "Tiền kỹ thuật số, blockchain và thực tế ảo.",
                "vocab_topics": ["Digital Life - Cryptocurrencies & Blockchain", "Digital Life - Virtual Reality & Metaverse"],
                "grammar_hint": "Future perfect continuous, Advanced modals (must/can't have)",
            },
            {
                "title": "Games & Nhiếp ảnh",
                "description": "E-sports, nhiếp ảnh và nghệ thuật kỹ thuật số.",
                "vocab_topics": ["Entertainment - Video Games & E-sports", "Entertainment - Photography & Visual Arts"],
                "grammar_hint": "Habitual actions (will/would/used to), Aspect contrast",
            },
            {
                "title": "Xây dựng & Nông nghiệp",
                "description": "Ngành xây dựng hạ tầng và nông nghiệp công nghệ cao.",
                "vocab_topics": ["Industry - Construction & Heavy Machinery", "Industry - Agriculture & Farming"],
                "grammar_hint": "Complex passive (was being built, had been installed)",
            },
            {
                "title": "Luật pháp & An ninh",
                "description": "Thực thi pháp luật, hệ thống tư pháp và an toàn cộng đồng.",
                "vocab_topics": ["Industry - Law Enforcement & Policing", "Industry - Firefighting & Emergency Services"],
                "grammar_hint": "Defining vs non-defining relative clauses",
            },
            {
                "title": "Hàng không & Hàng hải",
                "description": "Ngành hàng không, vận tải biển và logistics quốc tế.",
                "vocab_topics": ["Industry - Aviation & Aerospace", "Industry - Maritime, Shipping & Ports"],
                "grammar_hint": "Nominalization (decide → decision), Formal written register",
            },
            {
                "title": "Xung đột & Tranh luận",
                "description": "Giải quyết mâu thuẫn công sở và thể hiện quan điểm.",
                "vocab_topics": ["Modern Career - Workplace Conflict & Resolution", "Communication - Expressing Opinions & Debating"],
                "grammar_hint": "Discourse markers and hedging (apparently/it seems/arguably)",
            },
            {
                "title": "Ôn tập TOEIC B2",
                "description": "Luyện thi TOEIC với bài đọc, ngữ pháp và từ vựng chuyên ngành.",
                "vocab_topics": [],
                "grammar_hint": "Full B2 grammar review, TOEIC question patterns",
            },
        ],
    },

    "C1": {
        "title": "Tiếng Anh học thuật & Chuyên gia",
        "title_en": "Academic & Expert English",
        "description": (
            "Khoá C1 hướng đến tiếng Anh học thuật, IELTS và ngôn ngữ chuyên gia "
            "trong các lĩnh vực khoa học, kinh doanh và pháp lý."
        ),
        "is_premium": True,
        "chapters": [
            {
                "title": "Toàn cầu hoá",
                "description": "Phân tích tác động của toàn cầu hoá và thương mại quốc tế.",
                "vocab_topics": ["IELTS & Academic - Global Issues & Globalization", "Advanced Business - International Trade & Tariffs"],
                "grammar_hint": "Complex sentence architecture, Cohesive devices",
            },
            {
                "title": "Tội phạm & Pháp luật",
                "description": "Thảo luận về hệ thống pháp luật và tư pháp hình sự.",
                "vocab_topics": ["IELTS & Academic - Crime, Law & Justice", "Law & Society - Legal Proceedings & Courtrooms"],
                "grammar_hint": "Subjunctive in formal contexts, Concessive clauses",
            },
            {
                "title": "Truyền thông & Báo chí",
                "description": "Phân tích vai trò của báo chí và truyền thông đại chúng.",
                "vocab_topics": ["IELTS & Academic - Media, News & Journalism", "Industry - Journalism, Broadcasting & Podcasting"],
                "grammar_hint": "Reporting verbs, Nominalizations",
            },
            {
                "title": "Nghệ thuật & Văn hoá",
                "description": "Bình luận về nghệ thuật, văn học và di sản văn hoá.",
                "vocab_topics": ["IELTS & Academic - Arts, Culture & Museums", "Culture - Fine Arts, Sculptures & Exhibitions"],
                "grammar_hint": "Inversion for emphasis, Literary/aesthetic language",
            },
            {
                "title": "Đô thị hoá & Kiến trúc",
                "description": "Xu hướng đô thị hoá, thiết kế đô thị và kiến trúc.",
                "vocab_topics": ["IELTS & Academic - City Life & Urbanization", "Arts & Design - Architecture & Urban Planning"],
                "grammar_hint": "Academic register, Hedging language (tend to/appear to)",
            },
            {
                "title": "Triết học & Đạo đức",
                "description": "Thảo luận triết học, đạo đức và quan điểm cuộc sống.",
                "vocab_topics": ["Academic - Philosophy & Ethics", "Academic - Psychology & Cognitive Science"],
                "grammar_hint": "Complex modality, Hypothetical and counterfactual",
            },
            {
                "title": "Chính trị & Kinh tế",
                "description": "Phân tích hệ thống chính trị, bầu cử và kinh tế vĩ mô.",
                "vocab_topics": ["Academic - Political Science & Government", "Academic - Macroeconomics & Microeconomics"],
                "grammar_hint": "Formal passive chains, Impersonal structures (It is argued that…)",
            },
            {
                "title": "Khoa học tự nhiên",
                "description": "Ngôn ngữ khoa học cho vật lý, hoá học và sinh học.",
                "vocab_topics": ["Academic - Physics & Quantum Mechanics", "Academic - Chemistry & Materials Science", "Academic - Biology & Anatomy"],
                "grammar_hint": "Reduced relative clauses, Technical register",
            },
            {
                "title": "AI & Robotics",
                "description": "Trí tuệ nhân tạo, tự động hoá và tác động xã hội.",
                "vocab_topics": ["Science - Artificial Intelligence & Data", "Science - Robotics & Automation"],
                "grammar_hint": "Fronting and topicalisation, Ellipsis",
            },
            {
                "title": "Môi trường & Năng lượng sạch",
                "description": "Biến đổi khí hậu, năng lượng tái tạo và chính sách môi trường.",
                "vocab_topics": ["Science - Environment & Conservation", "Science - Climate Change & Global Warming", "Science - Renewable Energy & Green Tech"],
                "grammar_hint": "Academic argument structure, Counter-argument patterns",
            },
            {
                "title": "Y tế & Y khoa",
                "description": "Ngôn ngữ y khoa cho phẫu thuật, dược học và nhi khoa.",
                "vocab_topics": ["Medicine - Surgery & Operating Room", "Medicine - Pharmacology & Drugs", "Medicine - Pediatrics & Child Healthcare"],
                "grammar_hint": "Technical collocations, Latin/Greek-root vocabulary",
            },
            {
                "title": "Kinh doanh nâng cao",
                "description": "Mua bán doanh nghiệp, trách nhiệm xã hội và huy động vốn.",
                "vocab_topics": ["Advanced Business - Mergers & Acquisitions", "Advanced Business - Corporate Social Responsibility", "Advanced Business - Venture Capital & Fundraising"],
                "grammar_hint": "Negotiation language, Hedging and strengthening",
            },
            {
                "title": "Xã hội & Nhân quyền",
                "description": "Nhân quyền, di cư và các vấn đề xã hội toàn cầu.",
                "vocab_topics": ["Law & Society - Immigration, Refugees & Borders", "Law & Society - Human Rights & Civil Liberties", "Law & Society - Elections & Voting Systems"],
                "grammar_hint": "Evaluative language, Concession (while/although/even though)",
            },
            {
                "title": "Nghiên cứu & Học thuật",
                "description": "Phương pháp nghiên cứu, ngôn ngữ học thuật và trích dẫn.",
                "vocab_topics": ["Academic - Linguistics & Language Learning", "Academic - Research & Methodology"],
                "grammar_hint": "Citation language (according to/as X claims), Academic hedging",
            },
            {
                "title": "Ôn tập IELTS C1",
                "description": "Luyện IELTS: đọc hiểu học thuật, từ vựng nâng cao và ngữ pháp phức tạp.",
                "vocab_topics": [],
                "grammar_hint": "Full C1 grammar, IELTS Writing/Reading task types",
            },
        ],
    },
}

# Lesson template per chapter
LESSON_TEMPLATES = [
    {
        "order": 1,
        "name": "Khám phá từ vựng",
        "lesson_type": "vocabulary",
        "estimated_minutes": 10,
    },
    {
        "order": 2,
        "name": "Ngữ pháp trong ngữ cảnh",
        "lesson_type": "grammar",
        "estimated_minutes": 15,
    },
    {
        "order": 3,
        "name": "Đọc hiểu",
        "lesson_type": "reading",
        "estimated_minutes": 15,
    },
    {
        "order": 4,
        "name": "Luyện nghe",
        "lesson_type": "listening",
        "estimated_minutes": 10,
    },
    {
        "order": 5,
        "name": "Luyện nói",
        "lesson_type": "speaking",
        "estimated_minutes": 8,
    },
    {
        "order": 6,
        "name": "Luyện viết",
        "lesson_type": "writing",
        "estimated_minutes": 10,
    },
    {
        "order": 7,
        "name": "Thực hành tổng hợp",
        "lesson_type": "assessment",
        "estimated_minutes": 10,
    },
]


class Command(BaseCommand):
    help = "Seed CEFRLevel, Course, Chapter and skeleton Lesson records for A1–C1"

    def add_arguments(self, parser):
        parser.add_argument(
            "--level",
            dest="levels",
            action="append",
            choices=list(COURSES.keys()),
            default=None,
            help="Which level(s) to seed (default: all)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Delete existing courses for the given level(s) before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        levels = options["levels"] or list(COURSES.keys())

        # 1. Ensure CEFRLevel rows exist
        for lv in CEFR_LEVELS:
            obj, created = CEFRLevel.objects.update_or_create(
                code=lv["code"],
                defaults={
                    "name": lv["name"],
                    "name_vi": lv["name_vi"],
                    "order": lv["order"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"  Created CEFRLevel: {obj.code}")

        for level_code in levels:
            cefr = CEFRLevel.objects.get(code=level_code)
            course_def = COURSES[level_code]

            if options["clear"]:
                deleted, _ = Course.objects.filter(level=cefr).delete()
                if deleted:
                    self.stdout.write(self.style.WARNING(f"  [{level_code}] Cleared {deleted} courses"))

            # 2. Create / update Course
            slug = f"{level_code.lower()}-{course_def['title_en'].lower().replace(' ', '-').replace('&', 'and')}"
            course, c_created = Course.objects.update_or_create(
                slug=slug,
                defaults={
                    "level": cefr,
                    "title": course_def["title"],
                    "description": course_def["description"],
                    "order": cefr.order,
                    "is_premium": course_def.get("is_premium", True),
                    "is_active": True,
                },
            )
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"\n[{level_code}] {'Created' if c_created else 'Updated'} course: {course.title}"
                )
            )

            ch_count = les_count = 0

            # 3. Create Chapters + skeleton Lessons
            for ch_order, ch_def in enumerate(course_def["chapters"], start=1):
                chapter, _ = Chapter.objects.update_or_create(
                    course=course,
                    order=ch_order,
                    defaults={
                        "title": ch_def["title"],
                        "description": ch_def.get("description", ""),
                        "passing_score": 60,
                    },
                )
                ch_count += 1

                for tmpl in LESSON_TEMPLATES:
                    lesson_title = f"{ch_def['title']} — {tmpl['name']}"
                    Lesson.objects.update_or_create(
                        chapter=chapter,
                        order=tmpl["order"],
                        defaults={
                            "title": lesson_title,
                            "lesson_type": tmpl["lesson_type"],
                            "estimated_minutes": tmpl["estimated_minutes"],
                            "is_active": True,
                        },
                    )
                    les_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  → {ch_count} chapters, {les_count} lessons"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nDone — seed_courses complete."))
