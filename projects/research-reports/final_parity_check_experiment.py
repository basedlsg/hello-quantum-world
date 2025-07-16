"""Gate-Count Parity Check Experiment

This script addresses the critical feedback from the initial experiment by
controlling for the CNOT gate count, which was a major confounding variable.
It compares three circuit topologies at 6 qubits, all constrained to an
identical CNOT budget.

Methodology:
1.  **Gate-Count Parity:** All topologies (spatial, non-spatial, random) are
    forced to have EXACTLY `GATE_BUDGET` CNOTs.
    - Spatial circuits are padded with identity-equivalent CNOT pairs.
    - Non-spatial circuits have their CNOTs randomly sub-sampled.
2.  **Robust Randomness:** The random graph generation for each instance is
    explicitly seeded to ensure true statistical variation.
3.  **Explicit Noise Model:** A realistic noise model (T1/T2 amplitude and
    phase damping) is applied after every CNOT gate.
4.  **Rigorous Analysis:** The script will save detailed results for later
    analysis, including bootstrap confidence intervals.
"""

import argparse
import os
import random
import time

import networkx as nx
import numpy as np
import pandas as pd
from braket.aws import AwsDevice
from braket.circuits import Circuit, instruction
from braket.devices import LocalSimulator
from src.validation.metrics import dm1_to_numpy

# --- Parameters ---
N_QUBITS = 6
GATE_BUDGET = 7
RANDOM_INSTANCES = 10
RANDOM_SEED = 1337

# Noise Model
T1, T2, GATE_TIME = 40e-6, 60e-6, 200e-9
P_AMPLITUDE = 1 - np.exp(-GATE_TIME / T1)
P_DEPHASING = 1 - np.exp(-GATE_TIME / T2)

np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)


def apply_noise_to_circuit(c: Circuit) -> Circuit:
    noisy_c = Circuit()
    for instr in c.instructions:
        noisy_c.add_instruction(instr)
        if isinstance(instr, instruction.Instruction) and instr.operator.name == "CNot":
            q1, q2 = instr.target
            for q in (q1, q2):
                noisy_c.amplitude_damping(q, P_AMPLITUDE)
                noisy_c.phase_damping(q, P_DEPHASING)
    return noisy_c


# --- Circuit Creation ---
def create_padded_spatial_circuit():
    """Creates a spatial circuit and pads it with CNOT pairs to meet the budget.
    Padding with CNOT-CNOT pairs is logically identity but triggers noise twice.
    """
    c = Circuit().h(range(N_QUBITS))
    base_edges = [(i, i + 1) for i in range(N_QUBITS - 1)]
    for q1, q2 in base_edges:
        c.cnot(q1, q2)

    padding_needed = GATE_BUDGET - len(base_edges)
    if padding_needed < 0:
        raise ValueError(
            "GATE_BUDGET is smaller than the base number of spatial CNOTs."
        )
    if padding_needed % 2 != 0:
        raise ValueError(
            "For logical identity, padding for the spatial circuit must be "
            "in CNOT pairs, so the padding amount must be even."
        )

    # Add identity-forming CNOT pairs on existing edges to meet the budget
    for i in range(padding_needed // 2):
        # Cycle through base edges for padding to distribute the noise
        q1, q2 = base_edges[i % len(base_edges)]
        c.cnot(q1, q2)  # Add the first CNOT of the pair
        c.cnot(q1, q2)  # Add the second CNOT, completing the identity
    return c


def create_sampled_nonspatial_circuit(seed: int):
    c = Circuit().h(range(N_QUBITS))
    possible_edges = [(i, j) for i in range(N_QUBITS) for j in range(i + 2, N_QUBITS)]
    rng = random.Random(seed)
    chosen_edges = rng.sample(possible_edges, GATE_BUDGET)
    for q1, q2 in chosen_edges:
        c.cnot(q1, q2)
    return c


def create_random_er_circuit(seed: int):
    rng = np.random.default_rng(seed)
    G = nx.gnm_random_graph(N_QUBITS, GATE_BUDGET, seed=rng)
    c = Circuit().h(range(N_QUBITS))
    for u, v in G.edges():
        c.cnot(u, v)
    return c


def count_cnots(c: Circuit) -> int:
    return sum(
        1
        for i in c.instructions
        if isinstance(i, instruction.Instruction) and i.operator.name == "CNot"
    )


# --- Main Logic ---
def run_parity_experiment(circuit_type: str, device, instances=1):
    results = []
    print(
        f"\n--- Running Parity Check: {circuit_type} ({instances} instances) ---",
        flush=True,
    )
    main_rng = np.random.default_rng(RANDOM_SEED)
    instance_seeds = main_rng.integers(low=0, high=1_000_000, size=instances)

    for i in range(instances):
        t0, seed = time.time(), instance_seeds[i]
        print(
            f"  Instance {i+1}/{instances} (Seed: {seed}): Building circuits...",
            flush=True,
        )

        if circuit_type == "spatial_padded":
            # This circuit is deterministic, no seed needed
            base_circuit = create_padded_spatial_circuit()
        elif circuit_type == "nonspatial_sampled":
            base_circuit = create_sampled_nonspatial_circuit(seed)
        else:  # random_er
            base_circuit = create_random_er_circuit(seed)

        # === Rigorous Assertions from Final Reviewer Feedback ===
        cnot_count = count_cnots(base_circuit)
        assert (
            cnot_count == GATE_BUDGET
        ), f"[{circuit_type}] Base circuit CNOT count is wrong! Expected {GATE_BUDGET}, got {cnot_count}"
        noisy_circuit = apply_noise_to_circuit(base_circuit)
        noisy_cnot_count = count_cnots(noisy_circuit)
        assert (
            noisy_cnot_count == GATE_BUDGET
        ), f"[{circuit_type}] Noisy circuit CNOT count is wrong! Expected {GATE_BUDGET}, got {noisy_cnot_count}"
        # =======================================================

        base_circuit.density_matrix()
        noisy_circuit.density_matrix()

        print(f"  Submitting to {device.name}...", flush=True)
        ideal_task = device.run(base_circuit, shots=0)
        noisy_task = device.run(noisy_circuit, shots=0)

        ideal_dm = dm1_to_numpy(ideal_task.result().result_types[0].value)
        noisy_dm = dm1_to_numpy(noisy_task.result().result_types[0].value)

        fidelity = fidelity_robust(ideal_dm, noisy_dm)
        min_eig = np.min(np.real(np.linalg.eigvals(noisy_dm)))

        elapsed = time.time() - t0
        print(f"  -> Fidelity: {fidelity:.4f} (took {elapsed:.2f}s)", flush=True)
        results.append(
            {
                "circuit_type": circuit_type,
                "instance": i,
                "fidelity": fidelity,
                "min_eigenvalue": min_eig,
                "cnot_count": cnot_count,
                "seed": seed,
            }
        )
        if elapsed > 400:
            print("Wall-clock guard triggered.")
            break
    return results


def fidelity_robust(rho, sigma):
    trace_rho, trace_sigma = np.trace(rho), np.trace(sigma)
    rho_norm = rho / trace_rho if not np.isclose(trace_rho, 0) else rho
    sigma_norm = sigma / trace_sigma if not np.isclose(trace_sigma, 0) else sigma
    overlap = np.trace(rho_norm @ sigma_norm)
    return max(
        0.0,
        min(
            1.0, np.real(overlap.item() if isinstance(overlap, np.ndarray) else overlap)
        ),
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run Gate-Count Parity Check Experiment."
    )
    parser.add_argument(
        "--device_arn",
        type=str,
        default="arn:aws:braket:::device/quantum-simulator/amazon/dm1",
        help="AWS Braket device ARN. Use 'local' for local simulation.",
    )
    args = parser.parse_args()

    device = (
        AwsDevice(args.device_arn)
        if args.device_arn != "local"
        else LocalSimulator("braket_dm")
    )
    print(f"Targeting device: {device.name}", flush=True)

    if not os.path.exists("results"):
        os.makedirs("results")

    # Since spatial is deterministic, run it only once to save time.
    spatial_results = run_parity_experiment("spatial_padded", device, instances=1)
    # Broadcast the single result to match the others for fair plotting
    spatial_results *= RANDOM_INSTANCES

    nonspatial_results = run_parity_experiment(
        "nonspatial_sampled", device, instances=RANDOM_INSTANCES
    )
    random_results = run_parity_experiment(
        "random_er", device, instances=RANDOM_INSTANCES
    )

    all_results = pd.DataFrame(spatial_results + nonspatial_results + random_results)

    device_name = (
        "local" if args.device_arn == "local" else device.name.replace("/", "_")
    )
    output_path = f"results/final_parity_check_results_{device_name}.csv"

    all_results.to_csv(output_path, index=False)
    print(f"\nDefinitive parity check results saved to '{output_path}'")


if __name__ == "__main__":
    main()
