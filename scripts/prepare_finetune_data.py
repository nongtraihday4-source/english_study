import json
import os
import random
from pathlib import Path

# Cấu hình đường dẫn
DATA_DIR = Path("/home/n2t/Documents/english_study/prompt/generated_prompts/individual")
OUTPUT_DIR = Path("/home/n2t/Documents/english_study/data/finetune")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def prepare_data():
    all_data = []
    
    # 1. Đọc toàn bộ file JSON
    json_files = list(DATA_DIR.glob("*.json"))
    print(f"Tìm thấy {len(json_files)} file dữ liệu.")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    # Chuyển đổi sang định dạng ChatML cho Qwen
                    formatted_item = {
                        "messages": [
                            {
                                "role": "system", 
                                "content": "Bạn là giáo viên Tiếng Anh chuyên sửa lỗi cho người Việt. Hãy sửa lỗi ngữ pháp và giải thích bằng Tiếng Việt."
                            },
                            {
                                "role": "user", 
                                "content": item["input"]
                            },
                            {
                                "role": "assistant", 
                                "content": item["output"]
                            }
                        ]
                    }
                    all_data.append(formatted_item)
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path.name}: {e}")

    # 2. Loại bỏ trùng lặp (nếu có)
    # Dùng string representation để check duplicate
    unique_data = {json.dumps(i, sort_keys=True): i for i in all_data}.values()
    final_list = list(unique_data)
    
    print(f"Tổng số mẫu dữ liệu sau khi làm sạch: {len(final_list)}")

    # 3. Trộn ngẫu nhiên
    random.shuffle(final_list)

    # 4. Chia Train/Val (90/10)
    split_idx = int(len(final_list) * 0.9)
    train_data = final_list[:split_idx]
    val_data = final_list[split_idx:]

    # 5. Lưu file (Định dạng JSONL - phổ biến nhất cho Fine-tune)
    with open(OUTPUT_DIR / "train.jsonl", 'w', encoding='utf-8') as f:
        for entry in train_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    with open(OUTPUT_DIR / "val.jsonl", 'w', encoding='utf-8') as f:
        for entry in val_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Đã lưu {len(train_data)} mẫu vào train.jsonl")
    print(f"✅ Đã lưu {len(val_data)} mẫu vào val.jsonl")

if __name__ == "__main__":
    prepare_data()
