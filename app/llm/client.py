import os
from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.models import ToolSchema


class BaseLLMClient(ABC):
    """
    Abstract base class for all LLM clients.
    Provides shared fields and interface.
    """

    def __init__(self, api_key: Optional[str], url: str):
        if not api_key:
            raise ValueError("API key is required for LLM client")
        self.api_key = api_key
        self.url = url

    @abstractmethod
    async def generate_response(self, user_description: str, tools: List[ToolSchema]) -> str:
        """Send prompt and return raw LLM string output"""
        pass


def get_llm_client() -> BaseLLMClient:
    """Factory to return an LLM client implementation"""

    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from app.llm.gemini_client import GeminiClient
        return GeminiClient()

    raise NotImplementedError(f"LLM provider '{provider}' is not supported.")
