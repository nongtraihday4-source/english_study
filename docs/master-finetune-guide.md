# 🎓 Master Guide: Huấn luyện AI English Teacher (Qwen 2.5)

Tài liệu này hướng dẫn bạn cách biến mô hình Qwen 2.5 (1.5B hoặc 7B) thành một giáo viên Tiếng Anh chuyên nghiệp, am hiểu lỗi sai của người Việt thông qua kỹ thuật Fine-tuning.

---

## 🛠 Giai đoạn 1: Chuẩn bị dữ liệu (Data Preparation)

Trước khi gửi AI đi học, ta cần "soạn giáo trình". Chúng ta dùng script đã viết để gộp 5,000 câu từ các file JSON lẻ thành định dạng `.jsonl`.

1. **Chạy script chuẩn hóa**:
   ```bash
   python scripts/prepare_finetune_data.py
   ```
2. **Kết quả**: Bạn sẽ có 2 file tại `data/finetune/`:
   - `train.jsonl`: Dữ liệu cho AI học.
   - `val.jsonl`: Dữ liệu để kiểm tra AI.

---

## ☁️ Giai đoạn 2: Đưa dữ liệu lên Google Colab

Để huấn luyện miễn phí trên GPU T4 của Google, cách tốt nhất là dùng Google Drive làm cầu nối.

1. Tải 2 file `.jsonl` lên một thư mục trên Google Drive của bạn (ví dụ: `EnglishStudy/data/`).
2. Mở Google Colab và Mount Drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

---

## 🚀 Giai đoạn 3: Huấn luyện với Unsloth (Khuyên dùng)

**Unsloth** giúp tốc độ huấn luyện nhanh gấp 2 lần và tiết kiệm 70% bộ nhớ.

### 1. Cài đặt thư viện trên Colab
```python
!pip install unsloth
!pip install --no-deps xformers trl peft accelerate bitsandbytes
```

### 2. Tải mô hình Qwen 2.5 (Bản 4-bit cực nhẹ)
```python
from unsloth import FastLanguageModel
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen2.5-1.5B-bnb-4bit", # Hoặc 7B nếu dùng bản Pro
    max_seq_length = 2048,
    load_in_4bit = True,
)
```

### 3. Cấu hình Tham số học (LoRA)
```python
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Càng cao càng học kỹ nhưng tốn VRAM
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
)
```

---

## 📚 Giai đoạn 4: Bắt đầu Huấn luyện

### 1. Nạp dữ liệu từ Drive
```python
from datasets import load_dataset
dataset = load_dataset("json", data_files={"train": "/content/drive/MyDrive/EnglishStudy/data/train.jsonl"}, split="train")
```

### 2. Chạy Trainer
```python
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = 2048,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Tăng lên 300-500 để học kỹ hơn
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        output_dir = "outputs",
    ),
)
trainer.train()
```

---

## 📦 Giai đoạn 5: Xuất bản và Sử dụng

Sau khi huấn luyện xong, bạn cần xuất mô hình sang định dạng **GGUF** để mang về chạy trên máy tính cá nhân bằng Ollama.

### 1. Lưu mô hình GGUF
```python
model.save_pretrained_gguf("qwen_english_teacher", tokenizer, quantization_method = "q4_k_m")
```

### 2. Sử dụng trên máy Local (Ollama)
1. Tải file `.gguf` từ Colab về máy.
2. Tạo file `Modelfile` với nội dung:
   ```text
   FROM ./qwen_english_teacher.gguf
   SYSTEM "Bạn là giáo viên Tiếng Anh chuyên sửa lỗi cho người Việt."
   ```
3. Chạy lệnh: `ollama create english-teacher -f Modelfile`
4. Thưởng thức thành quả: `ollama run english-teacher`

---
> [!TIP]
> Hãy bắt đầu với bản **1.5B** trước để làm quen quy trình, sau đó mới nâng cấp lên bản **7B** khi bạn đã có dữ liệu chất lượng cao.
