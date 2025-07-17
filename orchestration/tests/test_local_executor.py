"""
Unit tests for the local executor.
"""

import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from orchestration.core.models import Experiment, ExperimentStatus
from orchestration.executors.local_executor import LocalExecutor


class TestLocalExecutor(unittest.TestCase):
    """Test cases for LocalExecutor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = LocalExecutor()
        
        # Create temporary project directory
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test_project"
        self.project_path.mkdir()
        
        # Create a simple main.py file
        main_file = self.project_path / "main.py"
        main_file.write_text("""
import json
import sys

def main():
    # Simple test function that returns parameters as metrics
    params = {}
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    
    result = {
        "metrics": {
            "test_metric": params.get("test_param", 1.0),
            "execution_count": 1
        }
    }
    
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    main()
""")
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_can_execute_valid_project(self):
        """Test can_execute with a valid project."""
        experiment = Experiment(
            experiment_id="test_exp",
            project_path=str(self.project_path),
            parameters={"test_param": 1.0},
            objectives=["test_metric"]
        )
        
        with patch('orchestration.adapters.base.ProjectAdapter.validate_compatibility') as mock_validate:
            mock_validate.return_value = {"compatible": True}
            
            result = self.executor.can_execute(experiment)
            self.assertTrue(result)
    
    def test_can_execute_invalid_project(self):
        """Test can_execute with an invalid project path."""
        experiment = Experiment(
            experiment_id="test_exp",
            project_path="/nonexistent/path",
            parameters={"test_param": 1.0},
            objectives=["test_metric"]
        )
        
        result = self.executor.can_execute(experiment)
        self.assertFalse(result)
    
    def test_estimate_duration(self):
        """Test duration estimation."""
        experiment = Experiment(
            experiment_id="test_exp",
            project_path=str(self.project_path),
            parameters={"param1": 1.0, "param2": 2.0},
            objectives=["test_metric"]
        )
        
        duration = self.executor.estimate_duration(experiment)
        self.assertIsInstance(duration, timedelta)
        self.assertGreater(duration.total_seconds(), 0)
    
    def test_estimate_cost(self):
        """Test cost estimation (should be 0 for local execution)."""
        experiment = Experiment(
            experiment_id="test_exp",
            project_path=str(self.project_path),
            parameters={"test_param": 1.0},
            objectives=["test_metric"]
        )
        
        cost = self.executor.estimate_cost(experiment)
        self.assertEqual(cost, 0.0)
    
    @patch('orchestration.adapters.base.ProjectAdapter.execute_with_parameters')
    @patch('orchestration.adapters.base.ProjectAdapter.adapt_project')
    def test_execute_success(self, mock_adapt, mock_execute):
        """Test successful experiment execution."""
        # Mock adapter behavior
        mock_adapt.return_value = True
        
        from orchestration.core.models import ExperimentResult
        mock_result = ExperimentResult(
            experiment_id="test_exp",
            project_name="test_project",
            parameters={"test_param": 1.0},
            metrics={"test_metric": 1.5},
            execution_time=0.1,
            status=ExperimentStatus.COMPLETED
        )
        mock_execute.return_value = mock_result
        
        experiment = Experiment(
            experiment_id="test_exp",
            project_path=str(self.project_path),
            parameters={"test_param": 1.0},
            objectives=["test_metric"]
        )
        
        result = self.executor.execute(experiment)
        
        self.assertEqual(result.experiment_id, "test_exp")
        self.assertEqual(result.status, ExperimentStatus.COMPLETED)
        self.assertIn("test_metric", result.metrics)
        self.assertGreater(result.execution_time, 0)
    
    @patch('orchestration.adapters.base.ProjectAdapter.execute_with_parameters')
    @patch('orchestration.adapters.base.ProjectAdapter.adapt_project')
    def test_execute_failure(self, mock_adapt, mock_execute):
        """Test experiment execution failure."""
        # Mock adapter behavior
        mock_adapt.return_value = True
        mock_execute.side_effect = RuntimeError("Test execution error")
        
        experiment = Experiment(
            experiment_id="test_exp",
            project_path=str(self.project_path),
            parameters={"test_param": 1.0},
            objectives=["test_metric"]
        )
        
        result = self.executor.execute(experiment)
        
        self.assertEqual(result.experiment_id, "test_exp")
        self.assertEqual(result.status, ExperimentStatus.FAILED)
        self.assertIn("Test execution error", result.error_message)
        self.assertGreater(result.execution_time, 0)
    
    def test_fmo_project_detection(self):
        """Test FMO project adapter selection."""
        # Create FMO project directory
        fmo_path = Path(self.temp_dir) / "fmo_project"
        fmo_path.mkdir()
        
        experiment = Experiment(
            experiment_id="fmo_exp",
            project_path=str(fmo_path),
            parameters={"test_param": 1.0},
            objectives=["test_metric"]
        )
        
        with patch('orchestration.adapters.fmo_adapter.FMOProjectAdapter') as mock_fmo_adapter:
            mock_adapter_instance = Mock()
            mock_adapter_instance.adapt_project.return_value = True
            mock_adapter_instance.validate_compatibility.return_value = {"compatible": True}
            mock_fmo_adapter.return_value = mock_adapter_instance
            
            # This should create an FMO adapter
            adapter = self.executor._get_adapter(str(fmo_path))
            mock_fmo_adapter.assert_called_once()
    
    def test_adapter_caching(self):
        """Test that adapters are cached for reuse."""
        project_path = str(self.project_path)
        
        # First call should create adapter
        adapter1 = self.executor._get_adapter(project_path)
        
        # Second call should return cached adapter
        adapter2 = self.executor._get_adapter(project_path)
        
        # Should be the same instance (cached)
        self.assertIs(adapter1, adapter2)
        
        # Should be in the cache
        self.assertIn(project_path, self.executor.adapters)
        self.assertEqual(len(self.executor.adapters), 1)
    
    def test_cleanup(self):
        """Test executor cleanup."""
        # Add some adapters
        self.executor.adapters["test1"] = Mock()
        self.executor.adapters["test2"] = Mock()
        
        self.assertEqual(len(self.executor.adapters), 2)
        
        # Cleanup should clear adapters
        self.executor.cleanup()
        self.assertEqual(len(self.executor.adapters), 0)


if __name__ == "__main__":
    unittest.main()