from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class DiagramType(str, Enum):
    ARCHITECTURE = "architecture"
    ACTIVITY = "activity"
    SCHEMA = "schema"
    USER_FLOW = "user_flow"
    WORKFLOW = "workflow"

class FileContent(BaseModel):
    content: str
    filepath: str

class DiagramGenRequest(BaseModel):
    files: List[FileContent]
    diagram_type: DiagramType
    description: Optional[str] = "Generate diagram based on the provided files"

# Base elements for all diagram types
class BaseResponseElement(BaseModel):
    id: str
    type: str
    position: Dict[str, int]

class ConnectionElement(BaseResponseElement):
    source: str
    target: str
    label: Optional[str] = None
    style: Optional[Dict[str, Any]] = None

# Architecture diagram specific elements
class ArchitectureComponent(BaseResponseElement):
    name: str
    description: str
    tech_stack: Optional[List[str]] = None
    icon: Optional[str] = None
    style: Optional[Dict[str, Any]] = None

class ArchitectureDiagramResponse(BaseModel):
    elements: List[Union[Dict[str, Any], Dict[str, Any]]]  # Simplified for API compatibility
    layout: str
    metadata: Dict[str, Any]
    title: str
    description: str

# Activity diagram specific elements
class ActivityNode(BaseResponseElement):
    name: str
    description: Optional[str] = None
    node_type: str  # action, decision, start, end, etc.
    style: Optional[Dict[str, Any]] = None

class ActivityDiagramResponse(BaseModel):
    nodes: List[Dict[str, Any]]  # Simplified for API compatibility
    connections: List[Dict[str, Any]]
    swimlanes: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any]
    title: str
    description: str

# Schema diagram specific elements
class SchemaEntity(BaseResponseElement):
    name: str
    attributes: List[Dict[str, Any]]
    primaryKey: Optional[List[str]] = None
    foreignKeys: Optional[List[Dict[str, str]]] = None
    style: Optional[Dict[str, Any]] = None

class SchemaRelation(ConnectionElement):
    relationship_type: str  # one-to-one, one-to-many, etc.
    cardinality: Dict[str, str]

class SchemaDiagramResponse(BaseModel):
    entities: List[Dict[str, Any]]  # Simplified for API compatibility
    relations: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    title: str
    description: str

# User flow diagram specific elements
class UserFlowScreen(BaseResponseElement):
    name: str
    content: str
    interactions: List[Dict[str, Any]]
    style: Optional[Dict[str, Any]] = None

class UserFlowTransition(ConnectionElement):
    action: str
    condition: Optional[str] = None

class UserFlowDiagramResponse(BaseModel):
    screens: List[Dict[str, Any]]  # Simplified for API compatibility
    transitions: List[Dict[str, Any]]
    user_personas: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any]
    title: str
    description: str

# Workflow diagram specific elements
class WorkflowStep(BaseResponseElement):
    name: str
    description: str
    step_type: str  # task, subprocess, gateway, etc.
    actors: Optional[List[str]] = None
    style: Optional[Dict[str, Any]] = None

class WorkflowTransition(ConnectionElement):
    condition: Optional[str] = None
    priority: Optional[int] = None

class WorkflowDiagramResponse(BaseModel):
    steps: List[Dict[str, Any]]  # Simplified for API compatibility
    transitions: List[Dict[str, Any]]
    swim_lanes: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any]
    title: str
    description: str

class DiagramResponse(BaseModel):
    diagram_type: DiagramType
    data: Dict[str, Any]  # More flexible approach