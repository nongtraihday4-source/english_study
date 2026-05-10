from django.conf import settings
from openai import OpenAI, APITimeoutError
import json


class QwenClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=getattr(settings, "AI_BASE_URL", "http://localhost:11434/v1"),
            api_key=getattr(settings, "AI_API_KEY", "ollama"),
            timeout=15.0,
        )
        self.model = getattr(settings, "AI_MODEL", "qwen3.5-9b")

    def generate_json(self, messages: list) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1024,
        )
        return json.loads(response.choices[0].message.content)