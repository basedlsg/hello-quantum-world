#!/usr/bin/env python3
"""
Max-Cut to QUBO Conversion

Converts the 6-node Max-Cut problem from gate-model quantum computing 
to quantum annealing formulation using D-Wave Ocean SDK.

Building on the spatial locality and QEC work - same controlled methodology
applied to quantum annealing vs classical optimization comparison.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Tuple, Any
import time

# Ocean SDK imports (install: pip install dwave-ocean-sdk)
try:
    import dimod
    from dwave.system import DWaveSampler, EmbeddingComposite
    from dwave.system import LeapHybridSampler
    from dwave.cloud import Client
    from dwave.system.samplers import DWaveCliqueSampler
    from dwave.system.testing import MockDWaveSampler
    from dwave.system import FixedEmbeddingComposite
    OCEAN_AVAILABLE = True
    print("✅ D-Wave Ocean SDK available")
except ImportError:
    OCEAN_AVAILABLE = False
    print("⚠️  D-Wave Ocean SDK not available - using mock implementation")

# Classical optimization baseline
try:
    import tabu
    TABU_AVAILABLE = True
except ImportError:
    TABU_AVAILABLE = False
    print("ℹ️  Tabu search not available - using NetworkX approximation")

print(f"QUBO Track: Max-Cut Quantum Annealing Implementation")
print(f"Ocean SDK: {'✅ Available' if OCEAN_AVAILABLE else '❌ Not Available'}")

class MaxCutQUBO:
    """
    Max-Cut problem formulated as QUBO for quantum annealing
    
    QUBO formulation: minimize x^T Q x
    where Q encodes the Max-Cut objective as a quadratic form
    
    Scientific methodology: Same controlled variables approach from 
    spatial locality and QEC work
    """
    
    def __init__(self, graph: nx.Graph):
        """
        Initialize Max-Cut QUBO formulation
        
        Args:
            graph: NetworkX graph for Max-Cut problem
        """
        self.graph = graph
        self.n_nodes = len(graph.nodes())
        self.n_edges = len(graph.edges())
        self.qubo_matrix = None
        self.problem_id = f"maxcut_{self.n_nodes}nodes_{self.n_edges}edges"
        
        print(f"Max-Cut QUBO Problem: {self.n_nodes} nodes, {self.n_edges} edges")
        
    def build_qubo_matrix(self) -> np.ndarray:
        """
        Build QUBO matrix Q for Max-Cut problem
        
        Max-Cut objective: maximize Σ_{(i,j) ∈ E} w_{ij} * (x_i + x_j - 2*x_i*x_j)
        QUBO form: minimize x^T Q x where Q_{ii} = -Σ_{j∈N(i)} w_{ij}
                                          Q_{ij} = 2*w_{ij} for (i,j) ∈ E
        
        Returns:
            QUBO matrix Q (n×n symmetric matrix)
        """
        
        Q = np.zeros((self.n_nodes, self.n_nodes))
        
        # Build QUBO matrix from graph edges
        for i, j, data in self.graph.edges(data=True):
            weight = data.get('weight', 1.0)  # Default weight = 1
            
            # Off-diagonal terms: Q_{ij} = 2*w_{ij}
            Q[i, j] += 2 * weight
            Q[j, i] += 2 * weight
            
            # Diagonal terms: Q_{ii} -= w_{ij}, Q_{jj} -= w_{ij}
            Q[i, i] -= weight
            Q[j, j] -= weight
        
        self.qubo_matrix = Q
        
        print(f"QUBO matrix built: {Q.shape}, density: {np.count_nonzero(Q)}/{Q.size}")
        print(f"Diagonal terms: {np.diag(Q)}")
        
        return Q
    
    def qubo_to_bqm(self) -> 'dimod.BinaryQuadraticModel':
        """
        Convert QUBO matrix to D-Wave Binary Quadratic Model (BQM)
        
        Returns:
            BQM representation for D-Wave samplers
        """
        
        if not OCEAN_AVAILABLE:
            raise ImportError("D-Wave Ocean SDK required for BQM conversion")
        
        if self.qubo_matrix is None:
            self.build_qubo_matrix()
        
        # Convert to dictionary format for dimod
        Q_dict = {}
        n = self.qubo_matrix.shape[0]
        
        for i in range(n):
            for j in range(i, n):  # Upper triangular
                if self.qubo_matrix[i, j] != 0:
                    if i == j:
                        Q_dict[(i, i)] = self.qubo_matrix[i, i]
                    else:
                        Q_dict[(i, j)] = self.qubo_matrix[i, j]
        
        # Create BQM from QUBO
        bqm = dimod.BinaryQuadraticModel.from_qubo(Q_dict)
        
        print(f"BQM created: {len(bqm.variables)} variables, {len(bqm.quadratic)} interactions")
        
        return bqm
    
    def evaluate_cut_value(self, solution: List[int]) -> int:
        """
        Evaluate Max-Cut value for a given binary solution
        
        Args:
            solution: Binary assignment (0 or 1 for each node)
            
        Returns:
            Cut value (number of edges crossing the cut)
        """
        
        cut_value = 0
        
        for i, j, data in self.graph.edges(data=True):
            weight = data.get('weight', 1.0)
            # Edge contributes to cut if endpoints in different partitions
            if solution[i] != solution[j]:
                cut_value += weight
        
        return int(cut_value)
    
    def classical_approximation(self) -> Tuple[List[int], int, float]:
        """
        Classical approximation using NetworkX or tabu search
        
        Returns:
            (solution, cut_value, execution_time)
        """
        
        start_time = time.time()
        
        try:
            # Try NetworkX max_weight_matching approximation
            if hasattr(nx, 'approximation') and hasattr(nx.approximation, 'max_cut'):
                cut_edges = nx.approximation.max_cut(self.graph)
                partition_0 = set(cut_edges[0])
                solution = [1 if node in partition_0 else 0 for node in range(self.n_nodes)]
                cut_value = self.evaluate_cut_value(solution)
            else:
                # Simple greedy approximation
                solution = self._greedy_max_cut()
                cut_value = self.evaluate_cut_value(solution)
                
        except Exception as e:
            print(f"Classical approximation failed: {e}")
            # Random solution as fallback
            solution = [np.random.randint(0, 2) for _ in range(self.n_nodes)]
            cut_value = self.evaluate_cut_value(solution)
        
        execution_time = time.time() - start_time
        
        print(f"Classical approximation: cut_value={cut_value}, time={execution_time:.3f}s")
        
        return solution, cut_value, execution_time
    
    def _greedy_max_cut(self) -> List[int]:
        """Simple greedy Max-Cut approximation"""
        
        solution = [0] * self.n_nodes
        
        for node in range(self.n_nodes):
            # Try both assignments and keep the better one
            cut_0 = self.evaluate_cut_value(solution)
            
            solution[node] = 1
            cut_1 = self.evaluate_cut_value(solution)
            
            if cut_0 > cut_1:
                solution[node] = 0
        
        return solution

def create_test_graphs() -> Dict[str, nx.Graph]:
    """Create test graphs for QUBO analysis"""
    
    graphs = {}
    
    # 1. Six-node complete graph (same as gate-model work)
    K6 = nx.complete_graph(6)
    graphs['K6_complete'] = K6
    
    # 2. Six-node path graph  
    P6 = nx.path_graph(6)
    graphs['P6_path'] = P6
    
    # 3. Six-node cycle graph
    C6 = nx.cycle_graph(6)
    graphs['C6_cycle'] = C6
    
    # 4. Random 6-node graph (same seed as spatial locality work)
    np.random.seed(1337)
    G_random = nx.erdos_renyi_graph(6, 0.5, seed=1337)
    graphs['G6_random'] = G_random
    
    # 5. Weighted 6-node graph
    G_weighted = nx.complete_graph(6)
    for i, j in G_weighted.edges():
        G_weighted[i][j]['weight'] = np.random.uniform(0.5, 2.0)
    graphs['K6_weighted'] = G_weighted
    
    print(f"Test graphs created: {list(graphs.keys())}")
    
    return graphs

def analyze_qubo_properties(qubo: MaxCutQUBO):
    """Analyze QUBO matrix properties"""
    
    print(f"\n🔍 QUBO Analysis: {qubo.problem_id}")
    print("=" * 40)
    
    Q = qubo.qubo_matrix
    
    # Matrix properties
    print(f"Matrix size: {Q.shape}")
    print(f"Density: {np.count_nonzero(Q)}/{Q.size} ({100*np.count_nonzero(Q)/Q.size:.1f}%)")
    print(f"Symmetry check: {np.allclose(Q, Q.T)}")
    print(f"Eigenvalue range: [{np.min(np.linalg.eigvals(Q)):.3f}, {np.max(np.linalg.eigvals(Q)):.3f}]")
    
    # Problem difficulty indicators
    condition_number = np.linalg.cond(Q)
    print(f"Condition number: {condition_number:.2e}")
    
    if condition_number > 1e12:
        print("⚠️  High condition number - may be numerically challenging")
    else:
        print("✅ Well-conditioned matrix")
    
    # Graph properties
    print(f"\nGraph properties:")
    print(f"  Max degree: {max(dict(qubo.graph.degree()).values())}")
    print(f"  Clustering: {nx.average_clustering(qubo.graph):.3f}")
    print(f"  Connectivity: {'Connected' if nx.is_connected(qubo.graph) else 'Disconnected'}")

def run_qubo_analysis():
    """Run comprehensive QUBO analysis on test graphs"""
    
    print("\n🔬 QUBO Analysis Suite")
    print("=" * 50)
    
    graphs = create_test_graphs()
    results = []
    
    for graph_name, graph in graphs.items():
        print(f"\n📊 Analyzing {graph_name}")
        print("-" * 30)
        
        # Create QUBO problem
        qubo = MaxCutQUBO(graph)
        Q = qubo.build_qubo_matrix()
        
        # Analyze properties
        analyze_qubo_properties(qubo)
        
        # Classical baseline
        classical_solution, classical_cut, classical_time = qubo.classical_approximation()
        
        # Store results
        result = {
            'graph_name': graph_name,
            'n_nodes': qubo.n_nodes,
            'n_edges': qubo.n_edges,
            'classical_cut_value': classical_cut,
            'classical_time_s': classical_time,
            'matrix_density': np.count_nonzero(Q) / Q.size,
            'condition_number': np.linalg.cond(Q)
        }
        
        results.append(result)
        
        print(f"✅ Classical baseline: {classical_cut} (time: {classical_time:.3f}s)")
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv('../results/qubo_analysis_results.csv', index=False)
    
    print(f"\n📊 QUBO Analysis Summary:")
    print(f"  Graphs analyzed: {len(results)}")
    print(f"  Best classical cut: {df['classical_cut_value'].max()}")
    print(f"  Average density: {df['matrix_density'].mean():.3f}")
    print(f"  Results saved: ../results/qubo_analysis_results.csv")
    
    return df

def create_qubo_visualization(results_df: pd.DataFrame):
    """Create visualization of QUBO analysis results"""
    
    print(f"\n📈 Creating QUBO Visualizations")
    print("=" * 35)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Cut values by graph type
    ax1.bar(results_df['graph_name'], results_df['classical_cut_value'])
    ax1.set_title('Max-Cut Values by Graph Type')
    ax1.set_ylabel('Cut Value')
    ax1.tick_params(axis='x', rotation=45)
    
    # Plot 2: Execution times
    ax2.bar(results_df['graph_name'], results_df['classical_time_s'])
    ax2.set_title('Classical Solver Execution Time')
    ax2.set_ylabel('Time (seconds)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Plot 3: Matrix properties
    ax3.scatter(results_df['matrix_density'], results_df['classical_cut_value'])
    ax3.set_xlabel('QUBO Matrix Density')
    ax3.set_ylabel('Cut Value')
    ax3.set_title('Cut Value vs Matrix Density')
    
    # Plot 4: Problem difficulty
    ax4.semilogy(results_df['graph_name'], results_df['condition_number'])
    ax4.set_title('QUBO Matrix Condition Number')
    ax4.set_ylabel('Condition Number (log scale)')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save plot
    import os
    os.makedirs('../results', exist_ok=True)
    plt.savefig('../results/qubo_analysis_plots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Visualization saved: ../results/qubo_analysis_plots.png")

def main():
    """Main execution function"""
    
    print("Max-Cut to QUBO Conversion")
    print("=" * 50)
    
    # Create results directory
    import os
    os.makedirs('../results', exist_ok=True)
    
    # Run QUBO analysis
    results_df = run_qubo_analysis()
    
    # Create visualizations
    create_qubo_visualization(results_df)
    
    # Summary
    print(f"\n🎯 QUBO IMPLEMENTATION SUMMARY")
    print("=" * 40)
    
    print(f"✅ QUBO formulation implemented")
    print(f"✅ Classical baselines established")
    print(f"✅ Problem analysis completed")
    print(f"✅ Visualization generated")
    
    if OCEAN_AVAILABLE:
        print(f"✅ D-Wave Ocean SDK ready")
        print(f"🚀 Ready for quantum annealing experiments!")
    else:
        print(f"⚠️  Install D-Wave Ocean SDK for quantum annealing:")
        print(f"   pip install dwave-ocean-sdk")
    
    print(f"\n📋 Next Steps:")
    print(f"  🎯 D-Wave Advantage simulator validation")
    print(f"  🎯 Quantum vs classical comparison")
    print(f"  🎯 Scaling analysis to 20+ nodes")
    print(f"  🎯 Integration with spatial locality findings")
    
    return results_df

if __name__ == "__main__":
    results = main()
    print(f"\n🎉 Max-Cut QUBO implementation complete!")
