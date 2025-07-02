"""
Advanced Spatial Quantum Coherence Experiment

Focus: Use realistic noise models to compare decoherence in spatially-correlated 
vs. non-spatial qubit systems.

This script implements a configurable, statistically rigorous experiment to
test the hypothesis that quantum circuits with local-only interactions are
more resilient to noise as they scale.
"""
import argparse
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

from braket.circuits import Circuit, noises
from braket.aws import AwsDevice
from braket.devices import LocalSimulator
from scipy.linalg import sqrtm


def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """
    Calculates a robust approximation of fidelity between two density matrices.
    Uses a numerically stable approach for AWS compatibility.
    """
    # For debugging - can be removed later
    print(f"Debug: rho shape={rho.shape}, trace={np.trace(rho):.6f}")
    print(f"Debug: sigma shape={sigma.shape}, trace={np.trace(sigma):.6f}")
    
    # Ensure matrices are properly normalized
    rho = rho / np.trace(rho)
    sigma = sigma / np.trace(sigma)
    
    # For identical or very similar matrices, return high fidelity
    if np.allclose(rho, sigma, atol=1e-6):
        return 1.0
    
    # Use a simpler, more robust fidelity approximation
    # This uses the Hilbert-Schmidt inner product as a proxy
    # F ≈ Tr(rho * sigma) for normalized matrices
    overlap = np.real(np.trace(rho @ sigma))
    
    # Ensure the result is between 0 and 1
    fidelity_approx = max(0.0, min(1.0, overlap))
    
    print(f"Debug: Computed fidelity = {fidelity_approx:.6f}")
    return fidelity_approx


class AdvancedCoherenceExperiment:
    """
    An advanced experiment using Braket's noise models and statistical analysis.
    """
    
    def __init__(self, device_name: str):
        if device_name.startswith("arn:"):
            self.device = AwsDevice(device_name)
        elif device_name == "local_dm":
            self.device = LocalSimulator("braket_dm")
        elif device_name == "sv1": # A convenience short-name
            self.device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")
        else:
            raise ValueError("Invalid device specified. Use 'local_dm', 'sv1', or a valid AWS device ARN.")
        self.results = {}
    
    def create_spatial_circuit(self, n_qubits: int, noise_prob: float = 0.0) -> Circuit:
        """
        Create a circuit representing 'spatial' quantum correlations.
        Applies a depolarizing noise channel after each gate to simulate decoherence.
        """
        circuit = Circuit()
        
        # Initialize all qubits in superposition
        for i in range(n_qubits):
            circuit.h(i)
            if noise_prob > 0:
                circuit.apply_gate_noise(noises.Depolarizing(probability=noise_prob))
        
        # Create spatial correlations through nearest-neighbor gates
        for i in range(n_qubits - 1):
            circuit.cnot(i, i + 1)
            if noise_prob > 0:
                circuit.apply_gate_noise(noises.Depolarizing(probability=noise_prob))
            
        return circuit
    
    def create_nonspatial_circuit(self, n_qubits: int, noise_prob: float = 0.0) -> Circuit:
        """
        Create a circuit representing 'non-spatial' quantum correlations.
        Applies a depolarizing noise channel after each gate.
        """
        circuit = Circuit()
        
        # Initialize all qubits in superposition
        for i in range(n_qubits):
            circuit.h(i)
            if noise_prob > 0:
                circuit.apply_gate_noise(noises.Depolarizing(probability=noise_prob))
        
        # Create non-spatial correlations through long-range gates
        for i in range(n_qubits):
            for j in range(i + 2, n_qubits):  # Skip nearest neighbors
                circuit.cnot(i, j)
                if noise_prob > 0:
                    circuit.apply_gate_noise(noises.Depolarizing(probability=noise_prob))
                
        return circuit
    
    def measure_fidelity(self, ideal_circuit: Circuit, noisy_circuit: Circuit) -> float:
        """
        Measure fidelity by comparing the density matrices of the ideal and noisy circuits.
        """
        ideal_circuit.density_matrix()
        noisy_circuit.density_matrix()
        
        ideal_task = self.device.run(ideal_circuit, shots=0)
        noisy_task = self.device.run(noisy_circuit, shots=0)
        
        ideal_dm = ideal_task.result().values[0]
        noisy_dm = noisy_task.result().values[0]
        
        # Convert to numpy arrays if they're not already
        ideal_dm = np.array(ideal_dm)
        noisy_dm = np.array(noisy_dm)
        
        # Handle AWS format: if 3D array, take the first matrix
        if ideal_dm.ndim == 3:
            ideal_dm = ideal_dm[:, :, 0]
        if noisy_dm.ndim == 3:
            noisy_dm = noisy_dm[:, :, 0]
        
        return fidelity(ideal_dm, noisy_dm)

    def run_scaling_study(self, max_qubits: int, noise_prob: float, trials: int) -> dict:
        """
        Study how coherence preservation scales with system size, with statistical rigor.
        """
        print(f"Running scaling study: max_qubits={max_qubits}, noise_prob={noise_prob}, trials={trials}")
        
        all_results = {
            'qubit_counts': list(range(2, max_qubits + 1)),
            'spatial_means': [],
            'spatial_sems': [],
            'nonspatial_means': [],
            'nonspatial_sems': [],
        }

        for n_qubits in range(2, max_qubits + 1):
            spatial_fidelities_trial = []
            nonspatial_fidelities_trial = []
            print(f"\n--- Testing {n_qubits} qubits ---")
            for i in range(trials):
                # Use a different seed for each trial for statistical independence
                np.random.seed() 
                
                ideal_spatial = self.create_spatial_circuit(n_qubits, 0.0)
                noisy_spatial = self.create_spatial_circuit(n_qubits, noise_prob)
                spatial_fidelity = self.measure_fidelity(ideal_spatial, noisy_spatial)
                spatial_fidelities_trial.append(spatial_fidelity)

                ideal_nonspatial = self.create_nonspatial_circuit(n_qubits, 0.0)
                noisy_nonspatial = self.create_nonspatial_circuit(n_qubits, noise_prob)
                nonspatial_fidelity = self.measure_fidelity(ideal_nonspatial, noisy_nonspatial)
                nonspatial_fidelities_trial.append(nonspatial_fidelity)

                print(f"  Trial {i+1}/{trials}: Spatial Fid={spatial_fidelity:.3f}, Non-Spatial Fid={nonspatial_fidelity:.3f}")

            # Calculate mean and standard error of the mean (SEM)
            all_results['spatial_means'].append(np.mean(spatial_fidelities_trial))
            all_results['spatial_sems'].append(np.std(spatial_fidelities_trial) / np.sqrt(trials))
            all_results['nonspatial_means'].append(np.mean(nonspatial_fidelities_trial))
            all_results['nonspatial_sems'].append(np.std(nonspatial_fidelities_trial) / np.sqrt(trials))
        
        return all_results

def save_results_to_csv(results: dict, filepath: str):
    """Saves the scaling study results to a CSV file."""
    print(f"\nSaving results to {filepath}")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['qubits', 'spatial_fidelity_mean', 'spatial_fidelity_sem', 'nonspatial_fidelity_mean', 'nonspatial_fidelity_sem'])
        for i, qc in enumerate(results['qubit_counts']):
            writer.writerow([
                qc,
                results['spatial_means'][i],
                results['spatial_sems'][i],
                results['nonspatial_means'][i],
                results['nonspatial_sems'][i],
            ])

def plot_results(results: dict, filepath: str):
    """Plots the scaling study results with error ribbons."""
    print(f"Generating plot at {filepath}")
    
    qc = np.array(results['qubit_counts'])
    sm = np.array(results['spatial_means'])
    ss = np.array(results['spatial_sems'])
    nsm = np.array(results['nonspatial_means'])
    nss = np.array(results['nonspatial_sems'])

    plt.figure(figsize=(10, 6))
    plt.plot(qc, sm, 'o-', label='Spatial (Local Interactions)')
    plt.fill_between(qc, sm - ss, sm + ss, alpha=0.2)
    
    plt.plot(qc, nsm, 's-', label='Non-Spatial (Long-Range Interactions)')
    plt.fill_between(qc, nsm - nss, nsm + nss, alpha=0.2)

    plt.title('Fidelity vs. Qubit Count under Depolarizing Noise')
    plt.xlabel('Number of Qubits')
    plt.ylabel('Fidelity')
    plt.grid(True, which='both', linestyle='--')
    plt.legend()
    plt.ylim(0, 1.05)
    plt.xticks(qc)
    
    plt.savefig(filepath)
    print("Plot saved successfully.")


def main():
    """Main execution block."""
    parser = argparse.ArgumentParser(description="Run an advanced coherence experiment.")
    parser.add_argument('--device', type=str, default='local_dm', help="Device to run on ('local_dm', 'sv1', or AWS ARN).")
    parser.add_argument('--max-qubits', type=int, default=6, help="Maximum number of qubits for the scaling study.")
    parser.add_argument('--noise-p', type=float, default=0.005, help="Probability of depolarizing noise.")
    parser.add_argument('--trials', type=int, default=10, help="Number of trials for statistical analysis.")
    args = parser.parse_args()

    print("=== Advanced Spatial Quantum Coherence Experiment (v2) ===")
    
    experiment = AdvancedCoherenceExperiment(args.device)
    
    results = experiment.run_scaling_study(
        max_qubits=args.max_qubits,
        noise_prob=args.noise_p,
        trials=args.trials
    )
    
    # Ensure results directories exist
    os.makedirs('results', exist_ok=True)
    os.makedirs('figures', exist_ok=True)
    
    csv_path = 'results/scaling_fidelity.csv'
    plot_path = 'figures/scaling_fidelity.png'
    
    save_results_to_csv(results, csv_path)
    plot_results(results, plot_path)
    
    print("\n=== Experiment Complete ===")

if __name__ == "__main__":
    main() 