import requests
import json
import time

# Địa chỉ API của Local FastAPI Server (Qwen3.5-2B)
LOCAL_API_URL = "http://localhost:8001/fix_grammar"

def call_local_ai(user_prompt):
    """Gửi yêu cầu tới FastAPI server chứa Qwen3.5-2B"""
    payload = {"text": user_prompt}
    
    try:
        start_time = time.time()
        # Gọi API với timeout 60 giây (mô hình 2B cần thời gian để sinh chữ nếu chạy CPU)
        response = requests.post(LOCAL_API_URL, json=payload, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json().get("result", "")
            print(f"⏱️ Thời gian phản hồi: {end_time - start_time:.2f} giây")
            return result
        else:
            return f"Lỗi từ Server: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Lỗi kết nối: Không thể kết nối tới http://localhost:8000. Hãy đảm bảo bạn đã chạy 'python local_qwen_server.py' trước."
    except requests.exceptions.Timeout:
        return "⏳ Lỗi Timeout: Server phản hồi quá lâu (>60s). Có thể do đang chạy trên CPU thuần."

def test_grammar_scenario(sentence="She don't like playing football in the weekends."):
    print(f"\n2. Kịch bản: Kiểm tra Ngữ pháp (Grammar)")
    print(f"Học viên viết: '{sentence}'")
    feedback = call_local_ai(sentence)
    print(f"✅ Gia sư AI phản hồi:\n{feedback}")
    print("-" * 40)

def test_vinglish_scenario():
    print("\n3. Kịch bản: Lỗi Vinglish đặc trưng")
    sentence = "I very like eat apple."
    print(f"Học viên viết: '{sentence}'")
    feedback = call_local_ai(sentence)
    print(f"✅ Gia sư AI phản hồi:\n{feedback}")
    print("-" * 40)

def test_edge_cases():
    print("\n4. Kịch bản: Các trường hợp đặc biệt (Edge Cases)")
    
    print("\n4.1: Gửi câu hoàn toàn đúng")
    test_grammar_scenario("I have been learning English for three years.")
    
    print("\n4.2: Gửi câu tiếng lóng / cụm từ ngắn")
    test_grammar_scenario("gonna sleep now")
    
if __name__ == "__main__":
    print("🚀 BẮT ĐẦU TEST QWEN3.5-2B LOCAL SERVER...")
    print("Vui lòng đảm bảo bạn đã mở 1 tab Terminal khác và chạy: python local_qwen_server.py\n")
    
    test_grammar_scenario()
    test_vinglish_scenario()
    test_edge_cases()