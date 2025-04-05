from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union

class FileContent(BaseModel):
    content: str
    filepath: str

class RequirementsContent(BaseModel):
    content: str
    filepath: Optional[str] = None

class RequirementsAnalysisRequest(BaseModel):
    requirements_content: RequirementsContent
    source_files: Optional[List[FileContent]] = []  # Source code files for context
    description: Optional[str] = "Analyze requirements file for performance and memory usage"

class RequirementDependency(BaseModel):
    name: str
    version: str
    size_kb: float
    memory_usage_estimate_mb: float
    startup_time_impact_ms: float
    is_direct: bool
    imported_by: List[str] = []
    alternatives: List[str] = []
    usage_in_code: Optional[List[str]] = None  # References in source code

class RequirementsAnalysisResponse(BaseModel):
    summary: Dict[str, Any]
    dependencies: List[RequirementDependency]
    performance_impact: Dict[str, Any]
    memory_impact: Dict[str, Any]
    security_concerns: List[Dict[str, Any]]
    optimization_opportunities: List[Dict[str, str]]
    visualization_data: Dict[str, Any]
    code_specific_insights: Optional[Dict[str, Any]] = None  # Insights based on source code

class RequirementsOptimizationRequest(BaseModel):
    requirements_content: RequirementsContent
    source_files: Optional[List[FileContent]] = []  # Source code files for context
    optimization_goals: List[str] = ["memory", "performance", "security"]
    keep_dependencies: Optional[List[str]] = None
    description: Optional[str] = "Optimize requirements file for better performance and lower memory usage"

class OptimizedRequirement(BaseModel):
    name: str
    original_version: Optional[str] = None
    optimized_version: str
    reason: str
    impact: Dict[str, Any]
    code_references: Optional[List[str]] = None  # Where in the code this dependency is used

class RequirementsOptimizationResponse(BaseModel):
    optimized_content: str
    summary: Dict[str, Any]
    changes: List[OptimizedRequirement]
    performance_improvement: Dict[str, Any]
    memory_improvement: Dict[str, Any]
    security_improvement: Optional[Dict[str, Any]] = None
    recommendations: List[str]
    unused_dependencies: Optional[List[str]] = None  # Dependencies not actually used in code