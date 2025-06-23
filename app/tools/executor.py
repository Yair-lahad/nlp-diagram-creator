async def execute_tool(tool_call: dict) -> str:
    # Dummy execution
    tool = tool_call.get("tool")
    args = tool_call.get("args", {})
    return f"[DUMMY] Called tool `{tool}` with args {args}"
