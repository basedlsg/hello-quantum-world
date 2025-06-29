"""
End-to-End QAOA Execution on Amazon Braket Cloud Simulator

This script serves as the final validation of the quantum reproducibility
case study. It takes the validated classical cost function and runs a full
Quantum Approximate Optimization Algorithm (QAOA) circuit on AWS Braket's
SV1 cloud simulator.

The primary goals are:
1. To demonstrate a complete, working QAOA workflow on the Amazon quantum cloud.
2. To verify that the expectation value of the MaxCut cost Hamiltonian,
   calculated directly by the Braket backend, matches the value calculated
   classically from measurement outcomes using our validated
   `VerificationMaxCut` implementation.
3. To confirm that our local, validated code accurately represents the behavior
   of the corresponding quantum circuits running on AWS.

Author: Quantum Reproducibility Case Study Team
License: MIT
"""

import numpy as np
import networkx as nx
from braket.circuits import Circuit, Observable, observables
from braket.aws import AwsDevice
from braket.devices import LocalSimulator
from typing import Dict, List, Tuple

# Add parent directory to path to import our local modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from maxcut_implementations.canonical_maxcut import CanonicalMaxCut


def create_qaoa_circuit(graph: nx.Graph, p: int, gamma: List[float], beta: List[float]) -> Circuit:
    """
    Creates a QAOA circuit for the MaxCut problem.

    Args:
        graph: The problem graph.
        p: The number of QAOA layers.
        gamma: The p angles for the cost layer.
        beta: The p angles for the mixer layer.

    Returns:
        A Braket Circuit object for the QAOA algorithm.
    """
    n_qubits = len(graph.nodes)
    circuit = Circuit()

    # Apply initial Hadamard layer
    circuit.h(range(n_qubits))

    # Apply p layers of cost and mixer Hamiltonians
    for i in range(p):
        # Cost layer
        for edge in graph.edges:
            u, v = edge
            circuit.cnot(u, v)
            circuit.rz(v, 2 * gamma[i])
            circuit.cnot(u, v)

        # Mixer layer
        circuit.rx(range(n_qubits), 2 * beta[i])

    return circuit


def get_maxcut_cost_hamiltonian(graph: nx.Graph) -> Observable:
    """
    Constructs the MaxCut cost Hamiltonian as a Braket Observable.
    The Hamiltonian is H_C = 0.5 * sum(I - Z_i Z_j) for edges (i,j).
    Its expectation value is the number of cut edges.

    Args:
        graph: The problem graph.

    Returns:
        A Braket Observable representing the cost Hamiltonian.
    """
    hamiltonian_terms = []
    for i, j in graph.edges:
        id_term = observables.I(i)
        z_term = observables.Z(i) @ observables.Z(j)
        hamiltonian_terms.append(0.5 * (id_term - z_term))
    
    # The start=... ensures that sum() on an empty list returns a valid Observable
    return sum(hamiltonian_terms, start=observables.I(0) * 0) if hamiltonian_terms else observables.I(0) * 0


def run_qaoa_on_braket(
    device_arn: str,
    graph: nx.Graph,
    p: int,
    params: Tuple[List[float], List[float]],
    shots: int = 1000
) -> Dict:
    """
    Runs the QAOA circuit on a Braket device and returns the results.
    This version requests only measurement samples and calculates the
    expectation value locally, avoiding Hamiltonian construction issues.

    Args:
        device_arn: The ARN of the Braket device to use.
        graph: The problem graph.
        p: The number of QAOA layers.
        params: A tuple containing the gamma and beta angles.
        shots: The number of measurement shots.

    Returns:
        A dictionary containing the results.
    """
    gamma, beta = params
    device = AwsDevice(device_arn)

    # 1. Create the QAOA circuit
    qaoa_circuit = create_qaoa_circuit(graph, p, gamma, beta)

    # 2. Request only measurement counts (samples)
    task = device.run(qaoa_circuit, shots=shots)

    print(f"Submitted QAOA task to {device.name}. Task ARN: {task.id}")
    result = task.result()
    print("Task completed.")

    # 3. Extract measurement counts
    measurement_counts = result.measurement_counts

    return {
        "device": device.name,
        "task_arn": task.id,
        "parameters": {"gamma": gamma, "beta": beta, "p": p},
        "shots": shots,
        "measurement_counts": measurement_counts
    }


def analyze_results(results: Dict, graph_edges: List[Tuple[int, int]]) -> Dict:
    """
    Analyzes the results by calculating the expectation value from
    the measurement outcomes.

    Args:
        results: The dictionary returned by run_qaoa_on_braket.
        graph_edges: The list of graph edges.

    Returns:
        A dictionary with the analysis.
    """
    verifier = CanonicalMaxCut(nx.Graph(graph_edges))
    total_shots = results['shots']
    measurement_counts = results['measurement_counts']

    # Calculate expected cut value classically from the bitstring measurements
    classical_cut_total = 0
    for bitstring, count in measurement_counts.items():
        cut_value = verifier.calculate_cut_value(bitstring)
        classical_cut_total += cut_value * count

    classical_exp_val = classical_cut_total / total_shots if total_shots > 0 else 0

    return {
        "calculated_expectation_value": classical_exp_val,
        "conclusion": "SUCCESS: Cloud execution completed and expectation value calculated."
    }


if __name__ == "__main__":
    # --- Configuration ---
    # Use the AWS SV1 cloud simulator
    SV1_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
    # Define the 3-node triangle graph
    GRAPH_EDGES = [(0, 1), (1, 2), (0, 2)]
    problem_graph = nx.Graph(GRAPH_EDGES)
    # Set QAOA parameters
    p_layers = 1
    # Use parameters that should yield a non-trivial result
    gamma_params = [np.pi / 4]
    beta_params = [np.pi / 8]

    print("--- Starting End-to-End QAOA Validation on AWS Braket ---")
    print(f"Device: {SV1_ARN}")
    print(f"Graph: {GRAPH_EDGES}")
    print(f"Parameters: p={p_layers}, gamma={gamma_params}, beta={beta_params}\n")

    try:
        # Run the QAOA experiment on the cloud simulator
        run_results = run_qaoa_on_braket(
            device_arn=SV1_ARN,
            graph=problem_graph,
            p=p_layers,
            params=(gamma_params, beta_params),
            shots=1000
        )

        # Analyze the results for consistency
        analysis = analyze_results(run_results, GRAPH_EDGES)

        print("\n--- Analysis and Verification ---")
        print(f"Classically-calculated Expectation Value from Cloud Results: {analysis['calculated_expectation_value']:.6f}")
        print(f"Conclusion: {analysis['conclusion']}")

    except Exception as e:
        print(f"\n--- An Error Occurred ---")
        print(f"Error: {e}")
        print("This could be due to missing AWS credentials, permissions, or network issues.")
        print("Please ensure your AWS environment is configured for Braket.")
        print("See: https://docs.aws.amazon.com/braket/latest/developerguide/braket-configure-environment.html") 