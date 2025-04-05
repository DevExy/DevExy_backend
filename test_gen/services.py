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
    
    async def analyze_test_coverage(self, request: schemas.CoverageAnalysisRequest) -> schemas.CoverageAnalysisResponse:
        """Analyze test coverage of the provided code and tests"""
        
        # Create prompt with source code files
        source_files_content = "\n\n".join([
            f"Source File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.source_files
        ])
        
        # Create prompt with test files
        test_files_content = "\n\n".join([
            f"Test File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.test_files
        ])
        
        prompt = f"""
        I need you to analyze the test coverage for the following code and its test files. 
        Only analyze the source files, not the test files themselves.
        
        ## SOURCE CODE FILES
        {source_files_content}
        
        ## TEST FILES
        {test_files_content}
        
        Additional context: {request.description}
        
        Provide a detailed analysis of the test coverage including the following metrics:
        
        1. Statement Coverage: Percentage of executable lines run by tests. 
           Explanation: This measures if each line of code was executed during testing.
           For each source file, identify specific lines that are not covered and explain why this matters.
           
        2. Branch Coverage: Percentage of control flow branches tested.
           Explanation: This verifies if both true and false paths were taken in conditional statements (if/else, switch).
           For each source file, identify conditional branches that lack coverage for either true or false conditions.
           
        3. Function/Method Coverage: Percentage of functions called during tests.
           Explanation: This confirms if every function in the codebase was executed at least once.
           For each source file, list any functions that were never called during testing.
           
        4. Condition/Decision Coverage: Percentage of boolean conditions tested.
           Explanation: This checks if all combinations of boolean expressions were evaluated (e.g., in if (x > 0 && y < 5), testing all combinations).
           For each source file, identify complex conditions that don't have full coverage of all possible combinations.
        
        For each coverage metric in each source file:
        1. Provide the estimated percentage value
        2. Explain why that value was reached (what parts are covered/not covered)
        3. Explain the impact of this coverage level on code reliability
        4. Provide specific examples of what was missed in testing
        
        For each source file, include:
        - Overall coverage metrics (percentages for each category)
        - Line-by-line analysis of uncovered code
        - Identification of edge cases or scenarios not covered
        - Functions/methods with low coverage
        - Specific recommendations to improve coverage
        
        For visualization purposes, include:
        - Data for a coverage summary chart (filename, statement_coverage, branch_coverage, function_coverage, condition_coverage)
        - Data for a coverage heatmap showing hotspots of uncovered code with severity scores (0-10, where 0 is not covered at all)
        - Data for a "missed test cases" chart showing the count of missed test scenarios per file
        - Data for a "coverage improvement potential" chart showing how much each file's coverage could improve
        
        Format your response as a detailed JSON object with the following structure:
        
        {{
            "summary": {{
                "overall_coverage": {{
                    "statement_coverage": {{
                        "value": 85.5,
                        "explanation": "85.5% of all executable statements are covered by tests. This indicates good basic coverage but still leaves some code untested."
                    }},
                    "branch_coverage": {{
                        "value": 75.2,
                        "explanation": "75.2% of all branches (if/else paths) are tested. This moderate coverage means some conditional logic paths remain untested."
                    }},
                    "function_coverage": {{
                        "value": 90.0,
                        "explanation": "90% of functions are called at least once during testing. While most code is executed, some functions are never tested."
                    }},
                    "condition_coverage": {{
                        "value": 70.5,
                        "explanation": "70.5% of boolean conditions are fully tested. This indicates that many complex conditions don't have all combinations tested."
                    }}
                }},
                "recommendations": [
                    "Add tests for error handling in module X",
                    "Improve coverage of edge cases in function Y"
                ]
            }},
            "files_analysis": [
                {{
                    "filepath": "path/to/file.py",
                    "metrics": {{
                        "statement_coverage": {{
                            "value": 90.5,
                            "explanation": "90.5% of statements are covered. The high percentage indicates good line coverage, but some error handling code remains untested.",
                            "uncovered_areas": "Error handling code on lines 45, 67, and 89 is not executed by any test."
                        }},
                        "branch_coverage": {{
                            "value": 85.2,
                            "explanation": "85.2% of branches are tested. Most if/else paths are covered, but some exception paths are missed.",
                            "uncovered_areas": "The false branch of 'if user_authenticated' on line 45 is never tested."
                        }},
                        "function_coverage": {{
                            "value": 95.0,
                            "explanation": "95% of functions are tested. Nearly all functions have test coverage, but helper functions may be missed.",
                            "uncovered_areas": "The helper functions 'process_data' and 'handle_error' are never directly tested."
                        }},
                        "condition_coverage": {{
                            "value": 80.5,
                            "explanation": "80.5% of conditions are fully tested. Complex boolean logic in authentication checks lacks complete testing.",
                            "uncovered_areas": "In the condition 'if (x > 0 && y < 5)', the combination where x > 0 is true but y < 5 is false isn't tested."
                        }}
                    }},
                    "uncovered_lines": [45, 67, 89],
                    "uncovered_branches": ["if condition at line 45", "else branch at line 67"],
                    "uncovered_functions": ["process_data", "handle_error"],
                    "missed_edge_cases": [
                        "Authentication failure scenario at line 45",
                        "Database connection timeout at line 67",
                        "Input validation for empty strings at line 89"
                    ],
                    "test_improvement_suggestions": [
                        {{
                            "description": "Add test for error condition at line 45",
                            "implementation_hint": "Mock authentication to return false to trigger this branch"
                        }},
                        {{
                            "description": "Test the alternate branch at line 67",
                            "implementation_hint": "Mock database to throw timeout exception"
                        }}
                    ],
                    "risk_assessment": "Medium risk due to untested error handling paths that could lead to unhandled exceptions in production."
                }}
            ],
            "visualization_data": {{
                "summary_chart_data": [
                    {{
                        "filename": "file1.py",
                        "statement_coverage": 90.5,
                        "branch_coverage": 85.2,
                        "function_coverage": 95.0,
                        "condition_coverage": 80.5
                    }}
                ],
                "heatmap_data": [
                    {{
                        "filepath": "file1.py",
                        "hotspots": [
                            {{ "line": 45, "coverage_score": 0, "description": "Critical authentication logic uncovered" }},
                            {{ "line": 67, "coverage_score": 0, "description": "Database error handling not tested" }},
                            {{ "line": 89, "coverage_score": 0, "description": "Validation logic uncovered" }}
                        ]
                    }}
                ],
                "missed_test_cases_chart": [
                    {{
                        "filename": "file1.py",
                        "count": 5,
                        "categories": {{
                            "error_handling": 2,
                            "edge_cases": 2,
                            "input_validation": 1
                        }}
                    }}
                ],
                "improvement_potential_chart": [
                    {{
                        "filename": "file1.py",
                        "current_overall_coverage": 87.8,
                        "potential_coverage": 98.5,
                        "improvement_percentage": 10.7
                    }}
                ]
            }}
        }}
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
                coverage_analysis_data = json.loads(response_text)
                
                # Convert the parsed JSON data to our schema object
                return schemas.CoverageAnalysisResponse(**coverage_analysis_data)
                
            except json.JSONDecodeError as e:
                # If response isn't valid JSON, try to extract JSON from the text
                import re
                json_match = re.search(r'{.*}', response.text, re.DOTALL)
                if json_match:
                    try:
                        coverage_analysis_data = json.loads(json_match.group(0))
                        return schemas.CoverageAnalysisResponse(**coverage_analysis_data)
                    except:
                        pass
                    
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse coverage analysis: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing test coverage: {str(e)}"
            )
    
    async def analyze_test_priority(self, request: schemas.TestPriorityRequest) -> schemas.TestPriorityResponse:
        """Analyze test case priority and provide risk assessment"""
        
        # Create prompt with source code files
        source_files_content = "\n\n".join([
            f"Source File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.source_files
        ])
        
        # Create prompt with test files
        test_files_content = "\n\n".join([
            f"Test File: {file.filepath}\n```\n{file.content}\n```" 
            for file in request.test_files
        ])
        
        prompt = f"""
        Analyze the following source code and test files to create a comprehensive test priority and risk assessment report.
        Determine which test cases are most critical, what security concerns exist, and what the impact would be if tests fail.
        
        ## SOURCE CODE FILES
        {source_files_content}
        
        ## TEST FILES
        {test_files_content}
        
        Additional context: {request.description}
        Business criticality context: {request.code_criticality_context or "No specific business context provided"}
        
        Create a detailed report that includes:
        
        1. Test Case Prioritization:
           - Assign priority scores (0-10) to each test case based on:
             - Code complexity
             - Business criticality of the tested feature
             - Security implications
             - Data integrity concerns
             - User impact if the feature fails
             - Error handling coverage
             - Edge case coverage
           - For each high-priority test, explain why it's critical
        
        2. Risk Assessment:
           - Identify potential security vulnerabilities and their severity
           - Classify tests by risk categories (security, data integrity, etc.)
           - Assess the impact of test failures on production systems
           - Identify tests that verify critical business logic
           - Evaluate tests that check compliance requirements
        
        3. Security Analysis:
           - Identify tests that verify authentication, authorization, input validation
           - Flag missing security tests for potential attack vectors
           - Recommend additional security tests where needed
           - Reference relevant CWE (Common Weakness Enumeration) identifiers
        
        4. Dependency Analysis:
           - Identify relationships between tests and components
           - Determine which tests verify integration points
           - Assess cascading failure risks
        
        Format your response as a detailed JSON object with the following structure:
        
        {{
            "summary": {{
                "overall_assessment": "Detailed summary of the overall test priority assessment",
                "critical_areas": ["Area1", "Area2"],
                "high_risk_count": 5,
                "medium_risk_count": 8,
                "low_risk_count": 12,
                "security_vulnerability_count": 3,
                "top_priority_tests_count": 5
            }},
            "test_priorities": [
                {{
                    "test_name": "test_user_authentication",
                    "filepath": "tests/test_auth.py",
                    "test_line": 45,
                    "priority_score": 9.5,
                    "risk_categories": [
                        {{
                            "name": "security",
                            "description": "Tests authentication logic which is critical for system security",
                            "severity": 9.8,
                            "impact_areas": ["security", "data_protection", "compliance"]
                        }}
                    ],
                    "failure_impact": "Authentication bypass could allow unauthorized access to sensitive data",
                    "security_concerns": "Potential for authentication bypass if this functionality fails",
                    "dependencies": ["user_service", "authentication_middleware"],
                    "coverage_impact": 85.5
                }}
            ],
            "security_vulnerabilities": [
                {{
                    "description": "Potential SQL injection in user input handling",
                    "severity": 8.5,
                    "affected_code": "src/api/user_controller.py:78-92",
                    "mitigation_recommendations": [
                        "Use parameterized queries",
                        "Add input validation tests"
                    ],
                    "cwe_reference": "CWE-89"
                }}
            ],
            "visualization_data": {{
                "priority_distribution": {{
                    "high": 5,
                    "medium": 8,
                    "low": 12
                }},
                "risk_category_distribution": {{
                    "security": 7,
                    "data_integrity": 5,
                    "performance": 3,
                    "compliance": 4
                }},
                "critical_tests_by_module": {{
                    "authentication": 3,
                    "payment_processing": 4,
                    "data_storage": 2
                }},
                "security_impact_scores": [
                    {{
                        "test_name": "test_user_authentication",
                        "score": 9.5,
                        "category": "authentication"
                    }},
                    {{
                        "test_name": "test_input_validation",
                        "score": 8.7,
                        "category": "input_validation"
                    }}
                ]
            }},
            "recommendations": [
                "Add more tests for authentication failure scenarios",
                "Implement CSRF protection tests",
                "Increase test coverage for payment processing edge cases"
            ]
        }}
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
                priority_analysis_data = json.loads(response_text)
                
                # Convert the parsed JSON data to our schema object
                return schemas.TestPriorityResponse(**priority_analysis_data)
                
            except json.JSONDecodeError as e:
                # If response isn't valid JSON, try to extract JSON from the text
                import re
                json_match = re.search(r'{.*}', response.text, re.DOTALL)
                if json_match:
                    try:
                        priority_analysis_data = json.loads(json_match.group(0))
                        return schemas.TestPriorityResponse(**priority_analysis_data)
                    except:
                        pass
                    
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse test priority analysis: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing test priorities: {str(e)}"
            )