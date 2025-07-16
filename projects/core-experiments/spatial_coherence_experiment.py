"""Spatial Quantum Coherence Experiment - Revised Implementation
Addressing Scientific Committee Feedback

Focus: Compare decoherence in spatially-correlated vs. non-spatial qubit systems
Method: Use AWS Braket to implement well-defined quantum circuits
"""

from typing import List

import numpy as np
from braket.circuits import Circuit
from braket.devices import LocalSimulator


class SpatialCoherenceExperiment:
    """Revised experiment focusing on achievable measurements with current hardware.
    Tests whether spatially-arranged qubit interactions show different decoherence
    properties compared to non-spatial entanglement.
    """

    def __init__(self):
        self.device = LocalSimulator()
        self.results = {}

    def create_spatial_circuit(self, n_qubits: int) -> Circuit:
        """Create a circuit representing 'spatial' quantum correlations.
        Uses nearest-neighbor interactions to simulate spatial locality.

        Mathematical Definition: Spatial system has interactions only between
        adjacent qubits, representing local spatial correlations.
        """
        circuit = Circuit()

        # Initialize all qubits in superposition
        for i in range(n_qubits):
            circuit.h(i)

        # Create spatial correlations through nearest-neighbor gates
        for i in range(n_qubits - 1):
            circuit.cnot(i, i + 1)  # Local spatial interaction

        return circuit

    def create_nonspatial_circuit(self, n_qubits: int) -> Circuit:
        """Create a circuit representing 'non-spatial' quantum correlations.
        Uses long-range interactions between distant qubits.

        Mathematical Definition: Non-spatial system has interactions between
        all qubit pairs, representing non-local correlations.
        """
        circuit = Circuit()

        # Initialize all qubits in superposition
        for i in range(n_qubits):
            circuit.h(i)

        # Create non-spatial correlations through long-range gates
        for i in range(n_qubits):
            for j in range(i + 2, n_qubits):  # Skip nearest neighbors
                circuit.cnot(i, j)  # Non-local interaction

        return circuit

    def add_decoherence(self, circuit: Circuit, noise_prob: float) -> Circuit:
        """Add controlled decoherence to test robustness.
        Uses depolarizing noise as a simple environmental model.
        """
        # Note: This is a simplified noise model for proof-of-concept
        # Real implementation would use Braket's noise models

        for i in range(circuit.qubit_count):
            if np.random.random() < noise_prob:
                circuit.x(i)  # Bit flip error
            if np.random.random() < noise_prob:
                circuit.z(i)  # Phase flip error

        return circuit

    def measure_fidelity(self, ideal_circuit: Circuit, noisy_circuit: Circuit) -> float:
        """Measure fidelity between ideal and noisy quantum states.
        This is our primary metric for coherence preservation.
        """
        # Simplified fidelity calculation for proof-of-concept
        # Real implementation would use state vector overlap

        # Run both circuits
        ideal_result = self.device.run(ideal_circuit, shots=1000).result()
        noisy_result = self.device.run(noisy_circuit, shots=1000).result()

        # Calculate overlap in measurement statistics
        ideal_counts = ideal_result.measurement_counts
        noisy_counts = noisy_result.measurement_counts

        # Simple fidelity metric based on measurement overlap
        overlap = 0
        total_shots = 1000

        for state in ideal_counts:
            ideal_prob = ideal_counts.get(state, 0) / total_shots
            noisy_prob = noisy_counts.get(state, 0) / total_shots
            overlap += np.sqrt(ideal_prob * noisy_prob)

        return overlap

    def run_coherence_comparison(
        self, n_qubits: int, noise_levels: List[float]
    ) -> dict:
        """Compare coherence preservation between spatial and non-spatial systems.

        Returns
        -------
            Dictionary with fidelity measurements for both system types

        """
        results = {
            "spatial_fidelity": [],
            "nonspatial_fidelity": [],
            "noise_levels": noise_levels,
        }

        print(f"Testing {n_qubits}-qubit systems...")

        for noise_prob in noise_levels:
            print(f"  Noise level: {noise_prob:.3f}")

            # Test spatial system
            spatial_circuit = self.create_spatial_circuit(n_qubits)
            spatial_noisy = self.add_decoherence(spatial_circuit.copy(), noise_prob)
            spatial_fidelity = self.measure_fidelity(spatial_circuit, spatial_noisy)

            # Test non-spatial system
            nonspatial_circuit = self.create_nonspatial_circuit(n_qubits)
            nonspatial_noisy = self.add_decoherence(
                nonspatial_circuit.copy(), noise_prob
            )
            nonspatial_fidelity = self.measure_fidelity(
                nonspatial_circuit, nonspatial_noisy
            )

            results["spatial_fidelity"].append(spatial_fidelity)
            results["nonspatial_fidelity"].append(nonspatial_fidelity)

        return results

    def run_scaling_study(self, qubit_counts: List[int], noise_level: float) -> dict:
        """Study how coherence preservation scales with system size.

        This addresses the committee's concern about scale-dependent effects.
        """
        results = {
            "qubit_counts": qubit_counts,
            "spatial_scaling": [],
            "nonspatial_scaling": [],
        }

        print(f"Scaling study at noise level: {noise_level:.3f}")

        for n_qubits in qubit_counts:
            if n_qubits > 10:  # Practical limit for local simulation
                print(f"  Skipping {n_qubits} qubits (too large for local simulation)")
                continue

            print(f"  Testing {n_qubits} qubits...")

            # Test both system types
            spatial_circuit = self.create_spatial_circuit(n_qubits)
            spatial_noisy = self.add_decoherence(spatial_circuit.copy(), noise_level)
            spatial_fidelity = self.measure_fidelity(spatial_circuit, spatial_noisy)

            nonspatial_circuit = self.create_nonspatial_circuit(n_qubits)
            nonspatial_noisy = self.add_decoherence(
                nonspatial_circuit.copy(), noise_level
            )
            nonspatial_fidelity = self.measure_fidelity(
                nonspatial_circuit, nonspatial_noisy
            )

            results["spatial_scaling"].append(spatial_fidelity)
            results["nonspatial_scaling"].append(nonspatial_fidelity)

        return results

    def statistical_analysis(self, results: dict, n_trials: int = 10) -> dict:
        """Perform statistical analysis with multiple trials.

        Addresses committee concern about statistical rigor.
        """
        print(f"Running statistical analysis with {n_trials} trials...")

        # Collect multiple measurements
        spatial_trials = []
        nonspatial_trials = []

        for trial in range(n_trials):
            print(f"  Trial {trial + 1}/{n_trials}")
            trial_results = self.run_coherence_comparison(
                n_qubits=4, noise_levels=[0.01, 0.05, 0.1, 0.2]
            )
            spatial_trials.append(trial_results["spatial_fidelity"])
            nonspatial_trials.append(trial_results["nonspatial_fidelity"])

        # Calculate statistics
        spatial_mean = np.mean(spatial_trials, axis=0)
        spatial_std = np.std(spatial_trials, axis=0)
        nonspatial_mean = np.mean(nonspatial_trials, axis=0)
        nonspatial_std = np.std(nonspatial_trials, axis=0)

        return {
            "spatial_mean": spatial_mean,
            "spatial_std": spatial_std,
            "nonspatial_mean": nonspatial_mean,
            "nonspatial_std": nonspatial_std,
            "noise_levels": [0.01, 0.05, 0.1, 0.2],
        }


def main():
    """Main experimental protocol addressing committee feedback."""
    print("=== Spatial Quantum Coherence Experiment ===")
    print("Revised implementation addressing scientific committee feedback\n")

    experiment = SpatialCoherenceExperiment()

    # Phase 1: Basic comparison (addressing theoretical foundation concern)
    print("Phase 1: Basic Coherence Comparison")
    print("-" * 40)

    noise_levels = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2]
    basic_results = experiment.run_coherence_comparison(
        n_qubits=4, noise_levels=noise_levels
    )

    print("\nResults:")
    for i, noise in enumerate(noise_levels):
        spatial_fid = basic_results["spatial_fidelity"][i]
        nonspatial_fid = basic_results["nonspatial_fidelity"][i]
        difference = spatial_fid - nonspatial_fid

        print(
            f"Noise {noise:.3f}: Spatial={spatial_fid:.3f}, "
            f"Non-spatial={nonspatial_fid:.3f}, Diff={difference:+.3f}"
        )

    # Phase 2: Scaling study (addressing scale limitations concern)
    print("\n\nPhase 2: Scaling Study")
    print("-" * 40)

    qubit_counts = [2, 3, 4, 5, 6]  # Limited by local simulation
    scaling_results = experiment.run_scaling_study(qubit_counts, noise_level=0.05)

    print("\nScaling Results:")
    for i, n_qubits in enumerate(qubit_counts):
        if i < len(scaling_results["spatial_scaling"]):
            spatial_fid = scaling_results["spatial_scaling"][i]
            nonspatial_fid = scaling_results["nonspatial_scaling"][i]
            print(
                f"{n_qubits} qubits: Spatial={spatial_fid:.3f}, "
                f"Non-spatial={nonspatial_fid:.3f}"
            )

    # Phase 3: Statistical analysis (addressing reproducibility concern)
    print("\n\nPhase 3: Statistical Analysis")
    print("-" * 40)

    stats_results = experiment.statistical_analysis({}, n_trials=5)  # Reduced for demo

    print("\nStatistical Results (Mean ± Std):")
    for i, noise in enumerate(stats_results["noise_levels"]):
        spatial_mean = stats_results["spatial_mean"][i]
        spatial_std = stats_results["spatial_std"][i]
        nonspatial_mean = stats_results["nonspatial_mean"][i]
        nonspatial_std = stats_results["nonspatial_std"][i]

        print(f"Noise {noise:.3f}:")
        print(f"  Spatial: {spatial_mean:.3f} ± {spatial_std:.3f}")
        print(f"  Non-spatial: {nonspatial_mean:.3f} ± {nonspatial_std:.3f}")

    print("\n=== Experiment Complete ===")
    print("\nKey Findings:")
    print("• Explicit quantum circuits provided for both system types")
    print("• Mathematical definitions given for spatial vs. non-spatial")
    print("• Statistical analysis included with error bars")
    print("• Experiments limited to achievable hardware scales")
    print("• Results focus on measurable quantities (fidelity)")

    print("\nLimitations Acknowledged:")
    print("• Simplified noise models used")
    print("• Limited qubit counts due to classical simulation")
    print("• 'Spatial' effects are circuit-topology based, not true spatial")
    print("• Results may not generalize to larger scales")


if __name__ == "__main__":
    main()
