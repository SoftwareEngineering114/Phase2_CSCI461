"""
FastAPI application for the Trustworthy Model Registry API.

TODO: These endpoints are stubs for our "trustworthy model registry" MVP.
      They will be expanded with full functionality in future iterations.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

# Create FastAPI app instance
app = FastAPI(
    title="Trustworthy Model Registry API",
    description="API for registering and querying trustworthy ML models",
    version="0.1.0"
)

# Serve frontend HTML at root
@app.get("/", response_class=HTMLResponse)
async def frontend():
    """Serve the frontend HTML page."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trustworthy Model Registry</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .endpoint {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
        }
        .endpoint code {
            display: block;
            margin-top: 5px;
            padding: 5px;
            background-color: #e9ecef;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Trustworthy Model Registry</h1>
        <div class="status success">
            ✅ Frontend service is running
        </div>
        
        <p>This is the frontend interface for the Trustworthy Model Registry API.</p>
        
        <div class="endpoint">
            <strong>Health Check Endpoint:</strong>
            <code>/health</code>
        </div>
        
        <div class="endpoint">
            <strong>Models List Endpoint:</strong>
            <code>/models</code>
        </div>
        
        <div class="endpoint">
            <strong>Register Endpoint:</strong>
            <code>/register</code>
        </div>
        
        <p><em>Note: Full API functionality will be implemented in future iterations.</em></p>
    </div>
</body>
</html>
    """
    return html_content


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

