"""
Core models and prompt templates.

Contains all data models, prompt templates, and schemas used across
the application. Keeps prompts centralized and reusable.
"""

from pydantic import BaseModel
from dataclasses import dataclass
from typing import List, Dict, Any


# =============================================================================
# API Models
# =============================================================================

class DiagramRequest(BaseModel):
    """Request for diagram generation"""
    description: str


# =============================================================================
# Domain Models
# =============================================================================

@dataclass
class Node:
    name: str
    node_type: str
    cluster: str = None


@dataclass 
class Connection:
    from_node: str
    to_node: str


# =============================================================================
# LLM Models
# =============================================================================

class ToolSchema(BaseModel):
    """Schema for tool definitions"""
    name: str
    description: str
    parameters: Dict[str, str]


class ToolCall(BaseModel):
    """Single tool call from LLM"""
    tool: str
    args: Dict[str, Any]


class LLMResponse(BaseModel):
    """Parsed LLM response containing tool calls"""
    tool_calls: List[ToolCall]


# =============================================================================
# Tool Definitions
# =============================================================================

DIAGRAM_TOOLS = [
    ToolSchema(
        name="create_node",
        description="Create a node/component in the diagram",
        parameters={
            "name": "Display name for the node",
            "node_type": "Type of node (ec2, rds, elb)",
            "cluster": "Optional cluster/group name"
        }
    ),
    ToolSchema(
        name="connect_nodes",
        description="Create a connection between two nodes",
        parameters={
            "from_node": "Source node name",
            "to_node": "Target node name"
        }
    ),
    ToolSchema(
        name="render_diagram",
        description="Generate the final diagram image",
        parameters={
            "title": "Diagram title"
        }
    )
]


# =============================================================================
# Prompt Templates
# =============================================================================

class DiagramPromptTemplate:
    """Prompt template for diagram generation"""
    
    SYSTEM_PROMPT = """You are a diagram generation assistant. Your job is to analyze user requests and generate appropriate tool calls to create infrastructure diagrams.

IMPORTANT RULES:
1. You must ONLY use the tools provided below
2. Do NOT reference Python code, diagrams package, or any implementation details  
3. Think in terms of infrastructure components and their relationships
4. Generate tool calls in logical order: nodes first, then connections, then render

Available tools:
{tools_description}

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

Return ONLY valid JSON, no other text or markdown formatting."""

    @classmethod
    def build_prompt(cls, user_description: str, tools: List[ToolSchema]) -> str:
        """Build complete prompt from template"""
        
        # Format tools description
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}\n  Parameters: {tool.parameters}"
            for tool in tools
        ])
        
        # Build final prompt
        prompt = cls.SYSTEM_PROMPT.format(tools_description=tools_desc)
        prompt += f"\n\nUser request: {user_description}"
        
        return prompt