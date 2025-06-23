"""
Diagram generation agent.

Specialized agent for creating infrastructure and architecture diagrams
from natural language descriptions using the diagrams Python package.
"""

from typing import List, Dict, Any
from app.agent.base_agent import BaseAgent


class DiagramAgent(BaseAgent):
    """Agent specialized for diagram generation"""
    
    def _register_tools(self) -> List[Dict]:
        """Register diagram-specific tools"""
        return [
            {
                "name": "create_node",
                "description": "Create a new node/component in the diagram",
                "parameters": {
                    "name": "Display name for the node",
                    "node_type": "Type of node (aws_ec2, aws_rds, aws_elb, etc.)",
                    "cluster": "Optional cluster/group name to group nodes"
                }
            },
            {
                "name": "connect_nodes", 
                "description": "Create connection between two nodes",
                "parameters": {
                    "from_node": "Source node name",
                    "to_node": "Target node name",
                    "label": "Optional connection label"
                }
            },
            {
                "name": "generate_diagram",
                "description": "Generate final diagram image from created nodes and connections", 
                "parameters": {
                    "title": "Diagram title",
                    "output_format": "Output format (png, svg, etc.)"
                }
            }
        ]
    
    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute diagram-specific tools"""
        
        # For now, return dummy responses - will implement real logic later
        if tool_name == "create_node":
            return f"Created node: {args.get('name')} ({args.get('node_type')})"
        
        elif tool_name == "connect_nodes":
            return f"Connected {args.get('from_node')} -> {args.get('to_node')}"
        
        elif tool_name == "generate_diagram":
            return f"Generated diagram: {args.get('title', 'Untitled')}.png"
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _format_final_result(self, results: List[Any]) -> str:
        """Format diagram generation results"""
        
        # If last result looks like a file path, return it
        if results and isinstance(results[-1], str) and results[-1].endswith(('.png', '.svg')):
            return results[-1]
        
        # Otherwise, return summary of actions
        return f"Diagram created with {len(results)} operations: " + " | ".join(map(str, results))


# Agent instance and handler function for backward compatibility
diagram_agent = DiagramAgent()

async def handle_diagram_request(description: str) -> str:
    """Handle diagram generation request (used by dispatcher)"""
    return await diagram_agent.process_request(description)