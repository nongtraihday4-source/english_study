import requests
import time
import sys

# 1. CẬP NHẬT ĐỊA CHỈ SERVER KAGGLE (LẤY TỪ CLOUDFLARE)
BASE_URL = "https://add-combining-applies-pickup.trycloudflare.com"
API_URL = f"{BASE_URL}/chat/completions"
HEALTH_URL = f"{BASE_URL}/health"
MODEL_NAME = "gemma-4-26b-a4b-it"

# Quy tắc khắt khe để ép mô hình trả lời đúng định dạng
STRICT_RULE = (
    "\n\nSTRICT RULE: DO NOT show your thinking process. ONLY output the response following the format: "
    "[Result] || Hint: [Explanation in Vietnamese]. "
    "EXAMPLE: He goes to school. || Hint: Chủ ngữ số ít nên thêm 'es'."
)

def check_server_health():
    """Bước 1: Kiểm tra xem tunnel và Flask app có đang sống không."""
    print(f"\n🔍 [STEP 1] Checking Server Health...")
    try:
        start = time.time()
        response = requests.get(HEALTH_URL, timeout=10)
        latency = round((time.time() - start) * 1000, 2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is ALIVE!")
            print(f"   - Latency: {latency}ms")
            print(f"   - Target URL: {data.get('target')}")
            print(f"   - Model ID on server: {data.get('model')}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_model_capability():
    """Bước 2: Kiểm tra xem model có phản hồi đúng format và logic không."""
    print(f"\n🔍 [STEP 2] Testing Model Capability (Grammar Skill)...")
    
    system_prompt = "You are an English grammar teacher. Explain the rule asked by the student. Format: [Short, simple rule explanation] || Hint: [Giải thích quy tắc bằng tiếng Việt kèm 2 ví dụ]."
    user_prompt = "When should I say 'I lost my keys' versus 'I have lost my keys'? Explain simply."
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt + STRICT_RULE},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.2 # Giảm temperature để tăng tính ổn định cho format
    }
    
    try:
        start = time.time()
        response = requests.post(API_URL, json=payload, timeout=60)
        latency = round(time.time() - start, 2)
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            print(f"✅ Request Successful!")
            print(f"   - Latency: {latency}s")
            print("-" * 30)
            print(f"RAW CONTENT:\n{content}")
            print("-" * 30)

            # Kiểm tra format Strict Rule
            if "|| Hint:" in content:
                print("📊 FORMAT CHECK: PASSED (Found '|| Hint:')")
            else:
                print("⚠️ FORMAT CHECK: FAILED (Missing '|| Hint:')")
            
            # Kiểm tra xem có bị dính thinking token không (dựa trên proxy logic)
            if "<thought>" in content or "<start_of_thought" in content:
                print("⚠️ CLEANLINESS CHECK: FAILED (Thinking tokens detected in content!)")
            else:
                print("✨ CLEANLINESS CHECK: PASSED (Content is clean)")

        else:
            print(f"❌ Model Error ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("="*70)
    print(f"🚀 KAGGLE CLOUDFLARE TUNNEL DIAGNOSTIC TOOL")
    print("="*70)
    
    # Chạy chuỗi kiểm tra
    if check_server_health():
        test_model_capability()
    else:
        print("\n🛑 Diagnostic aborted due to server health failure.")
    
    print("\n" + "="*70)
