import pandas as pd
import os

def merge_datasets():
    print("⏳ Đang đọc hai file dữ liệu thô...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    
    local_file = os.path.join(root_dir, "super_raw_gec_local.jsonl")
    hf_file = os.path.join(root_dir, "super_raw_gec_25k.jsonl")
    
    # 1. Đọc dữ liệu
    df_local = pd.read_json(local_file, lines=True)
    df_hf = pd.read_json(hf_file, lines=True)
    
    print(f"   - File Local (BEA/FCE): {len(df_local)} câu.")
    print(f"   - File HF (C4/CoEdIT/JFLEG): {len(df_hf)} câu.")
    
    # 2. Gộp và loại bỏ trùng lặp
    df_merged = pd.concat([df_local, df_hf]).drop_duplicates(subset=['wrong'])
    
    # 3. Lấy ngẫu nhiên 25.000 câu để chưng cất (để tiết kiệm thời gian/chi phí)
    # Bạn có thể tăng số này lên nếu muốn model học nhiều hơn
    target_size = min(40000, len(df_merged))
    df_final = df_merged.sample(n=target_size, random_state=42)
    
    # 4. Lưu thành file cuối cùng
    output_path = os.path.join(root_dir, "final_raw_dataset_25k.jsonl")
    df_final.to_json(output_path, orient="records", lines=True, force_ascii=False)
    
    print(f"✅ Đã gộp thành công! File cuối cùng: {output_path}")
    print(f"📊 Số lượng câu chuẩn bị cho chưng cất: {len(df_final)}")

if __name__ == "__main__":
    merge_datasets()