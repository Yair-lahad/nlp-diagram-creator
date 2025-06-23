from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agent.diagram_agent import handle_diagram_request

router = APIRouter()

class DiagramRequest(BaseModel):
    description: str

@router.post("/")
async def create_diagram(request: DiagramRequest):
    try:
        result = await handle_diagram_request(request.description)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
