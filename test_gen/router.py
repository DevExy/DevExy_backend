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

@router.post("/generate-stress-tests", response_model=schemas.TestGenerationResponse)
async def generate_stress_tests(
    request: schemas.TestGenerationRequest,
    current_user: User = Depends(get_active_user)
):
    """Generate stress tests using Locust for provided files"""
    try:
        service = TestGenerationService()
        generated_tests = await service.generate_stress_tests(request)
        
        return schemas.TestGenerationResponse(
            tests=generated_tests,
            message="Stress tests generated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating stress tests: {str(e)}"
        )

@router.post("/analyze-coverage", response_model=schemas.CoverageAnalysisResponse)
async def analyze_coverage(
    request: schemas.CoverageAnalysisRequest,
    current_user: User = Depends(get_active_user)
):
    """Analyze test coverage for provided source and test files"""
    try:
        service = TestGenerationService()
        coverage_analysis = await service.analyze_test_coverage(request)
        
        return coverage_analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing test coverage: {str(e)}"
        )

