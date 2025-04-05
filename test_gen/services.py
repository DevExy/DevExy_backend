import os
from typing import List, AsyncGenerator
import asyncio
from google import genai
from fastapi import HTTPException, status
from pydantic import BaseModel

from test_gen import schemas
from core.config import settings

class TestGenerationService:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )
        self.client = genai.Client(api_key=api_key)
        
    async def generate_tests(self, request: schemas.TestGenerationRequest) -> List[schemas.GeneratedTest]:
        """Generate unit tests using Gemini API"""
        
        # Create prompt with file contents
        file_contents = "\n\n".join([
            f"File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.files
        ])
        
        prompt = f"""
        I need you to generate unit tests for the following files:
        
        {file_contents}
        
        Additional context: {request.description}
        
        Generate comprehensive unit tests that cover the main functionality.
        For each file, provide a corresponding test file in the appropriate location within {request.test_directory}.
        """
        
        try:
            response = await self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': List[schemas.GeneratedTest],
                }
            )
            
            return response.parsed
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating tests: {str(e)}"
            )
    
    async def generate_tests_stream(self, request: schemas.TestGenerationRequest) -> AsyncGenerator[str, None]:
        """Generate unit tests using Gemini API with streaming response"""
        
        # Create prompt with file contents
        file_contents = "\n\n".join([
            f"File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.files
        ])
        
        prompt = f"""
        I need you to generate unit tests for the following files:
        
        {file_contents}
        
        Additional context: {request.description}
        
        Generate comprehensive unit tests that cover the main functionality.
        For each file, provide a corresponding test file in the appropriate location within {request.test_directory}.
        
        Format your response as JSON compatible with this schema:
        List[{{
            "filepath": "path/to/test/file.py",
            "content": "# Test file content here"
        }}]
        """
        
        try:
            response = self.client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    await asyncio.sleep(0.01)  # Small delay to prevent overwhelming the client
                    
        except Exception as e:
            yield f"Error generating tests: {str(e)}"