import requests
import time

# Chú ý: Đảm bảo cổng 8000 khớp với local_gguf_server.py của bạn
LOCAL_API_URL = "http://localhost:8001/fix_grammar"

def call_local_ai(user_prompt):
    payload = {"text": user_prompt}
    try:
        start_time = time.time()
        # Tăng timeout lên 120s vì xử lý đoạn văn B1 dài sẽ tốn nhiều tính toán hơn
        response = requests.post(LOCAL_API_URL, json=payload, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json().get("result", "")
            print(f"⏱️ Thời gian phản hồi: {end_time - start_time:.2f} giây")
            return result
        else:
            return f"Lỗi từ Server: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

def test_b1_essay():
    print("\n" + "="*50)
    print("🔥 KỊCH BẢN 1: BÀI LUẬN B1 (SỰ PHỐI THÌ PHỨC TẠP)")
    # Học viên dùng lộn xộn Quá khứ đơn, Hiện tại hoàn thành, Quá khứ tiếp diễn
    essay = (
        "When I was a child, I have lived in a beautiful house. "
        "While my parents working in the garden, I usually play with my dog. "
        "We had lived there for 5 years before we are moving to the city."
    )
    print(f"📝 Học viên viết:\n'{essay}'\n")
    print("🤖 Gia sư AI phản hồi:")
    print(call_local_ai(essay))

def test_b1_reading_comprehension():
    print("\n" + "="*50)
    print("📖 KỊCH BẢN 2: TRẢ LỜI CÂU HỎI ĐỌC HIỂU (READING)")
    # Học viên trả lời sai ngữ pháp dựa trên một câu hỏi đọc hiểu
    reading_scenario = (
        "Reading passage: 'By the time the storm hit, John had already secured the windows.'\n"
        "Question: What did John do before the storm?\n"
        "My answer: John secure the windows before the storm hit."
    )
    print(f"📝 Học viên nhập:\n'{reading_scenario}'\n")
    print("🤖 Gia sư AI phản hồi:")
    print(call_local_ai(reading_scenario))

def test_b1_multiple_choice():
    print("\n" + "="*50)
    print("✅ KỊCH BẢN 3: GIẢI THÍCH TRẮC NGHIỆM (MULTIPLE CHOICE)")
    # Bắt AI đóng vai trò giải thích tại sao một đáp án lại sai
    mcq_scenario = (
        "Question: 'I _______ TV when the phone rang.'\n"
        "A. watched  B. was watching  C. have watched\n"
        "Tôi chọn đáp án A. Gia sư giải thích giúp tôi tại sao sai?"
    )
    print(f"📝 Học viên hỏi:\n'{mcq_scenario}'\n")
    print("🤖 Gia sư AI phản hồi:")
    print(call_local_ai(mcq_scenario))

if __name__ == "__main__":
    print("🚀 BẮT ĐẦU CHẠY BÀI TEST B1 NÂNG CAO CHO QWEN-4B GGUF...")
    test_b1_essay()
    test_b1_reading_comprehension()
    test_b1_multiple_choice()
    print("\n" + "="*50)