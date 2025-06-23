"""
Base agent class for all AI agents.

Provides common functionality for agent implementations including
LLM interaction, tool management, and error handling.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.llm.gemini_client import gemini_client


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self):
        self.llm_client = gemini_client
        self._tools = self._register_tools()
    
    @abstractmethod
    def _register_tools(self) -> List[Dict]:
        """
        Register available tools for this agent.
        
        Returns:
            List of tool schemas with name, description, and parameters
        """
        pass
    
    @abstractmethod
    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a specific tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
            
        Returns:
            Tool execution result
        """
        pass
    
    async def process_request(self, user_input: str) -> str:
        """
        Process user request through the agent pipeline.
        
        Args:
            user_input: Natural language user request
            
        Returns:
            Final result (e.g., image path, response text)
        """
        try:
            # Generate tool calls using LLM
            tool_calls = await self.llm_client.generate_tool_calls(
                user_input, 
                self._tools
            )
            
            # Execute tool calls sequentially
            results = []
            for tool_call in tool_calls:
                result = await self._execute_tool(
                    tool_call["tool"], 
                    tool_call.get("args", {})
                )
                results.append(result)
            
            # Return final result (last tool result or combined)
            return self._format_final_result(results)
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def _format_final_result(self, results: List[Any]) -> str:
        """
        Format the final result from tool executions.
        
        Can be overridden by specific agents for custom formatting.
        """
        if not results:
            return "No results generated"
        
        # Return last result by default (usually the final output)
        return str(results[-1])