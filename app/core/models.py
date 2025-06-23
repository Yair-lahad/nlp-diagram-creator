from pydantic import BaseModel
from typing import Literal


class BaseRequest(BaseModel):
    """Base request model for all agent requests"""
    request_type: str


class DiagramRequest(BaseRequest):
    """Request for diagram generation"""
    request_type: Literal["diagram"] = "diagram"
    description: str