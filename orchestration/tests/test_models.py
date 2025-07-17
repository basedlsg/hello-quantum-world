"""
Unit tests for core data models.

Tests data model validation, serialization, and core functionality.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from orchestration.core.models import (
    ExperimentResult,
    ExperimentStatus,
    Experiment,
    OptimizationRecommendation,
    ParameterRange,
    ParameterType,
    SweepConfiguration,
    SweepExecution,
)


class TestParameterRange(unittest.TestCase):
    """Test ParameterRange functionality."""
    
    def test_linear_parameter_range(self):
        """Test linear parameter range generation."""
        param_range = ParameterRange(
            name="test_param",
            param_type=ParameterType.LINEAR,
            min_value=0.0,
            max_value=1.0,
            num_points=5
        )
        
        values = param_range.generate_values()
        self.assertEqual(len(values), 5)
        self.assertAlmostEqual(values[0], 0.0)
        self.assertAlmostEqual(values[-1], 1.0)
        self.assertAlmostEqual(values[2], 0.5)
    
    def test_logarithmic_parameter_range(self):
        """Test logarithmic parameter range generation."""
        param_range = ParameterRange(
            name="test_param",
            param_type=ParameterType.LOGARITHMIC,
            min_value=1.0,
            max_value=100.0,
            num_points=3
        )
        
        values = param_range.generate_values()
        self.assertEqual(len(values), 3)
        self.assertAlmostEqual(values[0], 1.0)
        self.assertAlmostEqual(values[-1], 100.0)
        self.assertAlmostEqual(values[1], 10.0)
    
    def test_categorical_parameter_range(self):
        """Test categorical parameter range generation."""
        categories = ["option1", "option2", "option3"]
        param_range = ParameterRange(
            name="test_param",
            param_type=ParameterType.CATEGORICAL,
            values=categories
        )
        
        values = param_range.generate_values()
        self.assertEqual(values, categories)
    
    def test_boolean_parameter_range(self):
        """Test boolean parameter range generation."""
        param_range = ParameterRange(
            name="test_param",
            param_type=ParameterType.BOOLEAN
        )
        
        values = param_range.generate_values()
        self.assertEqual(set(values), {True, False})
    
    def test_invalid_linear_parameter_range(self):
        """Test validation of invalid linear parameter range."""
        with self.assertRaises(ValueError):
            ParameterRange(
                name="test_param",
                param_type=ParameterType.LINEAR,
                min_value=0.0
                # Missing max_value and num_points
            )
    
    def test_invalid_categorical_parameter_range(self):
        """Test validation of invalid categorical parameter range."""
        with self.assertRaises(ValueError):
            ParameterRange(
                name="test_param",
                param_type=ParameterType.CATEGORICAL
                # Missing values
            )


class TestSweepConfiguration(unittest.TestCase):
    """Test SweepConfiguration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.param1 = ParameterRange(
            name="param1",
            param_type=ParameterType.LINEAR,
            min_value=0.0,
            max_value=1.0,
            num_points=3
        )
        self.param2 = ParameterRange(
            name="param2",
            param_type=ParameterType.CATEGORICAL,
            values=["A", "B"]
        )
    
    def test_valid_sweep_configuration(self):
        """Test creation of valid sweep configuration."""
        config = SweepConfiguration(
            name="test_sweep",
            project_paths=["project1", "project2"],
            parameters={"param1": self.param1, "param2": self.param2},
            objectives=["accuracy", "speed"]
        )
        
        self.assertEqual(config.name, "test_sweep")
        self.assertEqual(len(config.project_paths), 2)
        self.assertEqual(len(config.parameters), 2)
        self.assertEqual(len(config.objectives), 2)
    
    def test_parameter_combination_generation(self):
        """Test parameter combination generation."""
        config = SweepConfiguration(
            name="test_sweep",
            project_paths=["project1"],
            parameters={"param1": self.param1, "param2": self.param2},
            objectives=["accuracy"]
        )
        
        combinations = config.generate_parameter_combinations()
        # 3 linear values × 2 categorical values = 6 combinations
        self.assertEqual(len(combinations), 6)
        
        # Check that all combinations have both parameters
        for combo in combinations:
            self.assertIn("param1", combo)
            self.assertIn("param2", combo)
            self.assertIn(combo["param2"], ["A", "B"])
    
    def test_invalid_sweep_configuration_no_projects(self):
        """Test validation of sweep configuration without projects."""
        with self.assertRaises(ValueError):
            SweepConfiguration(
                name="test_sweep",
                project_paths=[],  # Empty project paths
                parameters={"param1": self.param1},
                objectives=["accuracy"]
            )
    
    def test_invalid_sweep_configuration_no_parameters(self):
        """Test validation of sweep configuration without parameters."""
        with self.assertRaises(ValueError):
            SweepConfiguration(
                name="test_sweep",
                project_paths=["project1"],
                parameters={},  # Empty parameters
                objectives=["accuracy"]
            )
    
    def test_invalid_sweep_configuration_no_objectives(self):
        """Test validation of sweep configuration without objectives."""
        with self.assertRaises(ValueError):
            SweepConfiguration(
                name="test_sweep",
                project_paths=["project1"],
                parameters={"param1": self.param1},
                objectives=[]  # Empty objectives
            )
    
    def test_sweep_configuration_serialization(self):
        """Test sweep configuration serialization."""
        config = SweepConfiguration(
            name="test_sweep",
            project_paths=["project1"],
            parameters={"param1": self.param1},
            objectives=["accuracy"],
            budget_limit=100.0,
            max_duration=timedelta(hours=2)
        )
        
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict["name"], "test_sweep")
        self.assertEqual(config_dict["budget_limit"], 100.0)
        self.assertEqual(config_dict["max_duration"], 7200.0)  # 2 hours in seconds
        self.assertIn("param1", config_dict["parameters"])


class TestExperimentResult(unittest.TestCase):
    """Test ExperimentResult functionality."""
    
    def test_experiment_result_creation(self):
        """Test creation of experiment result."""
        result = ExperimentResult(
            experiment_id="test_exp_1",
            project_name="test_project",
            parameters={"param1": 0.5},
            metrics={"accuracy": 0.95, "speed": 1.2},
            execution_time=30.5
        )
        
        self.assertEqual(result.experiment_id, "test_exp_1")
        self.assertEqual(result.project_name, "test_project")
        self.assertEqual(result.parameters["param1"], 0.5)
        self.assertEqual(result.metrics["accuracy"], 0.95)
        self.assertEqual(result.execution_time, 30.5)
        self.assertEqual(result.status, ExperimentStatus.COMPLETED)
    
    def test_reproducibility_hash_generation(self):
        """Test automatic reproducibility hash generation."""
        result = ExperimentResult(
            experiment_id="test_exp_1",
            project_name="test_project",
            parameters={"param1": 0.5},
            metrics={"accuracy": 0.95},
            execution_time=30.5
        )
        
        self.assertIsNotNone(result.reproducibility_hash)
        self.assertEqual(len(result.reproducibility_hash), 16)
    
    def test_experiment_result_serialization(self):
        """Test experiment result serialization."""
        timestamp = datetime.now()
        result = ExperimentResult(
            experiment_id="test_exp_1",
            project_name="test_project",
            parameters={"param1": 0.5},
            metrics={"accuracy": 0.95},
            execution_time=30.5,
            cost=5.0,
            timestamp=timestamp
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict["experiment_id"], "test_exp_1")
        self.assertEqual(result_dict["cost"], 5.0)
        self.assertEqual(result_dict["status"], "completed")
        self.assertEqual(result_dict["timestamp"], timestamp.isoformat())


class TestSweepExecution(unittest.TestCase):
    """Test SweepExecution functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sweep_config = SweepConfiguration(
            name="test_sweep",
            project_paths=["project1"],
            parameters={
                "param1": ParameterRange(
                    name="param1",
                    param_type=ParameterType.LINEAR,
                    min_value=0.0,
                    max_value=1.0,
                    num_points=2
                )
            },
            objectives=["accuracy"]
        )
    
    def test_sweep_execution_creation(self):
        """Test creation of sweep execution."""
        execution = SweepExecution(
            execution_id="test_exec_1",
            sweep_config=self.sweep_config
        )
        
        self.assertEqual(execution.execution_id, "test_exec_1")
        self.assertEqual(execution.sweep_config.name, "test_sweep")
        self.assertEqual(execution.status, "pending")
        self.assertEqual(execution.progress, 0.0)
    
    def test_progress_calculation(self):
        """Test progress calculation."""
        execution = SweepExecution(
            execution_id="test_exec_1",
            sweep_config=self.sweep_config
        )
        
        # Add some experiments
        execution.experiments = [
            Experiment("exp1", "project1", {"param1": 0.0}, ["accuracy"]),
            Experiment("exp2", "project1", {"param1": 1.0}, ["accuracy"])
        ]
        
        # No results yet
        self.assertEqual(execution.progress, 0.0)
        
        # Add one completed result
        execution.results = [
            ExperimentResult(
                experiment_id="exp1",
                project_name="project1",
                parameters={"param1": 0.0},
                metrics={"accuracy": 0.9},
                execution_time=10.0,
                status=ExperimentStatus.COMPLETED
            )
        ]
        
        self.assertEqual(execution.progress, 50.0)
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        execution = SweepExecution(
            execution_id="test_exec_1",
            sweep_config=self.sweep_config
        )
        
        # Add results with mixed success
        execution.results = [
            ExperimentResult(
                experiment_id="exp1",
                project_name="project1",
                parameters={"param1": 0.0},
                metrics={"accuracy": 0.9},
                execution_time=10.0,
                status=ExperimentStatus.COMPLETED
            ),
            ExperimentResult(
                experiment_id="exp2",
                project_name="project1",
                parameters={"param1": 1.0},
                metrics={},
                execution_time=5.0,
                status=ExperimentStatus.FAILED,
                error_message="Test error"
            )
        ]
        
        self.assertEqual(execution.success_rate, 50.0)


class TestOptimizationRecommendation(unittest.TestCase):
    """Test OptimizationRecommendation functionality."""
    
    def test_optimization_recommendation_creation(self):
        """Test creation of optimization recommendation."""
        recommendation = OptimizationRecommendation(
            priority_adjustments={"exp1": 1.5, "exp2": 0.5},
            early_stop_candidates=["exp3"],
            confidence_level=0.8,
            reasoning="High variance detected in parameter region"
        )
        
        self.assertEqual(len(recommendation.priority_adjustments), 2)
        self.assertEqual(len(recommendation.early_stop_candidates), 1)
        self.assertEqual(recommendation.confidence_level, 0.8)
        self.assertIn("variance", recommendation.reasoning)


if __name__ == "__main__":
    unittest.main()