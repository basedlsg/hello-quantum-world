"""
Core data models for the experiment orchestration system.

This module defines the fundamental data structures used throughout
the orchestration system for configuration, results, and optimization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import uuid
import hashlib
import json


class ExperimentStatus(Enum):
    """Status of an individual experiment."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EARLY_STOPPED = "early_stopped"


class ParameterType(Enum):
    """Types of parameter ranges supported."""
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"


@dataclass
class ParameterRange:
    """Defines a parameter range for sweep generation."""
    name: str
    param_type: ParameterType
    min_value: Optional[Union[float, int]] = None
    max_value: Optional[Union[float, int]] = None
    num_points: Optional[int] = None
    values: Optional[List[Any]] = None
    
    def __post_init__(self):
        """Validate parameter range configuration."""
        if self.param_type in [ParameterType.LINEAR, ParameterType.LOGARITHMIC]:
            if self.min_value is None or self.max_value is None or self.num_points is None:
                raise ValueError(f"Linear/logarithmic parameters require min_value, max_value, and num_points")
        elif self.param_type == ParameterType.CATEGORICAL:
            if not self.values:
                raise ValueError("Categorical parameters require values list")
        elif self.param_type == ParameterType.BOOLEAN:
            self.values = [True, False]
    
    def generate_values(self) -> List[Any]:
        """Generate parameter values based on the range configuration."""
        if self.param_type == ParameterType.LINEAR:
            import numpy as np
            return np.linspace(self.min_value, self.max_value, self.num_points).tolist()
        elif self.param_type == ParameterType.LOGARITHMIC:
            import numpy as np
            return np.logspace(
                np.log10(self.min_value), 
                np.log10(self.max_value), 
                self.num_points
            ).tolist()
        elif self.param_type in [ParameterType.CATEGORICAL, ParameterType.BOOLEAN]:
            return self.values
        else:
            raise ValueError(f"Unknown parameter type: {self.param_type}")


@dataclass
class SweepConfiguration:
    """Configuration for a parameter sweep across one or more projects."""
    name: str
    project_paths: List[str]
    parameters: Dict[str, ParameterRange]
    objectives: List[str]
    constraints: Dict[str, Any] = field(default_factory=dict)
    budget_limit: Optional[float] = None
    max_duration: Optional[timedelta] = None
    adaptive_sampling: bool = True
    cross_project_analysis: bool = False
    max_concurrent_experiments: int = 4
    random_seed: int = 1337
    
    def __post_init__(self):
        """Validate sweep configuration."""
        if not self.project_paths:
            raise ValueError("At least one project path must be specified")
        if not self.parameters:
            raise ValueError("At least one parameter must be specified")
        if not self.objectives:
            raise ValueError("At least one objective must be specified")
    
    def generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """Generate all parameter combinations for the sweep."""
        import itertools
        
        param_values = {}
        for param_name, param_range in self.parameters.items():
            param_values[param_name] = param_range.generate_values()
        
        # Generate Cartesian product of all parameter values
        param_names = list(param_values.keys())
        value_combinations = itertools.product(*[param_values[name] for name in param_names])
        
        combinations = []
        for values in value_combinations:
            combination = dict(zip(param_names, values))
            combinations.append(combination)
        
        return combinations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "project_paths": self.project_paths,
            "parameters": {
                name: {
                    "name": param.name,
                    "param_type": param.param_type.value,
                    "min_value": param.min_value,
                    "max_value": param.max_value,
                    "num_points": param.num_points,
                    "values": param.values,
                }
                for name, param in self.parameters.items()
            },
            "objectives": self.objectives,
            "constraints": self.constraints,
            "budget_limit": self.budget_limit,
            "max_duration": self.max_duration.total_seconds() if self.max_duration else None,
            "adaptive_sampling": self.adaptive_sampling,
            "cross_project_analysis": self.cross_project_analysis,
            "max_concurrent_experiments": self.max_concurrent_experiments,
            "random_seed": self.random_seed,
        }


@dataclass
class ExperimentResult:
    """Result of a single experiment execution."""
    experiment_id: str
    project_name: str
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    execution_time: float
    cost: Optional[float] = None
    status: ExperimentStatus = ExperimentStatus.COMPLETED
    error_message: Optional[str] = None
    reproducibility_hash: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate reproducibility hash if not provided."""
        if not self.reproducibility_hash:
            self.reproducibility_hash = self._generate_reproducibility_hash()
    
    def _generate_reproducibility_hash(self) -> str:
        """Generate a hash for reproducibility tracking."""
        hash_data = {
            "project_name": self.project_name,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat(),
        }
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experiment_id": self.experiment_id,
            "project_name": self.project_name,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "execution_time": self.execution_time,
            "cost": self.cost,
            "status": self.status.value,
            "error_message": self.error_message,
            "reproducibility_hash": self.reproducibility_hash,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ParameterRegion:
    """Defines a region in parameter space for optimization."""
    center: Dict[str, Any]
    bounds: Dict[str, tuple]
    priority: float = 1.0
    confidence: float = 0.5


@dataclass
class ResourceAllocation:
    """Resource allocation recommendation."""
    executor_type: str
    max_concurrent: int
    priority: float


@dataclass
class OptimizationRecommendation:
    """Recommendations from the adaptive optimizer."""
    priority_adjustments: Dict[str, float] = field(default_factory=dict)
    early_stop_candidates: List[str] = field(default_factory=list)
    promising_regions: List[ParameterRegion] = field(default_factory=list)
    resource_reallocation: Dict[str, ResourceAllocation] = field(default_factory=dict)
    confidence_level: float = 0.5
    reasoning: str = ""


@dataclass
class Experiment:
    """Represents a single experiment to be executed."""
    experiment_id: str
    project_path: str
    parameters: Dict[str, Any]
    objectives: List[str]
    priority: float = 1.0
    estimated_duration: Optional[timedelta] = None
    estimated_cost: Optional[float] = None
    
    def __post_init__(self):
        """Generate experiment ID if not provided."""
        if not self.experiment_id:
            self.experiment_id = str(uuid.uuid4())
    
    def __lt__(self, other):
        """Less than comparison for priority queue ordering."""
        if not isinstance(other, Experiment):
            return NotImplemented
        # Higher priority experiments should come first (reverse order)
        if self.priority != other.priority:
            return self.priority > other.priority
        # If priorities are equal, compare by experiment_id for consistent ordering
        return self.experiment_id < other.experiment_id
    
    def __eq__(self, other):
        """Equality comparison."""
        if not isinstance(other, Experiment):
            return NotImplemented
        return self.experiment_id == other.experiment_id


@dataclass
class SweepExecution:
    """Tracks the execution of a parameter sweep."""
    execution_id: str
    sweep_config: SweepConfiguration
    experiments: List[Experiment] = field(default_factory=list)
    results: List[ExperimentResult] = field(default_factory=list)
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_cost: float = 0.0
    
    def __post_init__(self):
        """Generate execution ID if not provided."""
        if not self.execution_id:
            self.execution_id = str(uuid.uuid4())
    
    @property
    def progress(self) -> float:
        """Calculate completion progress as a percentage."""
        if not self.experiments:
            return 0.0
        completed = len([r for r in self.results if r.status in [
            ExperimentStatus.COMPLETED, 
            ExperimentStatus.FAILED, 
            ExperimentStatus.EARLY_STOPPED
        ]])
        return (completed / len(self.experiments)) * 100.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of completed experiments."""
        if not self.results:
            return 0.0
        completed = [r for r in self.results if r.status != ExperimentStatus.PENDING]
        if not completed:
            return 0.0
        successful = [r for r in completed if r.status == ExperimentStatus.COMPLETED]
        return (len(successful) / len(completed)) * 100.0