# Hướng Dẫn Tinh Chỉnh (Fine-tuning) Qwen2.5-7B Cho Ứng Dụng Học Tiếng Anh

Dựa trên yêu cầu của bạn, việc **tinh chỉnh (fine-tune) lại mô hình Qwen2.5-7B** để tập trung vào việc sửa lỗi ngữ pháp và nhận xét phát âm cho học viên Việt Nam là một hướng đi hoàn toàn khả thi và tối ưu. Dưới đây là phân tích chi tiết và các bước triển khai cụ thể.

---

## 1. Phân Tích Yêu Cầu & Giải Pháp

### Mục tiêu:
- **Rút gọn bối cảnh:** Thay vì để AI trả lời vạn năng, ta "dạy" nó chỉ tập trung làm giáo viên Tiếng Anh cho người Việt (giải thích ngữ pháp, nhận xét phát âm).
- **Tối ưu bộ nhớ (VRAM) & Tốc độ:** Fine-tune xong sẽ xuất ra định dạng **GGUF (Q4_K_M)** để chạy cực nhẹ qua Ollama trên Server thực tế.
- **Mô phỏng thực tế:** Đưa các kịch bản đang chạy trên `scripts/test_colab_ai.py` (như lỗi ngữ pháp `"She don't like..."`, lỗi phát âm) vào dữ liệu huấn luyện để AI trả lời đúng chuẩn (format, giọng văn) mà ứng dụng mong muốn.

### Công cụ sử dụng:
1. **Unsloth:** Thư viện giúp fine-tune LLM siêu nhanh và tiết kiệm VRAM. Nó cho phép train mô hình 7B ngay trên GPU Tesla T4 (miễn phí) của Google Colab.
2. **QLoRA (Quantized LoRA):** Đóng băng mô hình gốc, chỉ train một phần nhỏ trọng số (Adapter) dạng 4-bit giúp tiết kiệm tối đa phần cứng.
3. **Ollama & GGUF:** Đóng gói mô hình sau khi train để chạy trên Production Server với tài nguyên VPS tầm trung (RAM 16GB, GPU VRAM ~6GB-8GB).

---

## 2. Các Bước Triển Khai Chi Tiết

### BƯỚC 1: Chuẩn bị Dữ liệu Huấn Luyện (Dataset)
Mô hình cần học cách phản hồi đúng định dạng mà FastAPI của bạn đang sử dụng ở `model_AI_for_my_english_study.ipynb`.

Hãy tạo một file `dataset.json` chứa khoảng 500-1000 mẫu theo format sau. Ở đây tôi sẽ chia làm 2 loại kịch bản chính: **Grammar** và **Speaking**.

```json
[
  {
    "instruction": "Bạn là giáo viên tiếng Anh cho người Việt. Hãy phân tích lỗi ngữ pháp trong câu của học viên và giải thích bằng Tiếng Việt.",
    "input": "She don't like playing football in the weekends.",
    "output": "Câu của bạn có 2 lỗi ngữ pháp cơ bản cần sửa:\n1. Sai động từ to be/trợ động từ: Chủ ngữ 'She' là ngôi thứ 3 số ít, nên trợ động từ phủ định phải là 'doesn't' thay vì 'don't'.\n2. Sai giới từ chỉ thời gian: Với 'the weekends' (cuối tuần), người Anh thường dùng 'at the weekends', còn người Mỹ hay dùng 'on the weekends'. KHÔNG dùng 'in'.\n👉 Câu sửa lại: 'She doesn't like playing football on the weekends.'"
  },
  {
    "instruction": "Bạn là giáo viên tiếng Anh. So sánh câu phát âm yêu cầu và thực tế của học viên, sau đó nhận xét bằng Tiếng Việt.",
    "input": "Yêu cầu: 'I want to travel the world'. Thực tế: 'I want to travo the word'.",
    "output": "Phát âm của bạn khá tốt nhưng cần chú ý các điểm sau:\n1. Từ 'travel': Bạn phát âm thành 'travo', thiếu âm /l/ ở cuối từ. Hãy uốn cong đầu lưỡi chạm vòm miệng trên để tạo âm /l/.\n2. Từ 'world': Bạn phát âm thành 'word'. Âm /ɜːld/ khá khó, hãy cố gắng ngân dài âm /ɜː/ rồi uốn lưỡi âm /l/ trước khi bật âm /d/ nhé.\n👉 Đánh giá chung: Cố gắng phát âm rõ các phụ âm cuối (ending sounds) nhé!"
  }
]
```

### BƯỚC 2: Khởi tạo Notebook trên Google Colab
1. Mở **Google Colab**, tạo Notebook mới.
2. Vào **Runtime** > **Change runtime type** > Chọn **T4 GPU** > **Save**.

### BƯỚC 3: Cài đặt Môi trường & Viết Code Huấn Luyện
Chạy các ô (cell) sau trong Colab của bạn:

**Cell 1: Cài đặt thư viện Unsloth**
```python
%%capture
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps "xformers<0.1.0" "trl<0.9.0" peft accelerate bitsandbytes datasets
```

**Cell 2: Tải mô hình cơ sở Qwen2.5-7B (4-bit)**
```python
from unsloth import FastLanguageModel
import torch

max_seq_length = 2048 # Độ dài ngữ cảnh
dtype = None # Tự động phát hiện (float16 cho T4)
load_in_4bit = True # Bắt buộc để chạy trên T4

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# Thêm cấu hình LoRA Adapter
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Càng lớn càng học được nhiều nhưng nặng hơn
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, # Tối ưu tốc độ
    bias = "none",    # Tối ưu tốc độ
    use_gradient_checkpointing = "unsloth", # Tiết kiệm VRAM
    random_state = 3407,
)
```

**Cell 3: Nạp Dataset của bạn**
```python
from datasets import load_dataset
# Đảm bảo bạn đã upload file dataset.json lên môi trường Colab
dataset = load_dataset("json", data_files="dataset.json", split="train")

prompt_template = """<|im_start|>system
{instruction}<|im_end|>
<|im_start|>user
{input}<|im_end|>
<|im_start|>assistant
{output}<|im_end|>"""

def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for inst, inp, out in zip(instructions, inputs, outputs):
        text = prompt_template.format(instruction=inst, input=inp, output=out)
        texts.append(text)
    return { "text" : texts, }

dataset = dataset.map(formatting_prompts_func, batched = True,)
```

**Cell 4: Huấn luyện (Train) mô hình**
```python
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 100, # Tăng số bước này (VD: 500-1000) tuỳ vào dữ liệu thực tế
        learning_rate = 2e-4,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)
# Bắt đầu train!
trainer_stats = trainer.train()
```

### BƯỚC 4: Xuất mô hình sang định dạng GGUF (Để chạy với Ollama)
Sau khi train xong, chúng ta cần ép nó thành file GGUF `q4_k_m` (Khoảng 4.5GB) để chạy siêu nhẹ.

**Cell 5: Xuất file GGUF**
```python
# Lưu mô hình LoRA
model.save_pretrained("qwen2.5-english-lora")
tokenizer.save_pretrained("qwen2.5-english-lora")

# Sử dụng công cụ tích hợp của Unsloth để convert sang GGUF (Cần liên kết HuggingFace Token nếu muốn push lên mạng)
# Tuy nhiên, ta lưu thẳng vào ổ cứng Colab:
model.save_pretrained_gguf("qwen2.5-english-gguf", tokenizer, quantization_method = "q4_k_m")
```
Sau khi chạy xong, bạn sẽ thấy một thư mục `qwen2.5-english-gguf` chứa file `.gguf`. Bạn hãy **tải file này về máy tính hoặc Server VPS của bạn**.

---

## 3. Chạy Mô Hình Trên Server Thực Tế (Ollama)

Sau khi có file `.gguf` (Giả sử tên là `unsloth.Q4_K_M.gguf`), chúng ta tích hợp nó vào Ollama trên VPS/Server của bạn:

1. **Copy file `.gguf` lên VPS của bạn**.
2. **Tạo một file tên là `Modelfile`** (không có phần mở rộng) đặt cùng thư mục với file gguf, với nội dung:
```dockerfile
FROM ./unsloth.Q4_K_M.gguf
# Tham số giúp model sinh chữ sáng tạo và đa dạng
PARAMETER temperature 0.6
PARAMETER top_p 0.9

# (Tùy chọn) Gán luôn system prompt mặc định
SYSTEM """Bạn là giáo viên tiếng Anh cho người Việt. Chỉ trả lời bằng Tiếng Việt."""
```

3. **Tạo mô hình tuỳ chỉnh trong Ollama:**
```bash
ollama create qwen-english-teacher -f Modelfile
```

4. **Chạy thử mô hình:**
```bash
ollama run qwen-english-teacher
```

## 4. Cập Nhật Code API Trong Hệ Thống Của Bạn
Khi mô hình của bạn đã chạy trên Ollama với tên `qwen-english-teacher`, bạn chỉ cần sửa file code FastAPI của bạn để trỏ vào nó.

Ví dụ trong script đang có (`model_AI_for_my_english_study.ipynb`):
```python
response = llm_client.chat.completions.create(
    model="qwen-english-teacher", # Đổi tên model ở đây!
    messages=[
        {"role": "user", "content": prompt}
    ]
)
```

## Kết Luận
Bằng cách Fine-tune, mô hình Qwen 7B của bạn sẽ:
1. Trả lời thẳng vào vấn đề (sửa lỗi ngữ pháp/phát âm) thay vì dông dài.
2. Nắm bắt được các lỗi kinh điển của người học Tiếng Anh tại Việt Nam.
3. Chạy ổn định trên VPS với chỉ ~5GB VRAM nhờ định dạng GGUF q4_k_m, loại bỏ hoàn toàn sự phụ thuộc vào API đắt đỏ bên ngoài.
