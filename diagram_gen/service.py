import os
import json
from typing import Dict, Any, List
from google import genai
from fastapi import HTTPException, status
from diagram_gen.schemas import (
    DiagramType, 
    FileContent
)
from core.config import settings
import asyncio


class DiagramGenerator:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )
        self.client = genai.Client(api_key=api_key)

    async def generate_diagram(
        self,
        files: List[FileContent],
        diagram_type: DiagramType,
        description: str = "Generate diagram based on the provided files"
    ):
        # Build a prompt based on the diagram type
        prompt = self._build_prompt(files, diagram_type, description)
        
        # Call Gemini API with free-form output
        try:
            # Using a simpler approach without response_schema to avoid default value issues
            response = self.client.models.generate_content(
                model='gemini-1.5-pro',
                contents=prompt
            )
            
            # Return the structured response
            return response.text
        except Exception as e:
            # Handle errors properly in production
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating diagram: {str(e)}"
            )

    def _build_prompt(
        self, 
        files: List[FileContent], 
        diagram_type: DiagramType, 
        description: str
    ) -> str:
        # Create file contents string
        file_contents = "\n\n".join([
            f"File: {file.filepath}\n```\n{file.content}\n```" 
            for file in files
        ])
        
        # Common intro
        prompt = f"""
        You are a software architect expert at creating {diagram_type.value} diagrams.
        
        I need you to analyze the following files and create a {diagram_type.value} diagram:
        
        {file_contents}
        
        Additional context: {description}
        """
        
        # Add diagram-specific instructions
        if diagram_type == DiagramType.ARCHITECTURE:
            prompt += """
            Create an architecture diagram that shows:
            - All major components and services
            - Their relationships and interactions
            - Technologies used for each component
            - Data flow between components
            - External systems and integrations
            
            Provide the diagram as a valid JSON with the following structure:
            ```json
            {
              "elements": [
                {
                  "id": "unique_id",
                  "type": "component",  
                  "name": "Component Name",
                  "description": "What this component does",
                  "tech_stack": ["tech1", "tech2"],
                  "position": {"x": 100, "y": 200},
                  "style": {"optional": "styling"}
                }
              ],
              "layout": "hierarchical",
              "metadata": {"version": "1.0"},
              "title": "Architecture Diagram",
              "description": "System architecture showing key components"
            }
            ```
            
            Connections between elements should be included in the elements array.
            """
        
        elif diagram_type == DiagramType.ACTIVITY:
            prompt += """
            Create an activity diagram that shows:
            - Start and end points
            - Actions and activities
            - Decision points and branches
            - Parallel activities where applicable
            - Important transitions and their conditions
            
            Provide the diagram as a valid JSON with the following structure:
            ```json
            {
              "nodes": [
                {
                  "id": "unique_id",
                  "type": "action|decision|start|end",
                  "name": "Node Name",
                  "description": "What happens here",
                  "node_type": "action",
                  "position": {"x": 100, "y": 200},
                  "style": {"optional": "styling"}
                }
              ],
              "connections": [
                {
                  "id": "conn_1",
                  "source": "node_id_1",
                  "target": "node_id_2",
                  "label": "Yes/No or action description",
                  "style": {"optional": "styling"}
                }
              ],
              "swimlanes": [
                {"id": "lane1", "name": "Actor/System Name"}
              ],
              "metadata": {"version": "1.0"},
              "title": "Activity Diagram",
              "description": "Description of the activity flow"
            }
            ```
            """
        
        elif diagram_type == DiagramType.SCHEMA:
            prompt += """
            Create a schema diagram that shows:
            - All entities in the system
            - Their attributes and data types
            - Relationships between entities
            - Primary and foreign keys
            - Cardinality of relationships
            
            Provide the diagram as a valid JSON with the following structure:
            ```json
            {
              "entities": [
                {
                  "id": "unique_id",
                  "type": "entity",
                  "name": "Table/Entity Name",
                  "attributes": [
                    {"name": "id", "type": "integer", "isPrimaryKey": true},
                    {"name": "name", "type": "string"}
                  ],
                  "primaryKey": ["id"],
                  "position": {"x": 100, "y": 200},
                  "style": {"optional": "styling"}
                }
              ],
              "relations": [
                {
                  "id": "rel_1",
                  "source": "entity_id_1",
                  "target": "entity_id_2",
                  "relationship_type": "one-to-many",
                  "cardinality": {"source": "1", "target": "0..*"},
                  "label": "has many",
                  "style": {"optional": "styling"}
                }
              ],
              "metadata": {"version": "1.0"},
              "title": "Schema Diagram",
              "description": "Database schema for the application"
            }
            ```
            """
        
        elif diagram_type == DiagramType.USER_FLOW:
            prompt += """
            Create a user flow diagram that shows:
            - All screens/pages in the application
            - User interactions on each screen
            - Transitions between screens
            - Decision points and alternate flows
            - Error states and recovery paths
            
            Provide the diagram as a valid JSON with the following structure:
            ```json
            {
              "screens": [
                {
                  "id": "unique_id",
                  "type": "screen",
                  "name": "Screen Name",
                  "content": "What's on this screen",
                  "interactions": [
                    {"type": "button", "name": "Submit", "action": "submit form"}
                  ],
                  "position": {"x": 100, "y": 200},
                  "style": {"optional": "styling"}
                }
              ],
              "transitions": [
                {
                  "id": "trans_1",
                  "source": "screen_id_1",
                  "target": "screen_id_2",
                  "action": "Click submit button",
                  "condition": "If form is valid",
                  "style": {"optional": "styling"}
                }
              ],
              "user_personas": [
                {"id": "user1", "name": "Customer", "description": "A typical user"}
              ],
              "metadata": {"version": "1.0"},
              "title": "User Flow Diagram",
              "description": "User journey through the application"
            }
            ```
            """
        
        elif diagram_type == DiagramType.WORKFLOW:
            prompt += """
            Create a workflow diagram that shows:
            - All steps in the business process
            - Actors responsible for each step
            - Decision gateways
            - Parallel processes where applicable
            - System boundaries and integrations
            
            Provide the diagram as a valid JSON with the following structure:
            ```json
            {
              "steps": [
                {
                  "id": "unique_id",
                  "type": "task|gateway|start|end",
                  "name": "Step Name",
                  "description": "What happens in this step",
                  "step_type": "task",
                  "actors": ["Role1", "System2"],
                  "position": {"x": 100, "y": 200},
                  "style": {"optional": "styling"}
                }
              ],
              "transitions": [
                {
                  "id": "trans_1",
                  "source": "step_id_1",
                  "target": "step_id_2",
                  "condition": "If approval granted",
                  "priority": 1,
                  "style": {"optional": "styling"}
                }
              ],
              "swim_lanes": [
                {"id": "lane1", "name": "Department/Role"}
              ],
              "metadata": {"version": "1.0"},
              "title": "Workflow Diagram",
              "description": "Business process workflow"
            }
            ```
            """
        
        # Add final instructions to ensure valid JSON
        prompt += """
        Make absolutely sure the output is valid JSON structure matching the specified schema.
        Don't include any explanatory text outside of the JSON structure.
        All elements must have complete required properties.
        """
        
        return prompt

    async def generate_diagram_stream(self, files: List[FileContent], diagram_type: DiagramType, description: str = "Generate diagram based on the provided files"):
        """Generate diagrams using Gemini API with streaming response"""
        
        # Build prompt with file contents
        prompt = self._build_prompt(files, diagram_type, description)
        
        try:
            response = self.client.models.generate_content_stream(
                model="gemini-1.5-pro",
                contents=prompt,
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    await asyncio.sleep(0.01)  # Small delay to prevent overwhelming the client
                
        except Exception as e:
            yield f"Error generating diagram: {str(e)}"