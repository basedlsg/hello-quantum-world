"""
Local experiment executor for running experiments on the local machine.
"""

import logging
import os
import subprocess
import tempfile
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List

from ..adapters.base import ProjectAdapter
from ..core.interfaces import IExperimentExecutor
from ..core.models import Experiment, ExperimentResult, ExperimentStatus


logger = logging.getLogger(__name__)


class LocalExecutor(IExperimentExecutor):
    """
    Executor for running experiments on the local machine.
    
    This executor uses project adapters to run experiments with different
    parameter configurations and extract standardized results.
    """
    
    def __init__(self, max_execution_time: int = 3600):
        """
        Initialize the local executor.
        
        Args:
            max_execution_time: Maximum execution time in seconds
        """
        self.max_execution_time = max_execution_time
        self.adapters: Dict[str, ProjectAdapter] = {}
    
    def execute(self, experiment: Experiment) -> ExperimentResult:
        """
        Execute a single experiment and return the result.
        
        Args:
            experiment: The experiment to execute
            
        Returns:
            ExperimentResult containing metrics and execution details
            
        Raises:
            ExecutionError: If the experiment fails to execute
        """
        logger.info(f"Executing experiment {experiment.experiment_id}")
        start_time = time.time()
        
        try:
            # Get or create adapter for this project
            adapter = self._get_adapter(experiment.project_path)
            
            # Execute experiment with parameters
            result = adapter.execute_with_parameters(experiment.parameters)
            
            # Update result with experiment metadata
            result.experiment_id = experiment.experiment_id
            result.execution_time = time.time() - start_time
            result.status = ExperimentStatus.COMPLETED
            
            logger.info(f"Experiment {experiment.experiment_id} completed successfully")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Experiment {experiment.experiment_id} failed: {e}")
            
            return ExperimentResult(
                experiment_id=experiment.experiment_id,
                project_name=Path(experiment.project_path).name,
                parameters=experiment.parameters,
                metrics={},
                execution_time=execution_time,
                status=ExperimentStatus.FAILED,
                error_message=str(e),
            )
    
    def estimate_duration(self, experiment: Experiment) -> timedelta:
        """
        Estimate how long an experiment will take to execute.
        
        Args:
            experiment: The experiment to estimate
            
        Returns:
            Estimated execution duration
        """
        # Simple heuristic based on project type and parameters
        base_time = 30  # Base 30 seconds
        
        # Add time based on parameter complexity
        param_complexity = len(experiment.parameters)
        complexity_time = param_complexity * 5
        
        # Add time based on project type
        project_name = Path(experiment.project_path).name.lower()
        if "fmo" in project_name:
            project_time = 60  # FMO experiments take longer
        elif "qec" in project_name:
            project_time = 45  # QEC experiments are moderate
        else:
            project_time = 30  # Default time
        
        total_seconds = base_time + complexity_time + project_time
        return timedelta(seconds=min(total_seconds, self.max_execution_time))
    
    def estimate_cost(self, experiment: Experiment) -> float:
        """
        Estimate the cost of executing an experiment.
        
        Args:
            experiment: The experiment to estimate
            
        Returns:
            Estimated cost in USD (0.0 for local execution)
        """
        # Local execution is free
        return 0.0
    
    def can_execute(self, experiment: Experiment) -> bool:
        """
        Check if this executor can handle the given experiment.
        
        Args:
            experiment: The experiment to check
            
        Returns:
            True if this executor can handle the experiment
        """
        try:
            # Check if project path exists
            project_path = Path(experiment.project_path)
            if not project_path.exists():
                return False
            
            # Try to create adapter
            adapter = self._get_adapter(experiment.project_path)
            compatibility = adapter.validate_compatibility()
            
            return compatibility.get("compatible", False)
            
        except Exception as e:
            logger.warning(f"Cannot execute experiment {experiment.experiment_id}: {e}")
            return False
    
    def _get_adapter(self, project_path: str) -> ProjectAdapter:
        """
        Get or create a project adapter for the given project path.
        
        Args:
            project_path: Path to the project
            
        Returns:
            ProjectAdapter instance
        """
        if project_path not in self.adapters:
            # Determine adapter type based on project
            project_name = Path(project_path).name.lower()
            
            if "fmo" in project_name:
                from ..adapters.fmo_adapter import FMOProjectAdapter
                adapter = FMOProjectAdapter(project_path)
            else:
                # Use base adapter for unknown projects
                adapter = ProjectAdapter(project_path)
            
            # Adapt the project
            if not adapter.adapt_project(project_path):
                raise RuntimeError(f"Failed to adapt project at {project_path}")
            
            self.adapters[project_path] = adapter
        
        return self.adapters[project_path]
    
    def cleanup(self) -> None:
        """Clean up resources used by the executor."""
        self.adapters.clear()
        logger.info("Local executor cleaned up")