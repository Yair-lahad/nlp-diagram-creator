"""
Diagram generation agent.

Uses the structured core system for clean separation of concerns.
Agent orchestrates the flow but doesn't implement the logic itself.
"""

from app.agent.base_agent import BaseAgent
from app.core.models import DiagramPromptTemplate, DIAGRAM_TOOLS
from app.core.parsers import LLMOutputParser
from app.core.generators import DiagramGenerator
from app.llm.gemini_client import GeminiClient
from fastapi.responses import FileResponse


class DiagramAgent(BaseAgent):
    """Agent for diagram generation using structured core system"""

    def __init__(self):
        self.llm_client = GeminiClient()
        self.parser = LLMOutputParser()
        self.generator = DiagramGenerator()
        self.tools = DIAGRAM_TOOLS

    async def process_request(self, user_input: str) -> str:
        """
        Process diagram request through structured pipeline.

        Flow: user_input → prompt → LLM → parse → generate → result
        """
        try:
            # Agent builds prompt using tool schema
            prompt = DiagramPromptTemplate.build_prompt(user_input, self.tools)
            # LLM Client just sends the prompt, nothing more
            raw_response = await self.llm_client.generate_response(prompt)
            # Agent parses raw LLM output
            parsed_response = self.parser.parse_tool_calls(raw_response)
            # Agent executes generator
            result_path = await self.generator.generate_diagram(parsed_response)

            return FileResponse(
                path=result_path,
                media_type="image/png",
                filename="diagram.png"
            )
        except Exception as e:
            # Optional: wrap in JSON response or raise HTTPException
            return {"error": str(e)}


# Agent instance and handler function for backward compatibility
diagram_agent = DiagramAgent()


async def handle_diagram_request(description: str) -> str:
    """Handle diagram generation request (used by dispatcher)"""
    return await diagram_agent.process_request(description)
