"""
FastAPI application entry point.

Async API service that generates diagrams using LLM agents.
Users describe diagrams in natural language and get back rendered images.
"""

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Diagram Agent API",
    description="Generate diagrams from natural language descriptions using LLM agents"
)

# Include API routes
app.include_router(router)