import json
import pandas as pd
import os
import re
import unicodedata

def remove_accents(text):
    """Tuyệt chiêu biến Tiếng Việt có dấu thành Không dấu chuẩn ASCII"""
    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text).replace('đ', 'd').replace('Đ', 'D')

def transform_target(raw_target):
    """Chuyển đổi định dạng cũ '|| Lỗi: ... || HD: ...' sang '|| Hint: ...' không dấu"""
    if not isinstance(raw_target, str):
        return raw_target
        
    # Chẻ chuỗi ra làm 3 khúc
    parts = [p.strip() for p in raw_target.split('||')]
    corrected = parts[0]
    
    hint_text = ""
    if len(parts) > 1:
        # Bóc tách Lỗi và Hướng dẫn, xóa chữ thừa
        error_type = parts[1].replace('Lỗi:', '').strip() if len(parts) > 1 else ""
        explanation = parts[2].replace('HD:', '').strip() if len(parts) > 2 else ""
        
        # Gộp lại thành 1 câu giải thích hoàn chỉnh
        hint_text = f"{error_type}. {explanation}".strip(' .')
        
    if hint_text:
        # Ép sang không dấu
        clean_hint = remove_accents(hint_text)
        return f"{corrected} || Hint: {clean_hint}"
        
    return corrected

print("🚀 Bắt đầu dọn dẹp và ĐỒNG BỘ HÓA 4 file dữ liệu bổ sung...")

# Định vị thư mục
current_dir = os.path.dirname(os.path.abspath(__file__))
json_files = ['1.json', '2.json', '3.json', '4.json']

all_data = []

for file_name in json_files:
    file_path = os.path.join(current_dir, file_name)
    if not os.path.exists(file_path):
        print(f"⚠️ Bỏ qua: Không tìm thấy '{file_name}'")
        continue
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
        # Chữa cháy cú pháp do AI sinh lỗi (Giữ lại từ bản cũ)
        content = re.sub(r'"input":\s*"tutor":\s*"', r'"input": "tutor: ', content)
        content = re.sub(r'"input":\s*"tutor":\s*(?!")', r'"input": "tutor: ', content)
        
        try:
            data = json.loads(content)
            for item in data:
                if 'input' in item and 'target' in item:
                    # Chuẩn hóa lại Target
                    new_target = transform_target(item['target'])
                    all_data.append({
                        "input": item['input'],
                        "target": new_target
                    })
            print(f"  ✅ Đã xử lý & chuyển đổi không dấu: {file_name} ({len(data)} mẫu)")
        except json.JSONDecodeError as e:
            print(f"  ❌ Lỗi cú pháp JSON ở '{file_name}': {e}")

# Xuất ra file CSV mới
print("-" * 50)
if all_data:
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates()
    
    # Lưu với tên có chữ "robust" để đồng bộ với file kia
    output_file = os.path.join(current_dir, "t5_additional_dataset_robust.csv")
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"🎉 HOÀN TẤT! Đã xuất {len(df)} câu ra file '{output_file}' thành công!")