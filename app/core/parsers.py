"""
Core parsing utilities.

Handles parsing and validation of LLM outputs, converting them into
structured data that can be processed by the tools.
"""

import json
from typing import List, Dict, Any
from app.core.models import LLMResponse, ToolCall


class LLMOutputParser:
    """Parser for LLM responses containing tool calls"""

    @staticmethod
    def parse_tool_calls(raw_response: str) -> LLMResponse:
        """
        Parse tool calls from LLM response text.
        Args:
            raw_response: Raw text response from LLM  
        Returns:
            Structured LLMResponse with parsed tool calls   
        Raises:
            ValueError: If response format is invalid
        """
        try:
            # Clean up response (remove markdown, extra whitespace)
            cleaned = LLMOutputParser._clean_response(raw_response)
            # Parse JSON
            parsed_data = json.loads(cleaned)
            # Validate structure
            if not isinstance(parsed_data, list):
                raise ValueError("Response must be a JSON array of tool calls")
            # Convert to ToolCall objects
            tool_calls = []
            for item in parsed_data:
                if not isinstance(item, dict):
                    raise ValueError("Each tool call must be a JSON object")
                if "tool" not in item:
                    raise ValueError("Each tool call must have a 'tool' field")
                tool_call = ToolCall(
                    tool=item["tool"],
                    args=item.get("args", {})
                )
                tool_calls.append(tool_call)
            return LLMResponse(tool_calls=tool_calls)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in LLM response: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {e}")

    @staticmethod
    def _clean_response(response: str) -> str:
        """Clean up LLM response text"""
        # Remove leading/trailing whitespace
        cleaned = response.strip()
        # Remove markdown code blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        # Remove any text before first [ or after last ]
        start_idx = cleaned.find('[')
        end_idx = cleaned.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]
        return cleaned.strip()

    @staticmethod
    def validate_tool_call(tool_call: ToolCall, available_tools: List[str]) -> bool:
        """
        Validate that a tool call uses an available tool.
        Args:
            tool_call: Tool call to validate
            available_tools: List of available tool names
        Returns:
            True if valid, False otherwise
        """
        return tool_call.tool in available_tools
