from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import time
from llama_cpp import Llama

app = FastAPI()

MODEL_PATH = "/home/n2t/Documents/english_study/models/qwen3-4b.Q4_K_M.gguf"

print(f"⏳ Đang nạp Qwen3-4B tutor từ: {MODEL_PATH}...")
# Khai báo model, KHÔNG CẦN CHỈNH SỬA GÌ Ở ĐÂY
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4, 
    verbose=False,
    chat_format="llama-3" # Thêm dòng này để ép nó dùng chuẩn Llama 3
)
print("✅ Llama Server đã sẵn sàng!")

class TutorRequest(BaseModel):
    system_message: str
    user_message: str

@app.post("/fix_grammar")
async def fix_grammar(request: TutorRequest):
    start_time = time.time()
    
    # SỬ DỤNG CREATE_CHAT_COMPLETION THAY VÌ CALL TRỰC TIẾP llm()
    # Thư viện sẽ tự động quản lý các thẻ <|begin_of_text|>
    output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": request.system_message},
            {"role": "user", "content": request.user_message}
        ],
        max_tokens=256,
        temperature=0.1,
    )
    
    # Cách lấy dữ liệu từ kết quả cũng thay đổi một chút
    response = output['choices'][0]['message']['content'].strip()
    return {"result": response, "time": round(time.time() - start_time, 2)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)