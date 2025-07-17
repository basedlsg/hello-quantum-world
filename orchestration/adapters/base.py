"""
Base project adapter implementation.

Provides common functionality for adapting existing projects to the orchestration system.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.interfaces import IProjectAdapter
from ..core.models import ExperimentResult, ExperimentStatus


class BaseProjectAdapter(IProjectAdapter):
    """Base implementation of project adapter with common functionality."""
    
    def __init__(self, project_path: str):
        """
        Initialize the project adapter.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path).resolve()
        self.project_name = self.project_path.name
        self._parameter_schema = None
        self._compatibility_report = None
    
    def adapt_project(self, project_path: str) -> bool:
        """
        Adapt a project for orchestration.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            True if adaptation was successful
        """
        try:
            self.project_path = Path(project_path).resolve()
            self.project_name = self.project_path.name
            
            # Validate project structure
            if not self.project_path.exists():
                raise FileNotFoundError(f"Project path does not exist: {project_path}")
            
            # Check for main.py
            main_py = self.project_path / "main.py"
            if not main_py.exists():
                raise FileNotFoundError(f"main.py not found in {project_path}")
            
            # Validate compatibility
            compatibility = self.validate_compatibility()
            if not compatibility.get("compatible", False):
                raise ValueError(f"Project not compatible: {compatibility.get('issues', [])}")
            
            return True
            
        except Exception as e:
            print(f"Failed to adapt project {project_path}: {e}")
            return False
    
    def execute_with_parameters(self, params: Dict[str, Any]) -> ExperimentResult:
        """
        Execute the project with given parameters.
        
        Args:
            params: Dictionary of parameter values
            
        Returns:
            ExperimentResult containing the execution results
        """
        experiment_id = f"{self.project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            # Create temporary parameter file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(params, f)
                param_file = f.name
            
            # Execute project with parameters
            result = self._execute_project(param_file, params)
            
            # Clean up
            os.unlink(param_file)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract metrics from result
            metrics = self.extract_metrics(result)
            
            return ExperimentResult(
                experiment_id=experiment_id,
                project_name=self.project_name,
                parameters=params,
                metrics=metrics,
                execution_time=execution_time,
                status=ExperimentStatus.COMPLETED,
                timestamp=start_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExperimentResult(
                experiment_id=experiment_id,
                project_name=self.project_name,
                parameters=params,
                metrics={},
                execution_time=execution_time,
                status=ExperimentStatus.FAILED,
                error_message=str(e),
                timestamp=start_time
            )
    
    def _execute_project(self, param_file: str, params: Dict[str, Any]) -> Any:
        """
        Execute the project with parameter file.
        
        Args:
            param_file: Path to temporary parameter file
            params: Parameter dictionary for fallback
            
        Returns:
            Raw execution result
        """
        # Default implementation: run main.py with --quick flag
        cmd = [
            sys.executable,
            str(self.project_path / "main.py"),
            "--quick"
        ]
        
        # Set environment variables for parameters
        env = os.environ.copy()
        for key, value in params.items():
            env[f"ORCH_PARAM_{key.upper()}"] = str(value)
        env["ORCH_PARAM_FILE"] = param_file
        
        # Execute the project
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Project execution failed: {result.stderr}")
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    
    def extract_metrics(self, result: Any) -> Dict[str, float]:
        """
        Extract standardized metrics from project output.
        
        Args:
            result: Raw result from project execution
            
        Returns:
            Dictionary of standardized metrics
        """
        metrics = {}
        
        if isinstance(result, dict) and "stdout" in result:
            stdout = result["stdout"]
            
            # Look for common metric patterns in stdout
            lines = stdout.split('\n')
            for line in lines:
                line = line.strip()
                
                # Pattern: "metric_name: value"
                if ':' in line and any(keyword in line.lower() for keyword in 
                                     ['accuracy', 'fidelity', 'efficiency', 'error', 'cost', 'time']):
                    try:
                        parts = line.split(':')
                        if len(parts) == 2:
                            metric_name = parts[0].strip().lower().replace(' ', '_')
                            metric_value = float(parts[1].strip())
                            metrics[metric_name] = metric_value
                    except ValueError:
                        continue
                
                # Pattern: "Final result: value"
                if line.lower().startswith('final') and ':' in line:
                    try:
                        value = float(line.split(':')[1].strip())
                        metrics['final_result'] = value
                    except ValueError:
                        continue
        
        # If no metrics found, add execution success metric
        if not metrics:
            metrics['execution_success'] = 1.0 if isinstance(result, dict) and result.get("returncode") == 0 else 0.0
        
        return metrics
    
    def validate_compatibility(self) -> Dict[str, Any]:
        """
        Validate that the project is compatible with orchestration.
        
        Returns:
            Dictionary containing compatibility report
        """
        if self._compatibility_report is not None:
            return self._compatibility_report
        
        issues = []
        warnings = []
        
        # Check for main.py
        main_py = self.project_path / "main.py"
        if not main_py.exists():
            issues.append("main.py not found")
        
        # Check for requirements files
        req_files = ["requirements.txt", "requirements_production.txt", "requirements_locked.txt"]
        has_requirements = any((self.project_path / req).exists() for req in req_files)
        if not has_requirements:
            warnings.append("No requirements file found")
        
        # Check if main.py accepts --quick flag
        if main_py.exists():
            try:
                with open(main_py, 'r') as f:
                    content = f.read()
                    if "--quick" not in content and "quick" not in content:
                        warnings.append("main.py may not support --quick flag")
            except Exception:
                warnings.append("Could not read main.py")
        
        # Check for test files
        test_files = list(self.project_path.glob("test_*.py"))
        if not test_files:
            warnings.append("No test files found")
        
        self._compatibility_report = {
            "compatible": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "project_path": str(self.project_path),
            "project_name": self.project_name
        }
        
        return self._compatibility_report
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the parameter schema for this project.
        
        Returns:
            Dictionary describing available parameters and their types
        """
        if self._parameter_schema is not None:
            return self._parameter_schema
        
        # Default schema - subclasses should override
        self._parameter_schema = {
            "quick": {
                "type": "boolean",
                "description": "Run quick version for testing",
                "default": True
            }
        }
        
        return self._parameter_schema


# Alias for backward compatibility
ProjectAdapter = BaseProjectAdapter