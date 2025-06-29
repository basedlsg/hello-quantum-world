"""
QAOA Performance Analysis with Noisy Simulation

This script addresses the critique that the case study was limited to
noiseless simulation. It investigates the impact of the cost function
implementation error on the performance of a QAOA optimization in a
simulated noisy environment.

Methodology:
1. Define a 4-node weighted graph for the MaxCut problem.
2. Set up a noisy simulator using the Amazon Braket SDK's Density Matrix
   simulator with a depolarizing error model.
3. Define a QAOA objective function that takes angles and a MaxCut
   implementation as input.
4. Run two separate optimizations using scipy.optimize.minimize:
    a) One using the correct `CanonicalMaxCut` implementation.
    b) One using the flawed `OriginalMaxCut` implementation.
5. Compare the results: convergence path, final cost, and the
   "true" quality of the solution (approximation ratio).

The hypothesis is that the flawed cost function will mislead the classical
optimizer, resulting in a suboptimal solution, and that this effect
will be observable even in the presence of quantum noise.

Author: Quantum Reproducibility Case Study Team
License: MIT
"""

import numpy as np
import networkx as nx
from scipy.optimize import minimize
import matplotlib.pyplot as plt

from braket.circuits import Circuit, Noise
from braket.devices import LocalSimulator

def create_qaoa_circuit(graph, p, gamma, beta):
    """Creates the QAOA circuit with noise channels."""
    n_qubits = graph.number_of_nodes()
    circuit = Circuit()
    circuit.h(range(n_qubits))

    for i in range(p):
        # Cost Layer
        for u, v in graph.edges:
            circuit.cnot(u, v)
            circuit.rz(v, 2 * gamma[i])
            circuit.cnot(u, v)
            # Add depolarizing noise after each 2-qubit gate
            circuit.depolarizing(target=[u, v], probability=0.01)

        # Mixer Layer
        circuit.rx(range(n_qubits), 2 * beta[i])

    return circuit

def get_qaoa_objective_function(graph, p, noisy_simulator, max_cut_impl):
    """
    Returns a function that calculates the expected cut value for given
    QAOA angles.
    """
    def objective_function(params):
        # Split params into gamma and beta
        gamma = params[:p]
        beta = params[p:]

        # Create and run the circuit
        qaoa_circuit = create_qaoa_circuit(graph, p, gamma, beta)
        # We need probabilities to calculate the classical expectation
        qaoa_circuit.probability()
        
        result = noisy_simulator.run(qaoa_circuit, shots=0).result()
        probabilities = result.values[0]

        # Calculate expectation value using the provided MaxCut implementation
        expected_value = 0
        for i, prob in enumerate(probabilities):
            bitstring = format(i, f'0{graph.number_of_nodes()}b')
            cut_value = max_cut_impl.calculate_cut_value(bitstring)
            expected_value += prob * cut_value
            
        # We are minimizing, so we return the expectation value.
        # For CanonicalMaxCut, a lower value (more negative) is better.
        # For OriginalMaxCut, the optimizer will also minimize its value.
        return expected_value

    return objective_function

def run_noisy_analysis():
    """
    Runs the full noisy analysis and compares the performance of optimizations
    using the canonical vs. the original flawed cost function.
    """
    print("=" * 70)
    print("  Starting QAOA Performance Analysis in a Noisy Environment")
    print("=" * 70)

    # --- Setup ---
    # 1. Define weighted graph
    graph = nx.Graph()
    graph.add_edge(0, 1, weight=1.5)
    graph.add_edge(1, 2, weight=2.0)
    graph.add_edge(2, 3, weight=0.5)
    graph.add_edge(3, 0, weight=1.0)
    
    # 2. Setup noisy simulator
    noisy_device = LocalSimulator(backend="braket_dm")
    
    # 3. Instantiate MaxCut implementations
    canonical_impl = CanonicalMaxCut(graph)
    original_impl = OriginalMaxCut(graph)

    p_layers = 2
    initial_params = np.random.rand(2 * p_layers)
    
    # --- Run Optimizations ---
    print("Running optimization with CANONICAL cost function...")
    canonical_objective = get_qaoa_objective_function(graph, p_layers, noisy_device, canonical_impl)
    canonical_res = minimize(canonical_objective, initial_params, method='COBYLA')
    print("Canonical optimization complete.")

    print("\nRunning optimization with FLAWED (Original) cost function...")
    original_objective = get_qaoa_objective_function(graph, p_layers, noisy_device, original_impl)
    original_res = minimize(original_objective, initial_params, method='COBYLA')
    print("Flawed optimization complete.")
    
    # --- Analyze and Compare Results ---
    print("\n" + "=" * 70)
    print("                 Comparison of Optimization Results")
    print("=" * 70)

    # Get final parameters and costs
    final_params_canonical = canonical_res.x
    final_cost_canonical = canonical_res.fun

    final_params_original = original_res.x
    final_cost_original = original_res.fun

    # What is the TRUE quality of the solution found by the flawed method?
    # We evaluate the parameters it found using the CANONICAL cost function.
    true_cost_of_original_solution = canonical_objective(final_params_original)

    # Find the true optimal solution for this weighted graph
    true_optimal_cut = canonical_impl.get_optimal_cut()[1]

    # Calculate approximation ratios
    approx_ratio_canonical = final_cost_canonical / true_optimal_cut
    approx_ratio_original = true_cost_of_original_solution / true_optimal_cut

    print(f"{'Metric':<25} | {'Canonical Optimizer':<25} | {'Flawed Optimizer'}")
    print("-" * 70)
    print(f"{'Final Cost Reported':<25} | {final_cost_canonical:<25.4f} | {final_cost_original:<.4f} (Incorrectly Scaled)")
    print(f"{'True Solution Quality':<25} | {final_cost_canonical:<25.4f} | {true_cost_of_original_solution:<.4f}")
    print("-" * 70)
    print(f"True Optimal Cut Value: {true_optimal_cut:.4f}")
    print(f"Approximation Ratio (Canonical): {approx_ratio_canonical:.3f}")
    print(f"Approximation Ratio (Flawed):   {approx_ratio_original:.3f}")
    print("=" * 70)

    print("\nConclusion:")
    if approx_ratio_canonical > approx_ratio_original:
        print("✅ Hypothesis Confirmed: The flawed cost function misled the optimizer.")
        print("   It found a solution with a worse approximation ratio than the canonical one.")
    else:
        print("Hypothesis Not Confirmed: For this instance, the flawed cost function did not")
        print("lead to a measurably worse result. This can happen due to noise or optimization landscape.")

if __name__ == '__main__':
    # Add project root to path to allow imports
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.maxcut_implementations.canonical_maxcut import CanonicalMaxCut
    from src.maxcut_implementations.original_maxcut import OriginalMaxCut
    
    run_noisy_analysis() 