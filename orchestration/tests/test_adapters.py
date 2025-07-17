"""
Unit tests for project adapters.

Tests adapter functionality for seamless project integration.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from orchestration.adapters.base import BaseProjectAdapter
from orchestration.adapters.fmo_adapter import FMOProjectAdapter
from orchestration.core.models import ExperimentStatus


class TestBaseProjectAdapter(unittest.TestCase):
    """Test BaseProjectAdapter functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary project directory
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test_project"
        self.project_path.mkdir()
        
        # Create a minimal main.py
        main_py = self.project_path / "main.py"
        main_py.write_text("""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    
    print("Test project executed successfully")
    print("Final result: 0.95")
    return 0

if __name__ == "__main__":
    main()
""")
        
        self.adapter = BaseProjectAdapter(str(self.project_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.project_name, "test_project")
        self.assertEqual(self.adapter.project_path.resolve(), self.project_path.resolve())
    
    def test_project_adaptation(self):
        """Test project adaptation process."""
        success = self.adapter.adapt_project(str(self.project_path))
        self.assertTrue(success)
    
    def test_project_adaptation_missing_path(self):
        """Test adaptation with missing project path."""
        success = self.adapter.adapt_project("/nonexistent/path")
        self.assertFalse(success)
    
    def test_compatibility_validation(self):
        """Test project compatibility validation."""
        report = self.adapter.validate_compatibility()
        
        self.assertIsInstance(report, dict)
        self.assertIn("compatible", report)
        self.assertIn("issues", report)
        self.assertIn("warnings", report)
        self.assertTrue(report["compatible"])  # Should be compatible with main.py
    
    def test_compatibility_validation_no_main(self):
        """Test compatibility validation without main.py."""
        # Remove main.py
        (self.project_path / "main.py").unlink()
        
        report = self.adapter.validate_compatibility()
        self.assertFalse(report["compatible"])
        self.assertIn("main.py not found", report["issues"])
    
    def test_parameter_schema(self):
        """Test parameter schema retrieval."""
        schema = self.adapter.get_parameter_schema()
        
        self.assertIsInstance(schema, dict)
        self.assertIn("quick", schema)
        self.assertEqual(schema["quick"]["type"], "boolean")
    
    @patch('subprocess.run')
    def test_execute_with_parameters(self, mock_run):
        """Test project execution with parameters."""
        # Mock successful execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Test project executed successfully\nFinal result: 0.95"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        params = {"quick": True, "test_param": 0.5}
        result = self.adapter.execute_with_parameters(params)
        
        self.assertEqual(result.status, ExperimentStatus.COMPLETED)
        self.assertEqual(result.project_name, "test_project")
        self.assertEqual(result.parameters, params)
        self.assertIn("final_result", result.metrics)
        self.assertEqual(result.metrics["final_result"], 0.95)
    
    @patch('subprocess.run')
    def test_execute_with_parameters_failure(self, mock_run):
        """Test project execution failure handling."""
        # Mock failed execution
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Test error"
        mock_run.side_effect = RuntimeError("Project execution failed: Test error")
        
        params = {"quick": True}
        result = self.adapter.execute_with_parameters(params)
        
        self.assertEqual(result.status, ExperimentStatus.FAILED)
        self.assertIsNotNone(result.error_message)
    
    def test_metric_extraction(self):
        """Test metric extraction from project output."""
        test_output = {
            "stdout": """
            Test project started
            Accuracy: 0.95
            Fidelity: 0.87
            Final efficiency: 0.92
            Test completed successfully
            """,
            "stderr": "",
            "returncode": 0
        }
        
        metrics = self.adapter.extract_metrics(test_output)
        
        self.assertIn("accuracy", metrics)
        self.assertIn("fidelity", metrics)
        self.assertIn("final_efficiency", metrics)
        self.assertEqual(metrics["accuracy"], 0.95)
        self.assertEqual(metrics["fidelity"], 0.87)
        self.assertEqual(metrics["final_efficiency"], 0.92)
    
    def test_metric_extraction_no_metrics(self):
        """Test metric extraction when no metrics are found."""
        test_output = {
            "stdout": "No metrics here",
            "stderr": "",
            "returncode": 0
        }
        
        metrics = self.adapter.extract_metrics(test_output)
        
        # Should have execution success metric as fallback
        self.assertIn("execution_success", metrics)
        self.assertEqual(metrics["execution_success"], 1.0)


class TestFMOProjectAdapter(unittest.TestCase):
    """Test FMOProjectAdapter functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.adapter = FMOProjectAdapter()
        # Override project path to avoid dependency on actual FMO project
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "fmo_project"
        self.project_path.mkdir()
        
        # Create minimal FMO project structure
        main_py = self.project_path / "main.py"
        main_py.write_text("""
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    
    print("FMO simulation started")
    print("Transport efficiency: 0.85")
    print("Final efficiency: 0.92")
    print("Quantitative Enhancement: +5.9% relative increase")
    print("FMO project analysis complete.")

if __name__ == "__main__":
    main()
""")
        
        fmo_py = self.project_path / "fmo.py"
        fmo_py.write_text("# FMO project implementation")
        
        self.adapter.project_path = self.project_path
        self.adapter.project_name = "fmo_project"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_fmo_parameter_schema(self):
        """Test FMO-specific parameter schema."""
        schema = self.adapter.get_parameter_schema()
        
        self.assertIn("dephasing_rate", schema)
        self.assertIn("simulation_time", schema)
        self.assertIn("num_sites", schema)
        self.assertIn("temperature", schema)
        self.assertIn("coupling_strength", schema)
        
        # Check parameter details
        dephasing = schema["dephasing_rate"]
        self.assertEqual(dephasing["type"], "float")
        self.assertIn("range", dephasing)
        self.assertEqual(len(dephasing["range"]), 2)
    
    def test_fmo_compatibility_validation(self):
        """Test FMO-specific compatibility validation."""
        report = self.adapter.validate_compatibility()
        
        self.assertTrue(report["compatible"])
        self.assertEqual(report["project_type"], "fmo")
        self.assertIn("project_type", report)
    
    def test_fmo_compatibility_missing_fmo_py(self):
        """Test FMO compatibility without fmo.py."""
        # Remove fmo.py
        (self.project_path / "fmo.py").unlink()
        
        report = self.adapter.validate_compatibility()
        self.assertFalse(report["compatible"])
        self.assertIn("fmo.py not found", report["issues"])
    
    @patch('subprocess.run')
    def test_fmo_execution_with_parameters(self, mock_run):
        """Test FMO project execution with parameters."""
        # Mock successful FMO execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
        FMO simulation started
        Transport efficiency: 0.85
        Final efficiency: 0.92
        Minimum efficiency: 0.78
        Quantitative Enhancement: +5.9% relative increase
        Convergence error: 1.2e-6
        FMO project analysis complete.
        """
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        params = {
            "quick": True,
            "dephasing_rate": 10.0,
            "simulation_time": 1.0,
            "num_sites": 4
        }
        
        result = self.adapter.execute_with_parameters(params)
        
        self.assertEqual(result.status, ExperimentStatus.COMPLETED)
        self.assertEqual(result.project_name, "fmo_project")
        
        # Check FMO-specific metrics
        metrics = result.metrics
        self.assertIn("transport_efficiency", metrics)
        self.assertIn("final_efficiency", metrics)
        self.assertIn("quantitative_enhancement", metrics)
        
        self.assertEqual(metrics["transport_efficiency"], 0.85)
        self.assertEqual(metrics["final_efficiency"], 0.92)
        self.assertEqual(metrics["quantitative_enhancement"], 5.9)
    
    def test_fmo_metric_extraction(self):
        """Test FMO-specific metric extraction."""
        fmo_output = {
            "stdout": """
            FMO Noise-Assisted Transport: Project Summary
            Transport efficiency: 0.471
            Final efficiency: 0.499
            Minimum efficiency: 0.450
            Quantitative Enhancement: +5.9% relative increase
            Convergence error: 2.1e-7
            Leakage: 1.5e-8
            """,
            "stderr": "",
            "returncode": 0,
            "project_type": "fmo"
        }
        
        metrics = self.adapter.extract_metrics(fmo_output)
        
        # Check all FMO metrics are extracted
        expected_metrics = [
            "transport_efficiency", "final_efficiency", "minimum_efficiency",
            "quantitative_enhancement", "convergence_error", "leakage_rate"
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
        
        # Check derived metrics
        self.assertIn("noise_enhancement_ratio", metrics)
        expected_ratio = 0.499 / 0.450
        self.assertAlmostEqual(metrics["noise_enhancement_ratio"], expected_ratio, places=3)
    
    def test_fmo_parameter_mapping(self):
        """Test FMO parameter mapping to environment variables."""
        # This is tested indirectly through the execution test
        # The _execute_project method should map parameters correctly
        params = {
            "dephasing_rate": 15.0,
            "simulation_time": 2.0,
            "num_sites": 6,
            "temperature": 77,
            "coupling_strength": 1.5
        }
        
        # Create a mock execution to test parameter mapping
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "FMO execution complete"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            # Execute with parameters
            self.adapter.execute_with_parameters(params)
            
            # Check that subprocess.run was called with correct environment
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            env = call_args[1]['env']
            
            # Verify parameter mapping
            self.assertEqual(env['FMO_DEPHASING_RATE'], '15.0')
            self.assertEqual(env['FMO_SIMULATION_TIME'], '2.0')
            self.assertEqual(env['FMO_NUM_SITES'], '6')
            self.assertEqual(env['FMO_TEMPERATURE'], '77')
            self.assertEqual(env['FMO_COUPLING_STRENGTH'], '1.5')


if __name__ == "__main__":
    unittest.main()