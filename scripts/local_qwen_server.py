from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

app = FastAPI()

# 1. CẤU HÌNH MÔ HÌNH VÀ ÉP CHẠY CPU
model_name = "heajea/qwen3.5-2b-english-tutor-v2"
device = "cpu"

print(f"⏳ Đang chuẩn bị nạp Qwen3.5-2B vào RAM hệ thống (CPU)...")
print(f"Lưu ý: Quá trình này có thể tốn khoảng 4GB - 8GB RAM.")

# 2. NẠP TOKENIZER VÀ MODEL (KHÔNG DÙNG 4-BIT)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu", # Ép buộc chạy trên CPU
    torch_dtype=torch.float32 # Định dạng chuẩn cho CPU
)

print(f"✅ Nạp xong! Mô hình đang chạy trên: {device}")

class GrammarRequest(BaseModel):
    text: str

@app.post("/fix_grammar")
async def fix_grammar(request: GrammarRequest):
    system_prompt = "Bạn là một giáo viên Tiếng Anh chuyên nghiệp. Hãy sửa lỗi ngữ pháp và giải thích chi tiết bằng Tiếng Việt theo cấu trúc: [Câu sửa đúng] || Hint: [Giải thích]"
    
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{request.text}<|im_end|>\n<|im_start|>assistant\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.1, 
            repetition_penalty=1.1,
            do_sample=True,
            top_p=0.9
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    assistant_response = response.split("assistant")[-1].strip()
    
    return {"result": assistant_response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)