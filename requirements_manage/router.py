from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from auth.dependencies import get_current_user, get_active_user
from auth.models import User
from db.database import get_db
from requirements_manage import schemas
from requirements_manage.service import RequirementsService

router = APIRouter(prefix="/requirements", tags=["Requirements Management"])

@router.post("/analyze", response_model=schemas.RequirementsAnalysisResponse)
async def analyze_requirements(
    request: schemas.RequirementsAnalysisRequest,
    current_user: User = Depends(get_active_user)
):
    """
    Analyze a requirements.txt file for performance, memory usage, and security insights.
    
    This endpoint performs a detailed analysis of Python dependencies, providing:
    - Dependency size and memory footprint estimates
    - Performance impact analysis
    - Memory usage assessment
    - Security vulnerability checks
    - Optimization recommendations
    
    You can optionally provide source code files to get more accurate insights:
    - Identification of unused dependencies
    - Analysis of how each dependency is actually used
    - More targeted optimization recommendations based on usage patterns
    
    The response includes detailed metrics, visualizations, and actionable insights
    to improve your Python dependency management.
    """
    try:
        service = RequirementsService()
        analysis = await service.analyze_requirements(request)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing requirements file: {str(e)}"
        )

@router.post("/optimize", response_model=schemas.RequirementsOptimizationResponse)
async def optimize_requirements(
    request: schemas.RequirementsOptimizationRequest,
    current_user: User = Depends(get_active_user)
):
    """
    Generate an optimized version of a requirements.txt file with improved performance and lower memory usage.
    
    This endpoint provides:
    - A memory and performance optimized requirements.txt file
    - Detailed explanations for each change
    - Quantified improvement estimates (startup time, memory usage)
    - Security enhancements
    - Best practice recommendations
    
    You can specify:
    - Optimization goals (memory, performance, security)
    - Critical dependencies that must be kept
    - Additional context about your application
    
    For more accurate optimization, include your source code files:
    - Dependencies not used in your code will be identified and may be removed
    - Recommendations will be tailored to how you use each dependency
    - Library alternatives will be suggested based on your specific usage patterns
    
    The response includes the optimized file content and comprehensive details about the improvements.
    """
    try:
        service = RequirementsService()
        optimization = await service.optimize_requirements(request)
        return optimization
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing requirements file: {str(e)}"
        )