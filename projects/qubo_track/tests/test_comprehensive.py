#!/usr/bin/env python3
"""
COMPREHENSIVE UNIT TESTS: QUBO Track v2.0
Tests exact optimum calculation, CSV schema, and NaN-aware statistics
"""

import unittest
import pandas as pd
import numpy as np
import os
import subprocess
import tempfile
from corrected_classical_optimization import (
    compute_exact_max_cut, 
    create_test_graphs,
    CorrectedClassicalComparison
)

class TestExactMaxCut(unittest.TestCase):
    """Test exact max-cut calculation (original tests)"""
    
    def test_k3_triangle(self):
        """Test K3 triangle - known optimum is 2"""
        import networkx as nx
        graph = nx.complete_graph(3)
        result = compute_exact_max_cut(graph)
        self.assertEqual(result, 2, "K3 max-cut should be 2")
    
    def test_k4_complete_graph(self):
        """Test K4 complete graph - known optimum is 4"""
        import networkx as nx
        graph = nx.complete_graph(4)
        result = compute_exact_max_cut(graph)
        self.assertEqual(result, 4, "K4 max-cut should be 4")
    
    def test_k6_complete_graph(self):
        """Test K6 complete graph - known optimum is 9"""
        import networkx as nx
        graph = nx.complete_graph(6)
        result = compute_exact_max_cut(graph)
        self.assertEqual(result, 9, "K6 max-cut should be 9")

class TestCSVSchemaAndStats(unittest.TestCase):
    """Test CSV output schema and NaN-aware statistical handling"""
    
    @classmethod
    def setUpClass(cls):
        """Run quick demo and load results for schema testing"""
        print("\n🧪 Running --quick demo for schema validation...")
        
        # Run the corrected implementation in quick mode
        result = subprocess.run([
            'python', 'corrected_classical_optimization.py', '--quick'
        ], capture_output=True, text=True, cwd='.')
        
        cls.subprocess_result = result
        
        # Load CSV if it exists
        if os.path.exists('classical_optimization_results.csv'):
            cls.df = pd.read_csv('classical_optimization_results.csv')
        else:
            cls.df = None
    
    def test_csv_file_created(self):
        """Test that CSV file is created and non-empty"""
        self.assertTrue(os.path.exists('classical_optimization_results.csv'), 
                       "CSV file should be created")
        self.assertGreater(os.path.getsize('classical_optimization_results.csv'), 1000,
                          "CSV file should be substantial (>1KB)")
    
    def test_csv_schema(self):
        """Test CSV has expected columns and data types"""
        self.assertIsNotNone(self.df, "CSV should be loadable")
        
        # Required columns (including schema version)
        required_cols = ['graph_name', 'method', 'trial_seed', 'cut_value', 
                        'exact_optimum', 'quality', 'execution_time', 'schema_version']
        
        for col in required_cols:
            self.assertIn(col, self.df.columns, f"CSV should have column: {col}")
        
        # Data type checks
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['cut_value']), 
                       "cut_value should be numeric")
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['quality']), 
                       "quality should be numeric")
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['exact_optimum']), 
                       "exact_optimum should be numeric")
    
    def test_quality_bounds(self):
        """Test quality metric is in [0, 1] range"""
        self.assertIsNotNone(self.df, "CSV should be loadable")
        
        # Quality should be in [0, 1]
        self.assertTrue((self.df['quality'] >= 0).all(), 
                       "All quality values should be >= 0")
        self.assertTrue((self.df['quality'] <= 1).all(), 
                       "All quality values should be <= 1")
    
    def test_no_duplicate_trials(self):
        """Test no duplicated graph/method/trial combinations"""
        self.assertIsNotNone(self.df, "CSV should be loadable")
        
        # Group by graph, method, trial - should have no duplicates
        groups = self.df.groupby(['graph_name', 'method', 'trial_seed']).size()
        self.assertTrue((groups == 1).all(), 
                       "No duplicate graph/method/trial combinations allowed")
    
    def test_nan_aware_statistics_handling(self):
        """Test that NaN-aware statistics were properly handled"""
        # Check console output for NaN-aware messaging
        output = self.subprocess_result.stdout
        
        # Should see evidence of NaN handling
        nan_indicators = [
            "t-test undefined (identical samples)",
            "Cohen's d: 0.0 (identical samples)", 
            "Skipped identical cases",
            "No valid p-values"
        ]
        
        found_nan_handling = any(indicator in output for indicator in nan_indicators)
        self.assertTrue(found_nan_handling, 
                       "Should show evidence of NaN-aware statistical handling")
    
    def test_no_p_value_column_in_csv(self):
        """Test that p-values aren't stored in CSV (ensures proper NaN handling)"""
        self.assertIsNotNone(self.df, "CSV should be loadable")
        
        # Should NOT have p_value column (they're computed and reported but not stored)
        self.assertNotIn('p_value', self.df.columns, 
                        "CSV should not store p-values (computed dynamically)")
    
    def test_schema_version(self):
        """Test that schema_version column exists and has correct value"""
        self.assertIsNotNone(self.df, "CSV should be loadable")
        
        # Schema version should exist and be 1
        self.assertIn('schema_version', self.df.columns, 
                     "CSV should have schema_version column")
        self.assertTrue((self.df['schema_version'] == 1).all(), 
                       "All schema_version values should be 1")
    
    def test_png_file_created(self):
        """Test that visualization PNG is created"""
        self.assertTrue(os.path.exists('classical_optimization_comparison.png'), 
                       "PNG visualization should be created")
        self.assertGreater(os.path.getsize('classical_optimization_comparison.png'), 10000,
                          "PNG file should be substantial (>10KB)")

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_large_graph_error_message(self):
        """Test that large graphs give helpful error message"""
        import networkx as nx
        
        # Create 25-node graph (too large)
        large_graph = nx.complete_graph(25)
        
        with self.assertRaises(ValueError) as context:
            compute_exact_max_cut(large_graph, quick_mode=False)
        
        error_msg = str(context.exception)
        self.assertIn("Use --quick flag", error_msg, 
                     "Error message should suggest --quick flag")
        self.assertIn("max 24", error_msg,
                     "Error message should mention size limit")

if __name__ == '__main__':
    print("🧪 COMPREHENSIVE UNIT TESTS: QUBO Track v2.0")
    print("=" * 55)
    print("Testing: Exact optimum, CSV schema, NaN-aware statistics")
    print()
    
    # Run all test suites
    unittest.main(verbosity=2)
