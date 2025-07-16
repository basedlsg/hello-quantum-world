"""Week 1: Quantum Learning Project - Foundation Building
Practical exploration of spatial vs non-spatial quantum circuits

Budget: ~$10 AWS credits
Time: 6-8 hours over 3-4 days
Goal: Build understanding through hands-on experimentation
"""

import json
from datetime import datetime
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from braket.circuits import Circuit
from braket.devices import LocalSimulator


class QuantumLearningLab:
    """Simple lab for learning quantum computing basics"""

    def __init__(self):
        self.device = LocalSimulator()
        self.experiments = []
        print("🧪 Quantum Learning Lab initialized!")
        print("Using local simulator (FREE for small circuits)")

    def create_spatial_circuit(self, n_qubits: int) -> Circuit:
        """Create a 'spatial' circuit with nearest-neighbor connections
        Think: particles that can only interact with their neighbors
        """
        circuit = Circuit()

        print(f"Building spatial circuit with {n_qubits} qubits...")

        # Step 1: Put all qubits in superposition
        for i in range(n_qubits):
            circuit.h(i)
        print("  ✓ Added superposition (H gates)")

        # Step 2: Connect neighbors only (spatial locality)
        for i in range(n_qubits - 1):
            circuit.cnot(i, i + 1)
        print(f"  ✓ Added {n_qubits-1} nearest-neighbor connections")

        return circuit

    def create_nonspatial_circuit(self, n_qubits: int) -> Circuit:
        """Create a 'non-spatial' circuit with all-to-all connections
        Think: particles that can interact with anyone, anywhere
        """
        circuit = Circuit()

        print(f"Building non-spatial circuit with {n_qubits} qubits...")

        # Step 1: Put all qubits in superposition
        for i in range(n_qubits):
            circuit.h(i)
        print("  ✓ Added superposition (H gates)")

        # Step 2: Connect everything to everything (non-spatial)
        connections = 0
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                circuit.cnot(i, j)
                connections += 1
        print(f"  ✓ Added {connections} all-to-all connections")

        return circuit

    def add_simple_noise(self, circuit: Circuit, error_rate: float) -> Circuit:
        """Add simple bit-flip errors to simulate noise
        This is how real quantum computers behave!
        """
        noisy_circuit = circuit.copy()

        # Add random X gates (bit flips) with given probability
        for i in range(circuit.qubit_count):
            if np.random.random() < error_rate:
                noisy_circuit.x(i)

        return noisy_circuit

    def run_and_measure(self, circuit: Circuit, shots: int = 1000) -> Dict:
        """Run a quantum circuit and measure the results
        Returns measurement statistics
        """
        # Add measurements to all qubits
        measured_circuit = circuit.copy()
        for i in range(circuit.qubit_count):
            measured_circuit.measure(i)

        # Run the circuit
        result = self.device.run(measured_circuit, shots=shots).result()

        # Get measurement counts
        counts = result.measurement_counts

        # Convert to probabilities
        probabilities = {}
        for state, count in counts.items():
            probabilities[state] = count / shots

        return {"counts": counts, "probabilities": probabilities, "total_shots": shots}

    def compare_circuits(self, n_qubits: int, noise_level: float = 0.0) -> Dict:
        """Compare spatial vs non-spatial circuits side by side
        This is our main learning experiment!
        """
        print(f"\n🔬 EXPERIMENT: Comparing {n_qubits}-qubit circuits")
        print(f"   Noise level: {noise_level:.3f}")
        print("-" * 50)

        # Create both circuit types
        spatial_circuit = self.create_spatial_circuit(n_qubits)
        nonspatial_circuit = self.create_nonspatial_circuit(n_qubits)

        # Add noise if requested
        if noise_level > 0:
            spatial_circuit = self.add_simple_noise(spatial_circuit, noise_level)
            nonspatial_circuit = self.add_simple_noise(nonspatial_circuit, noise_level)
            print(f"  ✓ Added noise (error rate: {noise_level:.3f})")

        # Run both circuits
        print("\n🏃 Running circuits...")
        spatial_results = self.run_and_measure(spatial_circuit)
        nonspatial_results = self.run_and_measure(nonspatial_circuit)

        # Analyze results
        analysis = self.analyze_results(spatial_results, nonspatial_results)

        # Store experiment
        experiment = {
            "timestamp": datetime.now().isoformat(),
            "n_qubits": n_qubits,
            "noise_level": noise_level,
            "spatial_results": spatial_results,
            "nonspatial_results": nonspatial_results,
            "analysis": analysis,
        }
        self.experiments.append(experiment)

        # Print summary
        self.print_experiment_summary(analysis)

        return experiment

    def analyze_results(self, spatial_results: Dict, nonspatial_results: Dict) -> Dict:
        """Analyze the differences between spatial and non-spatial results
        Look for patterns and interesting behaviors
        """
        # Calculate entropy (measure of randomness)
        spatial_entropy = self.calculate_entropy(spatial_results["probabilities"])
        nonspatial_entropy = self.calculate_entropy(nonspatial_results["probabilities"])

        # Count number of different outcomes
        spatial_outcomes = len(spatial_results["probabilities"])
        nonspatial_outcomes = len(nonspatial_results["probabilities"])

        # Find most probable state for each
        spatial_max_prob = max(spatial_results["probabilities"].values())
        nonspatial_max_prob = max(nonspatial_results["probabilities"].values())

        return {
            "spatial_entropy": spatial_entropy,
            "nonspatial_entropy": nonspatial_entropy,
            "entropy_ratio": (
                spatial_entropy / nonspatial_entropy
                if nonspatial_entropy > 0
                else float("inf")
            ),
            "spatial_outcomes": spatial_outcomes,
            "nonspatial_outcomes": nonspatial_outcomes,
            "spatial_max_prob": spatial_max_prob,
            "nonspatial_max_prob": nonspatial_max_prob,
            "max_prob_ratio": (
                spatial_max_prob / nonspatial_max_prob
                if nonspatial_max_prob > 0
                else float("inf")
            ),
        }

    def calculate_entropy(self, probabilities: Dict[str, float]) -> float:
        """Calculate Shannon entropy of measurement outcomes"""
        entropy = 0
        for prob in probabilities.values():
            if prob > 0:
                entropy -= prob * np.log2(prob)
        return entropy

    def print_experiment_summary(self, analysis: Dict):
        """Print a human-readable summary of the experiment"""
        print("\n📊 RESULTS SUMMARY:")
        print(f"  Spatial entropy:     {analysis['spatial_entropy']:.3f}")
        print(f"  Non-spatial entropy: {analysis['nonspatial_entropy']:.3f}")
        print(f"  Entropy ratio:       {analysis['entropy_ratio']:.3f}")
        print(f"  Spatial outcomes:    {analysis['spatial_outcomes']}")
        print(f"  Non-spatial outcomes: {analysis['nonspatial_outcomes']}")
        print(f"  Max prob ratio:      {analysis['max_prob_ratio']:.3f}")

        # Interpretation
        if analysis["entropy_ratio"] > 1.1:
            print("  💡 Spatial circuit shows MORE randomness")
        elif analysis["entropy_ratio"] < 0.9:
            print("  💡 Spatial circuit shows LESS randomness")
        else:
            print("  💡 Both circuits show similar randomness")

    def run_noise_sensitivity_study(self):
        """Study how spatial vs non-spatial circuits respond to noise
        This is our Week 1 main experiment!
        """
        print("\n🎯 NOISE SENSITIVITY STUDY")
        print("=" * 60)

        noise_levels = [0.0, 0.01, 0.02, 0.05, 0.1]
        n_qubits = 4

        results = {
            "noise_levels": noise_levels,
            "spatial_entropies": [],
            "nonspatial_entropies": [],
            "entropy_ratios": [],
        }

        for noise in noise_levels:
            print(f"\n🔍 Testing noise level: {noise:.3f}")
            experiment = self.compare_circuits(n_qubits, noise)

            results["spatial_entropies"].append(
                experiment["analysis"]["spatial_entropy"]
            )
            results["nonspatial_entropies"].append(
                experiment["analysis"]["nonspatial_entropy"]
            )
            results["entropy_ratios"].append(experiment["analysis"]["entropy_ratio"])

        # Plot results
        self.plot_noise_study(results)

        return results

    def plot_noise_study(self, results: Dict):
        """Create plots to visualize noise sensitivity"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Entropy vs Noise
        ax1.plot(
            results["noise_levels"],
            results["spatial_entropies"],
            "b-o",
            label="Spatial",
            linewidth=2,
        )
        ax1.plot(
            results["noise_levels"],
            results["nonspatial_entropies"],
            "r-s",
            label="Non-spatial",
            linewidth=2,
        )
        ax1.set_xlabel("Noise Level")
        ax1.set_ylabel("Entropy (bits)")
        ax1.set_title("Entropy vs Noise Level")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Entropy Ratio
        ax2.plot(
            results["noise_levels"],
            results["entropy_ratios"],
            "g-^",
            linewidth=2,
            markersize=8,
        )
        ax2.axhline(y=1.0, color="k", linestyle="--", alpha=0.5)
        ax2.set_xlabel("Noise Level")
        ax2.set_ylabel("Spatial/Non-spatial Entropy Ratio")
        ax2.set_title("Relative Noise Sensitivity")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("noise_sensitivity_study.png", dpi=150, bbox_inches="tight")
        plt.show()

        print("\n📈 Plots saved as 'noise_sensitivity_study.png'")

    def save_learning_log(self, filename: str = "quantum_learning_log.json"):
        """Save all experiments for future reference"""
        learning_log = {
            "project": "Quantum Learning Week 1",
            "total_experiments": len(self.experiments),
            "experiments": self.experiments,
            "saved_at": datetime.now().isoformat(),
        }

        with open(filename, "w") as f:
            json.dump(learning_log, f, indent=2, default=str)

        print(f"\n💾 Learning log saved to: {filename}")
        print(f"   Total experiments: {len(self.experiments)}")


def main():
    """Week 1 Learning Program - Get hands dirty with quantum circuits!"""
    print("🚀 WEEK 1: QUANTUM LEARNING ADVENTURE")
    print("=" * 60)
    print("Goal: Understand spatial vs non-spatial quantum effects")
    print("Method: Build, run, and compare quantum circuits")
    print("Budget: ~$10 AWS credits (mostly local simulator)")
    print("Time: 2-3 hours of focused experimentation")
    print("=" * 60)

    # Initialize our learning lab
    lab = QuantumLearningLab()

    # Day 1-2: Basic circuit exploration
    print("\n📅 DAY 1-2: BASIC CIRCUIT EXPLORATION")
    print("Building and understanding quantum circuits...")

    # Start simple: 3-qubit circuits
    print("\n🔰 Starting with 3-qubit circuits (simple to understand)")
    lab.compare_circuits(n_qubits=3, noise_level=0.0)

    # Try with a bit of noise
    print("\n🔰 Same circuits with a little noise")
    lab.compare_circuits(n_qubits=3, noise_level=0.02)

    # Day 3-4: Systematic comparison
    print("\n\n📅 DAY 3-4: SYSTEMATIC COMPARISON")
    print("Running noise sensitivity study...")

    # Main experiment: How do circuits respond to noise?
    noise_results = lab.run_noise_sensitivity_study()

    # Day 5-7: Size scaling (if time permits)
    print("\n\n📅 DAY 5-7: SIZE SCALING (BONUS)")
    print("How does behavior change with circuit size?")

    for n_qubits in [2, 4, 5]:
        print(f"\n🔍 Testing {n_qubits}-qubit circuits")
        lab.compare_circuits(n_qubits=n_qubits, noise_level=0.05)

    # Save everything we learned
    lab.save_learning_log()

    # Week 1 summary
    print("\n\n🎉 WEEK 1 COMPLETE!")
    print("=" * 40)
    print("✅ Built spatial and non-spatial quantum circuits")
    print("✅ Learned to measure and analyze quantum states")
    print("✅ Studied how noise affects different circuit types")
    print("✅ Created visualization tools for quantum behavior")
    print("✅ Documented all experiments and insights")

    print("\n📚 KEY LEARNINGS:")
    print("• Quantum circuits are just sequences of gates")
    print("• Spatial vs non-spatial refers to connection patterns")
    print("• Noise affects quantum states in measurable ways")
    print("• Entropy is a useful measure of quantum randomness")
    print("• Local simulator is perfect for learning!")

    print("\n🚀 READY FOR WEEK 2:")
    print("• More systematic experiments")
    print("• Better analysis tools")
    print("• Deeper understanding of quantum effects")

    print("\n💰 Estimated AWS cost: <$5 (mostly free local simulator)")
    print("💡 Next: Week 2 - Systematic Investigation")


if __name__ == "__main__":
    main()
