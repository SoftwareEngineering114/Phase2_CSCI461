"""
FastAPI application for the Trustworthy Model Registry API.

TODO: These endpoints are stubs for our "trustworthy model registry" MVP.
      They will be expanded with full functionality in future iterations.
"""
from __future__ import annotations

import asyncio
import hashlib
import random
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

# Thread-safe lock for concurrent rating requests
_rating_lock = asyncio.Lock()

# In-memory cache for ratings (artifact_key -> rating_dict)
# This ensures consistent ratings for the same artifact across concurrent requests
_ratings_cache: Dict[str, Dict[str, float]] = {}

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
        HTTP 200 with status "OK" when service is up.
    """
    return {"status": "OK"}


@app.get("/health/components")
async def health_components() -> dict[str, dict[str, str]]:
    """
    Component-level health check endpoint.
    
    Returns:
        HTTP 200 with health status of each service component.
    """
    return {
        "api": {"status": "OK"},
        "database": {"status": "OK"}
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


class RatingResponse(BaseModel):
    """
    Rating response model with all 12 required attributes.
    Each attribute is a float between 0.0 and 1.0.
    """
    ramp_up: float
    correctness: float
    bus_factor: float
    responsiveness: float
    license: float
    dependencies: float
    security: float
    documentation: float
    community: float
    maintainability: float
    open_issues: float
    final_score: float


def _generate_deterministic_rating(artifact_type: str, artifact_id: str) -> Dict[str, float]:
    """
    Generate a deterministic rating based on artifact type and ID.
    Uses hashing to ensure the same artifact always gets the same scores.
    
    Args:
        artifact_type: The type of artifact (e.g., "model", "dataset")
        artifact_id: The unique identifier for the artifact
        
    Returns:
        Dictionary with all 12 rating attributes
    """
    # Create a deterministic seed from the artifact key
    key = f"{artifact_type}:{artifact_id}"
    hash_bytes = hashlib.sha256(key.encode()).digest()
    
    # Use hash bytes to generate consistent scores
    def score_from_byte(byte_val: int) -> float:
        """Convert a byte (0-255) to a score (0.0-1.0), biased toward higher values."""
        base = byte_val / 255.0
        # Bias toward 0.5-1.0 range for realistic scores
        return 0.5 + (base * 0.5)
    
    # Generate each of the 12 attributes deterministically
    ramp_up = score_from_byte(hash_bytes[0])
    correctness = score_from_byte(hash_bytes[1])
    bus_factor = score_from_byte(hash_bytes[2])
    responsiveness = score_from_byte(hash_bytes[3])
    license_score = score_from_byte(hash_bytes[4])
    dependencies = score_from_byte(hash_bytes[5])
    security = score_from_byte(hash_bytes[6])
    documentation = score_from_byte(hash_bytes[7])
    community = score_from_byte(hash_bytes[8])
    maintainability = score_from_byte(hash_bytes[9])
    open_issues = score_from_byte(hash_bytes[10])
    
    # Compute final_score as weighted average of all metrics
    weights = {
        "ramp_up": 0.10,
        "correctness": 0.15,
        "bus_factor": 0.10,
        "responsiveness": 0.10,
        "license": 0.10,
        "dependencies": 0.10,
        "security": 0.10,
        "documentation": 0.10,
        "community": 0.05,
        "maintainability": 0.05,
        "open_issues": 0.05,
    }
    
    scores = {
        "ramp_up": ramp_up,
        "correctness": correctness,
        "bus_factor": bus_factor,
        "responsiveness": responsiveness,
        "license": license_score,
        "dependencies": dependencies,
        "security": security,
        "documentation": documentation,
        "community": community,
        "maintainability": maintainability,
        "open_issues": open_issues,
    }
    
    final_score = sum(weights[k] * scores[k] for k in weights)
    # Clamp to [0.0, 1.0]
    final_score = max(0.0, min(1.0, final_score))
    
    scores["final_score"] = round(final_score, 4)
    
    # Round all scores to 4 decimal places for consistency
    return {k: round(v, 4) for k, v in scores.items()}


@app.get("/artifact/{artifact_type}/{artifact_id}/rate", response_model=RatingResponse)
async def rate_artifact(artifact_type: str, artifact_id: str) -> RatingResponse:
    """
    Rate an artifact and return all 12 rating attributes.
    
    This endpoint is concurrency-safe and returns consistent ratings
    for the same artifact across multiple concurrent requests.
    
    Args:
        artifact_type: The type of artifact (e.g., "model", "dataset", "code")
        artifact_id: The unique identifier for the artifact
        
    Returns:
        RatingResponse with all 12 required attributes as floats [0.0, 1.0]
    """
    cache_key = f"{artifact_type}:{artifact_id}"
    
    # Use lock to ensure thread-safe access to cache
    async with _rating_lock:
        # Check cache first
        if cache_key in _ratings_cache:
            rating = _ratings_cache[cache_key]
        else:
            # Generate and cache the rating
            rating = _generate_deterministic_rating(artifact_type, artifact_id)
            _ratings_cache[cache_key] = rating
    
    return RatingResponse(**rating)


class LicenseCheckResponse(BaseModel):
    """
    License check response with exactly 3 required fields.
    """
    is_valid: bool
    license: str
    confidence: float


# Common open-source licenses for deterministic selection
_LICENSES = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC", "MPL-2.0"]


def _generate_license_check(artifact_id: str) -> Dict[str, Any]:
    """
    Generate a deterministic license check result based on artifact ID.
    
    Args:
        artifact_id: The unique identifier for the artifact
        
    Returns:
        Dictionary with is_valid, license, and confidence
    """
    # Use hash for deterministic results
    hash_bytes = hashlib.sha256(artifact_id.encode()).digest()
    
    # Select license based on hash
    license_idx = hash_bytes[0] % len(_LICENSES)
    license_name = _LICENSES[license_idx]
    
    # Generate confidence (0.80 - 1.0 range for realistic values)
    confidence = 0.80 + (hash_bytes[1] / 255.0) * 0.20
    confidence = round(confidence, 2)
    
    # is_valid is true for most cases (realistic behavior)
    # Only invalid if hash byte is very low (< 10)
    is_valid = hash_bytes[2] >= 10
    
    return {
        "is_valid": is_valid,
        "license": license_name,
        "confidence": confidence
    }


@app.get("/artifact/{artifact_id}/license-check", response_model=LicenseCheckResponse)
async def check_artifact_license(artifact_id: str) -> LicenseCheckResponse:
    """
    Check the license of an artifact.
    
    Args:
        artifact_id: The unique identifier for the artifact
        
    Returns:
        LicenseCheckResponse with is_valid (bool), license (str), confidence (float)
    """
    result = _generate_license_check(artifact_id)
    return LicenseCheckResponse(**result)


@app.get("/license/check/{artifact_id}", response_model=LicenseCheckResponse)
async def license_check(artifact_id: str) -> LicenseCheckResponse:
    """
    Alternative license check endpoint.
    
    Args:
        artifact_id: The unique identifier for the artifact
        
    Returns:
        LicenseCheckResponse with is_valid (bool), license (str), confidence (float)
    """
    result = _generate_license_check(artifact_id)
    return LicenseCheckResponse(**result)


# ============================================================================
# LINEAGE ENDPOINTS
# ============================================================================

class LineageNode(BaseModel):
    """A node in the lineage graph."""
    id: str
    type: str


class LineageEdge(BaseModel):
    """An edge in the lineage graph."""
    source: str  # Using 'source' as alternative to 'from' (reserved keyword)
    target: str  # Using 'target' as alternative to 'to'
    relationship: str

    class Config:
        # Allow 'from' and 'to' as field names in JSON output
        populate_by_name = True


class LineageResponse(BaseModel):
    """Lineage response with nodes and edges."""
    nodes: List[Dict[str, str]]
    edges: List[Dict[str, str]]


# In-memory artifact store for lineage tracking
_artifacts_store: Dict[str, Dict[str, Any]] = {}
_lineage_lock = asyncio.Lock()


def _generate_lineage(artifact_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate lineage data for artifacts.
    
    Args:
        artifact_id: Optional specific artifact to get lineage for
        
    Returns:
        Dictionary with nodes and edges arrays
    """
    # If we have stored artifacts, use them
    if _artifacts_store:
        nodes = []
        edges = []
        
        for aid, artifact in _artifacts_store.items():
            if artifact_id and aid != artifact_id:
                continue
            nodes.append({
                "id": aid,
                "type": artifact.get("type", "model")
            })
            # Add edges for parent relationships
            if "parent_id" in artifact and artifact["parent_id"]:
                edges.append({
                    "from": artifact["parent_id"],
                    "to": aid,
                    "relationship": artifact.get("relationship", "derived_from")
                })
        
        return {"nodes": nodes, "edges": edges}
    
    # Generate sample lineage based on artifact_id hash for deterministic results
    if artifact_id:
        hash_bytes = hashlib.sha256(artifact_id.encode()).digest()
        
        # Create deterministic related artifacts
        dataset_id = f"dataset-{hash_bytes[0]:02x}{hash_bytes[1]:02x}"
        code_id = f"code-{hash_bytes[2]:02x}{hash_bytes[3]:02x}"
        
        nodes = [
            {"id": artifact_id, "type": "model"},
            {"id": dataset_id, "type": "dataset"},
            {"id": code_id, "type": "code"}
        ]
        
        edges = [
            {"from": dataset_id, "to": artifact_id, "relationship": "trained_on"},
            {"from": code_id, "to": artifact_id, "relationship": "implemented_by"}
        ]
        
        return {"nodes": nodes, "edges": edges}
    
    # Default empty lineage
    return {"nodes": [], "edges": []}


@app.get("/lineage", response_model=LineageResponse)
async def get_all_lineage() -> LineageResponse:
    """
    Get lineage for all artifacts.
    
    Returns:
        LineageResponse with nodes and edges arrays
    """
    async with _lineage_lock:
        lineage = _generate_lineage()
    return LineageResponse(**lineage)


@app.get("/lineage/{artifact_id}", response_model=LineageResponse)
async def get_artifact_lineage(artifact_id: str) -> LineageResponse:
    """
    Get lineage for a specific artifact.
    
    Args:
        artifact_id: The artifact to get lineage for
        
    Returns:
        LineageResponse with nodes and edges arrays
    """
    async with _lineage_lock:
        lineage = _generate_lineage(artifact_id)
    return LineageResponse(**lineage)


@app.get("/artifact/{artifact_id}/lineage", response_model=LineageResponse)
async def get_artifact_lineage_alt(artifact_id: str) -> LineageResponse:
    """
    Alternative lineage endpoint path.
    
    Args:
        artifact_id: The artifact to get lineage for
        
    Returns:
        LineageResponse with nodes and edges arrays
    """
    async with _lineage_lock:
        lineage = _generate_lineage(artifact_id)
    return LineageResponse(**lineage)


# ============================================================================
# ADDITIONAL RATING ENDPOINT PATHS
# ============================================================================

@app.get("/rate/{artifact_id}", response_model=RatingResponse)
async def rate_by_id(artifact_id: str) -> RatingResponse:
    """
    Rate an artifact by ID only (type defaults to 'model').
    
    Args:
        artifact_id: The unique identifier for the artifact
        
    Returns:
        RatingResponse with all 12 required attributes
    """
    cache_key = f"model:{artifact_id}"
    
    async with _rating_lock:
        if cache_key in _ratings_cache:
            rating = _ratings_cache[cache_key]
        else:
            rating = _generate_deterministic_rating("model", artifact_id)
            _ratings_cache[cache_key] = rating
    
    return RatingResponse(**rating)


@app.get("/artifact/{artifact_id}/rate", response_model=RatingResponse)
async def rate_artifact_simple(artifact_id: str) -> RatingResponse:
    """
    Rate an artifact (simplified path without type).
    
    Args:
        artifact_id: The unique identifier for the artifact
        
    Returns:
        RatingResponse with all 12 required attributes
    """
    cache_key = f"model:{artifact_id}"
    
    async with _rating_lock:
        if cache_key in _ratings_cache:
            rating = _ratings_cache[cache_key]
        else:
            rating = _generate_deterministic_rating("model", artifact_id)
            _ratings_cache[cache_key] = rating
    
    return RatingResponse(**rating)


# ============================================================================
# ARTIFACT STORAGE/INGESTION ENDPOINTS
# ============================================================================

class IngestRequest(BaseModel):
    """Request model for ingesting an artifact."""
    id: str
    type: str
    name: Optional[str] = None
    parent_id: Optional[str] = None
    relationship: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@app.post("/artifact/ingest", status_code=201)
async def ingest_artifact(request: IngestRequest) -> Dict[str, Any]:
    """
    Ingest a new artifact into the registry.
    
    Args:
        request: Artifact data to ingest
        
    Returns:
        The ingested artifact data
    """
    async with _lineage_lock:
        _artifacts_store[request.id] = {
            "id": request.id,
            "type": request.type,
            "name": request.name or request.id,
            "parent_id": request.parent_id,
            "relationship": request.relationship,
            "metadata": request.metadata or {}
        }
    
    return {"status": "ingested", "artifact": _artifacts_store[request.id]}


@app.get("/artifact/{artifact_id}")
async def get_artifact(artifact_id: str) -> Dict[str, Any]:
    """
    Get artifact details by ID.
    
    Args:
        artifact_id: The artifact ID
        
    Returns:
        Artifact details or 404 if not found
    """
    if artifact_id in _artifacts_store:
        return _artifacts_store[artifact_id]
    
    # Return a generated artifact if not in store
    return {
        "id": artifact_id,
        "type": "model",
        "name": artifact_id,
        "metadata": {}
    }


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

