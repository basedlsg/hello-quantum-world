"""
Unit Tests for MaxCut Reproducibility Case Study

This test suite validates both MaxCut implementations and reproduces the exact
discrepancy found in our quantum computing reproducibility investigation.

Author: Quantum Reproducibility Case Study Team
License: MIT
"""

import unittest
import numpy as np
import sys
import os
from typing import Dict, List
import networkx as nx

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from maxcut_implementations.original_maxcut import OriginalMaxCut, reproduce_original_qaoa_results
from maxcut_implementations.canonical_maxcut import CanonicalMaxCut


class TestOriginalMaxCut(unittest.TestCase):
    """Test cases for the original, flawed MaxCut implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Unweighted 3-node triangle graph
        self.triangle_graph = nx.Graph()
        self.triangle_graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
        self.maxcut_triangle = OriginalMaxCut(self.triangle_graph)
        
        # Weighted 4-node graph for testing generalization
        self.weighted_graph = nx.Graph()
        self.weighted_graph.add_edge(0, 1, weight=1.5)
        self.weighted_graph.add_edge(1, 2, weight=2.0)
        self.weighted_graph.add_edge(2, 3, weight=0.5)
        self.maxcut_weighted = OriginalMaxCut(self.weighted_graph)
        
    def test_initialization(self):
        """Test proper initialization of OriginalMaxCut."""
        self.assertEqual(list(self.maxcut_triangle.graph_edges), list(self.triangle_graph.edges))
        self.assertEqual(self.maxcut_triangle.num_nodes, 3)
        self.assertEqual(len(self.maxcut_triangle.lookup_table), 8)
        
    def test_custom_graph_initialization(self):
        """Test initialization with custom weighted graph."""
        self.assertEqual(self.maxcut_weighted.num_nodes, 4)
        self.assertEqual(len(self.maxcut_weighted.lookup_table), 16)
        
    def test_lookup_table_creation(self):
        """Test that lookup table is created correctly."""
        expected_bitstrings = {'000', '001', '010', '011', '100', '101', '110', '111'}
        actual_bitstrings = set(self.maxcut_triangle.lookup_table.keys())
        self.assertEqual(actual_bitstrings, expected_bitstrings)
        
    def test_cut_value_calculation(self):
        """Test individual cut value calculations for unweighted graph."""
        # Test specific cases from the case study
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('000'), 0.0)
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('111'), 0.0)
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('001'), 1.0)
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('101'), 1.0)

    def test_weighted_cut_value_calculation(self):
        """Test individual cut value calculations for weighted graph."""
        # For bitstring '0011', only edge (1,2) with weight 2.0 is cut.
        # Scaled by 0.5, the value should be 1.0.
        self.assertAlmostEqual(self.maxcut_weighted.calculate_cut_value('0011'), 1.0)
        
        # For bitstring '0101', all edges (0,1), (1,2), (2,3) are cut.
        # Total weight = 1.5 + 2.0 + 0.5 = 4.0. Scaled by 0.5, the value is 2.0.
        self.assertAlmostEqual(self.maxcut_weighted.calculate_cut_value('0101'), 2.0)
        
    def test_invalid_bitstring_length(self):
        """Test error handling for invalid bitstring length."""
        with self.assertRaises(ValueError):
            self.maxcut_triangle.calculate_cut_value('00')
        with self.assertRaises(ValueError):
            self.maxcut_triangle.calculate_cut_value('0000')
            
    def test_unknown_bitstring(self):
        """Test error handling for unknown bitstring."""
        # This shouldn't happen with proper initialization, but test anyway
        with self.assertRaises(KeyError):
            # Manually remove a bitstring from lookup table
            del self.maxcut_triangle.lookup_table['000']
            self.maxcut_triangle.calculate_cut_value('000')
            
    def test_optimal_cut_finding(self):
        """Test finding the optimal cut for unweighted graph."""
        _, optimal_value = self.maxcut_triangle.get_optimal_cut()
        self.assertEqual(optimal_value, 1.0)
        
    def test_qaoa_expectation_calculation(self):
        """Test QAOA expectation value calculation."""
        # Uniform distribution
        uniform_dist = {f'{i:03b}': 0.125 for i in range(8)}
        expectation = self.maxcut_triangle.calculate_qaoa_expectation(uniform_dist)
        
        # Manual calculation: sum of all cut values * 0.125
        expected = sum(self.maxcut_triangle.lookup_table.values()) * 0.125
        self.assertAlmostEqual(expectation, expected, places=10)
        
    def test_debug_calculation(self):
        """Test debug calculation functionality."""
        debug_info = self.maxcut_triangle.debug_calculation('101')
        
        self.assertEqual(debug_info['bitstring'], '101')
        self.assertEqual(debug_info['partition_0'], [1])
        self.assertEqual(debug_info['partition_1'], [0, 2])
        self.assertEqual(debug_info['raw_cut_count'], 2)
        self.assertEqual(debug_info['scaling_factor'], 0.5)
        self.assertEqual(debug_info['final_cut_value'], 1.0)
        
    def test_method_info(self):
        """Test method information retrieval."""
        method_info = self.maxcut_triangle.get_method_info()
        
        self.assertEqual(method_info['method_name'], 'Generalized Original Lookup Table Method')
        self.assertEqual(method_info['scaling_factor'], 0.5)
        self.assertEqual(method_info['agreement_rate'], 0.25)
        self.assertEqual(method_info['verification_status'], 'disputed')


class TestCanonicalMaxCut(unittest.TestCase):
    """Test cases for the canonical, correct MaxCut implementation."""

    def setUp(self):
        """Set up test fixtures."""
        # Unweighted 3-node triangle graph
        self.triangle_graph = nx.Graph()
        self.triangle_graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
        self.maxcut_triangle = CanonicalMaxCut(self.triangle_graph)

        # Weighted 4-node graph for testing generalization
        self.weighted_graph = nx.Graph()
        self.weighted_graph.add_edge(0, 1, weight=1.5)
        self.weighted_graph.add_edge(1, 2, weight=2.0)
        self.weighted_graph.add_edge(2, 3, weight=0.5)
        self.maxcut_weighted = CanonicalMaxCut(self.weighted_graph)

    def test_initialization(self):
        """Test proper initialization of CanonicalMaxCut."""
        self.assertEqual(self.maxcut_triangle.num_nodes, 3)

    def test_cut_value_calculation(self):
        """Test individual cut value calculations for unweighted graph."""
        # Test specific cases from the case study
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('000'), 0.0)
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('111'), 0.0)
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('001'), 2.0)
        self.assertEqual(self.maxcut_triangle.calculate_cut_value('101'), 2.0)

    def test_weighted_cut_value_calculation(self):
        """Test individual cut value calculations for weighted graph."""
        # For bitstring '0011', only edge (1,2) with weight 2.0 is cut.
        self.assertAlmostEqual(self.maxcut_weighted.calculate_cut_value('0011'), 2.0)

        # For bitstring '0101', all edges (0,1), (1,2), (2,3) are cut.
        # Total weight = 1.5 + 2.0 + 0.5 = 4.0
        self.assertAlmostEqual(self.maxcut_weighted.calculate_cut_value('0101'), 4.0)

    def test_direct_edge_counting(self):
        """Test the direct edge counting method for unweighted graph."""
        bitstring = '101'
        cut_weight = 0.0

        for u, v, data in self.maxcut_triangle.graph.edges(data=True):
            if bitstring[u] != bitstring[v]:
                cut_weight += data.get('weight', 1.0)

        expected_value = float(cut_weight)
        actual_value = self.maxcut_triangle.calculate_cut_value(bitstring)
        self.assertEqual(actual_value, expected_value)

    def test_optimal_cut_finding(self):
        """Test finding the optimal cut for unweighted graph."""
        _, optimal_value = self.maxcut_triangle.get_optimal_cut()
        self.assertEqual(optimal_value, 2.0)


class TestMaxCutComparison(unittest.TestCase):
    """Test cases for comparing the flawed and canonical implementations."""

    def setUp(self):
        """Set up test fixtures."""
        triangle_graph = nx.Graph()
        triangle_graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
        self.original = OriginalMaxCut(triangle_graph)
        self.canonical = CanonicalMaxCut(triangle_graph)

    def test_implementation_differences(self):
        """Test that implementations produce different results."""
        original_value = self.original.calculate_cut_value('101')
        canonical_value = self.canonical.calculate_cut_value('101')

        self.assertNotEqual(original_value, canonical_value)
        self.assertEqual(original_value, 1.0)
        self.assertEqual(canonical_value, 2.0)

    def test_agreement_rate(self):
        """Test the exact agreement rate for the unweighted triangle graph."""
        original_cuts = self.original.get_all_cut_values()
        canonical_cuts = self.canonical.get_all_cut_values()
        
        agreements = 0
        for bitstring in original_cuts:
            if np.isclose(original_cuts[bitstring], canonical_cuts[bitstring]):
                agreements += 1
        
        self.assertEqual(agreements / len(original_cuts), 0.25) # Agree on '000' and '111'

    def test_scaling_factor_effect(self):
        """Test that the methods differ by the 0.5 scaling factor."""
        for bitstring in ['001', '010', '100', '011', '101', '110']:
            original_value = self.original.calculate_cut_value(bitstring)
            canonical_value = self.canonical.calculate_cut_value(bitstring)

            if canonical_value != 0:
                self.assertAlmostEqual(original_value, canonical_value * 0.5, places=10)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up the test fixtures."""
        # Empty graph
        self.empty_graph = nx.Graph()
        self.original_empty = OriginalMaxCut(self.empty_graph)
        self.canonical_empty = CanonicalMaxCut(self.empty_graph)

        # Disconnected graph
        self.disconnected_graph = nx.Graph()
        self.disconnected_graph.add_edges_from([(0, 1), (2, 3)])
        self.original_disconnected = OriginalMaxCut(self.disconnected_graph)
        self.canonical_disconnected = CanonicalMaxCut(self.disconnected_graph)

    def test_empty_probability_distribution(self):
        """Test handling of empty probability distributions."""
        original = OriginalMaxCut(nx.Graph([(0,1)]))
        canonical = CanonicalMaxCut(nx.Graph([(0,1)]))
        
        empty_dist = {}
        
        self.assertEqual(original.calculate_qaoa_expectation(empty_dist), 0.0)
        # The canonical implementation doesn't have this method, which is fine.
        
    def test_empty_graph(self):
        """Test handling of a graph with no nodes or edges."""
        self.assertEqual(self.original_empty.calculate_cut_value(""), 0.0)
        self.assertEqual(self.canonical_empty.calculate_cut_value(""), 0.0)

    def test_single_node_graph(self):
        """Test handling of single node graph."""
        single_node_graph = nx.Graph()
        single_node_graph.add_node(0)

        original = OriginalMaxCut(single_node_graph)
        canonical = CanonicalMaxCut(single_node_graph)
        
        self.assertEqual(original.calculate_cut_value("0"), 0.0)
        self.assertEqual(canonical.calculate_cut_value("0"), 0.0)
            
    def test_disconnected_graph(self):
        """Test handling of disconnected graph."""
        # bitstring '0110' should cut edge (0,1) and (2,3) -> total cut = 2
        self.assertEqual(self.canonical_disconnected.calculate_cut_value('0110'), 2.0)
        # original implementation scales by 0.5 -> total cut = 1
        self.assertEqual(self.original_disconnected.calculate_cut_value('0110'), 1.0)


class TestNumericalPrecision(unittest.TestCase):
    """Test numerical precision and floating point issues."""
    
    def test_floating_point_precision(self):
        """Test that floating point calculations are precise enough."""
        graph = nx.Graph([(0,1, {'weight':0.1}), (1,2, {'weight':0.2})])
        original = OriginalMaxCut(graph)
        canonical = CanonicalMaxCut(graph)

        # Test multiple calculations to ensure consistency
        for _ in range(100):
            bitstring = '010'
            original_value = original.calculate_cut_value(bitstring)
            canonical_value = canonical.calculate_cut_value(bitstring)

            self.assertAlmostEqual(original_value, (0.1 + 0.2) * 0.5)
            self.assertAlmostEqual(canonical_value, 0.1 + 0.2)
            
    def test_expectation_value_precision(self):
        """Test precision of expectation value calculations."""
        graph = nx.Graph([(0,1), (1,2), (0,2)])
        original = OriginalMaxCut(graph)
        canonical = CanonicalMaxCut(graph)
        
        # Create a probability distribution that should sum to exactly 1.0
        prob_dist = {
            '000': 0.1, '001': 0.1, '010': 0.1, '011': 0.1,
            '100': 0.1, '101': 0.1, '110': 0.1, '111': 0.3
        }
        
        # Verify probabilities sum to 1.0
        self.assertAlmostEqual(sum(prob_dist.values()), 1.0, places=15)
        
        # Calculate expectations
        original_expectation = original.calculate_qaoa_expectation(prob_dist)
        canonical_expectation = canonical.calculate_qaoa_expectation(prob_dist)
        
        # Should be finite numbers
        self.assertFalse(np.isnan(original_expectation))
        self.assertFalse(np.isnan(canonical_expectation))
        self.assertTrue(np.isfinite(original_expectation))
        self.assertTrue(np.isfinite(canonical_expectation))


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestOriginalMaxCut,
        TestCanonicalMaxCut,
        TestMaxCutComparison,
        TestEdgeCases,
        TestNumericalPrecision
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors))/result.testsRun*100:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
            
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
            
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    print(f"\nExiting with code: {exit_code}")
    exit(exit_code) 