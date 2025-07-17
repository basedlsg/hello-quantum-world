"""
Unit tests for the experiment scheduler.
"""

import time
import unittest
from datetime import timedelta
from unittest.mock import Mock, patch

from orchestration.core.models import (
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    ParameterRange,
    ParameterType,
    SweepConfiguration,
)
from orchestration.core.scheduler import ExperimentScheduler
from orchestration.executors.local_executor import LocalExecutor


class MockExecutor:
    """Mock executor for testing."""
    
    def __init__(self, execution_time: float = 0.1, should_fail: bool = False):
        self.execution_time = execution_time
        self.should_fail = should_fail
        self.executed_experiments = []
    
    def execute(self, experiment: Experiment) -> ExperimentResult:
        """Mock execute method."""
        time.sleep(self.execution_time)
        self.executed_experiments.append(experiment)
        
        if self.should_fail:
            raise RuntimeError("Mock execution failure")
        
        return ExperimentResult(
            experiment_id=experiment.experiment_id,
            project_name="test_project",
            parameters=experiment.parameters,
            metrics={"test_metric": 1.0},
            execution_time=self.execution_time,
            status=ExperimentStatus.COMPLETED,
        )
    
    def estimate_duration(self, experiment: Experiment) -> timedelta:
        """Mock duration estimation."""
        return timedelta(seconds=self.execution_time)
    
    def estimate_cost(self, experiment: Experiment) -> float:
        """Mock cost estimation."""
        return 0.0
    
    def can_execute(self, experiment: Experiment) -> bool:
        """Mock compatibility check."""
        return True


class TestExperimentScheduler(unittest.TestCase):
    """Test cases for ExperimentScheduler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_executor = MockExecutor()
        self.scheduler = ExperimentScheduler(
            executors=[self.mock_executor],
            max_concurrent_experiments=2
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.scheduler.stop_scheduler()
    
    def test_schedule_simple_sweep(self):
        """Test scheduling a simple parameter sweep."""
        # Create sweep configuration
        config = SweepConfiguration(
            name="test_sweep",
            project_paths=["test_project"],
            parameters={
                "param1": ParameterRange(
                    name="param1",
                    param_type=ParameterType.LINEAR,
                    min_value=0.0,
                    max_value=1.0,
                    num_points=3
                )
            },
            objectives=["test_metric"]
        )
        
        # Schedule sweep
        execution = self.scheduler.schedule_sweep(config)
        
        # Verify execution was created
        self.assertIsNotNone(execution)
        self.assertEqual(execution.sweep_config.name, "test_sweep")
        self.assertEqual(len(execution.experiments), 3)  # 3 parameter points
        
        # Wait for completion
        timeout = 5.0
        start_time = time.time()
        while execution.progress < 100.0 and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        # Verify completion
        self.assertEqual(execution.progress, 100.0)
        self.assertEqual(len(execution.results), 3)
        self.assertEqual(execution.status, "completed")
    
    def test_multiple_projects(self):
        """Test sweep with multiple projects."""
        config = SweepConfiguration(
            name="multi_project_sweep",
            project_paths=["project1", "project2"],
            parameters={
                "param1": ParameterRange(
                    name="param1",
                    param_type=ParameterType.CATEGORICAL,
                    values=[1, 2]
                )
            },
            objectives=["test_metric"]
        )
        
        execution = self.scheduler.schedule_sweep(config)
        
        # Should have 2 projects × 2 parameter values = 4 experiments
        self.assertEqual(len(execution.experiments), 4)
        
        # Wait for completion
        timeout = 5.0
        start_time = time.time()
        while execution.progress < 100.0 and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        self.assertEqual(execution.progress, 100.0)
        self.assertEqual(len(execution.results), 4)
    
    def test_experiment_failure_handling(self):
        """Test handling of experiment failures."""
        # Create failing executor
        failing_executor = MockExecutor(should_fail=True)
        scheduler = ExperimentScheduler(
            executors=[failing_executor],
            max_concurrent_experiments=1
        )
        
        try:
            config = SweepConfiguration(
                name="failing_sweep",
                project_paths=["test_project"],
                parameters={
                    "param1": ParameterRange(
                        name="param1",
                        param_type=ParameterType.CATEGORICAL,
                        values=[1]
                    )
                },
                objectives=["test_metric"]
            )
            
            execution = scheduler.schedule_sweep(config)
            
            # Wait for completion
            timeout = 5.0
            start_time = time.time()
            while execution.progress < 100.0 and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            # Verify failure was handled
            self.assertEqual(len(execution.results), 1)
            self.assertEqual(execution.results[0].status, ExperimentStatus.FAILED)
            self.assertIsNotNone(execution.results[0].error_message)
            
        finally:
            scheduler.stop_scheduler()
    
    def test_execution_control(self):
        """Test pause/resume/cancel functionality."""
        config = SweepConfiguration(
            name="control_test",
            project_paths=["test_project"],
            parameters={
                "param1": ParameterRange(
                    name="param1",
                    param_type=ParameterType.LINEAR,
                    min_value=0.0,
                    max_value=1.0,
                    num_points=5
                )
            },
            objectives=["test_metric"]
        )
        
        execution = self.scheduler.schedule_sweep(config)
        execution_id = execution.execution_id
        
        # Test pause
        self.assertTrue(self.scheduler.pause_execution(execution_id))
        self.assertEqual(execution.status, "paused")
        
        # Test resume
        self.assertTrue(self.scheduler.resume_execution(execution_id))
        self.assertEqual(execution.status, "running")
        
        # Test cancel
        self.assertTrue(self.scheduler.cancel_execution(execution_id))
        self.assertEqual(execution.status, "cancelled")
    
    def test_statistics(self):
        """Test scheduler statistics collection."""
        initial_stats = self.scheduler.get_statistics()
        self.assertEqual(initial_stats["total_experiments_executed"], 0)
        
        # Run a simple sweep
        config = SweepConfiguration(
            name="stats_test",
            project_paths=["test_project"],
            parameters={
                "param1": ParameterRange(
                    name="param1",
                    param_type=ParameterType.CATEGORICAL,
                    values=[1, 2]
                )
            },
            objectives=["test_metric"]
        )
        
        execution = self.scheduler.schedule_sweep(config)
        
        # Wait for completion
        timeout = 5.0
        start_time = time.time()
        while execution.progress < 100.0 and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        # Check updated statistics
        final_stats = self.scheduler.get_statistics()
        self.assertEqual(final_stats["total_experiments_executed"], 2)
        self.assertGreater(final_stats["total_execution_time"], 0)
    
    def test_parameter_generation(self):
        """Test parameter combination generation."""
        config = SweepConfiguration(
            name="param_test",
            project_paths=["test_project"],
            parameters={
                "linear_param": ParameterRange(
                    name="linear_param",
                    param_type=ParameterType.LINEAR,
                    min_value=0.0,
                    max_value=2.0,
                    num_points=3
                ),
                "categorical_param": ParameterRange(
                    name="categorical_param",
                    param_type=ParameterType.CATEGORICAL,
                    values=["a", "b"]
                )
            },
            objectives=["test_metric"]
        )
        
        execution = self.scheduler.schedule_sweep(config)
        
        # Should have 3 × 2 = 6 parameter combinations
        self.assertEqual(len(execution.experiments), 6)
        
        # Verify parameter values
        param_sets = [exp.parameters for exp in execution.experiments]
        linear_values = set(params["linear_param"] for params in param_sets)
        categorical_values = set(params["categorical_param"] for params in param_sets)
        
        self.assertEqual(len(linear_values), 3)  # 3 linear points
        self.assertEqual(categorical_values, {"a", "b"})  # 2 categorical values


if __name__ == "__main__":
    unittest.main()