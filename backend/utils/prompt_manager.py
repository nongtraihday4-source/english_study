class PromptManager:
    """Quản lý tập trung các lời nhắc (Prompts) cho hệ thống English Study"""
    
    @staticmethod
    def get_grammar_prompt(student_text):
        system_instruction = (
            "Bạn là giáo viên Tiếng Anh chuyên sửa lỗi cho người Việt. "
            "Hãy phân tích câu của học viên, sửa lỗi và giải thích ngắn gọn bằng Tiếng Việt."
        )
        # Sử dụng cấu trúc Few-shot đa dạng hơn để tránh AI bị rập khuôn
        examples = [
            {"wrong": "She don't go", "right": "She doesn't go", "reason": "Chủ ngữ số ít."},
            {"wrong": "I am student", "right": "I am a student", "reason": "Thiếu mạo từ."},
            {"wrong": "In the weekend", "right": "At the weekend", "reason": "Dùng sai giới từ."}
        ]
        
        # Build prompt string
        return f"{system_instruction}\nInput: {student_text}"

    @staticmethod
    def get_ai_config(model_type="local"):
        """Trả về cấu hình tham số dựa trên loại mô hình"""
        if model_type == "local": # 1.5B
            return {
                "temperature": 0.05, # Cực thấp để ép AI bớt nói nhảm
                "top_p": 0.8,
                "num_predict": 256
            }
        else: # 7B hoặc Cloud
            return {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 512
            }
