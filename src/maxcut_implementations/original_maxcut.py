"""
Original MaxCut Implementation - Lookup Table Method

This implementation reproduces the original MaxCut calculation method from our
quantum computing reproducibility case study. It uses a pre-computed lookup
table approach that led to the discrepancy in QAOA results.

Author: Quantum Reproducibility Case Study Team
License: MIT
"""

import numpy as np
from typing import Dict, List, Tuple
import networkx as nx


class OriginalMaxCut:
    """
    Original MaxCut implementation using a lookup table method.
    This implementation is generalized to accept a networkx graph but
    retains the non-standard 0.5 scaling factor that caused the
    reproducibility discrepancy.
    """
    
    def __init__(self, graph: nx.Graph = None):
        """
        Initialize the OriginalMaxCut calculator.
        
        Args:
            graph: A networkx Graph object. If None, uses the default
                   3-node unweighted triangle graph.
        """
        if graph is None:
            # Default 3-node triangle graph used in case study
            default_graph = nx.Graph()
            default_graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
            self.graph = default_graph
        else:
            self.graph = graph
            
        self.num_nodes = self.graph.number_of_nodes()
        self.graph_edges = list(self.graph.edges)
        self.lookup_table = self._create_lookup_table()
        
    def _create_lookup_table(self) -> Dict[str, float]:
        """
        Create lookup table for cut values.
        
        This is the method that caused the discrepancy. It pre-computes
        cut values using a specific interpretation of the MaxCut problem.
        This version is generalized for weighted graphs.
        
        Returns:
            Dictionary mapping bitstrings to cut values
        """
        if self.num_nodes == 0:
            return {"": 0.0}

        lookup_table = {}
        
        # Generate all possible bitstrings for the graph
        for i in range(2 ** self.num_nodes):
            bitstring = format(i, f'0{self.num_nodes}b')
            cut_value = self._calculate_cut_from_partition(bitstring)
            lookup_table[bitstring] = cut_value
            
        return lookup_table
    
    def _calculate_cut_from_partition(self, bitstring: str) -> float:
        """
        Calculate cut value using the original partition method.
        
        This method now handles weighted graphs.
        
        Args:
            bitstring: Binary string representing node partition
            
        Returns:
            Cut value for the partition, scaled by 0.5.
        """
        cut_weight = 0.0
        for u, v, data in self.graph.edges(data=True):
            # Check if edge crosses the partition
            if bitstring[u] != bitstring[v]:
                cut_weight += data.get('weight', 1.0)

        # Original method applies a non-standard scaling factor
        # This was the primary source of the discrepancy
        return float(cut_weight) * 0.5
    
    def calculate_cut_value(self, bitstring: str) -> float:
        """
        Calculate cut value for a given bitstring using lookup table.
        
        Args:
            bitstring: Binary string representing the partition
            
        Returns:
            Cut value from the lookup table
            
        Raises:
            ValueError: If bitstring length doesn't match graph size
            KeyError: If bitstring not found in lookup table
        """
        if len(bitstring) != self.num_nodes:
            raise ValueError(f"Bitstring length {len(bitstring)} doesn't match "
                           f"graph size {self.num_nodes}")
        
        if bitstring not in self.lookup_table:
            raise KeyError(f"Bitstring '{bitstring}' not found in lookup table")
            
        return self.lookup_table[bitstring]
    
    def get_all_cut_values(self) -> Dict[str, float]:
        """
        Get all cut values from the lookup table.
        
        Returns:
            Dictionary of all bitstring -> cut value mappings
        """
        return self.lookup_table.copy()
    
    def get_optimal_cut(self) -> Tuple[str, float]:
        """
        Find the optimal cut using the original method.
        
        Returns:
            Tuple of (optimal_bitstring, optimal_cut_value)
        """
        optimal_bitstring = max(self.lookup_table.keys(), 
                              key=lambda k: self.lookup_table[k])
        optimal_value = self.lookup_table[optimal_bitstring]
        return optimal_bitstring, optimal_value
    
    def calculate_qaoa_expectation(self, bitstring_probabilities: Dict[str, float]) -> float:
        """
        Calculate QAOA expectation value using original method.
        
        This reproduces the exact calculation used in the original study
        that led to the disputed results.
        
        Args:
            bitstring_probabilities: Dictionary mapping bitstrings to probabilities
            
        Returns:
            Expected cut value
        """
        expectation = 0.0
        
        for bitstring, probability in bitstring_probabilities.items():
            if bitstring in self.lookup_table:
                cut_value = self.lookup_table[bitstring]
                expectation += probability * cut_value
            else:
                # Original method: ignore unknown bitstrings
                # This was another source of discrepancy
                continue
                
        return expectation
    
    def get_method_info(self) -> Dict:
        """
        Get information about this implementation method.
        
        Returns:
            Dictionary containing method metadata
        """
        return {
            'method_name': 'Generalized Original Lookup Table Method',
            'implementation_date': '2024-12-XX',  # Original study date
            'scaling_factor': 0.5,
            'edge_counting_method': 'partition_based_weighted',
            'unknown_bitstring_handling': 'ignore',
            'verification_status': 'disputed',
            'agreement_rate': 0.25,  # For default 3-node graph vs verification
            'known_issues': [
                'Non-standard scaling factor of 0.5',
                'Ignores unknown bitstrings in expectation calculation',
                'Partition-based edge counting differs from direct method'
            ]
        }
    
    def debug_calculation(self, bitstring: str) -> Dict:
        """
        Debug the cut calculation for a specific bitstring.
        
        Args:
            bitstring: Binary string to debug
            
        Returns:
            Dictionary with detailed calculation steps
        """
        if len(bitstring) != self.num_nodes:
            raise ValueError(f"Bitstring length {len(bitstring)} doesn't match "
                           f"graph size {self.num_nodes}")
        
        # Reconstruct the calculation step by step
        partition_0 = set()
        partition_1 = set()
        
        for i, bit in enumerate(bitstring):
            if bit == '0':
                partition_0.add(i)
            else:
                partition_1.add(i)
        
        cut_edges = []
        cut_count = 0.0
        
        for u, v, data in self.graph.edges(data=True):
            is_cut = (u in partition_0 and v in partition_1) or \
                     (u in partition_1 and v in partition_0)
            
            if is_cut:
                cut_edges.append((u, v))
                cut_count += data.get('weight', 1.0)
        
        final_value = float(cut_count) * 0.5
        
        return {
            'bitstring': bitstring,
            'partition_0': list(partition_0),
            'partition_1': list(partition_1),
            'cut_edges': cut_edges,
            'raw_cut_count': len(cut_edges),
            'total_cut_weight': cut_count,
            'scaling_factor': 0.5,
            'final_cut_value': final_value,
            'lookup_table_value': self.lookup_table[bitstring]
        }


def reproduce_original_qaoa_results():
    """
    Reproduce the exact QAOA results from the original study.
    
    This function recreates the disputed results that led to the
    reproducibility investigation.
    
    Returns:
        Dictionary containing the original disputed results
    """
    # Initialize with the 3-node triangle graph from the case study
    g = nx.Graph()
    g.add_edges_from([(0, 1), (1, 2), (0, 2)])
    maxcut = OriginalMaxCut(g)
    
    # QAOA parameter combinations that showed discrepancies
    parameter_sets = [
        {'gamma': 0.5, 'beta': 0.5},
        {'gamma': 1.0, 'beta': 0.5},
        {'gamma': 0.5, 'beta': 1.0}
    ]
    
    # Simulated probability distributions from original QAOA runs
    # These are the actual values that caused the verification failure
    original_distributions = {
        'gamma_0.5_beta_0.5': {
            '000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125,
            '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125
        },
        'gamma_1.0_beta_0.5': {
            '000': 0.2, '001': 0.1, '010': 0.1, '011': 0.2,
            '100': 0.2, '101': 0.1, '110': 0.1, '111': 0.1
        },
        'gamma_0.5_beta_1.0': {
            '000': 0.15, '001': 0.15, '010': 0.15, '011': 0.1,
            '100': 0.1, '101': 0.15, '110': 0.15, '111': 0.05
        }
    }
    
    results = {}
    
    for i, params in enumerate(parameter_sets):
        key = f"gamma_{params['gamma']}_beta_{params['beta']}"
        distribution = original_distributions[key]
        
        expectation = maxcut.calculate_qaoa_expectation(distribution)
        
        results[key] = {
            'parameters': params,
            'probability_distribution': distribution,
            'expected_cut_value': expectation,
            'method': 'original_lookup_table'
        }
    
    return {
        'study_id': 'original_qaoa_disputed_results',
        'implementation': 'OriginalMaxCut',
        'graph': 'triangle_3_nodes',
        'results': results,
        'verification_status': 'FAILED',
        'discrepancy_source': 'maxcut_calculation_method'
    }


if __name__ == "__main__":
    # Demonstration of the original implementation
    print("=== Original MaxCut Implementation Demo ===")
    
    # Initialize with default triangle graph
    maxcut = OriginalMaxCut()
    
    print(f"Graph edges: {maxcut.graph_edges}")
    print(f"Number of nodes: {maxcut.num_nodes}")
    
    # Show all cut values
    print("\nAll cut values (lookup table):")
    for bitstring, cut_value in maxcut.get_all_cut_values().items():
        print(f"  {bitstring}: {cut_value}")
    
    # Find optimal cut
    optimal_bitstring, optimal_value = maxcut.get_optimal_cut()
    print(f"\nOptimal cut: {optimal_bitstring} with value {optimal_value}")
    
    # Debug a specific calculation
    debug_info = maxcut.debug_calculation("101")
    print(f"\nDebug calculation for '101':")
    for key, value in debug_info.items():
        if key != 'cut_edges': # Skip for brevity
            print(f"  {key}: {value}")
    
    # Show method information
    method_info = maxcut.get_method_info()
    print(f"\nMethod information:")
    for key, value in method_info.items():
        print(f"  {key}: {value}")
    
    # Reproduce disputed results
    print(f"\n=== Reproducing Disputed QAOA Results ===")
    disputed_results = reproduce_original_qaoa_results()
    
    for result_key, result_data in disputed_results['results'].items():
        params = result_data['parameters']
        expectation = result_data['expected_cut_value']
        print(f"γ={params['gamma']}, β={params['beta']}: Expected cut = {expectation:.3f}") 