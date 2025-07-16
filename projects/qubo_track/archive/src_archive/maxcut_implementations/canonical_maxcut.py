"""
Canonical MaxCut Implementation - Direct Edge Counting

This implementation provides a correct, generalized, and validated
method for calculating the MaxCut cost function for weighted graphs.
It is based on the first-principles definition of the MaxCut problem,
which is to maximize the sum of weights of edges that cross a partition.

This implementation serves as the new "ground truth" for the case study,
following the discovery that the canonical PennyLane library (in the version
tested) does not correctly handle weighted graphs.

Author: Quantum Reproducibility Case Study Team
License: MIT
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple

# Add parent directory to path to import our local modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .original_maxcut import OriginalMaxCut


class CanonicalMaxCut:
    """
    Canonical MaxCut implementation using direct, weighted edge counting.
    This is the scientifically correct implementation for the weighted
    MaxCut problem.
    """

    def __init__(self, graph: nx.Graph = None):
        """
        Initialize the CanonicalMaxCut calculator.

        Args:
            graph: A networkx Graph object. If None, uses the default
                   3-node unweighted triangle graph.
        """
        if graph is None:
            default_graph = nx.Graph()
            default_graph.add_edges_from([(0, 1), (1, 2), (0, 2)])
            self.graph = default_graph
        else:
            self.graph = graph

        self.num_nodes = self.graph.number_of_nodes()

    def calculate_cut_value(self, bitstring: str) -> float:
        """
        Calculate cut value for a given bitstring by summing the weights
        of the edges that cross the partition.

        Args:
            bitstring: Binary string representing the partition.

        Returns:
            The total weight of the edges in the cut.
        """
        if len(bitstring) != self.num_nodes:
            raise ValueError(f"Bitstring length {len(bitstring)} doesn't match "
                           f"graph size {self.num_nodes}")

        cut_weight = 0.0
        for u, v, data in self.graph.edges(data=True):
            if bitstring[u] != bitstring[v]:
                cut_weight += data.get('weight', 1.0)

        return float(cut_weight)

    def get_all_cut_values(self) -> Dict[str, float]:
        """
        Calculate all cut values for every possible bitstring.
        """
        cut_values = {}
        for i in range(2 ** self.num_nodes):
            bitstring = format(i, f'0{self.num_nodes}b')
            cut_value = self.calculate_cut_value(bitstring)
            cut_values[bitstring] = cut_value
        return cut_values

    def get_optimal_cut(self) -> Tuple[str, float]:
        """
        Find the optimal cut by maximizing the total cut weight.
        """
        all_cuts = self.get_all_cut_values()
        optimal_bitstring = max(all_cuts, key=all_cuts.get)
        optimal_value = all_cuts[optimal_bitstring]
        return optimal_bitstring, optimal_value

    def calculate_qaoa_expectation(self, bitstring_probabilities: Dict[str, float]) -> float:
        """
        Calculates the QAOA expectation value (the average cut value) based
        on a given probability distribution of bitstrings.

        Args:
            bitstring_probabilities: Dictionary mapping bitstrings to probabilities.

        Returns:
            The expected cut value.
        """
        expectation = 0.0
        for bitstring, probability in bitstring_probabilities.items():
            cut_value = self.calculate_cut_value(bitstring)
            expectation += probability * cut_value
        return expectation

    def get_method_info(self) -> Dict:
        """
        Get information about this implementation method.
        """
        return {
            'method_name': 'Canonical Direct Weighted Edge Counting',
            'scaling_factor': 1.0,
            'description': 'Calculates the sum of weights for edges crossing the partition.',
            'verification_status': 'Validated against first principles.'
        } 