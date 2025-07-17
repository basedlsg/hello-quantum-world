"""
Core interfaces for the experiment orchestration system.

This module defines the abstract base classes that establish contracts
for different components of the orchestration system.
"""

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, List

from .models import (
    Experiment,
    ExperimentResult,
    OptimizationRecommendation,
    SweepConfiguration,
)


class IExperimentExecutor(ABC):
    """Interface for executing experiments on different backends."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def estimate_duration(self, experiment: Experiment) -> timedelta:
        """
        Estimate how long an experiment will take to execute.
        
        Args:
            experiment: The experiment to estimate
            
        Returns:
            Estimated execution duration
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, experiment: Experiment) -> float:
        """
        Estimate the cost of executing an experiment.
        
        Args:
            experiment: The experiment to estimate
            
        Returns:
            Estimated cost in USD
        """
        pass
    
    @abstractmethod
    def can_execute(self, experiment: Experiment) -> bool:
        """
        Check if this executor can handle the given experiment.
        
        Args:
            experiment: The experiment to check
            
        Returns:
            True if this executor can handle the experiment
        """
        pass


class IResultAnalyzer(ABC):
    """Interface for analyzing experiment results."""
    
    @abstractmethod
    def analyze_single(self, result: ExperimentResult) -> Dict[str, Any]:
        """
        Analyze a single experiment result.
        
        Args:
            result: The experiment result to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    @abstractmethod
    def analyze_batch(self, results: List[ExperimentResult]) -> Dict[str, Any]:
        """
        Analyze a batch of experiment results.
        
        Args:
            results: List of experiment results to analyze
            
        Returns:
            Dictionary containing batch analysis results
        """
        pass
    
    @abstractmethod
    def compare_cross_project(
        self, 
        results: Dict[str, List[ExperimentResult]]
    ) -> Dict[str, Any]:
        """
        Compare results across different projects.
        
        Args:
            results: Dictionary mapping project names to their results
            
        Returns:
            Dictionary containing cross-project comparison results
        """
        pass
    
    @abstractmethod
    def generate_recommendations(
        self, 
        results: List[ExperimentResult]
    ) -> OptimizationRecommendation:
        """
        Generate optimization recommendations based on results.
        
        Args:
            results: List of experiment results to analyze
            
        Returns:
            OptimizationRecommendation with suggested improvements
        """
        pass


class IProjectAdapter(ABC):
    """Interface for adapting existing projects to the orchestration system."""
    
    @abstractmethod
    def adapt_project(self, project_path: str) -> bool:
        """
        Adapt a project for orchestration.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            True if adaptation was successful
        """
        pass
    
    @abstractmethod
    def execute_with_parameters(
        self, 
        params: Dict[str, Any]
    ) -> ExperimentResult:
        """
        Execute the project with given parameters.
        
        Args:
            params: Dictionary of parameter values
            
        Returns:
            ExperimentResult containing the execution results
        """
        pass
    
    @abstractmethod
    def extract_metrics(self, result: Any) -> Dict[str, float]:
        """
        Extract standardized metrics from project output.
        
        Args:
            result: Raw result from project execution
            
        Returns:
            Dictionary of standardized metrics
        """
        pass
    
    @abstractmethod
    def validate_compatibility(self) -> Dict[str, Any]:
        """
        Validate that the project is compatible with orchestration.
        
        Returns:
            Dictionary containing compatibility report
        """
        pass
    
    @abstractmethod
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the parameter schema for this project.
        
        Returns:
            Dictionary describing available parameters and their types
        """
        pass


class IProgressMonitor(ABC):
    """Interface for monitoring experiment progress."""
    
    @abstractmethod
    def start_monitoring(self, execution_id: str) -> None:
        """
        Start monitoring an execution.
        
        Args:
            execution_id: ID of the execution to monitor
        """
        pass
    
    @abstractmethod
    def update_progress(
        self, 
        execution_id: str, 
        progress: float, 
        current_results: List[ExperimentResult]
    ) -> None:
        """
        Update progress information.
        
        Args:
            execution_id: ID of the execution
            progress: Progress percentage (0-100)
            current_results: Current experiment results
        """
        pass
    
    @abstractmethod
    def stop_monitoring(self, execution_id: str) -> None:
        """
        Stop monitoring an execution.
        
        Args:
            execution_id: ID of the execution to stop monitoring
        """
        pass


class IResourceManager(ABC):
    """Interface for managing compute resources."""
    
    @abstractmethod
    def get_available_resources(self) -> Dict[str, Any]:
        """
        Get information about available compute resources.
        
        Returns:
            Dictionary describing available resources
        """
        pass
    
    @abstractmethod
    def allocate_resources(
        self, 
        experiments: List[Experiment]
    ) -> Dict[str, Any]:
        """
        Allocate resources for a list of experiments.
        
        Args:
            experiments: List of experiments needing resources
            
        Returns:
            Dictionary describing resource allocation
        """
        pass
    
    @abstractmethod
    def check_service_limits(self) -> Dict[str, Any]:
        """
        Check current service limits and usage.
        
        Returns:
            Dictionary containing service limit information
        """
        pass
    
    @abstractmethod
    def estimate_costs(self, experiments: List[Experiment]) -> float:
        """
        Estimate total cost for a list of experiments.
        
        Args:
            experiments: List of experiments to estimate
            
        Returns:
            Total estimated cost in USD
        """
        pass