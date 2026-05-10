# Qwen3.5-9B Deployment Guide

## Option A: Ollama (Recommended)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama server
ollama serve

# 3. Pull Qwen3.5-9B model (first run only)
ollama pull hf.co/unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL

# 4. Verify server
curl http://localhost:11434/v1/models
# Expected: {"object":"list","data":[{"id":"hf.co/unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL",...}]}

# 5. Test completion
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"hf.co/unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL","messages":[{"role":"user","content":"Hello"}]}'
```

## Option B: llama-cpp-python

```bash
pip install llama-cpp-python

python << 'EOF'
from llama_cpp import Llama
llm = Llama.from_pretrained(
    repo_id="unsloth/Qwen3.5-9B-GGUF",
    filename="Qwen3.5-9B-Q4_K_M.gguf",
    n_ctx=4096
)
print(llm.create_chat_completion(messages=[{"role":"user","content":"Hello"}]))
EOF
```

## Verify Celery AI Queue

```bash
# Start Celery worker for AI queue
celery -A english_study worker -l info -Q ai_grading -c 2

# Test task from Django shell
python manage.py shell << 'EOF'
from apps.ai.tasks import grade_submission_task
result = grade_submission_task.delay(99, "writing", "Test text", "")
print(result.get(timeout=60))
EOF
```

## Environment Variables

```bash
# .env
AI_BASE_URL=http://localhost:11434/v1
AI_MODEL=Qwen3.5-9B
```
