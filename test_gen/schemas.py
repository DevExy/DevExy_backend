from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class FileContent(BaseModel):
    content: str
    filepath: str

class TestGenerationRequest(BaseModel):
    files: List[FileContent]
    description: Optional[str] = "Generate unit tests for the provided files"
    test_directory: str = "tests"

class GeneratedTest(BaseModel):
    filepath: str
    content: str

class TestGenerationResponse(BaseModel):
    tests: List[GeneratedTest]
    message: str = "Unit tests generated successfully"

class CoverageAnalysisRequest(BaseModel):
    source_files: List[FileContent]
    test_files: List[FileContent]
    description: Optional[str] = "Analyze test coverage for the provided source and test files"

class CoverageMetricDetail(BaseModel):
    value: float
    explanation: str
    uncovered_areas: Optional[str] = None

class DetailedCoverageMetrics(BaseModel):
    statement_coverage: CoverageMetricDetail
    branch_coverage: CoverageMetricDetail
    function_coverage: CoverageMetricDetail
    condition_coverage: CoverageMetricDetail

class TestImprovementSuggestion(BaseModel):
    description: str
    implementation_hint: str

class DetailedFileAnalysis(BaseModel):
    filepath: str
    metrics: DetailedCoverageMetrics
    uncovered_lines: List[int]
    uncovered_branches: List[str]
    uncovered_functions: List[str]
    missed_edge_cases: List[str]
    test_improvement_suggestions: List[TestImprovementSuggestion]
    risk_assessment: str

class EnhancedHotspotData(BaseModel):
    line: int
    coverage_score: float
    description: str

class EnhancedHeatmapData(BaseModel):
    filepath: str
    hotspots: List[EnhancedHotspotData]

class MissedTestCasesData(BaseModel):
    filename: str
    count: int
    categories: Dict[str, int]

class ImprovementPotentialData(BaseModel):
    filename: str
    current_overall_coverage: float
    potential_coverage: float
    improvement_percentage: float

# Add the missing SummaryChartData class
class SummaryChartData(BaseModel):
    filename: str
    statement_coverage: float
    branch_coverage: float
    function_coverage: float
    condition_coverage: float

class EnhancedVisualizationData(BaseModel):
    summary_chart_data: List[SummaryChartData]
    heatmap_data: List[EnhancedHeatmapData]
    missed_test_cases_chart: List[MissedTestCasesData]
    improvement_potential_chart: List[ImprovementPotentialData]

class EnhancedCoverageSummary(BaseModel):
    overall_coverage: DetailedCoverageMetrics
    recommendations: List[str]

class EnhancedCoverageAnalysisResponse(BaseModel):
    summary: EnhancedCoverageSummary
    files_analysis: List[DetailedFileAnalysis]
    visualization_data: EnhancedVisualizationData

CoverageAnalysisResponse = EnhancedCoverageAnalysisResponse

class TestPriorityRequest(BaseModel):
    source_files: List[FileContent]
    test_files: List[FileContent]
    description: Optional[str] = "Analyze test case priority and risk assessment"
    code_criticality_context: Optional[str] = None  # Additional business context about code criticality

class RiskCategory(BaseModel):
    name: str
    description: str
    severity: float  # 0-10 scale
    impact_areas: List[str]  # e.g., ["security", "data_integrity", "user_experience"]

class TestCasePriority(BaseModel):
    test_name: str
    filepath: str
    test_line: int
    priority_score: float  # 0-10 scale
    risk_categories: List[RiskCategory]
    failure_impact: str
    security_concerns: Optional[str] = None
    dependencies: List[str]  # Other components that depend on this functionality
    coverage_impact: float  # Percentage of critical code covered by this test

class SecurityVulnerability(BaseModel):
    description: str
    severity: float  # 0-10 scale
    affected_code: str
    mitigation_recommendations: List[str]
    cwe_reference: Optional[str] = None  # Common Weakness Enumeration reference

class PriorityVisualizationData(BaseModel):
    priority_distribution: Dict[str, int]  # Priority levels and count of tests
    risk_category_distribution: Dict[str, int]  # Risk categories and count of tests
    critical_tests_by_module: Dict[str, int]  # Module names and count of critical tests
    security_impact_scores: List[Dict[str, Any]]  # Security data for visualization

class TestPriorityResponse(BaseModel):
    summary: Dict[str, Any]
    test_priorities: List[TestCasePriority]
    security_vulnerabilities: List[SecurityVulnerability]
    visualization_data: PriorityVisualizationData
    recommendations: List[str]