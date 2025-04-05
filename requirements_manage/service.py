import os
import re
import json
import asyncio
from typing import Dict, List, Any, Optional
from google import genai
from fastapi import HTTPException, status

from requirements_manage import schemas
from core.config import settings

class RequirementsService:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )
        self.client = genai.Client(api_key=api_key)
    
    async def analyze_requirements(self, request: schemas.RequirementsAnalysisRequest) -> schemas.RequirementsAnalysisResponse:
        """
        Analyze a requirements.txt file to provide insights on memory usage,
        performance impact, and security considerations
        """
        content = request.requirements_content.content
        
        # Create prompt with source code files if provided
        source_files_content = ""
        if request.source_files:
            source_files_content = "\n\n".join([
                f"Source File: {file.filepath}\n```\n{file.content}\n```" 
                for file in request.source_files
            ])
            
            source_files_prompt = f"""
            ## SOURCE CODE FILES
            These files provide context about how the dependencies are being used:
            
            {source_files_content}
            
            When analyzing the requirements, consider how these dependencies are actually used in the code.
            Identify:
            1. Which imports are actually used in the code
            2. How extensively each dependency is used
            3. Whether any dependencies aren't being used at all
            4. Where dependencies could be imported more efficiently (e.g., from specific submodules)
            """
        else:
            source_files_prompt = ""
        
        # Using triple quotes for the JSON structure template instead of embedding it in the f-string
        json_structure = '''
{
    "summary": {
        "total_dependencies": 42,
        "direct_dependencies": 30,
        "transitive_dependencies": 12,
        "estimated_size_kb": 45000,
        "estimated_baseline_memory_mb": 120,
        "estimated_startup_time_sec": 2.5,
        "high_impact_packages": ["numpy", "tensorflow"],
        "security_concerns_count": 3,
        "optimization_opportunities_count": 5,
        "unused_dependencies_count": 2
    },
    "dependencies": [
        {
            "name": "numpy",
            "version": "1.21.0",
            "size_kb": 12000,
            "memory_usage_estimate_mb": 50,
            "startup_time_impact_ms": 300,
            "is_direct": true,
            "imported_by": [],
            "alternatives": ["array-api-standard (smaller but less feature-rich)"],
            "usage_in_code": ["main.py:45 - import numpy as np", "data_processing.py:12 - from numpy import array"]
        }
    ],
    "performance_impact": {
        "slow_startup_packages": [
            {"name": "tensorflow", "startup_time_ms": 1200, "mitigation": "Lazy import or use TensorFlow Lite"}
        ],
        "heavy_import_time_packages": [
            {"name": "pandas", "import_time_ms": 500, "mitigation": "Import only needed components"}
        ],
        "known_bottlenecks": [
            {"name": "matplotlib", "issue": "Slow rendering", "mitigation": "Use lighter alternatives like plotly"}
        ],
        "estimated_total_startup_time_ms": 2500,
        "lazy_loading_candidates": ["matplotlib", "tensorflow"]
    },
    "memory_impact": {
        "memory_intensive_libs": [
            {"name": "tensorflow", "baseline_mb": 400, "peak_mb": 600, "mitigation": "Use TensorFlow Lite"}
        ],
        "estimated_baseline_memory_mb": 120,
        "packages_with_memory_issues": [
            {"name": "pandas", "issue": "High memory usage for large datasets", "mitigation": "Use dask for large data"}
        ],
        "estimated_peak_memory_mb": 500,
        "optimization_strategies": [
            "Replace pandas with pyarrow for large datasets",
            "Use memory-efficient alternatives to matplotlib"
        ]
    },
    "security_concerns": [
        {
            "package": "requests<2.28.0",
            "severity": "high",
            "vulnerability": "CVE-2022-40897: open redirect vulnerability",
            "recommendation": "Upgrade to requests>=2.28.0"
        }
    ],
    "optimization_opportunities": [
        {
            "type": "removal",
            "package": "pytest",
            "reason": "Development dependency, not needed in production",
            "estimated_impact": "5MB memory reduction, 100ms faster startup"
        },
        {
            "type": "replacement",
            "package": "pandas",
            "alternative": "polars",
            "reason": "More memory efficient and faster",
            "estimated_impact": "30% memory reduction for data operations"
        }
    ],
    "visualization_data": {
        "size_distribution": [
            {"name": "numpy", "size_kb": 12000},
            {"name": "tensorflow", "size_kb": 150000}
        ],
        "memory_usage": [
            {"name": "numpy", "memory_mb": 50},
            {"name": "tensorflow", "memory_mb": 400}
        ],
        "startup_time": [
            {"name": "numpy", "time_ms": 300},
            {"name": "tensorflow", "time_ms": 1200}
        ],
        "dependency_graph": {
            "nodes": [
                {"id": "app", "group": 0},
                {"id": "numpy", "group": 1},
                {"id": "pandas", "group": 1}
            ],
            "links": [
                {"source": "app", "target": "numpy"},
                {"source": "pandas", "target": "numpy"}
            ]
        }
    },
    "code_specific_insights": {
        "unused_dependencies": [
            {"name": "pytest", "reason": "Not imported in any source files"}
        ],
        "suboptimal_imports": [
            {"file": "data_processing.py", "line": 5, "current": "import pandas as pd", "suggestion": "from pandas import DataFrame, read_csv"}
        ],
        "dependency_usage_frequency": [
            {"name": "numpy", "import_count": 12, "usage_count": 45},
            {"name": "pandas", "import_count": 8, "usage_count": 30}
        ]
    }
}
'''
        
        prompt = f"""
        You are a Python dependencies expert specializing in performance optimization and memory usage analysis.
        I need you to analyze the following requirements.txt file:

        ```
        {content}
        ```

        Additional context: {request.description}
        
        {source_files_prompt}

        Provide a comprehensive analysis including:

        1. Dependency Analysis:
           - List each dependency with its specified version
           - Estimate the size (in KB) and memory footprint (in MB) of each library
           - Estimate the startup time impact (in ms) of each dependency
           - Identify whether it's a direct or transitive dependency
           - List which other packages import this dependency
           - Suggest lightweight alternatives where applicable
           - If source code is provided, analyze how each dependency is used in the code

        2. Performance Impact Analysis:
           - Identify packages known for slow startup times
           - Identify packages with heavy import time
           - Flag packages with known performance bottlenecks
           - Estimate overall application startup time impact
           - Identify packages that could be lazily loaded
           - If source code is provided, identify inefficient import patterns

        3. Memory Usage Analysis:
           - Identify memory-intensive libraries
           - Estimate the baseline memory footprint of the application
           - Identify packages with memory leaks or poor memory management
           - Estimate peak memory usage
           - Suggest memory optimization strategies
           - If source code is provided, identify memory-intensive usage patterns

        4. Security Concerns:
           - Identify packages with known vulnerabilities
           - Flag packages that are no longer maintained
           - Identify packages with incompatible licenses
           - Suggest secure alternatives

        5. Optimization Opportunities:
           - Suggest packages that could be removed or replaced
           - Identify redundant functionality across packages
           - Flag unnecessary version constraints
           - Suggest more efficient alternatives
           - If source code is provided, identify unused dependencies

        Please format your response as a detailed JSON object with the structure shown in the example below:

        {json_structure}

        Be precise and thorough in your analysis, providing actionable insights.
        """
        
        try:
            # Run the API call in a thread pool to avoid blocking
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Parse the JSON response
            try:
                # Extract JSON from the response text
                response_text = response.text
                analysis_data = json.loads(response_text)
                
                # Convert to schema object
                return schemas.RequirementsAnalysisResponse(**analysis_data)
                
            except json.JSONDecodeError as e:
                # Try to extract JSON from text if it's embedded in a code block
                import re
                json_match = re.search(r'{.*}', response.text, re.DOTALL)
                if json_match:
                    try:
                        analysis_data = json.loads(json_match.group(0))
                        return schemas.RequirementsAnalysisResponse(**analysis_data)
                    except:
                        pass
                        
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse requirements analysis: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing requirements: {str(e)}"
            )
    
    async def optimize_requirements(self, request: schemas.RequirementsOptimizationRequest) -> schemas.RequirementsOptimizationResponse:
        """
        Generate an optimized version of a requirements.txt file focusing on
        performance, memory usage, and security improvements
        """
        content = request.requirements_content.content
        keep_deps = request.keep_dependencies or []
        goals = request.optimization_goals
        
        # Create prompt with source code files if provided
        source_files_content = ""
        if request.source_files:
            source_files_content = "\n\n".join([
                f"Source File: {file.filepath}\n```\n{file.content}\n```" 
                for file in request.source_files
            ])
            
            source_files_prompt = f"""
            ## SOURCE CODE FILES
            These files provide context about how the dependencies are being used:
            
            {source_files_content}
            
            When optimizing the requirements, consider:
            1. Which dependencies are actually used in the code and which can be safely removed
            2. Where more specific imports could be used instead of importing entire packages
            3. How dependencies are used to suggest appropriate alternatives
            4. Dependencies that are imported but rarely used (candidates for lazy loading)
            """
        else:
            source_files_prompt = ""
        
        # Using triple quotes for the JSON structure template instead of embedding it in the f-string
        json_structure = '''
{
    "optimized_content": "# Optimized requirements.txt\\npandas==1.5.0\\nnumpy==1.22.4\\n...",
    "summary": {
        "total_changes": 12,
        "removed_packages": 3,
        "updated_versions": 7,
        "replaced_packages": 2,
        "estimated_performance_improvement": "30% faster startup",
        "estimated_memory_reduction": "25% lower baseline memory",
        "security_vulnerabilities_addressed": 2,
        "unused_dependencies_removed": 3
    },
    "changes": [
        {
            "name": "tensorflow",
            "original_version": "2.8.0",
            "optimized_version": "tensorflow-cpu==2.10.0",
            "reason": "Using CPU-only version to reduce memory footprint. Code analysis shows no GPU operations.",
            "impact": {
                "performance": "10% faster import time",
                "memory": "60% memory reduction (300MB → 120MB)",
                "security": "Addresses 1 known CVE in 2.8.0"
            },
            "code_references": [
                "model.py:15 - import tensorflow as tf",
                "train.py:8 - from tensorflow import keras"
            ]
        }
    ],
    "performance_improvement": {
        "startup_time_reduction_ms": 800,
        "import_time_improvement": "30%",
        "key_improvements": [
            "Faster numpy import by upgrading to 1.22.4",
            "Removed slow matplotlib dependency"
        ]
    },
    "memory_improvement": {
        "baseline_reduction_mb": 150,
        "peak_reduction_mb": 250,
        "key_improvements": [
            "Replaced pandas with polars (70MB savings)",
            "Using tensorflow-cpu instead of full tensorflow (180MB savings)"
        ]
    },
    "security_improvement": {
        "vulnerabilities_fixed": 2,
        "key_fixes": [
            "Updated requests to 2.28.1 to fix CVE-2022-40897",
            "Replaced unmaintained package with maintained alternative"
        ]
    },
    "recommendations": [
        "Consider using virtual environments to isolate dependencies",
        "Review and update requirements.txt quarterly",
        "Use tools like pip-audit to regularly check for security vulnerabilities"
    ],
    "unused_dependencies": [
        "pytest - not imported in any source files",
        "flask-cors - no cross-origin requests found in code"
    ]
}
'''
        
        prompt = f"""
        You are a Python dependencies expert specializing in optimizing requirements.txt files for 
        performance, memory efficiency, and security.
        
        I need you to optimize the following requirements.txt file:

        ```
        {content}
        ```

        Optimization Goals: {', '.join(goals)}
        Dependencies that must be kept: {', '.join(keep_deps) if keep_deps else 'None specified'}
        Additional context: {request.description}
        
        {source_files_prompt}
        
        Provide an optimized requirements.txt file that:
        
        1. Improves Performance:
           - Replace slow packages with faster alternatives
           - Update versions to benefit from performance improvements
           - Remove unnecessary dependencies that slow down startup
           - Use minimal installs where possible (e.g., tensorflow-cpu vs full tensorflow)
           - Pin versions to specific releases known for good performance
        
        2. Reduces Memory Usage:
           - Replace memory-intensive libraries with lightweight alternatives
           - Remove unnecessary dependencies
           - Specify memory-optimized versions where available
           - Consider specialized variants (e.g., slim, lite versions)
        
        3. Enhances Security:
           - Update packages with known vulnerabilities
           - Replace unmaintained packages
           - Pin versions to secure releases
           - Avoid packages with security concerns
        
        4. Code-Specific Optimizations (if source code is provided):
           - Remove dependencies not used in the code
           - Suggest more targeted imports for specific use cases
           - Recommend lazy loading for infrequently used dependencies
        
        For each change you make, provide a detailed explanation of:
        - What was changed and why
        - The expected impact on performance, memory usage, and security
        - Any potential compatibility concerns
        - Alternative options considered
        - If source code is provided, references to where the dependency is used
        
        Format your response as a JSON object with the structure shown in the example below:
        
        {json_structure}
        
        Ensure the optimized requirements file maintains compatibility with Python 3.8+ and
        addresses all critical functionality needs while meeting the optimization goals.
        """
        
        try:
            # Run the API call in a thread pool to avoid blocking
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Parse the JSON response
            try:
                # Extract JSON from the response text
                response_text = response.text
                optimization_data = json.loads(response_text)
                
                # Convert to schema object
                return schemas.RequirementsOptimizationResponse(**optimization_data)
                
            except json.JSONDecodeError as e:
                # Try to extract JSON from text if it's embedded in a code block
                import re
                json_match = re.search(r'{.*}', response.text, re.DOTALL)
                if json_match:
                    try:
                        optimization_data = json.loads(json_match.group(0))
                        return schemas.RequirementsOptimizationResponse(**optimization_data)
                    except:
                        pass
                        
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse requirements optimization: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error optimizing requirements: {str(e)}"
            )