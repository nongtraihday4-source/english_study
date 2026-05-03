"""
Management command: seed_passages
Seeds realistic PracticePassage data for Dictation + Shadowing practice.

Usage:
    python manage.py seed_passages
    python manage.py seed_passages --clear   # delete all passages first
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.skill_practice.models import PracticePassage

PASSAGES = [
    # ── A1 ──────────────────────────────────────────────────────────────────
    {
        "title": "My Daily Routine",
        "full_text": (
            "My name is Linh. I wake up at six o'clock every morning. "
            "I brush my teeth and wash my face. "
            "Then I eat breakfast with my family. "
            "I usually have rice and eggs for breakfast. "
            "I go to school by bicycle. "
            "School starts at seven thirty. "
            "I study English, Maths, and Science. "
            "I come home at noon and have lunch. "
            "In the afternoon, I do my homework. "
            "I go to bed at ten o'clock at night."
        ),
        "translation_vi": (
            "Tên tôi là Linh. Tôi thức dậy lúc sáu giờ mỗi sáng. "
            "Tôi đánh răng và rửa mặt. "
            "Sau đó tôi ăn sáng cùng gia đình. "
            "Tôi thường ăn cơm và trứng vào bữa sáng. "
            "Tôi đi học bằng xe đạp. "
            "Trường bắt đầu lúc bảy giờ ba mươi. "
            "Tôi học tiếng Anh, Toán và Khoa học. "
            "Tôi về nhà lúc trưa và ăn trưa. "
            "Vào buổi chiều, tôi làm bài tập. "
            "Tôi đi ngủ lúc mười giờ tối."
        ),
        "topic": "Daily Life - Daily Routines & Habits",
        "cefr_level": "A1",
        "difficulty_tag": "easy",
        "grammar_notes": "Uses Present Simple tense for habitual daily actions.",
        "tts_voice": "en-US-AriaNeural",
    },
    {
        "title": "My Family",
        "full_text": (
            "I have a small family. "
            "There are four people in my family. "
            "My father is a doctor. He works at a big hospital. "
            "My mother is a teacher. She teaches at a primary school. "
            "My sister is eight years old. She is in grade three. "
            "I am fifteen years old. I am in grade nine. "
            "We live in a small house near the park. "
            "We love spending time together on weekends."
        ),
        "translation_vi": (
            "Tôi có một gia đình nhỏ. "
            "Có bốn người trong gia đình tôi. "
            "Bố tôi là bác sĩ. Ông ấy làm việc ở một bệnh viện lớn. "
            "Mẹ tôi là giáo viên. Bà dạy ở một trường tiểu học. "
            "Em gái tôi tám tuổi. Em học lớp ba. "
            "Tôi mười lăm tuổi. Tôi học lớp chín. "
            "Chúng tôi sống trong một ngôi nhà nhỏ gần công viên. "
            "Chúng tôi thích dành thời gian bên nhau vào cuối tuần."
        ),
        "topic": "Daily Life - Family & Relationships",
        "cefr_level": "A1",
        "difficulty_tag": "easy",
        "grammar_notes": "Uses 'to be' and Present Simple. Introduces family vocabulary.",
        "tts_voice": "en-US-JennyNeural",
    },
    {
        "title": "At the Market",
        "full_text": (
            "On Saturday morning, I go to the market with my mother. "
            "The market is near our house. "
            "We buy vegetables, fruit, and meat. "
            "My mother likes fresh tomatoes and green beans. "
            "I like apples and bananas. "
            "We also buy fish for dinner. "
            "The fish seller is very friendly. "
            "We spend about one hour at the market. "
            "Then we go home and cook lunch together."
        ),
        "translation_vi": (
            "Vào sáng thứ Bảy, tôi đi chợ với mẹ. "
            "Chợ ở gần nhà chúng tôi. "
            "Chúng tôi mua rau, trái cây và thịt. "
            "Mẹ tôi thích cà chua tươi và đậu que. "
            "Tôi thích táo và chuối. "
            "Chúng tôi cũng mua cá cho bữa tối. "
            "Người bán cá rất thân thiện. "
            "Chúng tôi dành khoảng một tiếng ở chợ. "
            "Sau đó chúng tôi về nhà và nấu ăn trưa cùng nhau."
        ),
        "topic": "Daily Life - Shopping & Retail",
        "cefr_level": "A1",
        "difficulty_tag": "easy",
        "grammar_notes": "Present Simple: habitual actions. Shopping vocabulary.",
        "tts_voice": "en-US-AriaNeural",
    },

    # ── A2 ──────────────────────────────────────────────────────────────────
    {
        "title": "A Weekend Trip to the Beach",
        "full_text": (
            "Last weekend, my friends and I went to the beach. "
            "We left early in the morning to avoid the traffic. "
            "The journey took about two hours by bus. "
            "When we arrived, the beach was already quite crowded. "
            "We found a nice spot near the water and spread out our towels. "
            "I swam in the sea while my friends played volleyball on the sand. "
            "We ate seafood for lunch at a small restaurant by the beach. "
            "The grilled fish was absolutely delicious. "
            "In the afternoon, we took lots of photos and collected shells. "
            "We returned home tired but very happy."
        ),
        "translation_vi": (
            "Cuối tuần trước, tôi và bạn bè đã đi biển. "
            "Chúng tôi khởi hành sớm vào buổi sáng để tránh kẹt xe. "
            "Chuyến đi mất khoảng hai tiếng bằng xe buýt. "
            "Khi đến nơi, bãi biển đã khá đông người. "
            "Chúng tôi tìm được một chỗ đẹp gần mặt nước và trải khăn ra. "
            "Tôi bơi trong biển trong khi các bạn chơi bóng chuyền trên cát. "
            "Chúng tôi ăn hải sản vào bữa trưa ở một nhà hàng nhỏ gần biển. "
            "Cá nướng ngon tuyệt vời. "
            "Vào buổi chiều, chúng tôi chụp nhiều ảnh và nhặt vỏ sò. "
            "Chúng tôi trở về nhà mệt mỏi nhưng rất vui."
        ),
        "topic": "Travel - Sightseeing & Attractions",
        "cefr_level": "A2",
        "difficulty_tag": "easy",
        "grammar_notes": "Past Simple for completed events. Time expressions: last weekend, early, in the afternoon.",
        "tts_voice": "en-US-AriaNeural",
    },
    {
        "title": "Ordering Food at a Café",
        "full_text": (
            "Good morning. Can I take your order? "
            "Yes, I'd like a cappuccino and a blueberry muffin, please. "
            "Would you like that for here or to go? "
            "For here, please. Oh, and do you have any sandwiches? "
            "Yes, we have chicken and avocado, or tuna and sweetcorn. "
            "I'll have the chicken and avocado sandwich, please. "
            "Would you like anything else? "
            "Actually, could I also get a glass of orange juice? "
            "Of course. That comes to twelve dollars fifty. "
            "Here you go. Can I get a receipt, please? "
            "Sure, I'll print that for you right away."
        ),
        "translation_vi": (
            "Chào buổi sáng. Tôi có thể lấy order của bạn không? "
            "Vâng, tôi muốn một cappuccino và một cái bánh muffin việt quất, xin vâng. "
            "Bạn muốn dùng tại đây hay mang đi? "
            "Dùng tại đây, cảm ơn. Ồ, và bạn có bánh mì sandwich không? "
            "Vâng, chúng tôi có gà và bơ, hoặc cá ngừ và ngô ngọt. "
            "Cho tôi bánh mì sandwich gà và bơ nhé. "
            "Bạn có muốn thêm gì không? "
            "À, tôi cũng muốn một ly nước cam được không? "
            "Tất nhiên rồi. Tổng cộng là mười hai đô la năm mươi xu. "
            "Đây bạn. Tôi có thể có hóa đơn không? "
            "Chắc chắn, tôi sẽ in ngay cho bạn."
        ),
        "topic": "Communication - Small Talk & Icebreakers",
        "cefr_level": "A2",
        "difficulty_tag": "medium",
        "grammar_notes": "Polite requests with 'would like', 'could I', 'can I'. Dialogue format.",
        "tts_voice": "en-US-JennyNeural",
    },
    {
        "title": "Making a Doctor's Appointment",
        "full_text": (
            "Hello, City Medical Clinic. How can I help you? "
            "Hi, I'd like to make an appointment with Doctor Sullivan. "
            "Yes, what seems to be the problem? "
            "I've had a sore throat and a fever for two days. "
            "I see. Are you an existing patient? "
            "Yes, my name is Minh Tran. "
            "Let me check Doctor Sullivan's schedule. "
            "He has an opening tomorrow at three fifteen in the afternoon. "
            "Does that work for you? "
            "Yes, that's perfect. Thank you very much. "
            "Great. Please arrive five minutes early and bring your insurance card."
        ),
        "translation_vi": (
            "Xin chào, Phòng khám Y tế Thành phố. Tôi có thể giúp gì cho bạn? "
            "Chào, tôi muốn đặt lịch hẹn với Bác sĩ Sullivan. "
            "Vâng, vấn đề của bạn là gì? "
            "Tôi bị đau họng và sốt hai ngày rồi. "
            "Tôi thấy rồi. Bạn có phải bệnh nhân cũ không? "
            "Vâng, tên tôi là Minh Trần. "
            "Để tôi kiểm tra lịch của Bác sĩ Sullivan. "
            "Ông ấy có chỗ trống vào ngày mai lúc ba giờ mười lăm chiều. "
            "Thời gian đó có phù hợp với bạn không? "
            "Vâng, hoàn hảo. Cảm ơn bạn rất nhiều. "
            "Tuyệt. Xin hãy đến sớm năm phút và mang theo thẻ bảo hiểm."
        ),
        "topic": "Health - Healthcare System & Medical Appointments",
        "cefr_level": "A2",
        "difficulty_tag": "medium",
        "grammar_notes": "Present Perfect for recent states: 'I've had'. Dialogue with polite requests.",
        "tts_voice": "en-US-GuyNeural",
    },

    # ── B1 ──────────────────────────────────────────────────────────────────
    {
        "title": "The Benefits of Learning a New Language",
        "full_text": (
            "Learning a new language is one of the most rewarding experiences a person can have. "
            "Not only does it open doors to new cultures and ways of thinking, "
            "but it also has significant cognitive benefits. "
            "Studies have shown that bilingual people tend to have better memory and "
            "stronger problem-solving skills than those who speak only one language. "
            "Furthermore, knowing another language can greatly improve your career prospects, "
            "especially in today's globalised economy. "
            "Many employers actively seek candidates who can communicate in multiple languages. "
            "Of course, learning a language requires patience and consistent practice. "
            "The key is to immerse yourself in the language as much as possible — "
            "watch films, listen to podcasts, and speak with native speakers whenever you get the chance. "
            "Even making small mistakes is part of the process, so don't be afraid to try."
        ),
        "translation_vi": (
            "Học một ngôn ngữ mới là một trong những trải nghiệm bổ ích nhất mà người ta có thể có. "
            "Nó không chỉ mở ra cánh cửa dẫn đến những nền văn hóa và cách suy nghĩ mới, "
            "mà còn có những lợi ích nhận thức đáng kể. "
            "Các nghiên cứu đã chỉ ra rằng người song ngữ có xu hướng có trí nhớ tốt hơn và "
            "kỹ năng giải quyết vấn đề mạnh hơn những người chỉ nói một ngôn ngữ. "
            "Hơn nữa, biết thêm một ngôn ngữ khác có thể cải thiện đáng kể triển vọng nghề nghiệp của bạn, "
            "đặc biệt trong nền kinh tế toàn cầu hóa ngày nay. "
            "Nhiều nhà tuyển dụng tích cực tìm kiếm các ứng viên có thể giao tiếp bằng nhiều ngôn ngữ. "
            "Tất nhiên, học ngôn ngữ đòi hỏi sự kiên nhẫn và thực hành đều đặn. "
            "Chìa khóa là đắm chìm bản thân vào ngôn ngữ càng nhiều càng tốt — "
            "xem phim, nghe podcast và nói chuyện với người bản ngữ bất cứ khi nào bạn có cơ hội. "
            "Ngay cả việc mắc những lỗi nhỏ cũng là một phần của quá trình, vì vậy đừng sợ thử."
        ),
        "topic": "Academic - Linguistics & Language Learning",
        "cefr_level": "B1",
        "difficulty_tag": "medium",
        "grammar_notes": "Not only...but also; Present Perfect; Gerunds as subjects; Passive voice.",
        "tts_voice": "en-US-AriaNeural",
    },
    {
        "title": "Working from Home: Pros and Cons",
        "full_text": (
            "Since the pandemic, working from home has become increasingly common around the world. "
            "For many employees, remote work offers a better work-life balance "
            "and eliminates the stress of commuting. "
            "You can work in comfortable clothes, set your own schedule, "
            "and spend more time with your family. "
            "However, working from home is not without its challenges. "
            "Many people struggle with distractions, especially if they have young children. "
            "It can also feel isolating without the social interaction of an office environment. "
            "Some workers find it difficult to separate their professional and personal lives "
            "when both happen in the same space. "
            "Despite these drawbacks, surveys suggest that most employees prefer a hybrid model — "
            "working partly from home and partly in the office. "
            "This approach seems to offer the best of both worlds."
        ),
        "translation_vi": (
            "Kể từ đại dịch, làm việc từ xa đã trở nên ngày càng phổ biến trên toàn thế giới. "
            "Đối với nhiều nhân viên, làm việc từ xa mang lại sự cân bằng giữa công việc và cuộc sống tốt hơn "
            "và loại bỏ căng thẳng khi di chuyển. "
            "Bạn có thể làm việc trong trang phục thoải mái, tự đặt lịch trình, "
            "và dành nhiều thời gian hơn cho gia đình. "
            "Tuy nhiên, làm việc tại nhà không phải không có thách thức. "
            "Nhiều người vật lộn với những phiền nhiễu, đặc biệt nếu họ có con nhỏ. "
            "Nó cũng có thể cảm thấy cô lập mà không có sự tương tác xã hội của môi trường văn phòng. "
            "Một số nhân viên thấy khó tách biệt cuộc sống chuyên nghiệp và cá nhân "
            "khi cả hai đều diễn ra trong cùng một không gian. "
            "Bất chấp những hạn chế này, khảo sát cho thấy hầu hết nhân viên thích mô hình kết hợp — "
            "làm việc một phần tại nhà và một phần tại văn phòng. "
            "Cách tiếp cận này dường như mang lại điều tốt nhất của cả hai thế giới."
        ),
        "topic": "Digital Life - Remote Work & Digital Nomad Lifestyle",
        "cefr_level": "B1",
        "difficulty_tag": "medium",
        "grammar_notes": "Present Perfect for recent trends; Contrast connectors: however, despite; Gerunds.",
        "tts_voice": "en-US-GuyNeural",
    },
    {
        "title": "Healthy Eating Habits",
        "full_text": (
            "Eating well is essential for maintaining good health and energy levels throughout the day. "
            "A balanced diet should include plenty of fruits, vegetables, whole grains, and lean protein. "
            "Many nutrition experts recommend eating at least five portions of fruit and vegetables daily, "
            "as they provide important vitamins, minerals, and fibre. "
            "It is also important to limit the intake of processed foods, sugary drinks, and saturated fats. "
            "These can contribute to obesity, heart disease, and other serious health conditions. "
            "Drinking enough water is equally crucial — most adults need around two litres per day. "
            "Skipping meals, particularly breakfast, can lead to low energy and poor concentration. "
            "Instead of following strict diets, nutritionists suggest making small, sustainable changes "
            "to your eating habits and focusing on variety and moderation."
        ),
        "translation_vi": (
            "Ăn uống lành mạnh là điều cần thiết để duy trì sức khỏe tốt và mức năng lượng trong suốt ngày. "
            "Chế độ ăn cân bằng nên bao gồm nhiều trái cây, rau, ngũ cốc nguyên hạt và protein nạc. "
            "Nhiều chuyên gia dinh dưỡng khuyến nghị ăn ít nhất năm phần trái cây và rau quả mỗi ngày, "
            "vì chúng cung cấp vitamin, khoáng chất và chất xơ quan trọng. "
            "Việc hạn chế tiêu thụ thực phẩm chế biến sẵn, đồ uống có đường và chất béo bão hòa cũng rất quan trọng. "
            "Những thứ này có thể dẫn đến béo phì, bệnh tim và các tình trạng sức khỏe nghiêm trọng khác. "
            "Uống đủ nước cũng rất quan trọng — hầu hết người lớn cần khoảng hai lít mỗi ngày. "
            "Bỏ bữa, đặc biệt là bữa sáng, có thể dẫn đến năng lượng thấp và khả năng tập trung kém. "
            "Thay vì tuân theo chế độ ăn kiêng nghiêm ngặt, các nhà dinh dưỡng gợi ý thực hiện những thay đổi nhỏ, bền vững "
            "đối với thói quen ăn uống và tập trung vào sự đa dạng và ăn uống điều độ."
        ),
        "topic": "Health - Diet & Nutrition",
        "cefr_level": "B1",
        "difficulty_tag": "medium",
        "grammar_notes": "Passive: 'should include', 'is recommended'. Modal verbs for advice. Contrast/addition.",
        "tts_voice": "en-US-JennyNeural",
    },

    # ── B2 ──────────────────────────────────────────────────────────────────
    {
        "title": "The Impact of Social Media on Mental Health",
        "full_text": (
            "The relationship between social media use and mental health has become a subject of intense debate "
            "among researchers, psychologists, and public health officials. "
            "While platforms like Instagram and TikTok allow people to stay connected and express themselves creatively, "
            "a growing body of evidence suggests that excessive use can have detrimental effects on well-being. "
            "Constant exposure to carefully curated images of other people's lives can foster feelings of inadequacy "
            "and fuel what psychologists call 'social comparison'. "
            "This is particularly concerning for teenagers, whose sense of identity is still developing. "
            "Studies have linked heavy social media use to increased rates of anxiety, depression, and sleep disturbances. "
            "The addictive design of these platforms — featuring infinite scrolling and notification alerts — "
            "is deliberately engineered to maximise engagement, often at the expense of users' mental health. "
            "However, it would be an oversimplification to condemn social media entirely. "
            "When used mindfully and in moderation, it can be a powerful tool for community building, "
            "mental health awareness, and peer support."
        ),
        "translation_vi": (
            "Mối quan hệ giữa việc sử dụng mạng xã hội và sức khỏe tâm thần đã trở thành chủ đề tranh luận sôi nổi "
            "trong giới nghiên cứu, nhà tâm lý học và các quan chức y tế công cộng. "
            "Trong khi các nền tảng như Instagram và TikTok cho phép mọi người kết nối và thể hiện bản thân một cách sáng tạo, "
            "ngày càng có nhiều bằng chứng cho thấy việc sử dụng quá mức có thể có những tác động có hại đến sức khỏe. "
            "Việc liên tục tiếp xúc với những hình ảnh được chọn lọc cẩn thận về cuộc sống của người khác có thể nuôi dưỡng cảm giác không đủ tốt "
            "và thúc đẩy điều mà các nhà tâm lý học gọi là 'so sánh xã hội'. "
            "Điều này đặc biệt đáng lo ngại đối với thanh thiếu niên, những người có ý thức về bản thân vẫn đang phát triển. "
            "Các nghiên cứu đã liên kết việc sử dụng mạng xã hội nhiều với tỷ lệ lo lắng, trầm cảm và rối loạn giấc ngủ tăng cao. "
            "Thiết kế gây nghiện của các nền tảng này — với tính năng cuộn vô hạn và cảnh báo thông báo — "
            "được thiết kế có chủ ý để tối đa hóa sự tương tác, thường là đánh đổi sức khỏe tâm thần của người dùng. "
            "Tuy nhiên, sẽ là quá đơn giản hóa nếu lên án mạng xã hội hoàn toàn. "
            "Khi được sử dụng có ý thức và điều độ, nó có thể là một công cụ mạnh mẽ để xây dựng cộng đồng, "
            "nâng cao nhận thức về sức khỏe tâm thần và hỗ trợ đồng đẳng."
        ),
        "topic": "Digital Life - Social Media & Networking",
        "cefr_level": "B2",
        "difficulty_tag": "hard",
        "grammar_notes": "Complex noun phrases; Passive voice; while/whereas contrast; Cleft sentences for emphasis.",
        "tts_voice": "en-US-AriaNeural",
    },
    {
        "title": "Climate Change and Individual Responsibility",
        "full_text": (
            "Climate change is arguably the most pressing challenge facing humanity in the twenty-first century. "
            "The scientific consensus is unequivocal: human activities, particularly the burning of fossil fuels "
            "and large-scale deforestation, are driving a rapid increase in global temperatures. "
            "The consequences — rising sea levels, more frequent extreme weather events, and widespread biodiversity loss — "
            "threaten the stability of ecosystems and human societies alike. "
            "In response, governments worldwide have pledged to reduce carbon emissions "
            "through international agreements such as the Paris Accord. "
            "However, the pace of institutional change has been frustratingly slow. "
            "This raises an important question: to what extent should individuals be held responsible "
            "for addressing a problem of this scale? "
            "Critics argue that placing the burden on consumers distracts from the systemic changes needed "
            "in industry and policy. "
            "Others contend that collective individual action — reducing meat consumption, "
            "using public transport, and cutting single-use plastics — can send powerful market signals "
            "and accelerate the transition to a sustainable economy."
        ),
        "translation_vi": (
            "Biến đổi khí hậu có thể nói là thách thức cấp bách nhất mà nhân loại phải đối mặt trong thế kỷ hai mươi mốt. "
            "Sự đồng thuận khoa học là rõ ràng: các hoạt động của con người, đặc biệt là đốt nhiên liệu hóa thạch "
            "và phá rừng quy mô lớn, đang thúc đẩy sự tăng nhiệt độ toàn cầu nhanh chóng. "
            "Hậu quả — mực nước biển dâng, thời tiết cực đoan thường xuyên hơn và mất đa dạng sinh học lan rộng — "
            "đe dọa sự ổn định của hệ sinh thái và xã hội loài người. "
            "Để đối phó, các chính phủ trên thế giới đã cam kết giảm lượng khí thải carbon "
            "thông qua các thỏa thuận quốc tế như Hiệp định Paris. "
            "Tuy nhiên, tốc độ thay đổi thể chế đã diễn ra chậm một cách đáng thất vọng. "
            "Điều này đặt ra một câu hỏi quan trọng: đến mức nào các cá nhân phải chịu trách nhiệm "
            "trong việc giải quyết một vấn đề ở quy mô này? "
            "Các nhà phê bình lập luận rằng đặt gánh nặng lên người tiêu dùng sẽ làm phân tán sự chú ý "
            "khỏi những thay đổi mang tính hệ thống cần thiết trong công nghiệp và chính sách. "
            "Những người khác lập luận rằng hành động cá nhân tập thể — giảm tiêu thụ thịt, "
            "sử dụng phương tiện giao thông công cộng và cắt giảm đồ nhựa dùng một lần — có thể gửi tín hiệu thị trường mạnh mẽ "
            "và đẩy nhanh quá trình chuyển đổi sang nền kinh tế bền vững."
        ),
        "topic": "Trends - Eco-friendly Living & Zero Waste",
        "cefr_level": "B2",
        "difficulty_tag": "hard",
        "grammar_notes": "Reporting verbs: argue, contend; Passive voice; Noun clauses; Academic register.",
        "tts_voice": "en-US-GuyNeural",
    },
    {
        "title": "Job Interview: Discussing Strengths and Weaknesses",
        "full_text": (
            "Tell me a little about yourself and why you are applying for this position. "
            "I have five years of experience in project management, "
            "primarily in the technology sector. "
            "I'm drawn to this role because your company is known for its innovative approach, "
            "and I believe my background in cross-functional team leadership aligns well with your needs. "
            "That's interesting. What would you say is your greatest strength? "
            "I'd say my ability to stay calm under pressure and prioritise effectively. "
            "In my previous role, I managed three simultaneous projects with competing deadlines, "
            "and I was able to deliver all of them on time by breaking tasks into clear milestones. "
            "And what about a weakness? "
            "I tend to be a perfectionist, which has occasionally slowed me down. "
            "However, I've been actively working on this by setting stricter time limits for each task "
            "and learning to recognise when 'good enough' is genuinely sufficient."
        ),
        "translation_vi": (
            "Hãy nói một chút về bản thân bạn và lý do bạn nộp đơn cho vị trí này. "
            "Tôi có năm năm kinh nghiệm trong quản lý dự án, "
            "chủ yếu trong lĩnh vực công nghệ. "
            "Tôi bị thu hút bởi vị trí này vì công ty của bạn được biết đến với cách tiếp cận đổi mới, "
            "và tôi tin rằng nền tảng của tôi trong lãnh đạo nhóm đa chức năng phù hợp tốt với nhu cầu của bạn. "
            "Thú vị đấy. Bạn sẽ nói điểm mạnh lớn nhất của mình là gì? "
            "Tôi sẽ nói là khả năng giữ bình tĩnh dưới áp lực và ưu tiên hiệu quả. "
            "Trong vai trò trước đây, tôi quản lý ba dự án đồng thời với thời hạn cạnh tranh, "
            "và tôi đã có thể hoàn thành tất cả đúng hạn bằng cách chia nhiệm vụ thành các mốc rõ ràng. "
            "Còn điểm yếu thì sao? "
            "Tôi có xu hướng là người cầu toàn, đôi khi làm tôi chậm lại. "
            "Tuy nhiên, tôi đã tích cực khắc phục điều này bằng cách đặt giới hạn thời gian chặt chẽ hơn cho mỗi nhiệm vụ "
            "và học cách nhận ra khi nào 'đủ tốt' thực sự là đủ."
        ),
        "topic": "Communication - Job Interviews & Professional Communication",
        "cefr_level": "B2",
        "difficulty_tag": "hard",
        "grammar_notes": "Professional register; I'd say (hedging); Present Perfect for experience; Participle clauses.",
        "tts_voice": "en-US-JennyNeural",
    },
    # Extra A2
    {
        "title": "Describing Your Hometown",
        "full_text": (
            "I come from a small city in the central part of Vietnam. "
            "The city is famous for its beautiful beaches and delicious seafood. "
            "The weather is usually warm and sunny, but it can be very hot in summer. "
            "There are many interesting things to do there. "
            "You can visit the old market in the morning or explore the nearby mountains. "
            "The people there are very friendly and welcoming. "
            "I miss my hometown a lot because I moved to the capital city for university. "
            "Whenever I go back to visit, I always feel relaxed and happy. "
            "I hope that one day I can return and live there permanently."
        ),
        "translation_vi": (
            "Tôi đến từ một thành phố nhỏ ở miền Trung Việt Nam. "
            "Thành phố này nổi tiếng với những bãi biển đẹp và hải sản ngon. "
            "Thời tiết thường ấm áp và nắng, nhưng có thể rất nóng vào mùa hè. "
            "Ở đó có nhiều điều thú vị để làm. "
            "Bạn có thể ghé thăm chợ cũ vào buổi sáng hoặc khám phá những ngọn núi gần đó. "
            "Người dân ở đó rất thân thiện và hiếu khách. "
            "Tôi rất nhớ quê hương vì tôi đã chuyển đến thành phố thủ đô để học đại học. "
            "Mỗi khi tôi về thăm, tôi luôn cảm thấy thư giãn và hạnh phúc. "
            "Tôi hy vọng một ngày nào đó tôi có thể trở về và sống ở đó vĩnh viễn."
        ),
        "topic": "Daily Life - Community & Neighborhood",
        "cefr_level": "A2",
        "difficulty_tag": "easy",
        "grammar_notes": "Can for possibility/ability; Present Simple for descriptions; Past Simple for narrative.",
        "tts_voice": "en-US-AriaNeural",
    },
    # Extra B1
    {
        "title": "How Technology is Changing Education",
        "full_text": (
            "The way we learn has changed dramatically over the past two decades. "
            "The internet has made it possible to access information on almost any subject instantly, "
            "transforming the role of the traditional teacher. "
            "Online learning platforms now allow students to take courses from world-class universities "
            "without leaving their homes. "
            "Interactive tools, virtual classrooms, and AI-powered tutoring software are making education "
            "more personalised and accessible than ever before. "
            "However, not everyone has benefited equally from these developments. "
            "In many developing countries, students lack reliable internet access and devices, "
            "which threatens to widen the educational gap between rich and poor. "
            "Teachers, too, face mounting pressure to keep up with rapidly evolving technology "
            "while managing other professional demands. "
            "Ultimately, technology should complement rather than replace the human connection "
            "that lies at the heart of good teaching."
        ),
        "translation_vi": (
            "Cách chúng ta học đã thay đổi đáng kể trong hai thập kỷ qua. "
            "Internet đã giúp có thể truy cập thông tin về hầu hết bất kỳ chủ đề nào ngay lập tức, "
            "thay đổi vai trò của giáo viên truyền thống. "
            "Các nền tảng học trực tuyến hiện cho phép học sinh theo học các khóa học từ các trường đại học hàng đầu thế giới "
            "mà không cần rời khỏi nhà. "
            "Các công cụ tương tác, lớp học ảo và phần mềm gia sư có AI đang làm cho giáo dục "
            "trở nên cá nhân hóa và dễ tiếp cận hơn bao giờ hết. "
            "Tuy nhiên, không phải ai cũng được hưởng lợi đồng đều từ những phát triển này. "
            "Ở nhiều nước đang phát triển, học sinh thiếu internet đáng tin cậy và thiết bị, "
            "điều này có nguy cơ làm rộng thêm khoảng cách giáo dục giữa người giàu và người nghèo. "
            "Giáo viên cũng phải đối mặt với áp lực ngày càng tăng để theo kịp công nghệ phát triển nhanh "
            "trong khi quản lý các đòi hỏi chuyên môn khác. "
            "Cuối cùng, công nghệ nên bổ sung thay vì thay thế kết nối con người "
            "vốn là trái tim của việc giảng dạy tốt."
        ),
        "topic": "Digital Life - Technology & Innovation",
        "cefr_level": "B1",
        "difficulty_tag": "medium",
        "grammar_notes": "Present Perfect for recent changes; however/ultimately as discourse markers; Gerunds.",
        "tts_voice": "en-US-GuyNeural",
    },
]


def _split_sentences(full_text: str) -> list:
    """Simple sentence splitter into structured list for sentences_json."""
    import re
    raw = re.split(r'(?<=[.!?])\s+', full_text.strip())
    return [
        {"index": i, "text": s.strip(), "translation_vi": "", "audio_url": ""}
        for i, s in enumerate(raw)
        if s.strip()
    ]


class Command(BaseCommand):
    help = "Seed PracticePassage data for Dictation + Shadowing."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete all passages first")

    def handle(self, *args, **options):
        if options["clear"]:
            deleted = PracticePassage.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing passages."))

        created = updated = 0
        for p in PASSAGES:
            sentences = _split_sentences(p["full_text"])
            obj, is_new = PracticePassage.objects.update_or_create(
                title=p["title"],
                defaults={
                    "full_text": p["full_text"],
                    "translation_vi": p.get("translation_vi", ""),
                    "sentences_json": sentences,
                    "topic": p["topic"],
                    "topic_slug": slugify(p["topic"])[:220],
                    "cefr_level": p["cefr_level"],
                    "difficulty_tag": p.get("difficulty_tag", "medium"),
                    "grammar_notes": p.get("grammar_notes", ""),
                    "tts_voice": p.get("tts_voice", "en-US-AriaNeural"),
                    "is_published": True,
                },
            )
            if is_new:
                created += 1
                self.stdout.write(f"  + {p['cefr_level']} | {p['title']}")
            else:
                updated += 1
                self.stdout.write(f"  ~ {p['cefr_level']} | {p['title']}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — created: {created}, updated: {updated}"
        ))
