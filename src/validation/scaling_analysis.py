"""
Scaling Analysis for MaxCut Implementation Discrepancy

This script addresses the critique that the reproducibility case study was
limited to a single, small 3-node graph. It programmatically demonstrates
that the discrepancy (a 0.5 scaling factor) between the `OriginalMaxCut`
and `CanonicalMaxCut` implementations is consistent and predictable
across graphs of increasing size and complexity.

Author: Quantum Reproducibility Case Study Team
License: MIT
"""

import networkx as nx
import time
import numpy as np

def run_scaling_analysis(graph_sizes: list):
    """
    Runs a scaling analysis by comparing the two MaxCut implementations
    on graphs of various sizes.

    Args:
        graph_sizes: A list of integers specifying the number of nodes
                     for the graphs to be tested.
    """
    print("=" * 70)
    print("      Starting MaxCut Implementation Scaling Analysis")
    print("=" * 70)
    print(f"Testing graph sizes: {graph_sizes}\n")

    all_tests_passed = True

    for size in graph_sizes:
        print(f"--- Testing Graph Size: {size} nodes ---")
        start_time = time.time()

        # Generate a random unweighted graph of the given size
        graph = nx.erdos_renyi_graph(n=size, p=0.7, seed=42)

        print(f"Generated a random graph with {graph.number_of_edges()} edges.")

        # Instantiate both implementations
        try:
            canonical_impl = CanonicalMaxCut(graph=graph)
            original_impl = OriginalMaxCut(graph=graph)
            
            canonical_cuts = canonical_impl.get_all_cut_values()
            original_cuts = original_impl.get_all_cut_values()

            discrepancy_found = False
            for bitstring in canonical_cuts:
                canonical_val = canonical_cuts[bitstring]
                original_val = original_cuts[bitstring]

                if canonical_val != 0:
                    if not np.isclose(original_val, canonical_val * 0.5):
                        print(f"❌ FAIL: Discrepancy relationship does not hold for size {size}.")
                        print(f"   Bitstring: {bitstring}, Canonical: {canonical_val}, Original: {original_val}")
                        discrepancy_found = True
                        all_tests_passed = False
                        break
            
            end_time = time.time()
            duration = end_time - start_time

            if not discrepancy_found:
                print(f"✅ PASS: Discrepancy relationship (original = canonical * 0.5) holds.")
                print(f"   (Validated on {2**size} bitstrings in {duration:.2f} seconds)")

        except Exception as e:
            print(f"❌ ERROR: An exception occurred during validation for graph size {size}.")
            print(f"   Error: {e}")
            all_tests_passed = False

        print("-" * 35 + "\n")

    print("=" * 70)
    if all_tests_passed:
        print("🎉 Scaling Analysis Complete: Discrepancy is consistent across all tested sizes.")
    else:
        print("🔥 Scaling Analysis Complete: One or more validations failed.")
    print("=" * 70)

if __name__ == "__main__":
    GRAPH_SIZES_TO_TEST = [4, 6, 8, 10, 12]
    
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from maxcut_implementations.canonical_maxcut import CanonicalMaxCut
    from maxcut_implementations.original_maxcut import OriginalMaxCut
    
    run_scaling_analysis(GRAPH_SIZES_TO_TEST) 