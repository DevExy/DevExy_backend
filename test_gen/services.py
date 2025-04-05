import os
from typing import List, AsyncGenerator
import asyncio
import json
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
        
        Format your response as a JSON array of test files, where each test file has a 'filepath' and 'content' property. Example:
        [
            {{
                "filepath": "tests/example_test.py",
                "content": "# Test content here\\n..."
            }}
        ]
        """
        
        try:
            # Run the synchronous API call in a thread pool to avoid blocking
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Parse the JSON response string into a Python object
            try:
                # Try to extract JSON from the response text
                response_text = response.text
                generated_tests_data = json.loads(response_text)
                
                # Convert the parsed JSON data to our schema objects
                generated_tests = [
                    schemas.GeneratedTest(filepath=test["filepath"], content=test["content"])
                    for test in generated_tests_data
                ]
                
                return generated_tests
            except json.JSONDecodeError as e:
                # If response isn't valid JSON, try to extract JSON from the text
                # It might be embedded in a markdown code block or have extra text
                import re
                json_match = re.search(r'\[\s*{.*}\s*\]', response.text, re.DOTALL)
                if json_match:
                    try:
                        generated_tests_data = json.loads(json_match.group(0))
                        generated_tests = [
                            schemas.GeneratedTest(filepath=test["filepath"], content=test["content"])
                            for test in generated_tests_data
                        ]
                        return generated_tests
                    except:
                        pass
                    
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse generated tests: {str(e)}"
                )
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
        Generate comprehensive unit tests for the following files:
        
        {file_contents}
        
        Follow these best practices for unit testing:
        1. Cover all main functionality and edge cases
        2. Use descriptive test names that explain what's being tested
        3. Structure tests with arrange/act/assert pattern
        4. Properly mock external dependencies
        5. Include appropriate assertions to verify correctness
        6. Follow pytest conventions if using pytest
        7. Add docstrings explaining test purpose
        
        For each file, provide a corresponding test file in the appropriate location within {request.test_directory}.
        
        Format your response as JSON compatible with this schema:
        [
            {{
                "filepath": "path/to/test/file.py",
                "content": "# Test file content here"
            }}
        ]
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
    
    async def generate_integration_tests(self, request: schemas.TestGenerationRequest) -> List[schemas.GeneratedTest]:
        """Generate integration tests using Gemini API"""
        
        # Create prompt with file contents
        file_contents = "\n\n".join([
            f"File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.files
        ])
        
        prompt = f"""
        I need you to generate integration tests for the following files:
        
        {file_contents}
        
        Additional context: {request.description}
        
        Generate comprehensive integration tests that:
        1. Test interactions between multiple components/modules
        2. Verify end-to-end functionality across system boundaries
        3. Test API endpoints with real (or properly mocked) dependencies
        4. Verify database interactions where applicable
        5. Test proper error handling across component boundaries
        6. Include setup and teardown for test environment/data
        
        For each file, provide a corresponding test file in the appropriate location within {request.test_directory}.
        
        Format your response as a JSON array of test files, where each test file has a 'filepath' and 'content' property. Example:
        [
            {{
                "filepath": "{request.test_directory}/example_integration_test.py",
                "content": "# Test content here\\n..."
            }}
        ]
        """
        
        try:
            # Run the synchronous API call in a thread pool to avoid blocking
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Parse the JSON response string into a Python object
            try:
                # Try to extract JSON from the response text
                response_text = response.text
                generated_tests_data = json.loads(response_text)
                
                # Convert the parsed JSON data to our schema objects
                generated_tests = [
                    schemas.GeneratedTest(filepath=test["filepath"], content=test["content"])
                    for test in generated_tests_data
                ]
                
                return generated_tests
            except json.JSONDecodeError as e:
                # If response isn't valid JSON, try to extract JSON from the text
                # It might be embedded in a markdown code block or have extra text
                import re
                json_match = re.search(r'\[\s*{.*}\s*\]', response.text, re.DOTALL)
                if json_match:
                    try:
                        generated_tests_data = json.loads(json_match.group(0))
                        generated_tests = [
                            schemas.GeneratedTest(filepath=test["filepath"], content=test["content"])
                            for test in generated_tests_data
                        ]
                        return generated_tests
                    except:
                        pass
                    
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse generated tests: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating integration tests: {str(e)}"
            )
            
    async def generate_stress_tests(self, request: schemas.TestGenerationRequest) -> List[schemas.GeneratedTest]:
        """Generate stress/load tests using Locust with Gemini API"""
        
        # Create prompt with file contents
        file_contents = "\n\n".join([
            f"File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.files
        ])
        
        prompt = f"""
        I need you to generate stress tests using Locust for the following files:
        
        {file_contents}
        
        Additional context: {request.description}
        
        Generate comprehensive stress/load tests that:
        1. Define appropriate user behaviors using Locust's HttpUser class
        2. Configure realistic wait times between requests
        3. Implement proper task sets with @task decorators
        4. Include proper assertions to verify responses
        5. Set up appropriate test scenarios for load testing
        6. Add configurations for different load profiles (users, spawn rate)
        7. Include proper documentation on how to run the tests
        
        For each file that contains APIs/endpoints, provide a corresponding Locust test file in the appropriate location within {request.test_directory}.
        
        Format your response as a JSON array of test files, where each test file has a 'filepath' and 'content' property. Example:
        [
            {{
                "filepath": "{request.test_directory}/locustfile.py",
                "content": "# Locust test content here\\n..."
            }},
            {{
                "filepath": "{request.test_directory}/README.md",
                "content": "# Instructions on how to run the stress tests\\n..."
            }}
        ]
        """
        
        try:
            # Run the synchronous API call in a thread pool to avoid blocking
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Parse the JSON response string into a Python object
            try:
                # Try to extract JSON from the response text
                response_text = response.text
                generated_tests_data = json.loads(response_text)
                
                # Convert the parsed JSON data to our schema objects
                generated_tests = [
                    schemas.GeneratedTest(filepath=test["filepath"], content=test["content"])
                    for test in generated_tests_data
                ]
                
                return generated_tests
            except json.JSONDecodeError as e:
                # If response isn't valid JSON, try to extract JSON from the text
                # It might be embedded in a markdown code block or have extra text
                import re
                json_match = re.search(r'\[\s*{.*}\s*\]', response.text, re.DOTALL)
                if json_match:
                    try:
                        generated_tests_data = json.loads(json_match.group(0))
                        generated_tests = [
                            schemas.GeneratedTest(filepath=test["filepath"], content=test["content"])
                            for test in generated_tests_data
                        ]
                        return generated_tests
                    except:
                        pass
                    
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse generated tests: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating stress tests: {str(e)}"
            )
