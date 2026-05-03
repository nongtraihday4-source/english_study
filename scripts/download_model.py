from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os

# Tên mô hình trên Hugging Face của bạn
model_name = "heajea/t5-base-vietnamese-english-tutor"

# Thư mục lưu trữ cục bộ
save_directory = "./models/t5_tutor"

if not os.path.exists(save_directory):
    os.makedirs(save_directory)

print(f"⏳ Đang tải mô hình từ Hugging Face về thư mục {save_directory}...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Lưu vĩnh viễn vào thư mục
tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)

print(f"✅ Đã lưu xong! Bây giờ bạn có thể ngắt mạng và chạy mô hình từ thư mục này.")