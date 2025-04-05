from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from auth.dependencies import get_current_user, get_active_user
from auth.models import User
from db.database import get_db
from test_gen import schemas
from test_gen.services import TestGenerationService

router = APIRouter(prefix="/test-gen", tags=["Test Generation"])

@router.post("/generate-tests", response_model=List[schemas.GeneratedTest])
async def generate_tests(
    request: schemas.TestGenerationRequest,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """Generate unit tests for provided files"""
    service = TestGenerationService()
    results = await service.generate_tests(request)
    return results

@router.post("/generate-tests-stream")
async def generate_tests_stream(
    request: schemas.TestGenerationRequest,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """Generate unit tests with streaming response"""
    service = TestGenerationService()
    return StreamingResponse(
        service.generate_tests_stream(request),
        media_type="text/event-stream"
    )