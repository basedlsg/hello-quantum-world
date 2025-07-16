import os
import unittest
import pandas as pd
from qec import QECProject

class TestQECProject(unittest.TestCase):
    def setUp(self):
        """Set up a quick QEC project for testing."""
        self.project = QECProject(quick=True)
        self.benchmark_file = os.path.join(
            self.project.data_dir, "3q_benchmark_results.csv"
        )
        self.comparison_file = os.path.join(
            self.project.data_dir, "controlled_comparison_results.csv"
        )
        # Clean up previous results
        for f in [self.benchmark_file, self.comparison_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_quick_run_produces_output(self):
        """
        Tests that a --quick run completes and produces valid CSV output files.
        """
        self.project.run_full_analysis()
        
        # Test benchmark file
        self.assertTrue(os.path.exists(self.benchmark_file))
        df_bench = pd.read_csv(self.benchmark_file)
        self.assertFalse(df_bench.empty)
        expected_bench_cols = ["evolution_steps", "physical_fidelity", "logical_fidelity", "qec_advantage"]
        self.assertListEqual(list(df_bench.columns), expected_bench_cols)
        
        # Test comparison file
        self.assertTrue(os.path.exists(self.comparison_file))
        df_comp = pd.read_csv(self.comparison_file)
        self.assertFalse(df_comp.empty)
        expected_comp_cols = ["trial", "fidelity_3qubit", "fidelity_5qubit", "qec_advantage"]
        self.assertListEqual(list(df_comp.columns), expected_comp_cols)

    def tearDown(self):
        """Clean up generated files."""
        for f in [self.benchmark_file, self.comparison_file]:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    unittest.main() 