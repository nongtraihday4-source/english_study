import tarfile
import json
import os
import pandas as pd

def apply_edits_json(text, edits):
    if not edits: return text
    # Sắp xếp sửa lỗi ngược từ cuối lên
    sorted_edits = sorted(edits, key=lambda x: x[0], reverse=True)
    for start, end, corr in sorted_edits:
        if corr is not None:
            text = text[:start] + corr + text[end:]
    return text

def parse_m2(m2_content):
    samples = []
    blocks = m2_content.strip().split("\n\n")
    for block in blocks:
        lines = block.split("\n")
        if not lines or not lines[0].startswith("S "): continue
        source = lines[0][2:] # Lấy câu gốc
        edits = []
        for line in lines[1:]:
            if line.startswith("A "):
                parts = line.split("|||")
                span = parts[0][2:].split()
                start, end = int(span[0]), int(span[1])
                corr = parts[2]
                if parts[1] != "noop": # Lấy các edit có lỗi thực sự
                    edits.append((start, end, corr))
        
        # Áp dụng edits
        edits.sort(key=lambda x: x[0], reverse=True)
        target = source
        tokens = target.split()
        for start, end, corr in edits:
            if start == -1: continue # Bỏ qua edit lỗi của annotator
            # Thay thế token
            tokens[start:end] = [corr]
        target = " ".join(tokens)
        
        # Chỉ lấy câu nếu có thay đổi
        if source.strip() != target.strip():
            samples.append({"wrong": source.strip(), "correct": target.strip()})
    return samples

def process_uploaded_files():
    final_data = []

    # Định vị file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    wi_tar_path = os.path.join(root_dir, "wi+locness_v2.1.bea19.tar.gz")
    fce_tar_path = os.path.join(root_dir, "fce_v2.1.bea19.tar.gz")

    if not os.path.exists(wi_tar_path):
        print(f"❌ Không tìm thấy: {wi_tar_path}")
        return
    if not os.path.exists(fce_tar_path):
        print(f"❌ Không tìm thấy: {fce_tar_path}")
        return

    # 1. Trích xuất Wi+Locness
    print(f"🚜 Đang quét {wi_tar_path}...")
    with tarfile.open(wi_tar_path, "r:gz") as tar:
        # Tìm BẤT KỲ file nào có chữ "json" trong gói
        json_files = [m for m in tar.getmembers() if ".json" in m.name]
        print(f"   Tìm thấy {len(json_files)} file JSON. Bắt đầu đọc...")
        
        for member in json_files:
            f = tar.extractfile(member)
            if f:
                for line in f:
                    try:
                        obj = json.loads(line.decode("utf-8"))
                        # Có thể có nhiều người đánh giá, ta ưu tiên người đầu tiên
                        if obj.get('edits') and len(obj['edits']) > 0 and len(obj['edits'][0]) > 1:
                            edits = obj['edits'][0][1] 
                            correct = apply_edits_json(obj['text'], edits)
                            if obj['text'].strip() != correct.strip():
                                final_data.append({"wrong": obj['text'].strip(), "correct": correct.strip()})
                    except Exception as e:
                        continue # Bỏ qua dòng lỗi

    # 2. Trích xuất FCE
    print(f"🚜 Đang quét {fce_tar_path}...")
    with tarfile.open(fce_tar_path, "r:gz") as tar:
        # Tìm BẤT KỲ file nào có đuôi ".m2"
        m2_files = [m for m in tar.getmembers() if m.name.endswith(".m2")]
        print(f"   Tìm thấy {len(m2_files)} file M2. Bắt đầu đọc...")
        
        for member in m2_files:
            f = tar.extractfile(member)
            if f:
                content = f.read().decode("utf-8", errors='ignore')
                extracted = parse_m2(content)
                final_data.extend(extracted)

    # 3. Chuẩn hóa và Ghi tệp
    print("⏳ Đang chuẩn hóa dữ liệu...")
    df = pd.DataFrame(final_data).drop_duplicates()
    
    # Nới lỏng độ dài: Lấy câu từ 5 đến 50 từ (rất nhiều câu thực tế dài/ngắn hơn chuẩn)
    df['wc'] = df['wrong'].str.split().str.len()
    df = df[(df['wc'] >= 5) & (df['wc'] <= 50)].drop(columns=['wc'])
    
    print(f"📊 Tổng số cặp câu thu được sau khi làm sạch: {len(df)}")
    
    # Lấy mẫu tối đa 25,000 câu
    df_final = df.sample(n=min(25000, len(df)), random_state=42)
    output_path = os.path.join(root_dir, "super_raw_gec_local.jsonl")
    df_final.to_json(output_path, orient="records", lines=True, force_ascii=False)
    
    print(f"✅ HOÀN THÀNH! Lưu tại {output_path} ({len(df_final)} câu).")

if __name__ == "__main__":
    process_uploaded_files()