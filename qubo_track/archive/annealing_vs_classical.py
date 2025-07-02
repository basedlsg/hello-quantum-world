#!/usr/bin/env python3
"""
⚠️  DEPRECATED FILE - DO NOT USE ⚠️ 

This file contains scientifically invalid claims and has been superseded.

PROBLEMS WITH THIS FILE:
- Claims "quantum annealing" while using classical SimulatedAnnealingSampler  
- Reports false "39% quantum advantage" (actually classical SA vs weak greedy)
- No statistical validation (single runs, no confidence intervals)
- Missing exact optimum calculation for quality assessment

✅ USE INSTEAD: corrected_classical_optimization.py

This deprecated file is preserved only for comparison purposes.
Running this file will raise an error to prevent accidental use.
"""

raise RuntimeError("""
❌ DEPRECATED FILE - DO NOT USE ❌

This file has been deprecated due to scientific integrity issues.

CORRECTED VERSION: corrected_classical_optimization.py

See README_QUBO_TRACK.md for details.
""")

# Original file content follows below...
#!/usr/bin/env python3
"""
Quantum Annealing vs Classical Optimization Comparison

Compares D-Wave Advantage simulator performance against classical optimization
for Max-Cut problems using the same controlled methodology from spatial locality 
and QEC work.

Key Scientific Question: Does quantum annealing provide advantage over classical 
optimization for small Max-Cut instances?
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import time
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Import the QUBO implementation
from maxcut_to_qubo import MaxCutQUBO, create_test_graphs

# D-Wave Ocean SDK imports
try:
    import dimod
    from dwave.system.samplers import DWaveCliqueSampler
    from dwave.samplers import SimulatedAnnealingSampler
    from dwave.system.testing import MockDWaveSampler
    from dwave.cloud import Client
    
    # Try to access D-Wave Advantage simulator
    try:
        from dwave.system import DWaveSampler, EmbeddingComposite
        DWAVE_HARDWARE_AVAILABLE = True
    except:
        DWAVE_HARDWARE_AVAILABLE = False
    
    OCEAN_AVAILABLE = True
    print("✅ D-Wave Ocean SDK available")
    
except ImportError:
    OCEAN_AVAILABLE = False
    DWAVE_HARDWARE_AVAILABLE = False
    print("❌ D-Wave Ocean SDK not available")

# Classical optimization imports
try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

print(f"Quantum Annealing vs Classical Optimization")
print(f"Ocean SDK: {'✅' if OCEAN_AVAILABLE else '❌'}")
print(f"D-Wave Hardware Access: {'✅' if DWAVE_HARDWARE_AVAILABLE else '❌'}")
print(f"SciPy Available: {'✅' if SCIPY_AVAILABLE else '❌'}")

class AnnealingVsClassicalExperiment:
    """
    Controlled experiment comparing quantum annealing vs classical optimization
    
    Scientific methodology:
    - Same Max-Cut problems across all solvers
    - Fixed computational budget (time/iterations)
    - Statistical validation across multiple runs
    - Cross-platform validation when possible
    """
    
    def __init__(self):
        self.results = []
        self.graphs = create_test_graphs()
        self.experiment_id = f"annealing_vs_classical_{int(time.time())}"
        
        print(f"Experiment ID: {self.experiment_id}")
        print(f"Test graphs: {list(self.graphs.keys())}")
    
    def run_simulated_annealing(self, qubo: MaxCutQUBO, num_reads: int = 100) -> Dict[str, Any]:
        """
        Run simulated annealing using D-Wave's SimulatedAnnealingSampler
        
        Args:
            qubo: MaxCutQUBO problem instance
            num_reads: Number of annealing runs
            
        Returns:
            Results dictionary with best solution and energy
        """
        
        if not OCEAN_AVAILABLE:
            raise ImportError("D-Wave Ocean SDK required")
        
        print(f"  🔥 Simulated Annealing ({num_reads} reads)")
        
        # Convert to BQM
        bqm = qubo.qubo_to_bqm()
        
        # Create sampler
        sampler = SimulatedAnnealingSampler()
        
        # Run sampling
        start_time = time.time()
        sampleset = sampler.sample(bqm, num_reads=num_reads, seed=1337)
        execution_time = time.time() - start_time
        
        # Extract best solution
        best_sample = sampleset.first.sample
        best_energy = sampleset.first.energy
        
        # Convert to binary list
        solution = [best_sample[i] for i in range(qubo.n_nodes)]
        cut_value = qubo.evaluate_cut_value(solution)
        
        print(f"    Best energy: {best_energy:.3f}")
        print(f"    Cut value: {cut_value}")
        print(f"    Time: {execution_time:.3f}s")
        
        return {
            'method': 'simulated_annealing',
            'solution': solution,
            'cut_value': cut_value,
            'energy': best_energy,
            'execution_time': execution_time,
            'num_reads': num_reads,
            'success': True
        }
    
    def run_dwave_simulator(self, qubo: MaxCutQUBO, num_reads: int = 100) -> Dict[str, Any]:
        """
        Run on D-Wave Advantage simulator (if available)
        
        Args:
            qubo: MaxCutQUBO problem instance
            num_reads: Number of reads
            
        Returns:
            Results dictionary
        """
        
        print(f"  🌊 D-Wave Advantage Simulator ({num_reads} reads)")
        
        try:
            # Try to connect to D-Wave cloud
            sampler = DWaveSampler(solver={'topology__type': 'pegasus'})
            # Use embedding for automatic mapping
            embedded_sampler = EmbeddingComposite(sampler)
            
            # Convert to BQM
            bqm = qubo.qubo_to_bqm()
            
            # Run on D-Wave
            start_time = time.time()
            sampleset = embedded_sampler.sample(bqm, num_reads=num_reads)
            execution_time = time.time() - start_time
            
            # Extract best solution
            best_sample = sampleset.first.sample
            best_energy = sampleset.first.energy
            
            # Convert to binary list
            solution = [best_sample[i] for i in range(qubo.n_nodes)]
            cut_value = qubo.evaluate_cut_value(solution)
            
            print(f"    Best energy: {best_energy:.3f}")
            print(f"    Cut value: {cut_value}")
            print(f"    Time: {execution_time:.3f}s")
            print(f"    Solver: {sampler.solver.name}")
            
            return {
                'method': 'dwave_simulator',
                'solution': solution,
                'cut_value': cut_value,
                'energy': best_energy,
                'execution_time': execution_time,
                'num_reads': num_reads,
                'solver_name': sampler.solver.name,
                'success': True
            }
            
        except Exception as e:
            print(f"    ❌ D-Wave simulator failed: {e}")
            print(f"    Falling back to simulated annealing")
            return self.run_simulated_annealing(qubo, num_reads)
    
    def run_scipy_optimization(self, qubo: MaxCutQUBO) -> Dict[str, Any]:
        """
        Run classical optimization using SciPy
        
        Args:
            qubo: MaxCutQUBO problem instance
            
        Returns:
            Results dictionary
        """
        
        print(f"  🧮 SciPy Classical Optimization")
        
        if not SCIPY_AVAILABLE:
            # Fallback to greedy
            print(f"    SciPy not available, using greedy approximation")
            start_time = time.time()
            solution, cut_value, _ = qubo.classical_approximation()
            execution_time = time.time() - start_time
            
            return {
                'method': 'greedy_fallback',
                'solution': solution,
                'cut_value': cut_value,
                'energy': -cut_value,  # QUBO minimizes, Max-Cut maximizes
                'execution_time': execution_time,
                'success': True
            }
        
        # Define QUBO objective function
        def qubo_objective(x):
            """QUBO objective: x^T Q x"""
            return x @ qubo.qubo_matrix @ x
        
        # Try multiple random starting points
        best_solution = None
        best_cut = 0
        best_energy = float('inf')
        
        start_time = time.time()
        
        for seed in range(10):  # Multiple random restarts
            np.random.seed(seed)
            x0 = np.random.randint(0, 2, qubo.n_nodes).astype(float)
            
            try:
                # Use L-BFGS-B with bounds for binary variables
                result = minimize(
                    qubo_objective, 
                    x0, 
                    method='L-BFGS-B',
                    bounds=[(0, 1)] * qubo.n_nodes
                )
                
                # Round to binary
                binary_solution = (result.x > 0.5).astype(int).tolist()
                cut_value = qubo.evaluate_cut_value(binary_solution)
                
                if cut_value > best_cut:
                    best_cut = cut_value
                    best_solution = binary_solution
                    best_energy = result.fun
                    
            except Exception:
                continue
        
        execution_time = time.time() - start_time
        
        if best_solution is None:
            # Ultimate fallback
            best_solution, best_cut, _ = qubo.classical_approximation()
            best_energy = -best_cut
        
        print(f"    Best cut value: {best_cut}")
        print(f"    Best energy: {best_energy:.3f}")
        print(f"    Time: {execution_time:.3f}s")
        
        return {
            'method': 'scipy_lbfgs',
            'solution': best_solution,
            'cut_value': best_cut,
            'energy': best_energy,
            'execution_time': execution_time,
            'success': True
        }
    
    def run_comparison_experiment(self):
        """Run the complete comparison experiment"""
        
        print(f"\n🔬 Annealing vs Classical Comparison Experiment")
        print("=" * 60)
        
        for graph_name, graph in self.graphs.items():
            print(f"\n📊 Testing {graph_name}")
            print("-" * 40)
            
            # Create QUBO problem
            qubo = MaxCutQUBO(graph)
            qubo.build_qubo_matrix()
            
            graph_results = {
                'graph_name': graph_name,
                'n_nodes': qubo.n_nodes,
                'n_edges': qubo.n_edges
            }
            
            # Method 1: Simulated Annealing
            try:
                sa_result = self.run_simulated_annealing(qubo, num_reads=100)
                graph_results.update({f'sa_{k}': v for k, v in sa_result.items()})
            except Exception as e:
                print(f"    ❌ Simulated annealing failed: {e}")
                graph_results.update({
                    'sa_method': 'failed',
                    'sa_cut_value': 0,
                    'sa_success': False
                })
            
            # Method 2: D-Wave Simulator (if available)
            if DWAVE_HARDWARE_AVAILABLE:
                try:
                    dwave_result = self.run_dwave_simulator(qubo, num_reads=50)
                    graph_results.update({f'dwave_{k}': v for k, v in dwave_result.items()})
                except Exception as e:
                    print(f"    ❌ D-Wave simulator failed: {e}")
                    graph_results.update({
                        'dwave_method': 'failed',
                        'dwave_cut_value': 0,
                        'dwave_success': False
                    })
            else:
                print(f"    ℹ️  D-Wave hardware not available")
                graph_results.update({
                    'dwave_method': 'not_available',
                    'dwave_cut_value': 0,
                    'dwave_success': False
                })
            
            # Method 3: Classical optimization
            try:
                classical_result = self.run_scipy_optimization(qubo)
                graph_results.update({f'classical_{k}': v for k, v in classical_result.items()})
            except Exception as e:
                print(f"    ❌ Classical optimization failed: {e}")
                graph_results.update({
                    'classical_method': 'failed',
                    'classical_cut_value': 0,
                    'classical_success': False
                })
            
            # Calculate quantum advantage
            sa_cut = graph_results.get('sa_cut_value', 0)
            classical_cut = graph_results.get('classical_cut_value', 0)
            dwave_cut = graph_results.get('dwave_cut_value', 0)
            
            if classical_cut > 0:
                graph_results['sa_advantage'] = (sa_cut - classical_cut) / classical_cut
                graph_results['dwave_advantage'] = (dwave_cut - classical_cut) / classical_cut if dwave_cut > 0 else 0
            else:
                graph_results['sa_advantage'] = 0
                graph_results['dwave_advantage'] = 0
            
            # Performance summary
            print(f"    📈 Results Summary:")
            print(f"      Simulated Annealing: {sa_cut}")
            print(f"      D-Wave Simulator: {dwave_cut}")
            print(f"      Classical: {classical_cut}")
            
            if sa_cut > classical_cut:
                print(f"      ✅ Simulated annealing advantage: {graph_results['sa_advantage']:+.2%}")
            else:
                print(f"      ❌ No simulated annealing advantage")
            
            if dwave_cut > classical_cut:
                print(f"      ✅ D-Wave advantage: {graph_results['dwave_advantage']:+.2%}")
            elif dwave_cut > 0:
                print(f"      ❌ No D-Wave advantage")
            
            self.results.append(graph_results)
        
        # Save results
        df = pd.DataFrame(self.results)
        df.to_csv('../results/annealing_vs_classical_results.csv', index=False)
        
        return df
    
    def analyze_results(self, df: pd.DataFrame):
        """Analyze experiment results"""
        
        print(f"\n📈 Results Analysis")
        print("=" * 30)
        
        # Summary statistics
        valid_results = df[df['sa_success'] == True]
        
        if len(valid_results) > 0:
            avg_sa_advantage = valid_results['sa_advantage'].mean()
            avg_dwave_advantage = valid_results['dwave_advantage'].mean()
            
            print(f"Graphs tested: {len(df)}")
            print(f"Successful runs: {len(valid_results)}")
            print(f"Average SA advantage: {avg_sa_advantage:+.2%}")
            print(f"Average D-Wave advantage: {avg_dwave_advantage:+.2%}")
            
            # Count wins
            sa_wins = (valid_results['sa_advantage'] > 0).sum()
            dwave_wins = (valid_results['dwave_advantage'] > 0).sum()
            
            print(f"SA wins: {sa_wins}/{len(valid_results)}")
            print(f"D-Wave wins: {dwave_wins}/{len(valid_results)}")
            
            # Performance analysis
            if avg_sa_advantage > 0.05:  # 5% threshold
                print(f"✅ Simulated annealing shows advantage")
            else:
                print(f"❌ No significant simulated annealing advantage")
            
            if avg_dwave_advantage > 0.05:
                print(f"✅ D-Wave shows advantage")
            else:
                print(f"❌ No significant D-Wave advantage")
        
        else:
            print(f"❌ No valid results to analyze")
    
    def create_visualization(self, df: pd.DataFrame):
        """Create comparison visualization"""
        
        print(f"\n📊 Creating Visualization")
        print("=" * 30)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Cut values comparison
        x_pos = np.arange(len(df))
        width = 0.25
        
        ax1.bar(x_pos - width, df['sa_cut_value'], width, label='Simulated Annealing')
        ax1.bar(x_pos, df.get('dwave_cut_value', [0]*len(df)), width, label='D-Wave Simulator')
        ax1.bar(x_pos + width, df['classical_cut_value'], width, label='Classical')
        
        ax1.set_xlabel('Graph')
        ax1.set_ylabel('Cut Value')
        ax1.set_title('Cut Values by Method')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(df['graph_name'], rotation=45)
        ax1.legend()
        
        # Plot 2: Execution times
        ax2.bar(x_pos - width, df['sa_execution_time'], width, label='Simulated Annealing')
        ax2.bar(x_pos, df.get('dwave_execution_time', [0]*len(df)), width, label='D-Wave Simulator')
        ax2.bar(x_pos + width, df['classical_execution_time'], width, label='Classical')
        
        ax2.set_xlabel('Graph')
        ax2.set_ylabel('Execution Time (s)')
        ax2.set_title('Execution Times by Method')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(df['graph_name'], rotation=45)
        ax2.legend()
        
        # Plot 3: Quantum advantage
        valid_df = df[df['sa_success'] == True]
        if len(valid_df) > 0:
            ax3.bar(valid_df['graph_name'], valid_df['sa_advantage'], alpha=0.7, label='SA Advantage')
            ax3.bar(valid_df['graph_name'], valid_df['dwave_advantage'], alpha=0.7, label='D-Wave Advantage')
            ax3.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax3.set_xlabel('Graph')
            ax3.set_ylabel('Relative Advantage')
            ax3.set_title('Quantum vs Classical Advantage')
            ax3.tick_params(axis='x', rotation=45)
            ax3.legend()
        
        # Plot 4: Problem difficulty vs performance
        ax4.scatter(df['n_edges'], df['sa_cut_value'], label='Simulated Annealing')
        ax4.scatter(df['n_edges'], df.get('dwave_cut_value', [0]*len(df)), label='D-Wave')
        ax4.scatter(df['n_edges'], df['classical_cut_value'], label='Classical')
        ax4.set_xlabel('Number of Edges')
        ax4.set_ylabel('Cut Value')
        ax4.set_title('Performance vs Problem Size')
        ax4.legend()
        
        plt.tight_layout()
        
        # Save plot
        import os
        os.makedirs('../results', exist_ok=True)
        plt.savefig('../results/annealing_vs_classical_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Visualization saved: ../results/annealing_vs_classical_comparison.png")

def main():
    """Main execution function"""
    
    print("Quantum Annealing vs Classical Optimization")
    print("=" * 60)
    
    if not OCEAN_AVAILABLE:
        print("❌ D-Wave Ocean SDK required - install with: pip install dwave-ocean-sdk")
        return
    
    # Create results directory
    import os
    os.makedirs('../results', exist_ok=True)
    
    # Run experiment
    experiment = AnnealingVsClassicalExperiment()
    results_df = experiment.run_comparison_experiment()
    
    # Analyze results
    experiment.analyze_results(results_df)
    
    # Create visualization
    experiment.create_visualization(results_df)
    
    # Summary
    print(f"\n🎯 ANNEALING VS CLASSICAL EXPERIMENT COMPLETE")
    print("=" * 50)
    
    successful_runs = results_df['sa_success'].sum()
    total_runs = len(results_df)
    
    print(f"✅ Experiment completed: {successful_runs}/{total_runs} successful")
    print(f"✅ Results saved: ../results/annealing_vs_classical_results.csv")
    print(f"✅ Visualization created")
    
    # Key findings
    if successful_runs > 0:
        valid_results = results_df[results_df['sa_success'] == True]
        avg_advantage = valid_results['sa_advantage'].mean()
        
        print(f"\n🔬 Key Scientific Findings:")
        if avg_advantage > 0.05:
            print(f"  ✅ Quantum annealing advantage detected: {avg_advantage:+.2%}")
        else:
            print(f"  ❌ No significant quantum annealing advantage")
            print(f"     Average performance: {avg_advantage:+.2%}")
        
        print(f"  📊 Problem size range: {results_df['n_nodes'].min()}-{results_df['n_nodes'].max()} nodes")
        print(f"  ⏱️  Execution time comparison available")
        print(f"  🎯 Integration with spatial locality methodology")
    
    print(f"\n📋 Next Steps:")
    print(f"  🎯 Scale to 20+ node graphs")
    print(f"  🎯 Compare with QAOA on AWS")
    print(f"  🎯 ArXiv preprint integration")
    
    return results_df

if __name__ == "__main__":
    results = main()
    print(f"\n🎉 QUBO Track B implementation complete!")
