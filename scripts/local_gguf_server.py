from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import time
from llama_cpp import Llama

app = FastAPI()

MODEL_PATH = "./models/qwen3-4b.Q4_K_M.gguf"

print(f"⏳ Đang nạp GGUF từ: {MODEL_PATH}...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4, 
    n_gpu_layers=0,
    verbose=False
)
print("✅ Nạp xong! API Server Đa Kỹ Năng đang chạy...")

class TutorRequest(BaseModel):
    text: str
    task_type: str = "grammar" # Mặc định là sửa ngữ pháp

@app.post("/fix_grammar")
async def fix_grammar(request: TutorRequest):
    start_time = time.time()
    # BỘ ĐỊNH TUYẾN "NHÂN CÁCH" (SYSTEM PROMPT) VÀ NHIỆT ĐỘ
    # Hạ nhiệt độ xuống thấp để ưu tiên tính logic và chính xác tuyệt đối
    ai_temp = 0.1 
    
    if request.task_type == "dictation":
        ai_temp = 0.1
        system_prompt = """Bạn là trợ lý so sánh văn bản.
                            So sánh [Câu gốc] và [Học viên viết]. Chỉ ra TỪNG TỪ bị nghe nhầm.
                            QUY TẮC:
                            1. TUYỆT ĐỐI KHÔNG giải thích ngữ pháp (như "dạng phủ định", "câu điều kiện").
                            2. Chỉ giải thích ngắn gọn là do "nghe lướt" hoặc "nối âm".
                            Tuân thủ định dạng: [Câu gốc] || Hint: [Chỉ ra từ nghe nhầm]."""

    elif request.task_type == "shadowing":
        ai_temp = 0.1 # Giữ nhiệt độ thấp
        # Dùng LỆNH BÀN TAY SẮT: Ép quy trình tư duy từng bước, cấm tự bịa lỗi
        system_prompt = """Bạn là trợ lý so sánh văn bản.
                        NHIỆM VỤ: So sánh TỪNG TỪ giữa [Câu cần đọc] và [AI nhận diện].
                        QUY TẮC:
                        1. Chỉ ra từ nào trong [Câu cần đọc] đã bị biến thành từ nào trong [AI nhận diện].
                        2. TUYỆT ĐỐI KHÔNG dùng ký hiệu phiên âm (IPA) như /s/, /t/, /p/.
                        3. TUYỆT ĐỐI KHÔNG giải thích cách đặt môi, răng, lưỡi.
                        4. TUYỆT ĐỐI KHÔNG nhắc đến từ "âm cuối" hay "ending sound" nếu từ đó không bị sai âm cuối.
                        Tuân thủ định dạng: [Câu gốc] || Hint: [Liệt kê các cặp từ bị sai]."""
    elif request.task_type == "word_stress":
        ai_temp = 0.1
        system_prompt = "Bạn là giáo viên phát âm chuyên về trọng âm. BẮT BUỘC tuân thủ đúng định dạng: [Từ đúng/Ngữ điệu đúng] || Hint: [Giải thích]."
        
    elif request.task_type == "collocations":
        ai_temp = 0.2
        system_prompt = "Bạn là chuyên gia từ vựng. Sửa lại câu Vinglish cho tự nhiên hơn dựa trên 'Collocations'. BẮT BUỘC tuân thủ đúng định dạng: [Câu tự nhiên] || Hint: [Giải thích]."
        
    elif request.task_type == "pragmatics":
        ai_temp = 0.2
        system_prompt = "Bạn là giáo viên giao tiếp. Biến đổi câu nói thô lỗ thành lịch sự nơi công sở. BẮT BUỘC tuân thủ đúng định dạng: [Câu lịch sự] || Hint: [Giải thích]."
        
    elif request.task_type == "listening":
        ai_temp = 0.15 # Hạ từ 0.5 xuống 0.15 để tránh dùng từ lóng sai ngữ cảnh
        system_prompt = "Bạn là giáo viên bản xứ. Giải thích tại sao học viên hiểu sai đoạn hội thoại. Tập trung vào thành ngữ/nghĩa bóng. BẮT BUỘC tuân thủ đúng định dạng: [Đáp án đúng] || Hint: [Giải thích ngắn gọn]."
    else: 
        ai_temp = 0.1 # Giữ nguyên độ an toàn tuyệt đối cho Ngữ pháp
        system_prompt = "Bạn là giáo viên Tiếng Anh. Nhiệm vụ là sửa lỗi ngữ pháp (Vinglish). Tuân thủ: [Câu sửa đúng] || Hint: [Giải thích ngắn gọn]."
    
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{request.text}<|im_end|>\n<|im_start|>assistant\n"
    
    output = llm(
        prompt,
        max_tokens=300, # Tăng giới hạn chữ để AI thoải mái giải thích
        temperature=ai_temp, # Sử dụng nhiệt độ đã tùy chỉnh theo Task
        top_p=0.85,
        repeat_penalty=1.05,
        stop=["<|im_end|>"]
    )
    
    assistant_response = output['choices'][0]['text'].strip()
    end_time = time.time()
    
    print(f"[{end_time - start_time:.2f}s] Task: {request.task_type} -> Thành công.")
    
    return {"result": assistant_response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)