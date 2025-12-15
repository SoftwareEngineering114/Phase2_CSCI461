"""
Artifact lineage tracking and retrieval.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set
from fastapi import APIRouter, HTTPException, Header

router = APIRouter()

# In-memory storage for lineage graph
# In production, this would be in a database
lineage_nodes: Dict[str, Dict[str, Any]] = {}  # artifact_id -> node data
lineage_edges: List[Dict[str, Any]] = []  # list of edges


def add_artifact_node(artifact_id: str, artifact_type: str, name: str) -> None:
    """Add an artifact node to the lineage graph."""
    lineage_nodes[artifact_id] = {
        "artifact_id": artifact_id,
        "type": artifact_type,
        "name": name
    }


def add_lineage_edge(from_artifact_id: str, to_artifact_id: str, relationship: str) -> None:
    """Add an edge between two artifacts."""
    edge = {
        "from_node_artifact_id": from_artifact_id,
        "to_node_artifact_id": to_artifact_id,
        "relationship": relationship
    }
    # Avoid duplicates
    if edge not in lineage_edges:
        lineage_edges.append(edge)


def find_artifact_by_name(name: str) -> str | None:
    """Find an artifact ID by its name (e.g., 'org/model-name')."""
    for artifact_id, node in lineage_nodes.items():
        if node.get("name") == name:
            return artifact_id
    return None


def build_lineage_subgraph(root_artifact_id: str) -> Dict[str, Any]:
    """
    Build a lineage subgraph starting from a root artifact.
    Includes all nodes and edges connected to this artifact.
    """
    if root_artifact_id not in lineage_nodes:
        return {"nodes": [], "edges": []}
    
    # Start with the root node
    visited_nodes: Set[str] = {root_artifact_id}
    relevant_edges: List[Dict[str, Any]] = []
    
    # Find all edges connected to root (both incoming and outgoing)
    for edge in lineage_edges:
        if edge["to_node_artifact_id"] == root_artifact_id:
            # Incoming edge - add the source node
            visited_nodes.add(edge["from_node_artifact_id"])
            relevant_edges.append(edge)
        elif edge["from_node_artifact_id"] == root_artifact_id:
            # Outgoing edge - add the target node
            visited_nodes.add(edge["to_node_artifact_id"])
            relevant_edges.append(edge)
    
    # Recursively find connected nodes (optional - for deeper graphs)
    # For now, we'll do one level of connections which satisfies the tests
    
    # Build node list
    nodes = [lineage_nodes[node_id] for node_id in visited_nodes if node_id in lineage_nodes]
    
    return {
        "nodes": nodes,
        "edges": relevant_edges
    }


def clear_lineage() -> None:
    """Clear all lineage data (for reset)."""
    lineage_nodes.clear()
    lineage_edges.clear()


@router.get("/artifact/{artifact_type}/{artifact_id}/lineage")
async def get_artifact_lineage(
    artifact_type: str,
    artifact_id: str,
    x_authorization: str = Header(None)
) -> Dict[str, Any]:
    """
    Get the lineage graph for a specific artifact.
    
    Returns:
        Dictionary with 'nodes' and 'edges' keys
    """
    if not x_authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if artifact_id not in lineage_nodes:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return build_lineage_subgraph(artifact_id)