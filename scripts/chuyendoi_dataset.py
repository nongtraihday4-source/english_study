import json
import os
import pandas as pd
import re

# Cấu hình đường dẫn
INPUT_FOLDER = "/home/n2t/Documents/english_study/data/json_topics/" # Thay bằng thư mục chứa 66 file của bạn
OUTPUT_FILE = "/home/n2t/Documents/english_study/data/t5_tutor_dataset.csv"

def clean_text(text):
    """Loại bỏ các ký tự xuống dòng và khoảng trắng thừa"""
    return text.replace('\n', ' ').strip()

def parse_output(output_text):
    """Bóc tách Corrected Sentence và Explanation từ định dạng cũ"""
    # Trích xuất câu đúng sau ✅
    corrected = re.search(r"✅ \*\*Corrected Sentence:\*\* (.*?)(?=\\n|🔍|$)", output_text)
    if not corrected:
        corrected = re.search(r"✅ (.*?)(?=\\n|🔍|$)", output_text)
        
    # Trích xuất Giải thích (kết hợp Error Identification và Vietnamese Explanation)
    error_id = re.search(r"🔍 \*\*Error Identification:\*\* (.*?)(?=\\n|📘|$)", output_text)
    viet_exp = re.search(r"📘 \*\*Vietnamese Explanation:\*\* (.*?)(?=\\n|💡|$)", output_text)
    
    corrected_val = corrected.group(1).strip() if corrected else ""
    error_val = error_id.group(1).strip() if error_id else ""
    # Lấy câu đầu tiên của giải thích tiếng Việt để giữ độ ngắn gọn cho T5
    viet_val = viet_exp.group(1).split('.')[0].strip() if viet_exp else ""
    
    # Ghép lại thành Target cho T5
    target = f"{corrected_val} || Lỗi: {error_val} || HD: {viet_val}."
    return target

def convert_all_files():
    all_data = []
    
    # Quét tất cả file .json trong thư mục
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.json')]
    print(f"📂 Tìm thấy {len(files)} file chuyên đề. Đang bắt đầu chuyển đổi...")

    for file_name in files:
        with open(os.path.join(INPUT_FOLDER, file_name), 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                t5_input = f"tutor: {item['input']}"
                t5_target = parse_output(item['output'])
                
                all_data.append({
                    "input": t5_input,
                    "target": t5_target
                })

    # Lưu thành file CSV để dễ dàng nạp vào Hugging Face Datasets
    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"✅ HOÀN TẤT! Đã tạo file: {OUTPUT_FILE}")
    print(f"📊 Tổng số mẫu dữ liệu: {len(df)}")

if __name__ == "__main__":
    convert_all_files()