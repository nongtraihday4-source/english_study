from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

app = FastAPI()

# 1. CẤU HÌNH ĐƯỜNG DẪN VÀ THIẾT BỊ
# Bạn có thể dùng model_id từ Hugging Face hoặc đường dẫn folder sau khi tải về
model_name = "heajea/qwen3.5-2b-english-tutor-v2"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"⏳ Đang nạp Qwen3.5 từ: {model_name} vào {device}...")

# 2. NẠP TOKENIZER VÀ MODEL
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto" # Tự động tối ưu hóa việc phân bổ giữa CPU/GPU
)

print("✅ Nạp xong! Qwen3.5 Server đang sẵn sàng...")

class GrammarRequest(BaseModel):
    text: str

@app.post("/fix_grammar")
async def fix_grammar(request: GrammarRequest):
    # Cấu hình Prompt chuẩn ChatML đã học
    system_prompt = "Bạn là một giáo viên Tiếng Anh chuyên nghiệp. Hãy sửa lỗi ngữ pháp và giải thích chi tiết bằng Tiếng Việt theo cấu trúc: [Câu sửa đúng] || Hint: [Giải thích]"
    
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{request.text}<|im_end|>\n<|im_start|>assistant\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.3,
            repetition_penalty=1.1
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Tách lấy phần trả lời của Assistant
    assistant_response = response.split("assistant")[-1].strip()
    
    return {"result": assistant_response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)