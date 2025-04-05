from pydantic import BaseModel
from typing import Dict, List, Optional

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