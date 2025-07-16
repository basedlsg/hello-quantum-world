 import os
import unittest
import pandas as pd
from fmo import FMOProject

class TestFMOProject(unittest.TestCase):
    def setUp(self):
        """Set up a quick FMO project for testing."""
        self.project = FMOProject(quick=True)
        self.output_file = os.path.join(
            self.project.data_dir, "quantum_transport_results.csv"
        )
        # Clean up previous results if they exist
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_quick_run_produces_output(self):
        """
        Tests that a --quick run completes and produces a valid CSV output file.
        """
        self.project.run_full_analysis()
        
        # 1. Check if the output file was created
        self.assertTrue(os.path.exists(self.output_file), "Output CSV file was not created.")
        
        # 2. Check if the CSV can be loaded and is not empty
        df = pd.read_csv(self.output_file)
        self.assertFalse(df.empty, "Output CSV is empty.")
        
        # 3. Check for expected columns
        expected_columns = ["gamma_ps_inv", "efficiency", "leakage"]
        self.assertListEqual(list(df.columns), expected_columns, "CSV columns are not correct.")
        
        # 4. Check that efficiency is within a plausible range (0 to 1)
        self.assertTrue((df['efficiency'] >= 0).all() and (df['efficiency'] <= 1).all(),
                        "Efficiency values are not within the plausible range [0, 1].")

    def tearDown(self):
        """Clean up generated files."""
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

if __name__ == "__main__":
    unittest.main() 