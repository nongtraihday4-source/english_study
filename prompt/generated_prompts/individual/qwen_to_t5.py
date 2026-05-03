import json
import os
import pandas as pd
import glob

# Cấu hình đường dẫn
INPUT_FOLDER = "/home/n2t/Documents/english_study/prompt/generated_prompts/individual" 
OUTPUT_CSV = "/home/n2t/Documents/english_study/dataset/qwen_tutor_dataset_full.csv"

def aggregate_to_qwen_csv():
    all_data = []
    # Tìm tất cả file .json trong thư mục
    json_files = glob.glob(os.path.join(INPUT_FOLDER, "*.json"))
    
    print(f"📂 Tìm thấy {len(json_files)} file dữ liệu. Đang xử lý...")

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Hỗ trợ cả định dạng list trực tiếp hoặc nằm trong key "data"
                items = data if isinstance(data, list) else data.get("data", [])

                for item in items:
                    instruction = item.get('instruction', 'Sửa lỗi ngữ pháp cho câu sau')
                    user_input = item.get('input', '')
                    assistant_output = item.get('output', '')

                    if user_input and assistant_output:
                        all_data.append({
                            "system": "Bạn là một giáo viên Tiếng Anh chuyên nghiệp. Hãy sửa lỗi ngữ pháp và giải thích chi tiết bằng Tiếng Việt theo cấu trúc: [Câu đúng] || Hint: [Giải thích]",
                            "user": f"{instruction}\n{user_input}",
                            "assistant": assistant_output
                        })
        except Exception as e:
            print(f"⚠️ Lỗi xử lý file {os.path.basename(file_path)}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        # Đảm bảo thư mục đầu ra tồn tại
        os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"✅ THÀNH CÔNG! Đã gộp {len(df)} mẫu câu vào file: {OUTPUT_CSV}")
    else:
        print("❌ Không tìm thấy dữ liệu hợp lệ để gộp.")

if __name__ == "__main__":
    aggregate_to_qwen_csv()