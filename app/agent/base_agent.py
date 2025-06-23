"""
Base agent class for all AI agents.

Provides a shared interface for agent implementations.
Agents must implement the request handling flow and optionally their own tool and LLM logic.
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    @abstractmethod
    async def process_request(self, user_input: str):
        """
        Process user request through the agent pipeline.

        Args:
            user_input: Natural language user request

        Returns:
            Final result (e.g., file response, text, or structured data)
        """
        pass
