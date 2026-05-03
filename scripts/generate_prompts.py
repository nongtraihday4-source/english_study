import os
import re

def parse_topics(text):
    # Dùng regex để tìm tất cả các mục có định dạng "Tên chuyên đề - Số câu"
    pattern = r'((?:\d{1,2}\.\s+|(?:Thì|Nhóm thì|Sự hòa hợp)\s+).*?)\s*-\s*(\d+)\s*[Cc][âa]u'
    
    results = []
    for match in re.finditer(pattern, text):
        topic = match.group(1).strip()
        count = int(match.group(2).strip())
        
        # Bỏ qua các tiêu đề nhóm (số lượng câu lớn hơn 500)
        if count >= 500:
            continue
            
        # Làm sạch các topic bị dính tiêu đề nhóm phía trước (ví dụ "4. NHÓM... 28. Câu Bị động")
        if re.search(r'\d{1,2}\.', topic):
            # Lấy từ số thứ tự cuối cùng
            parts = re.split(r'(\d{1,2}\.\s+)', topic)
            if len(parts) >= 3:
                topic = parts[-2] + parts[-1]
                
        results.append((topic, count))
        
    return results

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    topics_file = os.path.join(base_dir, 'prompt', 'Danh sách 50 chuyên đề với tổng 5,000 câu.md')
    master_prompt_file = os.path.join(base_dir, 'prompt', 'Master Prompt Sinh Dataset.md')
    output_dir = os.path.join(base_dir, 'prompt', 'generated_prompts')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(topics_file, 'r', encoding='utf-8') as f:
        topics_content = f.read()

    with open(master_prompt_file, 'r', encoding='utf-8') as f:
        master_prompt = f.read()

    # Chia làm 2 phần: Ngữ pháp (Part 1) và Phát âm (Part 2)
    parts = re.split(r'PHẦN 2:', topics_content)
    part1_text = parts[0]
    part2_text = parts[1] if len(parts) > 1 else ""

    part1_topics = parse_topics(part1_text)
    part2_topics = parse_topics(part2_text)

    all_prompts = []
    prompt_idx = 1

    # Tạo prompt cho phần 1 (Ngữ pháp)
    for topic, count in part1_topics:
        prompt = re.sub(
            r'# CHUYÊN ĐỀ CẦN TẠO:.*',
            f'# CHUYÊN ĐỀ CẦN TẠO: Ngữ pháp (Grammar Check) - {topic}\n# KỊCH BẢN: Kịch bản 1 (Grammar Check). Học viên viết một câu sai ngữ pháp tiếng Anh.',
            master_prompt
        )
        prompt = re.sub(
            r'Hãy tạo \d+ mẫu dữ liệu khác nhau cho chuyên đề trên.',
            f'Hãy tạo {count} mẫu dữ liệu khác nhau cho chuyên đề trên.',
            prompt
        )
        all_prompts.append((prompt_idx, topic, count, prompt))
        prompt_idx += 1

    # Tạo prompt cho phần 2 (Phát âm)
    for topic, count in part2_topics:
        prompt = re.sub(
            r'# CHUYÊN ĐỀ CẦN TẠO:.*',
            f'# CHUYÊN ĐỀ CẦN TẠO: Phát âm (Speaking Feedback) - {topic}\n# KỊCH BẢN: Kịch bản 2 (Speaking Feedback). Output cần có "Câu yêu cầu đọc", "Văn bản Whisper nghe được do học viên nuốt âm", và "Phản hồi của giáo viên".',
            master_prompt
        )
        prompt = re.sub(
            r'Hãy tạo \d+ mẫu dữ liệu khác nhau cho chuyên đề trên.',
            f'Hãy tạo {count} mẫu dữ liệu khác nhau cho chuyên đề trên.',
            prompt
        )
        all_prompts.append((prompt_idx, topic, count, prompt))
        prompt_idx += 1

    # Lưu tất cả vào 1 file text để dễ copy
    output_file = os.path.join(output_dir, 'all_50_prompts_for_chatgpt.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("BỘ PROMPT 50 CHUYÊN ĐỀ ĐỂ COPY VÀO CHATGPT\n")
        f.write("="*50 + "\n\n")
        
        for idx, topic, count, prompt_text in all_prompts:
            f.write(f"------------------------------------------------------------------------\n")
            f.write(f"PROMPT {idx}/50: {topic} ({count} câu)\n")
            f.write(f"------------------------------------------------------------------------\n\n")
            f.write(prompt_text)
            f.write("\n\n\n")

    # Lưu thành các file riêng lẻ
    individual_dir = os.path.join(output_dir, 'individual')
    if not os.path.exists(individual_dir):
        os.makedirs(individual_dir)
        
    for idx, topic, count, prompt_text in all_prompts:
        safe_topic = re.sub(r'[\\/*?:"<>|]', "", topic)
        # Lấy 50 ký tự đầu của topic name cho tên file
        file_name = f"{idx:02d}_{safe_topic[:50].strip()}.txt"
        file_path = os.path.join(individual_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(prompt_text)

    print(f"Đã tạo thành công {len(all_prompts)} prompts!")
    print(f"File gộp tất cả: {output_file}")
    print(f"Thư mục file lẻ: {individual_dir}")

if __name__ == '__main__':
    main()
