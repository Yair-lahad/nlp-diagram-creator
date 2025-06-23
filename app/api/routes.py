"""
API routes for diagram generation.

Handles incoming HTTP requests and routes them through the dispatcher
to appropriate agent handlers.
"""

from fastapi import APIRouter, HTTPException
from app.core.models import DiagramRequest
from app.core.dispatcher import dispatcher

router = APIRouter()


@router.post("/diagram")
async def create_diagram(request: DiagramRequest):
    """
    Generate diagram from natural language description.

    Takes a text description and returns a diagram image through
    the LLM agent pipeline.
    """
    try:
        result = await dispatcher.dispatch("diagram", request.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
