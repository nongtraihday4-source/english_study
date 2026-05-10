import requests
import time

# 1. CẬP NHẬT ĐỊA CHỈ SERVER KAGGLE (LẤY TỪ CLOUDFLARE)
BASE_URL = "https://add-combining-applies-pickup.trycloudflare.com"
API_URL = f"{BASE_URL}/chat/completions"
MODEL_NAME = "gemma-4-26b-a4b-it" # Tên model từ hướng dẫn trên Kaggle

# Quy tắc khắt khe để ép mô hình trả lời đúng định dạng
STRICT_RULE = (
    "\n\nSTRICT RULE: DO NOT show your thinking process. ONLY output the response following the format: "
    "[Result] || Hint: [Explanation in Vietnamese]. "
    "EXAMPLE: He goes to school. || Hint: Chủ ngữ số ít nên thêm 'es'."
)

test_cases = [
    {
        "skill": "1. LISTENING (Nghe hiểu & Chép chính tả)",
        "system": "You are an English listening tutor. Compare the audio transcript with the student's text. Point out mistakes caused by mishearing. Format: [Corrected sentence] || Hint: [Giải thích ngắn gọn bằng tiếng Việt lý do tại sao nghe sai].",
        "user": "Audio transcript: 'He should have gone to the bank.'\nStudent wrote: 'He should of got to the bank.'\nCorrect the student's text."
    },
    {
        "skill": "2. SPEAKING (Phát âm & Minimal Pairs)",
        "system": "You are an English pronunciation coach. Identify the phonetic errors. Format: [Corrected sentence] || Hint: [Đưa ra một mẹo thực tế bằng tiếng Việt để phát âm đúng].",
        "user": "Intended sentence: 'I want to eat a very big dessert.'\nRecognized sentence: 'I want to eat a very big desert.'\nFix my pronunciation."
    },
    {
        "skill": "3. READING (Đọc hiểu & Đoán nghĩa từ vựng)",
        "system": "You are an English reading tutor. Answer the vocabulary question based on the passage. Format: [Direct Answer] || Hint: [Trích dẫn ngắn gọn từ văn bản và giải thích nghĩa bằng tiếng Việt].",
        "user": "Passage: 'Despite the arduous journey and the glaring lack of resources, the team’s morale remained surprisingly buoyant.'\nQuestion: What does 'buoyant' mean in this context?"
    },
    {
        "skill": "4. WRITING (Viết & Nâng cấp văn phong)",
        "system": "You are an English writing tutor. Improve the tone to make it professional. Format: [Improved sentence] || Hint: [Giải thích bằng tiếng Việt tại sao văn phong này chuyên nghiệp hơn].",
        "user": "Make this email to my boss more professional: 'Hey boss, I want a day off tomorrow cause I am very tired. Tell me if it is ok.'"
    },
    {
        "skill": "5. GRAMMAR (Giải thích Ngữ pháp)",
        "system": "You are an English grammar teacher. Explain the rule asked by the student. Format: [Short, simple rule explanation] || Hint: [Giải thích quy tắc bằng tiếng Việt kèm 2 ví dụ].",
        "user": "When should I say 'I lost my keys' versus 'I have lost my keys'? Explain simply."
    },
    {
        "skill": "6. FILL-IN-THE-BLANKS (Trắc nghiệm Điền từ)",
        "system": "You are a helpful English tutor. Answer the multiple-choice question. Format: [Correct Option] || Hint: [Giải thích ngắn gọn bằng tiếng Việt TẠI SAO đáp án đó đúng].",
        "user": "Question: 'By the time we arrive at the station, the train _____.'\nOptions: A) leaves, B) will leave, C) will have left.\nWhich is correct and why?"
    }
]

def test_kaggle_server():
    print("="*70)
    print(f"🚀 KIỂM TRA SỨC KHỎE SERVER KAGGLE (GEMMA 26B)")
    print(f"🔗 URL: {BASE_URL}")
    print("="*70)
    
    for case in test_cases:
        print(f"\n🎯 {case['skill']}")
        
        # ĐỊNH DẠNG PAYLOAD THEO CHUẨN OPENAI MÀ KAGGLE ĐANG DÙNG
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": case['system'] + STRICT_RULE},
                {"role": "user", "content": case['user']}
            ],
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": "Bearer sk-1234",
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                # Trích xuất nội dung từ phản hồi chuẩn OpenAI
                result_text = data['choices'][0]['message']['content']
                latency = round(end_time - start_time, 2)
                
                if "|| Hint:" in result_text:
                    main_part, hint_part = result_text.split("|| Hint:", 1)
                    print(f"✅ TRẢ LỜI: {main_part.strip()}")
                    print(f"💡 GIẢI THÍCH: {hint_part.strip()}")
                else:
                    print(f"✅ PHẢN HỒI: \n{result_text}")
                
                print(f"⏱️ Độ trễ: {latency}s")
            else:
                print(f"❌ Server Lỗi {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Lỗi kết nối server: {e}")

if __name__ == "__main__":
    test_kaggle_server()