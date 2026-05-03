import requests
import time

# TRỎ VÀO CỔNG 8002 CỦA LLAMA SERVER
LOCAL_API_URL = "http://localhost:8001/fix_grammar"

def call_local_ai(user_prompt):
    payload = {"text": user_prompt}
    try:
        start_time = time.time()
        response = requests.post(LOCAL_API_URL, json=payload, timeout=120)
        end_time = time.time()
        if response.status_code == 200:
            result = response.json().get("result", "")
            print(f"⏱️ Thời gian phản hồi: {end_time - start_time:.2f} giây")
            return result
        return f"Lỗi từ Server: {response.text}"
    except Exception as e:
        return f"Lỗi kết nối: {str(e)}"

def test_dictation_with_tips():
    print("\n" + "="*50)
    print("🎧 KỊCH BẢN 1: NGHE CHÉP CHÍNH TẢ (KÈM MẸO GHI NHỚ)")
    prompt = """Audio: 'I would have gone if it hadn't rained.'
Student wrote: 'I would of gone if it haven't rain.'

Compare the audio and the student's text. Point out the spelling and grammar mistakes caused by mishearing.
Format your response EXACTLY like this:
[Correct sentence] || Hint: [Simple explanation of why they misheard it (e.g., connected speech)]. Tip to remember: [Give a short, practical mnemonic/trick to remember this rule]."""
    
    print(f"📝 Dữ liệu đầu vào:\n{prompt}\n")
    print("🤖 Llama 3.2 đang phân tích...")
    print(call_local_ai(prompt))

def test_shadowing_with_tips():
    print("\n" + "="*50)
    print("🗣️ KỊCH BẢN 2: CHẤM PHÁT ÂM (KÈM MẸO GHI NHỚ)")
    prompt = """Original text: 'He thinks the sheep is cheap.'
Student pronounced: 'He sink the ship is chip.'

Identify the pronunciation mistakes (minimal pairs). 
Format your response EXACTLY like this:
[Correct sentence] || Hint: [Simple explanation of the mispronounced sounds]. Tip to remember: [Give a practical, easy-to-visualize trick to help the student differentiate these sounds in everyday speaking]."""
    
    print(f"📝 Dữ liệu đầu vào:\n{prompt}\n")
    print("🤖 Llama 3.2 đang phân tích...")
    print(call_local_ai(prompt))

if __name__ == "__main__":
    print("🚀 BẮT ĐẦU CHẠY BÀI TEST TÌM MẸO HỌC CHO LLAMA 3.2 3B...")
    test_dictation_with_tips()
    test_shadowing_with_tips()