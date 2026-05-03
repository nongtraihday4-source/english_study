import json
import os
import time
import requests
from tqdm import tqdm

# ============================================================
# CẤU HÌNH API - Beeknoee Platform
# Docs: https://platform.beeknoee.com/docs/api-usage
# ============================================================
API_KEY = "sk-bee-7d7f8d06b1394f6a8d65281d1ac3b34b"

# ✅ Endpoint ĐÚNG của Beeknoee Platform
API_ENDPOINT = "https://platform.beeknoee.com/api/v1/chat/completions"
MODEL_NAME = "gemini-2.5-flash"
BATCH_SIZE = 30


def clean_json_response(raw_text):
    """Hàm 'cạo rác' Markdown để lấy chuẩn JSON."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def distill_batch():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    input_file = os.path.join(root_dir, "final_raw_dataset_25k.jsonl")
    output_file = os.path.join(root_dir, "distilled_dataset.jsonl")

    with open(input_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    processed_count = 0
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            processed_count = len(f.readlines())

    remaining_lines = all_lines[processed_count:]
    if not remaining_lines:
        print("✅ Đã chưng cất xong toàn bộ dataset!")
        return

    print(f"🚀 Tổng câu: {len(all_lines)}. Đã làm: {processed_count}. Còn lại: {len(remaining_lines)}.")

    # ✅ Header dùng Bearer token chuẩn OpenAI-compatible
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    with open(output_file, 'a', encoding='utf-8') as out_f:
        for i in tqdm(range(0, len(remaining_lines), BATCH_SIZE), desc="Đang chưng cất"):
            batch_lines = remaining_lines[i:i + BATCH_SIZE]
            batch_data = [json.loads(line) for line in batch_lines]

            system_prompt = """You are an expert English grammar tutor.
CRITICAL RULE: DO NOT use double quotes (") inside your explanations. If you need to quote a word, use single quotes (')."""

            user_content = "Provide a concise explanation (max 2 sentences) for WHY each correction was made in the list below.\n\n"
            for idx, item in enumerate(batch_data):
                user_content += f"ID: {idx} | Wrong: {item['wrong']} | Correct: {item['correct']}\n"

            user_content += """\nRespond STRICTLY in valid JSON format. Your response must be a single JSON object with a key "hints" containing a list of objects like this:
{"hints": [{"id": 0, "hint": "explanation here"}, {"id": 1, "hint": "explanation here"}]}"""

            # ✅ Payload chuẩn OpenAI-compatible
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }

            success = False
            retries = 3  # Tăng retry từ 2 lên 3

            while not success and retries > 0:
                try:
                    response = requests.post(
                        API_ENDPOINT,
                        headers=headers,
                        json=payload,
                        timeout=120  # Tăng timeout cho model lớn
                    )

                    if response.status_code != 200:
                        raise Exception(f"HTTP {response.status_code}: {response.text}")

                    response_data = response.json()
                    raw_content = response_data['choices'][0]['message']['content']

                    clean_content = clean_json_response(raw_content)
                    parsed_json = json.loads(clean_content)
                    hints_array = parsed_json.get("hints", [])

                    if len(hints_array) == 0:
                        raise ValueError("AI trả về JSON rỗng!")

                    for item in hints_array:
                        idx = item['id']
                        hint = str(item['hint']).replace('"', "'")
                        original_data = batch_data[idx]

                        assistant_response = f"{original_data['correct']} || Hint: {hint}"

                        distilled_data = {
                            "system": "You are a helpful English tutor. Correct the grammar and provide a hint.",
                            "user": f"Correct this sentence: {original_data['wrong']}",
                            "assistant": assistant_response
                        }

                        out_f.write(json.dumps(distilled_data, ensure_ascii=False) + "\n")

                    out_f.flush()
                    success = True
                    print(f"✅ Đã lưu thành công {len(hints_array)} câu vào file!")

                    time.sleep(2)

                except Exception as e:
                    raw_content_preview = locals().get('raw_content', '')
                    print(f"\n⚠️ Lỗi ở mẻ {i}: {e}. Đang đợi 5s để thử lại...")
                    if raw_content_preview:
                        print(f"Nội dung: {raw_content_preview[:200]}...")
                    time.sleep(5)
                    retries -= 1

            if not success:
                print(f"❌ Bỏ qua mẻ {i} sau 3 lần thử thất bại. Tiếp tục mẻ tiếp theo...")

    print(f"\n🎉 HOÀN THÀNH CHƯNG CẤT TOÀN BỘ DATASET!")


if __name__ == "__main__":
    distill_batch()