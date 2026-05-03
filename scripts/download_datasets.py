#!/usr/bin/env python3
"""Download all Jackrong datasets from HuggingFace into High-fidelity Dataset folder."""

import os
from huggingface_hub import snapshot_download, HfApi

TARGET_DIR = os.path.join(os.path.dirname(__file__), "High-fidelity Dataset")
os.makedirs(TARGET_DIR, exist_ok=True)

# Khởi tạo API và lấy danh sách dataset của tác giả
api = HfApi()
datasets = list(api.list_datasets(author="Jackrong"))
print(f"Found {len(datasets)} datasets from Jackrong\n")

for i, ds in enumerate(datasets, 1):
    ds_name = ds.id.split("/")[-1]
    local_dir = os.path.join(TARGET_DIR, ds_name)
    
    print(f"[{i}/{len(datasets)}] Downloading: {ds.id}")
    print(f"  -> {local_dir}")
    
    try:
        # Chỉ thực hiện tải dữ liệu về thư mục đích
        snapshot_download(
            repo_id=ds.id,
            repo_type="dataset",
            local_dir=local_dir,
            resume_download=True # Hỗ trợ tải tiếp nếu bị gián đoạn mạng
        )
        print(f"  ✓ Tải xong\n")

    except Exception as e:
        print(f"  ✗ Lỗi: {e}\n")

print("=" * 60)
print(f"Quá trình tải hoàn tất! Dữ liệu nằm ở: {TARGET_DIR}")