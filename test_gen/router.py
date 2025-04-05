from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import os

from auth.dependencies import get_current_user, get_active_user
from auth.models import User
from db.database import get_db
from test_gen import schemas
from test_gen.services import TestGenerationService

router = APIRouter(prefix="/test-gen", tags=["Test Generation"])

@router.websocket("/ws/generate-unit-tests")
async def generate_tests_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """Generate unit tests for provided files via WebSocket"""
    # Authenticate using the token before accepting the connection
    try:
        # Create a mock credentials object to use with get_current_user
        class MockCredentials:
            def __init__(self, token):
                self.credentials = token
        
        # Verify the token and get the user
        current_user = await get_active_user(
            current_user=await get_current_user(
                credentials=MockCredentials(token),
                db=db
            )
        )
        
        # If we reach here, authentication was successful
        await websocket.accept()
        
        try:
            # Receive the file contents from client
            data = await websocket.receive_json()
            files = [schemas.FileContent(**file) for file in data.get("files", [])]
            test_directory = data.get("test_directory", "tests")
            
            # Create request with predefined description for generating good unit tests
            request = schemas.TestGenerationRequest(
                files=files,
                description="Generate comprehensive unit tests following best practices: use proper assertions, test edge cases, include setup/teardown if needed, use mocks for dependencies, ensure high test coverage, and follow naming conventions.",
                test_directory=test_directory
            )
            
            service = TestGenerationService()
            
            # Stream test generation results back to client
            async for chunk in service.generate_tests_stream(request):
                await websocket.send_text(chunk)
                
        except WebSocketDisconnect:
            # Handle client disconnect
            pass
        except Exception as e:
            # Send error message to client
            await websocket.send_text(f"Error: {str(e)}")
    
    except HTTPException as e:
        # For auth errors, we need to accept the connection first to send the error
        await websocket.accept()
        await websocket.send_text(f"Authentication error: {e.detail}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        # Handle any other exceptions during authentication
        await websocket.accept()
        await websocket.send_text(f"Authentication error: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

@router.post("/generate-unit-tests", response_model=schemas.TestGenerationResponse)
async def generate_tests(
    request: schemas.TestGenerationRequest,
    current_user: User = Depends(get_active_user)
):
    """Generate unit tests for provided files"""
    try:
        service = TestGenerationService()
        generated_tests = await service.generate_tests(request)
        
        return schemas.TestGenerationResponse(
            tests=generated_tests,
            message="Unit tests generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating tests: {str(e)}"
        )

@router.post("/generate-integration-tests", response_model=schemas.TestGenerationResponse)
async def generate_integration_tests(
    request: schemas.TestGenerationRequest,
    current_user: User = Depends(get_active_user)
):
    """Generate integration tests for provided files"""
    try:
        service = TestGenerationService()
        generated_tests = await service.generate_integration_tests(request)
        
        return schemas.TestGenerationResponse(
            tests=generated_tests,
            message="Integration tests generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating integration tests: {str(e)}"
        )

