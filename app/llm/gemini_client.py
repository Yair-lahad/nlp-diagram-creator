"""
Gemini LLM client for diagram generation.

Handles communication with Google's Gemini API to process natural language
diagram descriptions and generate tool calls.
"""

import json
import os
from typing import Dict, List, Any
import httpx


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-flash"
    
    async def generate_tool_calls(self, user_description: str, available_tools: List[Dict]) -> List[Dict]:
        """
        Generate tool calls from user description using Gemini.
        
        Args:
            user_description: Natural language description of desired diagram
            available_tools: List of available tool schemas
            
        Returns:
            List of tool calls to execute
        """
        
        # Build system prompt with available tools
        system_prompt = self._build_system_prompt(available_tools)
        
        # Prepare request payload
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\nUser request: {user_description}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1000,
            }
        }
        
        # Make API call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Extract and parse tool calls from response
            return self._parse_tool_calls(result)
    
    def _build_system_prompt(self, available_tools: List[Dict]) -> str:
        """Build system prompt with tool definitions"""
        
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in available_tools
        ])
        
        return f"""You are a diagram generation assistant. Your job is to analyze user requests and generate appropriate tool calls to create diagrams.

Available tools:
{tools_desc}

You must respond with a JSON array of tool calls in this exact format:
[
  {{
    "tool": "tool_name",
    "args": {{
      "param1": "value1",
      "param2": "value2"
    }}
  }}
]

Rules:
- Only use the available tools listed above
- Generate tool calls in logical order (nodes first, then connections)
- Use descriptive names for diagram elements
- Return valid JSON only, no other text"""
    
    def _parse_tool_calls(self, gemini_response: Dict) -> List[Dict]:
        """Parse tool calls from Gemini response"""
        
        try:
            # Extract text from Gemini response
            content = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
            
            # Find JSON in the response (handle potential markdown formatting)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            tool_calls = json.loads(content)
            
            # Validate format
            if not isinstance(tool_calls, list):
                raise ValueError("Tool calls must be a list")
            
            for call in tool_calls:
                if not isinstance(call, dict) or "tool" not in call:
                    raise ValueError("Invalid tool call format")
            
            return tool_calls
            
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            raise Exception(f"Failed to parse tool calls from Gemini response: {e}")


# Global client instance
gemini_client = GeminiClient()