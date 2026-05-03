import requests
import time
import sys

# Ép hệ thống luôn in tiếng Việt chuẩn UTF-8 ra Terminal
sys.stdout.reconfigure(encoding='utf-8')

# =========================================================
# CẤU HÌNH KẾT NỐI CLOUD API (QWEN3 TRÊN HUGGING FACE)
# =========================================================
# ⚠️ BẠN HÃY SỬA LẠI ĐƯỜNG LINK NÀY CHO ĐÚNG VỚI SPACE CỦA BẠN
# Cách lấy link: Vào Space -> Bấm dấu 3 chấm góc phải trên cùng -> "Embed this Space" -> Copy phần Direct URL
API_URL = "https://heajea-qwen-english-tutor-api.hf.space/api/generate"


def test_grammar_api(text):
    """Gửi yêu cầu sửa lỗi lên Cloud API"""
    payload = {
        "text": text,
        "max_tokens": 200 # Tăng token để Qwen có không gian giải thích
    }
    
    try:
        start_time = time.time()
        # ⚠️ Tăng timeout lên 60s vì CPU trên Cloud chạy Qwen 4B sẽ mất từ 5-20s
        response = requests.post(API_URL, json=payload, timeout=600)
        end_time = time.time()
        latency = round(end_time - start_time, 3)

        if response.status_code == 200:
            raw_text = response.json().get("response", "")
            
            # Kiểm tra xem AI có trả về theo đúng cấu trúc || không
            if "||" in raw_text:
                parts = [p.strip() for p in raw_text.split("||")]
                corrected = parts[0]
                explanation = parts[1].replace("Hint:", "").strip() if len(parts) > 1 else ""
            else:
                # Nếu AI trả về một đoạn văn giải thích dài (thường gặp ở Qwen)
                corrected = "Xem phần giải thích bên dưới"
                explanation = raw_text
            
            return corrected, explanation, latency
        else:
            return f"Lỗi Server: {response.status_code} - {response.text}", "", latency
            
    except requests.exceptions.Timeout:
        return "Lỗi: Timeout (Đợi quá 60s mà AI chưa trả lời xong)", "", 0
    except requests.exceptions.ConnectionError:
        return "Lỗi Kết nối (Kiểm tra lại xem URL đã đúng chưa)", "", 0
    except Exception as e:
        return f"Lỗi không xác định: {str(e)}", "", 0

# =========================================================
# KỊCH BẢN KIỂM TRA ÁP LỰC
# =========================================================
def run_benchmark():
    print("🚀 BẮT ĐẦU KIỂM TRA MÔ HÌNH QWEN3-4B (HUGGING FACE CLOUD API)...")
    print("=" * 60)

    test_cases = [
        "Yesterday, I go to the store.",
        "She is totally obsessed on listening to K-pop.",
        "I need to do a decision right now."
    ]

    for i, sentence in enumerate(test_cases, 1):
        print(f"\n[{i}] ❌ Câu gốc: '{sentence}'")
        print("⏳ Đang gửi lên Cloud AI (Vui lòng kiên nhẫn chờ 5-20s)...")
        
        corrected, explanation, latency = test_grammar_api(sentence)
        
        print(f"✅ Câu đúng: {corrected}")
        if explanation:
            print(f"💡 Gia sư nói: {explanation}")
        
        print(f"⏱️ Độ trễ: {latency} giây")
        print("-" * 60)

if __name__ == "__main__":
    run_benchmark()