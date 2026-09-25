import requests

from app.config import OLLAMA_MODEL
from app.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        base_url: str = "http://127.0.0.1:11434",
    ):
        self.model = model
        self.base_url = base_url

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        prompt = (
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            f"USER REQUEST:\n{user_prompt}\n\n"
            "Provide a concise and helpful support response."
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 512,
                "num_predict": 64,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()
        return data["response"]
