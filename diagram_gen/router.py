import json
import asyncio
import os
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Dict, Any

from auth.dependencies import get_current_user, get_active_user
from auth.models import User
from db.database import get_db
from diagram_gen.schemas import DiagramGenRequest, DiagramType, FileContent
from diagram_gen.service import DiagramGenerator

router = APIRouter(prefix="/diagrams", tags=["Diagram Generation"])

@router.post("/generate", response_model=Dict[str, Any])
async def generate_diagram(
    request: DiagramGenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a diagram based on file contents.
    
    You can specify one of the following diagram types:
    - architecture: System architecture diagram showing components and their interactions
    - activity: Activity diagram showing process flow with actions and decisions
    - schema: Database schema diagram showing entities and relationships
    - user_flow: User flow diagram showing screens and interactions
    - workflow: Business workflow diagram showing process steps and actors
    
    Each diagram type returns a different structured response optimized for rendering by the frontend.
    """
    try:
        # Create diagram generator instance
        diagram_generator = DiagramGenerator()
        
        # Generate diagram using the service
        diagram_json = await diagram_generator.generate_diagram(
            files=request.files,
            diagram_type=request.diagram_type,
            description=request.description
        )
        
        # Parse JSON response - handle potential JSON-in-string issues
        try:
            # First try to parse as JSON directly
            response_data = json.loads(diagram_json)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from text
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', diagram_json)
            if json_match:
                response_data = json.loads(json_match.group(1))
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not parse diagram JSON from response"
                )
        
        # Create response with diagram type
        response = {
            "diagram_type": request.diagram_type,
            "data": response_data
        }
        
        return response
        
    except Exception as e:
        # Log the error properly in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating diagram: {str(e)}"
        )

@router.get("/types")
async def get_diagram_types(current_user: User = Depends(get_current_user)):
    """
    Get the list of supported diagram types with descriptions and response formats.
    """
    diagram_types = [
        {
            "type": DiagramType.ARCHITECTURE,
            "name": "Architecture Diagram",
            "description": "Visualizes the high-level components of a system and their interactions",
            "response_format": {
                "elements": [
                    {
                        "id": "string",
                        "type": "component",
                        "name": "string",
                        "description": "string",
                        "tech_stack": ["string"],
                        "position": {"x": "number", "y": "number"},
                        "style": {"optional": "styling"}
                    }
                ],
                "layout": "string",
                "metadata": {"version": "string"},
                "title": "string",
                "description": "string"
            }
        },
        {
            "type": DiagramType.ACTIVITY,
            "name": "Activity Diagram",
            "description": "Shows the flow of activities and actions within a process",
            "response_format": {
                "nodes": [
                    {
                        "id": "string",
                        "type": "action|decision|start|end",
                        "name": "string",
                        "description": "string",
                        "node_type": "string",
                        "position": {"x": "number", "y": "number"},
                        "style": {"optional": "styling"}
                    }
                ],
                "connections": [
                    {
                        "id": "string",
                        "source": "string",
                        "target": "string",
                        "label": "string",
                        "style": {"optional": "styling"}
                    }
                ],
                "swimlanes": [
                    {"id": "string", "name": "string"}
                ],
                "metadata": {"version": "string"},
                "title": "string",
                "description": "string"
            }
        },
        {
            "type": DiagramType.SCHEMA,
            "name": "Schema Diagram",
            "description": "Represents database entities, attributes, and relationships",
            "response_format": {
                "entities": [
                    {
                        "id": "string",
                        "type": "entity",
                        "name": "string",
                        "attributes": [
                            {"name": "string", "type": "string", "isPrimaryKey": "boolean"}
                        ],
                        "primaryKey": ["string"],
                        "position": {"x": "number", "y": "number"},
                        "style": {"optional": "styling"}
                    }
                ],
                "relations": [
                    {
                        "id": "string",
                        "source": "string",
                        "target": "string",
                        "relationship_type": "string",
                        "cardinality": {"source": "string", "target": "string"},
                        "label": "string",
                        "style": {"optional": "styling"}
                    }
                ],
                "metadata": {"version": "string"},
                "title": "string",
                "description": "string"
            }
        },
        {
            "type": DiagramType.USER_FLOW,
            "name": "User Flow Diagram",
            "description": "Illustrates the path users take through an application interface",
            "response_format": {
                "screens": [
                    {
                        "id": "string",
                        "type": "screen",
                        "name": "string",
                        "content": "string",
                        "interactions": [
                            {"type": "string", "name": "string", "action": "string"}
                        ],
                        "position": {"x": "number", "y": "number"},
                        "style": {"optional": "styling"}
                    }
                ],
                "transitions": [
                    {
                        "id": "string",
                        "source": "string",
                        "target": "string",
                        "action": "string",
                        "condition": "string",
                        "style": {"optional": "styling"}
                    }
                ],
                "user_personas": [
                    {"id": "string", "name": "string", "description": "string"}
                ],
                "metadata": {"version": "string"},
                "title": "string",
                "description": "string"
            }
        },
        {
            "type": DiagramType.WORKFLOW,
            "name": "Workflow Diagram",
            "description": "Depicts business processes, responsibilities, and decision points",
            "response_format": {
                "steps": [
                    {
                        "id": "string",
                        "type": "task|gateway|start|end",
                        "name": "string",
                        "description": "string",
                        "step_type": "string",
                        "actors": ["string"],
                        "position": {"x": "number", "y": "number"},
                        "style": {"optional": "styling"}
                    }
                ],
                "transitions": [
                    {
                        "id": "string",
                        "source": "string",
                        "target": "string",
                        "condition": "string",
                        "priority": "number",
                        "style": {"optional": "styling"}
                    }
                ],
                "swim_lanes": [
                    {"id": "string", "name": "string"}
                ],
                "metadata": {"version": "string"},
                "title": "string",
                "description": "string"
            }
        }
    ]
    
    return {"diagram_types": diagram_types}

