"""
Unit tests for core interfaces.

Tests interface definitions and contract compliance.
"""

import unittest
from abc import ABC
from datetime import timedelta
from typing import Any, Dict, List

from orchestration.core.interfaces import (
    IExperimentExecutor,
    IProjectAdapter,
    IProgressMonitor,
    IResourceManager,
    IResultAnalyzer,
)
from orchestration.core.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    OptimizationRecommendation,
)


class MockExperimentExecutor(IExperimentExecutor):
    """Mock implementation of IExperimentExecutor for testing."""
    
    def execute(self, experiment: Experiment) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            project_name="mock_project",
            parameters=experiment.parameters,
            metrics={"mock_metric": 0.5},
            execution_time=1.0
        )
    
    def estimate_duration(self, experiment: Experiment) -> timedelta:
        return timedelta(seconds=10)
    
    def estimate_cost(self, experiment: Experiment) -> float:
        return 1.0
    
    def can_execute(self, experiment: Experiment) -> bool:
        return True


class MockResultAnalyzer(IResultAnalyzer):
    """Mock implementation of IResultAnalyzer for testing."""
    
    def analyze_single(self, result: ExperimentResult) -> Dict[str, Any]:
        return {"analysis": "single_result"}
    
    def analyze_batch(self, results: List[ExperimentResult]) -> Dict[str, Any]:
        return {"analysis": "batch_results", "count": len(results)}
    
    def compare_cross_project(
        self, 
        results: Dict[str, List[ExperimentResult]]
    ) -> Dict[str, Any]:
        return {"analysis": "cross_project", "projects": list(results.keys())}
    
    def generate_recommendations(
        self, 
        results: List[ExperimentResult]
    ) -> OptimizationRecommendation:
        return OptimizationRecommendation(
            confidence_level=0.5,
            reasoning="Mock recommendation"
        )


class MockProjectAdapter(IProjectAdapter):
    """Mock implementation of IProjectAdapter for testing."""
    
    def adapt_project(self, project_path: str) -> bool:
        return True
    
    def execute_with_parameters(
        self, 
        params: Dict[str, Any]
    ) -> ExperimentResult:
        return ExperimentResult(
            experiment_id="mock_exp",
            project_name="mock_project",
            parameters=params,
            metrics={"mock_metric": 0.5},
            execution_time=1.0
        )
    
    def extract_metrics(self, result: Any) -> Dict[str, float]:
        return {"extracted_metric": 0.5}
    
    def validate_compatibility(self) -> Dict[str, Any]:
        return {"compatible": True}
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {"param1": {"type": "float", "range": [0, 1]}}


class MockProgressMonitor(IProgressMonitor):
    """Mock implementation of IProgressMonitor for testing."""
    
    def start_monitoring(self, execution_id: str) -> None:
        pass
    
    def update_progress(
        self, 
        execution_id: str, 
        progress: float, 
        current_results: List[ExperimentResult]
    ) -> None:
        pass
    
    def stop_monitoring(self, execution_id: str) -> None:
        pass


class MockResourceManager(IResourceManager):
    """Mock implementation of IResourceManager for testing."""
    
    def get_available_resources(self) -> Dict[str, Any]:
        return {"cpu_cores": 4, "memory_gb": 16}
    
    def allocate_resources(
        self, 
        experiments: List[Experiment]
    ) -> Dict[str, Any]:
        return {"allocated": len(experiments)}
    
    def check_service_limits(self) -> Dict[str, Any]:
        return {"limits_ok": True}
    
    def estimate_costs(self, experiments: List[Experiment]) -> float:
        return len(experiments) * 1.0


class TestInterfaces(unittest.TestCase):
    """Test interface definitions and implementations."""
    
    def test_experiment_executor_interface(self):
        """Test IExperimentExecutor interface compliance."""
        executor = MockExperimentExecutor()
        
        # Test that it's an instance of the interface
        self.assertIsInstance(executor, IExperimentExecutor)
        
        # Test execute method
        experiment = Experiment(
            experiment_id="test_exp",
            project_path="test_project",
            parameters={"param1": 0.5},
            objectives=["accuracy"]
        )
        
        result = executor.execute(experiment)
        self.assertIsInstance(result, ExperimentResult)
        self.assertEqual(result.experiment_id, "test_exp")
        
        # Test estimate methods
        duration = executor.estimate_duration(experiment)
        self.assertIsInstance(duration, timedelta)
        
        cost = executor.estimate_cost(experiment)
        self.assertIsInstance(cost, float)
        
        # Test can_execute method
        can_execute = executor.can_execute(experiment)
        self.assertIsInstance(can_execute, bool)
    
    def test_result_analyzer_interface(self):
        """Test IResultAnalyzer interface compliance."""
        analyzer = MockResultAnalyzer()
        
        # Test that it's an instance of the interface
        self.assertIsInstance(analyzer, IResultAnalyzer)
        
        # Create test result
        result = ExperimentResult(
            experiment_id="test_exp",
            project_name="test_project",
            parameters={"param1": 0.5},
            metrics={"accuracy": 0.9},
            execution_time=10.0
        )
        
        # Test analyze_single
        single_analysis = analyzer.analyze_single(result)
        self.assertIsInstance(single_analysis, dict)
        
        # Test analyze_batch
        batch_analysis = analyzer.analyze_batch([result])
        self.assertIsInstance(batch_analysis, dict)
        self.assertEqual(batch_analysis["count"], 1)
        
        # Test compare_cross_project
        cross_analysis = analyzer.compare_cross_project({"project1": [result]})
        self.assertIsInstance(cross_analysis, dict)
        
        # Test generate_recommendations
        recommendations = analyzer.generate_recommendations([result])
        self.assertIsInstance(recommendations, OptimizationRecommendation)
    
    def test_project_adapter_interface(self):
        """Test IProjectAdapter interface compliance."""
        adapter = MockProjectAdapter()
        
        # Test that it's an instance of the interface
        self.assertIsInstance(adapter, IProjectAdapter)
        
        # Test adapt_project
        adapted = adapter.adapt_project("test_project")
        self.assertIsInstance(adapted, bool)
        
        # Test execute_with_parameters
        result = adapter.execute_with_parameters({"param1": 0.5})
        self.assertIsInstance(result, ExperimentResult)
        
        # Test extract_metrics
        metrics = adapter.extract_metrics("mock_result")
        self.assertIsInstance(metrics, dict)
        
        # Test validate_compatibility
        compatibility = adapter.validate_compatibility()
        self.assertIsInstance(compatibility, dict)
        
        # Test get_parameter_schema
        schema = adapter.get_parameter_schema()
        self.assertIsInstance(schema, dict)
    
    def test_progress_monitor_interface(self):
        """Test IProgressMonitor interface compliance."""
        monitor = MockProgressMonitor()
        
        # Test that it's an instance of the interface
        self.assertIsInstance(monitor, IProgressMonitor)
        
        # Test methods (they should not raise exceptions)
        monitor.start_monitoring("test_exec")
        monitor.update_progress("test_exec", 50.0, [])
        monitor.stop_monitoring("test_exec")
    
    def test_resource_manager_interface(self):
        """Test IResourceManager interface compliance."""
        manager = MockResourceManager()
        
        # Test that it's an instance of the interface
        self.assertIsInstance(manager, IResourceManager)
        
        # Test get_available_resources
        resources = manager.get_available_resources()
        self.assertIsInstance(resources, dict)
        
        # Test allocate_resources
        experiment = Experiment(
            experiment_id="test_exp",
            project_path="test_project",
            parameters={"param1": 0.5},
            objectives=["accuracy"]
        )
        allocation = manager.allocate_resources([experiment])
        self.assertIsInstance(allocation, dict)
        
        # Test check_service_limits
        limits = manager.check_service_limits()
        self.assertIsInstance(limits, dict)
        
        # Test estimate_costs
        costs = manager.estimate_costs([experiment])
        self.assertIsInstance(costs, float)
    
    def test_interface_inheritance(self):
        """Test that interfaces properly inherit from ABC."""
        # All interfaces should be abstract base classes
        self.assertTrue(issubclass(IExperimentExecutor, ABC))
        self.assertTrue(issubclass(IResultAnalyzer, ABC))
        self.assertTrue(issubclass(IProjectAdapter, ABC))
        self.assertTrue(issubclass(IProgressMonitor, ABC))
        self.assertTrue(issubclass(IResourceManager, ABC))
    
    def test_abstract_methods_enforcement(self):
        """Test that abstract methods are properly enforced."""
        # Attempting to instantiate abstract classes should raise TypeError
        with self.assertRaises(TypeError):
            IExperimentExecutor()
        
        with self.assertRaises(TypeError):
            IResultAnalyzer()
        
        with self.assertRaises(TypeError):
            IProjectAdapter()
        
        with self.assertRaises(TypeError):
            IProgressMonitor()
        
        with self.assertRaises(TypeError):
            IResourceManager()


if __name__ == "__main__":
    unittest.main()