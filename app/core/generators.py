"""
Core generation engines.

Handles the execution of parsed tool calls and coordination of diagram generation.
"""

from app.core.models import LLMResponse
from app.core.tools import DiagramTools


class DiagramGenerator:
    """Diagram generator - builds diagram data in memory for each request"""

    def __init__(self):
        self.tools = DiagramTools()

    async def generate_diagram(self, llm_response: LLMResponse) -> str:
        """Generate diagram from parsed LLM response"""

        # Build diagram data in memory for this request only
        nodes = []
        connections = []
        title = "Infrastructure Diagram"

        # Process tool calls to build diagram data
        for tool_call in llm_response.tool_calls:
            if tool_call.tool == "create_node":
                node = self.tools.create_node(**tool_call.args)
                nodes.append(node)

            elif tool_call.tool == "connect_nodes":
                connection = self.tools.connect_nodes(**tool_call.args)
                connections.append(connection)

            elif tool_call.tool == "render_diagram":
                title = tool_call.args.get("title", title)

        # Render diagram with collected data
        if not nodes:
            raise ValueError("No nodes created")

        return self.tools.render_diagram(nodes, connections, title)
