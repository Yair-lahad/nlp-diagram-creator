from app.agent.diagram_agent import handle_diagram_request


class RequestDispatcher:
    """
    Central dispatcher that routes requests to appropriate agent handlers.

    Acts as a bridge between the API layer and agent implementations,
    providing a clean way to add new agent types without modifying
    the core routing logic.
    """

    def __init__(self):
        # Map request types to their corresponding agent handlers
        # To add new agents: just add "agent_type": handler_function
        self.handlers = {
            "diagram": handle_diagram_request,
        }

    async def dispatch(self, request_type: str, data: str) -> str:
        """
        Route request to appropriate agent handler based on request type.

        Args:
            request_type: Type of request (e.g., "diagram", "code")
            data: Request data to pass to the agent handler      
        Returns:
            Result from the agent handler   
        Raises:
            ValueError: If request_type is not supported
        """
        # Look up handler for this request type
        handler = self.handlers.get(request_type)
        if not handler:
            raise ValueError(f"Unknown request type: {request_type}")

        # Call the handler and return result
        return await handler(data)


# Global dispatcher instance - used by API routes
dispatcher = RequestDispatcher()
