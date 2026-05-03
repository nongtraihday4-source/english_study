import requests
import json
import time

# =========================================================
# CẤU HÌNH API
# LƯU Ý: Thay đổi URL này mỗi khi Colab sinh ra một link Ngrok mới
# =========================================================
COLAB_NGROK_URL = "https://food-limit-tamer.ngrok-free.dev/tutor" 

# ---------------------------------------------------------
# HÀM LÕI GỌI API COLAB
# ---------------------------------------------------------
def get_ai_tutor_feedback(user_input):
    if not COLAB_NGROK_URL or "xxxx" in COLAB_NGROK_URL:
        return "❌ Lỗi: Bạn chưa cập nhật link Ngrok từ Colab vào script."

    # Payload chuẩn khớp với class ChatRequest trên FastAPI của Colab
    payload = {
        "instruction": "Hãy kiểm tra ngữ pháp và giải thích chi tiết lỗi sai nếu có:",
        "text": user_input
    }

    try:
        start_time = time.time()
        
        # Gửi request lên Colab thông qua Ngrok
        response = requests.post(
            url=COLAB_NGROK_URL, 
            json=payload, 
            timeout=60 # Cho phép chờ lâu hơn một chút nếu ngrok/colab đang load
        )

        end_time = time.time()
        latency = round(end_time - start_time, 2)

        if response.status_code == 200:
            result = response.json()
            feedback = result.get('reply', 'Không có nội dung trả về.')
            return feedback, latency
        else:
            return f"❌ Lỗi API: {response.status_code} - {response.text}", latency

    except requests.exceptions.RequestException as e:
        return f"❌ Có lỗi kết nối mạng hoặc timeout: {e}", 0

# ---------------------------------------------------------
# CÁC KỊCH BẢN TEST (DÀNH CHO QWEN3-4B FINE-TUNED)
# ---------------------------------------------------------
def test_grammar_scenario(scenario_name, sentence):
    print(f"\n[{scenario_name}]")
    print(f"Học viên gửi câu: '{sentence}'")
    print("⏳ Đang gửi lên mô hình Colab...")
    
    feedback, latency = get_ai_tutor_feedback(sentence)
    
    print(f"⏱️ Thời gian phản hồi: {latency} giây")
    print(f"✅ Giáo viên AI (Qwen3) phản hồi:\n{feedback}")
    print("-" * 50)

def run_all_tests():
    print("🚀 Bắt đầu chạy kịch bản test API Gia sư Tiếng Anh (Local -> Colab)...")
    print(f"🔗 Đang kết nối tới: {COLAB_NGROK_URL}")
    print("=" * 60)
    
    # Kịch bản 1: Lỗi chia động từ cơ bản
    test_grammar_scenario(
        scenario_name="Test 1 - Lỗi chia động từ (Hiện tại đơn)", 
        sentence="She don't likes go to school."
    )
    
    # Kịch bản 2: Lỗi thì quá khứ (Giống hệt mẫu bạn đã test trên Colab)
    test_grammar_scenario(
        scenario_name="Test 2 - Lỗi thì quá khứ / Phân từ", 
        sentence="I have went to the market."
    )

    # Kịch bản 3: Câu đúng hoàn toàn
    test_grammar_scenario(
        scenario_name="Test 3 - Câu đúng ngữ pháp", 
        sentence="She doesn't like playing football on the weekends."
    )
    
    # Kịch bản 4: Ngoại lệ (Gửi câu trống hoặc vô nghĩa)
    test_grammar_scenario(
        scenario_name="Test 4 - Ngoại lệ (Câu trống)", 
        sentence="..."
    )

if __name__ == "__main__":
    run_all_tests()