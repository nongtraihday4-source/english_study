import json, os, re, time, uuid
import requests
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

TARGET_URL = "https://eyes-strategy-cash-surfing.trycloudflare.com"
MODEL_ID   = os.environ.get("MODEL_ID",   "/kaggle/working/Qwen3.6-27B-Q4_K_M.gguf")
API_KEY    = os.environ.get("UPSTREAM_API_KEY", "sk-1234")
TIMEOUT    = int(os.environ.get("REQUEST_TIMEOUT",    "180"))
MAX_TOKENS = int(os.environ.get("DEFAULT_MAX_TOKENS", "4096"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def json_resp(body, status=200):
    return Response(
        json.dumps(body, ensure_ascii=False),
        status=status,
        mimetype="application/json",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

def upstream_headers():
    return {
        "Authorization":          f"Bearer {API_KEY}",
        "Content-Type":           "application/json",
        "bypass-tunnel-reminder": "true",
        "User-Agent":             "qwen-agent-proxy/6.0",
    }

def normalize_model(m):
    if not m: return MODEL_ID
    if m.lower() in ("kaggle-gemma", "kaggle_gemma"): return MODEL_ID
    return m

def build_payload(data: dict) -> dict:
    p = {
        "model":       normalize_model(data.get("model")),
        "messages":    data.get("messages", []),
        "stream":      data.get("stream", False),
        "temperature": data.get("temperature", 0.7),
        "max_tokens":  min(data.get("max_tokens", MAX_TOKENS), 8192),
    }
    
    if "tools" in data: p["tools"] = data["tools"]
    if "tool_choice" in data: p["tool_choice"] = data["tool_choice"]

    for k in ["top_p", "top_k", "presence_penalty", "frequency_penalty", "stop"]:
        if k in data: p[k] = data[k]
    return p

# ---------------------------------------------------------------------------
# Parser Logic (HỖ TRỢ KÉP: JSON & BEGIN_ARG)
# ---------------------------------------------------------------------------

def extract_tool_calls_from_text(text: str):
    tool_calls = []
    clean_text = text

    # 1. Thử parse định dạng JSON (Qwen Native)
    pattern_json = r"(?:<\|tool_call\|>|<tool_call>)\s*(\{.*?\})\s*(?:</tool_call>|<\|im_end\|>)?"
    matches_json = list(re.finditer(pattern_json, clean_text, re.DOTALL))
    for m in matches_json:
        try:
            call_data = json.loads(m.group(1).strip())
            func_name = call_data.get("name")
            args = call_data.get("arguments", {})
            args_str = json.dumps(args, ensure_ascii=False) if isinstance(args, dict) else str(args)
            if func_name:
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {"name": func_name, "arguments": args_str}
                })
            clean_text = clean_text.replace(m.group(0), "")
        except Exception:
            pass

    # 2. Thử parse định dạng BEGIN_ARG...END_ARG (Continue.dev Fallback)
    pattern_legacy = r"(?:<\|tool_call\|>|<tool_call>)?\s*call:(\w+)\s+BEGIN_ARG:\s*(.*?)\s*END_ARG\s*(?:</tool_call>)?"
    matches_legacy = list(re.finditer(pattern_legacy, clean_text, re.DOTALL))
    for m in matches_legacy:
        func_name = m.group(1).strip()
        arg_str = m.group(2).strip()
        args_json = {}
        try:
            if arg_str.startswith("{"): args_json = json.loads(arg_str)
            else:
                arg_match = re.search(r'(\w+)[:\s]+"(.*?)"', arg_str, re.DOTALL)
                if arg_match: args_json[arg_match.group(1)] = arg_match.group(2)
                else: args_json["command"] = arg_str.strip('"\'')
        except Exception:
            args_json["command"] = arg_str.strip('"\'')

        tool_calls.append({
            "id": f"call_{uuid.uuid4().hex[:8]}",
            "type": "function",
            "function": {"name": func_name, "arguments": json.dumps(args_json, ensure_ascii=False)}
        })
        clean_text = clean_text.replace(m.group(0), "")

    # Dọn dẹp tags
    clean_text = clean_text.replace("<channel>", "").replace("</channel>", "").strip()
    clean_text = re.sub(r"<\|tool_call\|>", "", clean_text)
    clean_text = re.sub(r"<tool_call>", "", clean_text)
    clean_text = re.sub(r"</tool_call>", "", clean_text)
    
    return clean_text.strip(), tool_calls

# ---------------------------------------------------------------------------
# Streaming Logic (Fix lỗi treo luồng)
# ---------------------------------------------------------------------------

def stream_upstream(url: str, payload: dict):
    buffer_text = ""
    is_in_tool_block = False
    
    with requests.post(url, headers=upstream_headers(), json=payload, stream=True, timeout=TIMEOUT) as r:
        for raw_line in r.iter_lines():
            if not raw_line:
                yield b"\n"
                continue

            line = raw_line.decode("utf-8", errors="replace")
            if not line.startswith("data:"):
                yield (line + "\n").encode()
                continue

            data_str = line[5:].strip()
            if data_str == "[DONE]":
                if is_in_tool_block and buffer_text:
                    _, parsed_tools = extract_tool_calls_from_text(buffer_text)
                    if parsed_tools:
                        final_chunk = {
                            "choices": [{
                                "delta": {"tool_calls": [{"index": 0, "id": parsed_tools[0]["id"], "type": "function", "function": {"name": parsed_tools[0]["function"]["name"], "arguments": parsed_tools[0]["function"]["arguments"]}}]},
                                "finish_reason": "tool_calls"
                            }]
                        }
                        yield ("data: " + json.dumps(final_chunk, ensure_ascii=False) + "\n\n").encode()
                
                yield b"data: [DONE]\n\n"
                break

            try:
                chunk = json.loads(data_str)
            except Exception:
                yield (line + "\n").encode()
                continue

            for choice in chunk.get("choices", []):
                delta = choice.get("delta", {})
                content = delta.get("content", "")
                
                if not content: continue

                # Bắt đầu gọi tool
                if "call:" in content or "<|tool_call|>" in content or "<tool_call>" in content or is_in_tool_block:
                    is_in_tool_block = True
                    buffer_text += content
                    
                    # Dấu hiệu kết thúc đoạn tool
                    if "END_ARG" in buffer_text or "</tool_call>" in buffer_text or "<|im_end|>" in buffer_text or buffer_text.strip().endswith("}"):
                        clean_text, parsed_tools = extract_tool_calls_from_text(buffer_text)
                        
                        if parsed_tools:
                            t = parsed_tools[0]
                            tool_delta = {
                                "tool_calls": [{
                                    "index": 0,
                                    "id": t["id"],
                                    "type": "function",
                                    "function": {"name": t["function"]["name"], "arguments": t["function"]["arguments"]}
                                }]
                            }
                            choice["delta"] = tool_delta
                            choice["finish_reason"] = "tool_calls"
                            yield ("data: " + json.dumps(chunk, ensure_ascii=False) + "\n\n").encode()
                        else:
                            # FIX QUAN TRỌNG: Nếu parse thất bại, phải trả text về cho VSCode để khỏi bị treo!
                            choice["delta"] = {"content": buffer_text}
                            yield ("data: " + json.dumps(chunk, ensure_ascii=False) + "\n\n").encode()
                            
                        buffer_text = ""
                        is_in_tool_block = False
                        continue
                    else:
                        continue 
                
                yield ("data: " + json.dumps(chunk, ensure_ascii=False) + "\n\n").encode()

# ---------------------------------------------------------------------------
# CORS & Routes
# ---------------------------------------------------------------------------

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"]  = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    r.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return r

@app.route("/health")
def health():
    return jsonify({"ok": True, "target": TARGET_URL, "model": MODEL_ID})

@app.route("/v1/models")
def models():
    now = int(time.time())
    return json_resp({"object": "list", "data": [{"id": MODEL_ID, "object": "model", "created": now, "owned_by": "kaggle"}]})

@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS": return Response(status=204)
    data = request.get_json(silent=True) or {}
    p = build_payload(data)

    if not p["messages"]: return json_resp({"error": {"message": "messages required", "type": "invalid_request_error"}}, 400)

    url = f"{TARGET_URL}/v1/chat/completions"
    want_stream = p.get("stream", False)

    print(f"[PROXY] POST | msgs={len(p['messages'])} | stream={want_stream} | tools_count={len(p.get('tools', []))}")

    if want_stream:
        return Response(stream_upstream(url, p), status=200, mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    p["stream"] = False
    try:
        r = requests.post(url, headers=upstream_headers(), json=p, timeout=TIMEOUT)
    except Exception as e:
        return json_resp({"error": {"message": str(e)}}, 502)

    try:
        body = r.json()
    except Exception:
        return json_resp({"error": {"message": "Invalid JSON"}}, 502)

    for choice in body.get("choices", []):
        msg = choice.get("message", {})
        raw_content = msg.get("content", "")
        if raw_content and ("call:" in raw_content or "<|tool_call|>" in raw_content or "<tool_call>" in raw_content):
            clean_content, parsed_tools = extract_tool_calls_from_text(raw_content)
            msg["content"] = clean_content if clean_content else None
            if parsed_tools:
                msg["tool_calls"] = parsed_tools
                choice["finish_reason"] = "tool_calls"
                
    return json_resp(body, r.status_code)

@app.route("/v1/<path:path>", methods=["GET", "POST", "OPTIONS"])
def passthrough(path):
    if request.method == "OPTIONS": return Response(status=204)
    url = f"{TARGET_URL}/v1/{path}"
    try:
        if request.method == "GET": r = requests.get(url, headers=upstream_headers(), timeout=TIMEOUT)
        else: r = requests.post(url, headers=upstream_headers(), json=request.get_json(silent=True) or {}, timeout=TIMEOUT)
    except Exception as e:
        return json_resp({"error": {"message": str(e)}}, 502)
    return Response(r.content, status=r.status_code, mimetype=r.headers.get("Content-Type", "application/json"))

if __name__ == "__main__":
    print(f"[PROXY] Listening on http://0.0.0.0:8080 | TARGET = {TARGET_URL}")
    app.run(host="0.0.0.0", port=8080, threaded=True, debug=False)