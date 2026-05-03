import requests
import time

# SỬ DỤNG ENDPOINT /api/chat THAY VÌ /api/generate ĐỂ ÉP CHAT TEMPLATE
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "english-tutor"

def call_local_ai(user_input):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            # ĐÃ XÓA ROLE: SYSTEM Ở ĐÂY VÌ OLLAMA ĐÃ LẤY TỪ MODELFILE
            {
                "role": "user",
                "content": f"Correct this sentence: {user_input}"
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_thread": 4  # ĐÂY LÀ CHÌA KHÓA! Ép Ollama chỉ dùng 4 luồng giống FastAPI
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json().get("message", {}).get("content", "")
            print(f"⏱️ Thời gian phản hồi: {end_time - start_time:.2f} giây")
            return result.strip()
        else:
            return f"Lỗi từ Ollama Server: {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

def test_grammar_tutor():
    print("\n" + "="*50)
    print("🎓 KỊCH BẢN TEST LỖI NGỮ PHÁP (CHUẨN DỮ LIỆU HUẤN LUYỆN)")
    
    test_cases = [
        "She don't like playing football in the weekends.",
        "I would of gone if it haven't rain.", # Câu lỗi Listening biến thành lỗi Grammar
        "He sink the ship is chip."           # Câu lỗi Speaking Minimal Pairs
    ]
    
    for text in test_cases:
        print(f"\n📝 Học viên nhập: '{text}'")
        print("🤖 AI Đang chấm...")
        print(f"✅ Phản hồi: {call_local_ai(text)}")

if __name__ == "__main__":
    print("🚀 ĐANG KHỞI ĐỘNG BÀI TEST OLLAMA (API CHAT)...")
    test_grammar_tutor()