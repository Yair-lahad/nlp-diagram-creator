import os
import httpx
from app.llm.client import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Google Gemini implementation of the LLM client"""

    def __init__(self):
        super().__init__(
            api_key=os.getenv("GEMINI_API_KEY"),
            url="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        )

    async def generate_response(self, prompt: str) -> str:
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1000,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
