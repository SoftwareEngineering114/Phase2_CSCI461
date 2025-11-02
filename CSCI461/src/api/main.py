"""
FastAPI application for the Trustworthy Model Registry API.

TODO: These endpoints are stubs for our "trustworthy model registry" MVP.
      They will be expanded with full functionality in future iterations.
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

# Create FastAPI app instance
app = FastAPI(
    title="Trustworthy Model Registry API",
    description="API for registering and querying trustworthy ML models",
    version="0.1.0"
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status and message indicating the registry is running
    """
    return {
        "status": "ok",
        "message": "registry is running"
    }


@app.get("/models")
async def list_models() -> dict[str, str | list]:
    """
    List all registered models.
    
    TODO: Implement actual model storage and retrieval.
    
    Returns:
        Dictionary with models list and note
    """
    return {
        "models": [],
        "note": "placeholder"
    }


class RegisterRequest(BaseModel):
    """Request model for registering a new model."""
    name: str
    repo_url: str
    owner: str


@app.post("/register")
async def register_model(request: RegisterRequest) -> dict[str, str]:
    """
    Register a new model in the registry.
    
    TODO: Implement actual model registration and storage.
    
    Args:
        request: Registration request with name, repo_url, and owner
        
    Returns:
        The posted data back (as confirmation)
    """
    return {
        "name": request.name,
        "repo_url": request.repo_url,
        "owner": request.owner
    }

