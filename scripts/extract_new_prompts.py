import os
import re

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_prompts_file = os.path.join(base_dir, 'prompt', 'generated_prompts', 'all_50_prompts_for_chatgpt.txt')
    individual_dir = os.path.join(base_dir, 'prompt', 'generated_prompts', 'individual')

    if not os.path.exists(individual_dir):
        os.makedirs(individual_dir)

    with open(all_prompts_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex pattern to match the prompt headers
    # Example: 
    # ------------------------------------------------------------------------
    # PROMPT 51/66: Lỗi dịch Word-by-Word động từ sinh hoạt (100 câu)
    # ------------------------------------------------------------------------
    pattern = r'-{72}\nPROMPT\s+(\d+)/\d+:\s*(.*?)\s*\(\d+\s*câu\)\n-{72}\n'
    
    # Use re.finditer to find all matches and their positions
    matches = list(re.finditer(pattern, content))
    
    for i, match in enumerate(matches):
        prompt_idx = int(match.group(1))
        topic = match.group(2)
        
        # Get the text for this prompt
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        prompt_text = content[start_idx:end_idx].strip()
        
        if 51 <= prompt_idx <= 66:
            safe_topic = re.sub(r'[\\/*?:"<>|]', "", topic)
            file_name = f"{prompt_idx:02d}_{safe_topic[:50].strip()}.txt"
            file_path = os.path.join(individual_dir, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as out_f:
                out_f.write(prompt_text + '\n')
            
            print(f"Created: {file_name}")

if __name__ == '__main__':
    main()
