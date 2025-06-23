from app.llm.client import ask_llm
from app.tools.executor import execute_tool

async def handle_diagram_request(text: str) -> str:
    tool_call = await ask_llm(text)
    result = await execute_tool(tool_call)
    return result
