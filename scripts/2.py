import json
import os

def create_chunks_for_web():
    input_file = "final_raw_dataset_25k.jsonl"
    output_dir = "deepseek_chunks"
    chunk_size = 200 # Số câu cho mỗi lần paste vào web
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    prompt_header = """You are an expert English grammar tutor. I will provide a list of wrong and corrected sentences.
For each pair, write a concise explanation (1-2 sentences) of the grammar rule used to fix the error.

    **STRICT OUTPUT FORMAT:**

        You MUST return the output ONLY as raw JSONL (JSON Lines) format. Do not use Markdown formatting (```json). Do not add any introductory or concluding text.

        CRITICAL: Do NOT use double quotes (") inside the text of the sentences or the hint. If you need to quote a word, you MUST use single quotes (').

**JSON Line Format:**
Output exactly a JSONL block (one JSON object per line) in this structure:
{"system": "You are a helpful English tutor. Correct the grammar and provide a hint.", "user": "Correct this sentence: [WRONG_SENTENCE]", "assistant": "[CORRECT_SENTENCE] || Hint: [EXPLANATION]"}

**Data to process:**
"""

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_chunks = (len(lines) + chunk_size - 1) // chunk_size
    print(f"Tổng số file cần tạo: {total_chunks}")

    for i in range(total_chunks):
        chunk_lines = lines[i * chunk_size : (i + 1) * chunk_size]
        
        file_path = os.path.join(output_dir, f"chunk_{i+1:04d}.txt")
        with open(file_path, 'w', encoding='utf-8') as out_f:
            out_f.write(prompt_header)
            for line in chunk_lines:
                data = json.loads(line)
                out_f.write(f"Wrong: {data['wrong']} | Correct: {data['correct']}\n")
        
    print(f"✅ Đã tạo xong {total_chunks} file trong thư mục '{output_dir}'.")
    print("Mở từng file, copy toàn bộ nội dung và dán vào trang web DeepSeek.")

if __name__ == "__main__":
    create_chunks_for_web()