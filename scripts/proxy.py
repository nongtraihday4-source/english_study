import json, os, time, threading, queue
import requests
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# CHÚ Ý: Cập nhật link Cloudflare mới nhất vào đây (KHÔNG có /v1 ở cuối)
TARGET_URL = "https://richardson-unique-edt-victorian.trycloudflare.com" 
MODEL_ID   = os.environ.get("MODEL_ID", "/kaggle/working/Qwen3.6-27B-Q4_K_M.gguf")
API_KEY    = "sk-1234"
TIMEOUT    = 600 # Tăng thời gian chờ lên tận 10 phút

def json_resp(body, status=200):
    return Response(json.dumps(body, ensure_ascii=False), status=status, mimetype="application/json")

def upstream_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream", # Ép Cloudflare không được giữ gói tin
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", # Vượt rào chống Bot
        "bypass-tunnel-reminder": "true"
    }

def stream_upstream(url, payload):
    print(f"[PROXY] Đang gửi lệnh tới Kaggle. Đợi Qwen đọc prompt (có thể mất 40-60s)...")
    q = queue.Queue()
    
    # Luồng 1: Kết nối và lấy dữ liệu từ Kaggle
    def fetch_data():
        try:
            with requests.post(url, headers=upstream_headers(), json=payload, stream=True, timeout=TIMEOUT) as r:
                if r.status_code != 200:
                    print(f"[PROXY LỖI] Kaggle từ chối (Code {r.status_code}): {r.text[:200]}")
                    q.put(None)
                    return
                for line in r.iter_lines():
                    if line:
                        q.put(line + b"\n\n")
            q.put(None)
        except Exception as e:
            print(f"[PROXY LỖI] Đứt kết nối Kaggle: {e}")
            q.put(None)

    threading.Thread(target=fetch_data, daemon=True).start()

    # Gói tin giả (Heartbeat) đánh lừa OpenClaw
    heartbeat = f'data: {{"id":"chatcmpl-ping","object":"chat.completion.chunk","created":0,"model":"{MODEL_ID}","choices":[{{"index":0,"delta":{{"content":""}}}}]}}\n\n'.encode('utf-8')

    # Luồng 2: Bơm dữ liệu về OpenClaw (hoặc bơm Heartbeat nếu Kaggle nghĩ lâu)
    while True:
        try:
            chunk = q.get(timeout=5)
            if chunk is None:
                yield b'data: [DONE]\n\n'
                break
            yield chunk
        except queue.Empty:
            print("[PROXY] Kaggle đang nghĩ... Bơm Heartbeat giữ kết nối OpenClaw!")
            yield heartbeat

@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS": return Response(status=204)
    data = request.get_json(silent=True) or {}
    
    payload = {
        "model": MODEL_ID,
        "messages": data.get("messages", []),
        "stream": data.get("stream", False),
        "temperature": data.get("temperature", 0.7),
        "max_tokens": min(data.get("max_tokens", 8192), 8192),
    }
    for k in ["top_p", "stop", "tools", "tool_choice"]:
        if k in data: payload[k] = data[k]

    url = f"{TARGET_URL}/v1/chat/completions"
    print(f"[PROXY] Nhận lệnh từ OpenClaw | Tin nhắn: {len(payload['messages'])}")

    if payload["stream"]:
        return Response(stream_upstream(url, payload), mimetype="text/event-stream")

    try:
        r = requests.post(url, headers=upstream_headers(), json=payload, timeout=TIMEOUT)
        return Response(r.content, status=r.status_code, mimetype="application/json")
    except Exception as e:
        return json_resp({"error": str(e)}, 502)

@app.route("/health")
def health(): return jsonify({"ok": True, "target": TARGET_URL})

@app.route("/v1/models")
def models(): return jsonify({"object": "list", "data": [{"id": MODEL_ID, "object": "model", "created": int(time.time()), "owned_by": "kaggle"}]})

if __name__ == "__main__":
    print(f"[PROXY] SIÊU PROXY ĐANG CHẠY | MỤC TIÊU = {TARGET_URL}")
    app.run(host="0.0.0.0", port=8080, threaded=True)