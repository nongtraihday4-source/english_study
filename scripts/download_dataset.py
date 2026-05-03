import os
import pandas as pd
from datasets import load_dataset
import json
import random
import re

def apply_edits(text, edits):
    """Gộp các lỗi sửa của BEA-19 thành câu đúng hoàn chỉnh"""
    if not edits: return text
    # Edits có dạng: {'start': int, 'end': int, 'text': str}
    sorted_edits = sorted(edits, key=lambda x: x['start'], reverse=True)
    for edit in sorted_edits:
        text = text[:edit['start']] + edit['text'] + text[edit['end']:]
    return text

def download_and_mix_gec():
    data_frames = {}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # --- 1. BEA-19 (Wi+Locness) - XỬ LÝ THỦ CÔNG ĐỂ TRÁNH LỖI SCRIPT ---
    print("📦 Đang nạp BEA-19 (Wi+Locness)...")
    try:
        # Cách 1: Thử nạp qua script cục bộ với trust_remote_code
        script_path = os.path.join(current_dir, "wi_locness.py")
        if os.path.exists(script_path):
            dataset = load_dataset(script_path, "wi", split="train", trust_remote_code=True)
            samples = []
            for ex in dataset:
                wrong = ex['text']
                correct = apply_edits(wrong, ex['edits'])
                if wrong.strip() != correct.strip():
                    samples.append({"wrong": wrong.strip(), "correct": correct.strip()})
            data_frames['bea'] = pd.DataFrame(samples)
            print(f"✅ Nạp BEA-19 thành công: {len(data_frames['bea'])} câu.")
    except Exception as e:
        print(f"⚠️ Lỗi nạp BEA-19 qua script. Đang thử nguồn thay thế Lang-8...")
        try:
            # Fallback sang Lang-8 vì BEA-19 đang bị khóa/lỗi script
            l8 = load_dataset("lucadiliello/lang8_gec", split="train", trust_remote_code=True)
            data_frames['bea'] = pd.DataFrame(l8).rename(columns={'source': 'wrong', 'target': 'correct'})[['wrong', 'correct']]
            print(f"✅ Nạp Lang-8 (thay thế BEA) thành công: {len(data_frames['bea'])} câu.")
        except: print("❌ Không thể nạp BEA hoặc Lang-8.")

    # --- 2. C4_200M (Foundation) ---
    print("📦 Đang tải C4_200M...")
    try:
        c4 = load_dataset("hafidikhsan/c4_200m-gec-train100k-test25k", split="train", trust_remote_code=True)
        data_frames['c4'] = pd.DataFrame(c4).rename(columns={'input': 'wrong', 'output': 'correct'})[['wrong', 'correct']]
        print(f"✅ Tải C4_200M thành công: {len(data_frames['c4'])} câu.")
    except Exception as e: print(f"❌ Lỗi tải C4: {e}")

    # --- 3. CoEdIT (Sửa lỗi lọc 0 dòng) ---
    print("📦 Đang tải CoEdIT...")
    try:
        coedit = load_dataset("grammarly/coedit", split="train", trust_remote_code=True)
        df_ce = pd.DataFrame(coedit)
        # Nới lỏng regex để bắt được tất cả các task sửa lỗi ngữ pháp
        mask = df_ce['task'].astype(str).str.contains(r"fix|grammar|gec|correct", flags=re.IGNORECASE, na=False)
        df_filtered = df_ce[mask].rename(columns={'src': 'wrong', 'tgt': 'correct'})[['wrong', 'correct']]
        data_frames['coedit'] = df_filtered
        print(f"✅ Tải CoEdIT thành công: {len(data_frames['coedit'])} câu.")
    except Exception as e: print(f"❌ Lỗi tải CoEdIT: {e}")

    # --- 4. JFLEG (Fluency) ---
    print("📦 Đang tải JFLEG...")
    try:
        jfleg = load_dataset("jhu-clsp/jfleg", split="validation", trust_remote_code=True)
        df_jf = pd.DataFrame(jfleg)
        df_jf['correct'] = df_jf['corrections'].apply(lambda x: x[0] if isinstance(x, list) else x)
        data_frames['jfleg'] = df_jf.rename(columns={'sentence': 'wrong'})[['wrong', 'correct']]
        print(f"✅ Tải JFLEG thành công: {len(data_frames['jfleg'])} câu.")
    except Exception as e: print(f"❌ Lỗi tải JFLEG: {e}")

    # --- TRỘN DỮ LIỆU THEO TỶ LỆ VÀNG ---
    print("\n⚖️ Đang thực hiện trộn dữ liệu theo tỷ lệ 40/30/20/10...")
    final_samples = []
    # Mục tiêu tổng: 25,000 câu
    ratios = {'c4': 10000, 'coedit': 7500, 'bea': 5000, 'jfleg': 2500}
    
    for key, target in ratios.items():
        df_temp = data_frames.get(key)
        if df_temp is not None and not df_temp.empty:
            actual = min(target, len(df_temp))
            final_samples.append(df_temp.sample(n=actual, random_state=42))
            print(f"   🔹 Lấy {actual} mẫu từ {key.upper()}")

    if not final_samples:
        print("❌ Thất bại! Không có dữ liệu để trộn.")
        return

    final_df = pd.concat(final_samples).drop_duplicates()
    
    # Lọc độ dài chuẩn (8-40 từ)
    final_df['wc'] = final_df['wrong'].str.split().str.len()
    final_df = final_df[(final_df['wc'] >= 7) & (final_df['wc'] <= 40)].drop(columns=['wc'])
    
    # Xáo trộn và lưu
    final_df = final_df.sample(frac=1, random_state=42)
    output_file = "super_raw_gec_25k.jsonl"
    final_df.to_json(output_file, orient="records", lines=True, force_ascii=False)
    
    print(f"\n🎉 HOÀN THÀNH! File đã lưu tại: {os.path.abspath(output_file)}")
    print(f"📊 Tổng số câu thô sạch: {len(final_df)}")

if __name__ == "__main__":
    download_and_mix_gec()