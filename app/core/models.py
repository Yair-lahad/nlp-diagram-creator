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

NODE_MAPPINGS = {
    "ec2": ("diagrams.aws.compute", "EC2"),
    "rds": ("diagrams.aws.database", "RDS"),
    "elb": ("diagrams.aws.network", "ELB"),
    "api_gateway": ("diagrams.aws.network", "APIGateway"),
    "sqs": ("diagrams.aws.integration", "SQS"),
    "cloudwatch": ("diagrams.aws.management", "Cloudwatch")
}


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
5. Do not add extra terms like 'Architecture' or 'Diagram' unless they appear in the user's specific title request.
6. Use only the following node_type values: ec2, rds, elb, api_gateway, sqs, cloudwatch.
   Do not invent types like 'microservice', 'service', 'architecture', etc.
   Use names like 'Microservices' only as cluster names (not as node_type).
7. Avoid clutter by limiting non-essential connections.
   However, if a pattern is implied (e.g., multiple services using monitoring or messaging),
   do not exclude similar nodes unless the user makes it explicit.
8. Apply connection patterns consistently to all nodes in the same role.
   If one service connects to a database, message queue, or monitoring node,
   assume other peer services do the same unless stated otherwise.
9. If a utility node (e.g., monitoring, logging, messaging) is included, ensure it is used at least once in the architecture.
Do not leave such nodes unconnected.

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

Return ONLY valid JSON. Make sure:
- All strings use standard double quotes
- All braces/brackets are closed
- No trailing commas
- The entire response is a valid JSON array"""

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
