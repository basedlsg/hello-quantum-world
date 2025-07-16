"""Advanced Analysis of AWS Cloud Execution Results

This script performs a detailed statistical analysis of the raw measurement
data obtained from an Amazon Braket cloud execution. It addresses the critique
on uncertainty quantification by calculating a confidence interval for the
final expectation value using the bootstrap method.

Methodology:
1. Load the raw measurement results from the `aws_cloud_result.json` file.
2. For a specified number of bootstrap iterations:
    a. Create a new "resample" of the data by drawing N shots with
       replacement from the original N-shot dataset.
    b. Calculate the expectation value for this resampled data.
3. Collect the distribution of these resampled expectation values.
4. Compute the mean and standard deviation of the distribution. The standard
   deviation serves as the bootstrap standard error of the mean.
5. Report the final result as `mean ± 1 standard error`.
"""

import json
import os
import sys
from collections import Counter

import networkx as nx
import numpy as np

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
from maxcut_implementations.canonical_maxcut import CanonicalMaxCut


def analyze_results(log_file="aws_cloud_result.json", bootstrap_iterations=5000):
    """Analyzes the cloud results, including bootstrap error estimation.

    Args:
    ----
        log_file (str): The path to the AWS results JSON file.
        bootstrap_iterations (int): The number of bootstrap samples to generate.

    """
    if not os.path.exists(log_file):
        print(f"Error: Log file not found at '{log_file}'.")
        print("Please run 'run_qaoa_on_braket.py' first to generate the results.")
        return

    # --- 1. Initial Calculation ---
    # Define the graph used in the experiment
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
    maxcut_calculator = CanonicalMaxCut(graph)

    with open(log_file, "r") as f:
        log_data = json.load(f)

    # The log file contains a list of individual measurements.
    raw_measurements = ["".join(map(str, m)) for m in log_data["measurements"]]
    total_shots = len(raw_measurements)
    measurement_counts = Counter(raw_measurements)

    # Convert to a list of individual cut values for bootstrapping
    all_cut_values = np.array(
        [maxcut_calculator.calculate_cut_value(bs) for bs in raw_measurements]
    )

    mean_exp_val = np.mean(all_cut_values)

    # --- 2. Bootstrap Analysis ---
    print(f"\nPerforming bootstrap analysis with {bootstrap_iterations} iterations...")
    bootstrap_exp_vals = []
    if total_shots > 0:
        for _ in range(bootstrap_iterations):
            # Create a bootstrap sample by drawing with replacement
            resample_indices = np.random.choice(
                len(all_cut_values), size=len(all_cut_values), replace=True
            )
            resample_values = all_cut_values[resample_indices]
            bootstrap_exp_vals.append(np.mean(resample_values))

    # The standard deviation of the bootstrap distribution is the standard error
    bootstrap_std_err = np.std(bootstrap_exp_vals) if bootstrap_exp_vals else 0
    print("Bootstrap analysis complete.")

    # --- 3. Report Final Results ---
    print("\n" + "=" * 70)
    print("          Final Analysis of AWS Cloud Execution Results")
    print("=" * 70)
    print(f"Task ARN:         {log_data['taskMetadata']['id']}")
    print(f"Total Shots:      {total_shots}")
    print("-" * 70)
    print(f"Expectation Value: {mean_exp_val:.6f} ± {bootstrap_std_err:.6f}")
    print("Confidence Interval: ±1 Standard Error (from bootstrap method)")
    print("\nMeasurement Distribution:")
    for bitstring, count in sorted(measurement_counts.items()):
        print(f"  - State |{bitstring}>: {count} counts")
    print("=" * 70)


if __name__ == "__main__":
    analyze_results()
