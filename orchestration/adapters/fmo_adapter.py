"""
FMO Project Adapter for orchestration system.

Specialized adapter for the Fenna-Matthews-Olson quantum transport project.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict

from .base import BaseProjectAdapter


class FMOProjectAdapter(BaseProjectAdapter):
    """Adapter for the FMO quantum transport project."""
    
    def __init__(self, project_path: str = "projects/fmo_project"):
        """Initialize FMO project adapter."""
        super().__init__(project_path)
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the parameter schema for the FMO project.
        
        Returns:
            Dictionary describing available FMO parameters
        """
        if self._parameter_schema is not None:
            return self._parameter_schema
        
        self._parameter_schema = {
            "quick": {
                "type": "boolean",
                "description": "Run quick version for testing",
                "default": True
            },
            "dephasing_rate": {
                "type": "float",
                "description": "Dephasing rate (gamma) in ps^-1",
                "range": [0.1, 100.0],
                "default": 10.0
            },
            "simulation_time": {
                "type": "float", 
                "description": "Total simulation time in ps",
                "range": [0.1, 10.0],
                "default": 1.0
            },
            "num_sites": {
                "type": "integer",
                "description": "Number of sites in FMO complex",
                "range": [3, 8],
                "default": 4
            },
            "temperature": {
                "type": "float",
                "description": "Temperature in Kelvin",
                "range": [77, 300],
                "default": 300
            },
            "coupling_strength": {
                "type": "float",
                "description": "Inter-site coupling strength scaling factor",
                "range": [0.1, 2.0],
                "default": 1.0
            }
        }
        
        return self._parameter_schema
    
    def _execute_project(self, param_file: str, params: Dict[str, Any]) -> Any:
        """
        Execute the FMO project with parameters.
        
        Args:
            param_file: Path to parameter file
            params: Parameter dictionary
            
        Returns:
            Execution result with FMO-specific handling
        """
        # Modify the FMO project execution to accept orchestration parameters
        cmd = [sys.executable, str(self.project_path / "main.py")]
        
        # Always use quick mode for orchestration
        cmd.append("--quick")
        
        # Set up environment with FMO-specific parameters
        env = os.environ.copy()
        
        # Map orchestration parameters to FMO environment variables
        param_mapping = {
            "dephasing_rate": "FMO_DEPHASING_RATE",
            "simulation_time": "FMO_SIMULATION_TIME", 
            "num_sites": "FMO_NUM_SITES",
            "temperature": "FMO_TEMPERATURE",
            "coupling_strength": "FMO_COUPLING_STRENGTH"
        }
        
        for orch_param, env_var in param_mapping.items():
            if orch_param in params:
                env[env_var] = str(params[orch_param])
        
        # Also set the parameter file path
        env["ORCH_PARAM_FILE"] = param_file
        
        # Execute with extended timeout for quantum simulations
        import subprocess
        result = subprocess.run(
            cmd,
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
            env=env,
            timeout=600  # 10 minute timeout for quantum simulations
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FMO project execution failed: {result.stderr}")
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "project_type": "fmo"
        }
    
    def extract_metrics(self, result: Any) -> Dict[str, float]:
        """
        Extract FMO-specific metrics from project output.
        
        Args:
            result: Raw result from FMO project execution
            
        Returns:
            Dictionary of standardized FMO metrics
        """
        metrics = {}
        
        if isinstance(result, dict) and "stdout" in result:
            stdout = result["stdout"]
            
            # FMO-specific metric extraction patterns
            patterns = {
                "transport_efficiency": r"efficiency[:\s]+([0-9.]+)",
                "final_efficiency": r"final efficiency[:\s]+([0-9.]+)",
                "minimum_efficiency": r"minimum efficiency[:\s]+([0-9.]+)",
                "enhancement_factor": r"enhancement[:\s]+([0-9.]+)%",
                "simulation_time": r"simulation time[:\s]+([0-9.]+)",
                "convergence_error": r"convergence error[:\s]+([0-9.e-]+)",
                "leakage_rate": r"leakage[:\s]+([0-9.e-]+)"
            }
            
            for metric_name, pattern in patterns.items():
                matches = re.findall(pattern, stdout, re.IGNORECASE)
                if matches:
                    try:
                        # Take the last match (most recent/final value)
                        value = float(matches[-1])
                        metrics[metric_name] = value
                    except ValueError:
                        continue
            
            # Look for quantitative results in the output
            lines = stdout.split('\n')
            for line in lines:
                line = line.strip()
                
                # Pattern: "Quantitative Enhancement: +X.X% relative increase"
                if "quantitative enhancement" in line.lower():
                    match = re.search(r"([+-]?[0-9.]+)%", line)
                    if match:
                        metrics["quantitative_enhancement"] = float(match.group(1))
                
                # Pattern: efficiency values
                if "efficiency" in line.lower() and ":" in line:
                    try:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            value_part = parts[1].strip()
                            # Extract numeric value
                            match = re.search(r"([0-9.]+)", value_part)
                            if match:
                                metrics["transport_efficiency"] = float(match.group(1))
                    except ValueError:
                        continue
        
        # Add FMO-specific derived metrics
        if "minimum_efficiency" in metrics and "final_efficiency" in metrics:
            min_eff = metrics["minimum_efficiency"]
            final_eff = metrics["final_efficiency"]
            if min_eff > 0:
                metrics["noise_enhancement_ratio"] = final_eff / min_eff
        
        # Ensure we have at least one metric
        if not metrics:
            # Default success metric
            success = 1.0 if isinstance(result, dict) and result.get("returncode") == 0 else 0.0
            metrics["execution_success"] = success
            
            # Try to extract any numeric values as fallback
            if isinstance(result, dict) and "stdout" in result:
                numbers = re.findall(r"([0-9.]+)", result["stdout"])
                if numbers:
                    # Use the last number found as a general metric
                    try:
                        metrics["final_value"] = float(numbers[-1])
                    except ValueError:
                        pass
        
        return metrics
    
    def validate_compatibility(self) -> Dict[str, Any]:
        """
        Validate FMO project compatibility.
        
        Returns:
            Compatibility report with FMO-specific checks
        """
        report = super().validate_compatibility()
        
        # Add FMO-specific compatibility checks
        fmo_py = self.project_path / "fmo.py"
        if not fmo_py.exists():
            report["issues"].append("fmo.py not found")
        
        # Check for FMO-specific requirements
        requirements_file = self.project_path / "requirements_production.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read()
                    required_packages = ["numpy", "scipy", "matplotlib"]
                    missing_packages = []
                    for package in required_packages:
                        if package not in content.lower():
                            missing_packages.append(package)
                    
                    if missing_packages:
                        report["warnings"].append(f"Missing recommended packages: {missing_packages}")
            except Exception:
                report["warnings"].append("Could not read requirements file")
        
        # Update compatibility based on FMO-specific issues
        report["compatible"] = len(report["issues"]) == 0
        report["project_type"] = "fmo"
        
        return report