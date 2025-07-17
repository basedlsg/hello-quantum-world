"""
Intelligent Experiment Orchestration System

A comprehensive platform for coordinating quantum computing experiments
across multiple projects with adaptive optimization and resource management.
"""

__version__ = "0.1.0"
__author__ = "Quantum Research Team"

from .core.models import (
    SweepConfiguration,
    ExperimentResult,
    OptimizationRecommendation,
    ExperimentStatus,
    ParameterRange,
)

from .core.interfaces import (
    IExperimentExecutor,
    IResultAnalyzer,
    IProjectAdapter,
)

__all__ = [
    "SweepConfiguration",
    "ExperimentResult", 
    "OptimizationRecommendation",
    "ExperimentStatus",
    "ParameterRange",
    "IExperimentExecutor",
    "IResultAnalyzer", 
    "IProjectAdapter",
]