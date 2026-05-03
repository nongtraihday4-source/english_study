import requests
import time

# 1. ĐỊNH NGHĨA ĐỊA CHỈ SERVER CỤC BỘ CỦA BẠN
LOCAL_API_URL = "http://localhost:8001/fix_grammar"

# Quy tắc khắt khe để ép mô hình 4B không trả lời lan man
STRICT_RULE = (
    "\n\nSTRICT RULE: DO NOT show your thinking process. ONLY output the response following the format: "
    "[Result] || Hint: [Explanation in Vietnamese]. "
    "EXAMPLE: He goes to school. || Hint: Chủ ngữ số ít nên thêm 'es'."
)

test_cases = [
    {
        "skill": "1. LISTENING (Nghe hiểu & Chép chính tả)",
        "system": "You are an English listening tutor. Compare the audio transcript with the student's text. Point out mistakes caused by mishearing (like connected speech or homophones). Format: [Corrected sentence] || Hint: [Giải thích ngắn gọn bằng tiếng Việt lý do tại sao nghe sai].",
        "user": "Audio transcript: 'He should have gone to the bank.'\nStudent wrote: 'He should of got to the bank.'\nCorrect the student's text."
    },
    {
        "skill": "2. SPEAKING (Phát âm & Minimal Pairs)",
        "system": "You are an English pronunciation coach. Identify the phonetic errors between the intended sentence and what the Speech-to-Text recognized. Format: [Corrected sentence] || Hint: [Đưa ra một mẹo thực tế bằng tiếng Việt để phát âm đúng].",
        "user": "Intended sentence: 'I want to eat a very big dessert.'\nRecognized sentence: 'I want to eat a very big desert.'\nFix my pronunciation."
    },
    {
        "skill": "3. READING (Đọc hiểu & Đoán nghĩa từ vựng)",
        "system": "You are an English reading tutor. Answer the vocabulary question based on the passage. Format: [Direct Answer] || Hint: [Trích dẫn ngắn gọn từ văn bản và giải thích nghĩa bằng tiếng Việt].",
        "user": "Passage: 'Despite the arduous journey and the glaring lack of resources, the team’s morale remained surprisingly buoyant.'\nQuestion: What does 'buoyant' mean in this context?"
    },
    {
        "skill": "4. WRITING (Viết & Nâng cấp văn phong)",
        "system": "You are an English writing tutor. Improve the tone of the student's text to make it professional. Format: [Improved sentence] || Hint: [Giải thích bằng tiếng Việt tại sao văn phong này chuyên nghiệp hơn].",
        "user": "Make this email to my boss more professional: 'Hey boss, I want a day off tomorrow cause I am very tired. Tell me if it is ok.'"
    },
    {
        "skill": "5. GRAMMAR (Giải thích Ngữ pháp)",
        "system": "You are an English grammar teacher. Explain the grammar rule asked by the student simply. Format: [Short, simple rule explanation] || Hint: [Giải thích quy tắc bằng tiếng Việt kèm 2 ví dụ].",
        "user": "I always get confused. When should I say 'I lost my keys' versus 'I have lost my keys'? Explain simply."
    },
    {
        "skill": "6. FILL-IN-THE-BLANKS (Trắc nghiệm Điền từ)",
        "system": "You are a helpful English tutor. Answer the multiple-choice question. Format: [Correct Option] || Hint: [Giải thích ngắn gọn bằng tiếng Việt TẠI SAO đáp án đó đúng].",
        "user": "Question: 'By the time we arrive at the station, the train _____.'\nOptions: A) leaves, B) will leave, C) will have left.\nWhich is correct and why?"
    }
]

def test_via_api():
    print("="*70)
    print(f"🚀 CHẠY 6 KỊCH BẢN - LOCAL SERVER (PORT 8001)")
    print(f"📦 MODEL: qwen3-4b.Q4_K_M.gguf")
    print("="*70)
    
    for case in test_cases:
        print(f"\n🎯 {case['skill']}")
        
        # 2. PAYLOAD PHẢI KHỚP VỚI TutorRequest TRONG FASTAPI
        payload = {
            "system_message": case['system'] + STRICT_RULE,
            "user_message": case['user']
        }
        
        try:
            start_time = time.time()
            # Gửi request đến LOCAL_API_URL
            response = requests.post(LOCAL_API_URL, json=payload, timeout=120)
            end_time = time.time()
            
            if response.status_code == 200:
                # 3. TRÍCH XUẤT TỪ TRƯỜNG 'result' NHƯ FASTAPI TRẢ VỀ
                data = response.json()
                result_text = data['result']
                latency = data.get('time', round(end_time - start_time, 2))
                
                # Bóc tách giao diện
                if "|| Hint:" in result_text:
                    main_part, hint_part = result_text.split("|| Hint:", 1)
                    print(f"✅ TRẢ LỜI: {main_part.strip()}")
                    print(f"💡 GIẢI THÍCH: {hint_part.strip()}")
                else:
                    print(f"⚠️ LỖI FORMAT (Model trả lời không đúng chuẩn): \n{result_text}")
                
                print(f"⏱️ Độ trễ: {latency}s")
            else:
                print(f"❌ Server Lỗi {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ LỖI KẾT NỐI: Server FastAPI chưa chạy tại {LOCAL_API_URL}")
        except Exception as e:
            print(f"❌ Lỗi phát sinh: {e}")

if __name__ == "__main__":
    test_via_api()