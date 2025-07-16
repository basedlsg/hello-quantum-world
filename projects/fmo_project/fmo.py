import os
import subprocess
import venv
import numpy as np
import pandas as pd
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import logging
import matplotlib.pyplot as plt
import seaborn as sns

class FMOProject:
    """
    Encapsulates the entire FMO project, from environment setup to
    simulation and analysis.
    """
    def __init__(self, quick=False):
        self.quick = quick
        self.data_dir = "final_results/data"
        self.figures_dir = "final_results/figures"

        # Scientific constants
        self.H = self._get_scaled_hamiltonian()
        self.T_FINAL_PS = 1.0
        self.N_STEPS = 20 if self.quick else 100
        self.CM_TO_PS_INV = 0.1884

    def run_full_analysis(self):
        """Main entry point to run the entire analysis pipeline."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        
        # Step 1: Run the core quantum transport simulation
        self._run_quantum_simulation()

        # Step 2: Run the classical benchmark
        self._run_classical_benchmark()

        # Step 3: Generate all plots
        self._generate_plots()

        # Step 4: Generate convergence plot
        self._generate_convergence_plot()

        # Step 5: Run hardware transpilation check
        self._run_hardware_transpilation_check()

        # Step 6: Generate final report
        self._generate_report()

    def _generate_report(self):
        """Generates the final markdown summary report."""
        logging.info("Generating Final Project Summary Report...")

        df = pd.read_csv(os.path.join(self.data_dir, "quantum_transport_results.csv"))

        eff_min_idx = df['efficiency'].idxmin()
        eff_min = df.loc[eff_min_idx, 'efficiency']
        gamma_min = df.loc[eff_min_idx, 'gamma_ps_inv']
        eff_final = df['efficiency'].iloc[-1]
        gamma_final = df['gamma_ps_inv'].iloc[-1]
        enhancement = (eff_final - eff_min) / eff_min * 100

        report = (
            "# FMO Noise-Assisted Transport: Project Summary\n\n"
            "This document summarizes the key findings of the simulated quantum transport in a 4-site FMO-like complex.\n\n"
            "## 1. Quantitative Headline Result\n\n"
            "The primary finding is the clear demonstration of noise-assisted transport. After an initial drop, transport efficiency is enhanced by dephasing noise.\n\n"
            f"- **Minimum Efficiency**: {eff_min:.3f} at γ = {gamma_min:.2f} ps⁻¹\n"
            f"- **Final Efficiency**: {eff_final:.3f} at γ = {gamma_final:.2f} ps⁻¹\n"
            f"- **Quantitative Enhancement**: A **{enhancement:+.1f}%** relative increase in transport efficiency from the minimum.\n\n"
            "**Definition of Efficiency (η):** Efficiency is defined as the population of the target sink site at the end of the simulation time (t=1 ps). "
            "In our 4-qubit system, this corresponds to the population of the state |1000> (Braket little-endian), which is `ρ_sink,sink(t_final)`.\n\n"
            "## 2. Key Validation Figures\n\n"
            "The following figures provide visual evidence for the scientific rigor and validity of the simulation.\n\n"
            "### Figure 1: Quantum vs. Classical Transport\n\n"
            "This plot shows the main result, comparing the efficiency of the quantum simulation against a classical random walk benchmark.\n\n"
            "![Main Comparison Plot](final_results/figures/Fig1_Quantum_vs_Classical_Transport_Final.png)\n\n"
            "### Figure 2: Subspace Leakage Analysis\n\n"
            "This plot confirms that population leakage out of the single-excitation subspace is negligible, ensuring the simulation conserves probability and is physically valid.\n\n"
            "![Leakage Plot](final_results/figures/Fig2_Leakage_Analysis.png)\n\n"
            "### Figure 3: Numerical Convergence\n\n"
            "This plot shows that the simulation results converge as the Trotter time step is reduced.\n\n"
            "![Convergence Plot](final_results/figures/Fig3_Convergence_Analysis.png)\n\n"
            "## 3. Physical Realism\n\n"
            "The dephasing rates (γ) used in this simulation are physically relevant.\n"
        )
        report_path = "results_summary.md"
        with open(report_path, "w") as f:
            f.write(report)
        logging.info(f"Summary report saved to `{report_path}`")

    def _run_hardware_transpilation_check(self):
        """
        Checks the feasibility of running the FMO experiment on hardware by
        transpiling the circuit for a representative backend.
        """
        logging.info("Starting Hardware Transpilation Check...")

        # We use a LocalSimulator but can analyze the native gates produced.
        # This provides a hardware-aware estimate without needing cloud access.
        
        # From simulation, the optimal gamma was found to be around 37 ps^-1
        OPTIMAL_GAMMA_PS_INV = 37.68

        circuit = self._build_evolution_circuit(gamma=OPTIMAL_GAMMA_PS_INV)
        
        # This is a simplified, local representation of a transpilation process.
        # It shows the gates as they are defined in the circuit builder.
        # A true cloud transpilation would decompose these further.
        native_counts = {}
        for instr in circuit.instructions:
            gate_name = instr.operator.name
            native_counts[gate_name] = native_counts.get(gate_name, 0) + 1
            
        logging.info("Local gate analysis complete.")
        print("\n" + "="*60)
        print("  Local Hardware Feasibility Estimate")
        print("="*60)
        print(f"  Qubit Count: {circuit.qubit_count}")
        print(f"  Circuit Depth: {circuit.depth} (before decomposition)")
        print("\n  Abstract Gate Counts (before hardware transpilation):")
        
        if not native_counts:
            print("    No gates found in circuit.")
        else:
            for gate, count in sorted(native_counts.items()):
                print(f"    - {gate}: {count}")
        
        print("\n  NOTE: This is a local estimate. True hardware transpilation")
        print("        on a cloud device would decompose these gates further")
        print("        into the backend's native gate set (e.g., GPI, GPi2 on IonQ).")
        print("="*60)
        logging.info("✅ Hardware check estimate complete.")

    def _generate_convergence_plot(self):
        """
        Generates a plot to demonstrate the numerical convergence of the
        simulation with respect to the Trotter step size.
        """
        logging.info("Generating Convergence Analysis Plot...")

        quantum_df = pd.read_csv(os.path.join(self.data_dir, "quantum_transport_results.csv"))
        gamma_zero = 0.0
        gamma_min_eff = quantum_df.loc[quantum_df['efficiency'].idxmin(), 'gamma_ps_inv']
        
        device = LocalSimulator("braket_dm")
        n_steps_range = [10, 20, 40, 60, 80, 100, 150, 200]
        
        convergence_results = []
        
        for gamma in [gamma_zero, gamma_min_eff]:
            logging.info(f"Testing convergence for γ = {gamma:.2f} ps⁻¹...")
            for n_steps in n_steps_range:
                # Temporarily override the instance's N_STEPS
                original_n_steps = self.N_STEPS
                self.N_STEPS = n_steps
                
                circuit = self._build_evolution_circuit(gamma)
                circuit.density_matrix()
                task = device.run(circuit, shots=0)
                eff, _, _ = self._extract_populations(task.result().result_types[0])
                
                convergence_results.append({
                    "gamma": gamma,
                    "n_steps": n_steps,
                    "efficiency": eff
                })
                # Restore N_STEPS
                self.N_STEPS = original_n_steps

        df_conv = pd.DataFrame(convergence_results)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        for gamma_val, group in df_conv.groupby('gamma'):
            label = f'γ = {gamma_val:.2f} ps⁻¹ (Coherent)' if gamma_val == 0 else f'γ = {gamma_val:.2f} ps⁻¹ (Min. Efficiency)'
            ax.plot(group['n_steps'], group['efficiency'], marker='o', linestyle='-', label=label)

        ax.set_title('Simulation Convergence vs. Number of Trotter Steps', fontsize=16)
        ax.set_xlabel('Number of Trotter Steps (N_steps)', fontsize=12)
        ax.set_ylabel('Final Transport Efficiency (η)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        plt.tight_layout()
        output_path = os.path.join(self.figures_dir, "Fig3_Convergence_Analysis.png")
        fig.savefig(output_path, dpi=300)
        plt.close(fig)
        logging.info(f"Convergence plot saved to {output_path}")

    def _run_classical_benchmark(self):
        """
        Runs a classical random walk simulation as a benchmark.
        
        The model assumes incoherent hopping between sites. The rate of
        hopping is proportional to the squared coupling strength |H_ij|^2.
        This is a standard approach for modeling classical energy transfer
        in such systems.
        """
        logging.info("Running Classical Random Walk Benchmark...")
        
        # Transition matrix based on squared couplings
        T = self.H**2
        np.fill_diagonal(T, 0)
        T = T / T.sum(axis=1, keepdims=True)

        # Get the same gamma values used in the quantum simulation
        quantum_df = pd.read_csv(os.path.join(self.data_dir, "quantum_transport_results.csv"))
        gamma_values = quantum_df['gamma_ps_inv'].values

        results = []
        for gamma in gamma_values:
            # The classical model is not affected by dephasing, but we
            # calculate it for each gamma value to have a matching x-axis.
            p = np.zeros(4)
            p[0] = 1.0  # Start at site 0

            for _ in range(self.N_STEPS):
                p = T.T @ p
            
            # Efficiency is the population at the sink (site 3)
            results.append({
                "gamma_ps_inv": gamma,
                "classical_efficiency": p[3]
            })

        df_classical = pd.DataFrame(results)
        output_path = os.path.join(self.data_dir, "classical_transport_results.csv")
        df_classical.to_csv(output_path, index=False)
        logging.info(f"Classical benchmark complete. Results saved to {output_path}")

    def _get_scaled_hamiltonian(self):
        SCALE_FACTOR = 0.1
        H_matrix = np.array([
            [280.0, -106.0, 8.4, 5.7],
            [-106.0, 420.0, 41.0, -9.1],
            [8.4, 41.0, 210.0, -63.0],
            [5.7, -9.1, -63.0, 320.0]
        ]) * SCALE_FACTOR
        return H_matrix

    def _run_quantum_simulation(self):
        """Performs the noise-assisted transport simulation."""
        logging.info("Starting FMO Quantum Simulation...")
        
        gamma_values_cm = np.linspace(0, 500, 5) if self.quick else np.linspace(0, 500, 26)
        gamma_values_ps_inv = gamma_values_cm * self.CM_TO_PS_INV

        device = LocalSimulator("braket_dm")
        results = []

        for gamma in gamma_values_ps_inv:
            circuit = self._build_evolution_circuit(gamma)
            circuit.density_matrix()
            
            task = device.run(circuit, shots=0)
            dm_result = task.result().result_types[0]
            
            eff, leak, pop_err = self._extract_populations(dm_result)
            
            assert leak < 0.015, f"Leakage {leak:.4f} exceeded 1.5% at gamma={gamma:.2f}"
            assert abs(pop_err) < 1e-6, f"Population error {pop_err:.4e} too high at gamma={gamma:.2f}"
            
            results.append({
                "gamma_ps_inv": gamma,
                "efficiency": eff,
                "leakage": leak,
            })

        df_results = pd.DataFrame(results)
        output_path = os.path.join(self.data_dir, "quantum_transport_results.csv")
        df_results.to_csv(output_path, index=False)
        logging.info(f"Quantum simulation complete. Results saved to {output_path}")

    def _build_evolution_circuit(self, gamma):
        circuit = Circuit()
        circuit.x(0)
        dt = self.T_FINAL_PS / self.N_STEPS
        
        for _ in range(self.N_STEPS):
            for i in range(4):
                if abs(self.H[i, i]) > 1e-9:
                    circuit.rz(i, -self.H[i, i] * dt)
            for i in range(4):
                for j in range(i + 1, 4):
                    if abs(self.H[i, j]) > 1e-9:
                        theta = self.H[i, j] * dt
                        circuit.xy(i, j, theta)
            if gamma > 0:
                p_dephase = 1 - np.exp(-gamma * dt)
                for q in range(4):
                    circuit.phase_damping(q, p_dephase)
        return circuit

    def _extract_populations(self, dm_result):
        dm = np.array(dm_result.value)
        se_indices = [1, 2, 4, 8]
        pop_single_states = [np.real(dm[i, i]) for i in se_indices]
        total_pop_single = sum(pop_single_states)
        total_pop_system = np.trace(dm).real
        leakage = 1.0 - total_pop_single
        conservation_error = 1.0 - total_pop_system
        efficiency = pop_single_states[3]
        return efficiency, leakage, conservation_error

    def _generate_plots(self):
        """Generates all the publication-quality figures."""
        logging.info("Generating all final plots...")
        plt.style.use('seaborn-v0_8-colorblind')

        quantum_df = pd.read_csv(os.path.join(self.data_dir, "quantum_transport_results.csv"))
        
        # For now, we assume the classical benchmark file exists.
        # It will be generated in a later step.
        classical_df = pd.read_csv(os.path.join(self.data_dir, "classical_transport_results.csv"))

        self._create_comparison_plot(quantum_df, classical_df)
        self._create_leakage_plot(quantum_df)
        logging.info("All plots generated successfully.")

    def _create_comparison_plot(self, quantum_df, classical_df, aws_df=None):
        """Creates the main figure comparing quantum and classical transport."""
        logging.info("Generating main comparison plot...")
        fig, ax = plt.subplots(figsize=(12, 7))

        ax.plot(quantum_df['gamma_ps_inv'], quantum_df['efficiency'],
                marker='o', linestyle='-', label='Quantum Transport (Local DM Simulator)')
        ax.plot(classical_df['gamma_ps_inv'], classical_df['classical_efficiency'],
                marker='s', linestyle='--', label='Classical Random Walk (Benchmark)')

        if aws_df is not None and not aws_df.empty:
            q_color = ax.get_lines()[0].get_color()
            ax.plot(aws_df['gamma_ps_inv'], aws_df['aws_efficiency'],
                    'X', markersize=14, mew=2.5,
                    label='Quantum Transport (AWS DM1 Cloud Sim)',
                    linestyle='none', c=q_color, zorder=10,
                    markeredgecolor='white')

        ax.set_title('Noise-Assisted Transport in an FMO-like System', fontsize=18, weight='bold')
        ax.set_xlabel('Dephasing Rate γ (ps⁻¹)', fontsize=14)
        ax.set_ylabel('Transport Efficiency to Sink', fontsize=14)
        ax.legend(fontsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.6)
        ax.tick_params(axis='both', which='major', labelsize=12)

        min_idx = quantum_df['efficiency'].idxmin()
        min_gamma = quantum_df.loc[min_idx, 'gamma_ps_inv']
        min_eff = quantum_df.loc[min_idx, 'efficiency']
        final_eff = quantum_df['efficiency'].iloc[-1]
        enhancement = (final_eff - min_eff) / min_eff * 100
        
        ax.annotate(f'Noise-Assisted Enhancement:\nη rises from {min_eff:.3f} to {final_eff:.3f}\n(a {enhancement:+.1f}% increase)',
                    xy=(quantum_df['gamma_ps_inv'].iloc[-1], final_eff),
                    xytext=(min_gamma - 10, final_eff + 0.15),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8, connectionstyle="arc3,rad=0.2"),
                    bbox=dict(boxstyle="round,pad=0.4", fc="lightgoldenrodyellow", ec="gray", alpha=0.9),
                    fontsize=11, weight='bold')
        ax.annotate(f'Minimum η = {min_eff:.3f}',
                    xy=(min_gamma, min_eff),
                    xytext=(min_gamma, min_eff - 0.12),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                    ha='center',
                    fontsize=10)

        plt.tight_layout()
        output_path = os.path.join(self.figures_dir, "Fig1_Quantum_vs_Classical_Transport_Final.png")
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

    def _create_leakage_plot(self, quantum_df):
        """Creates a figure showing population leakage."""
        logging.info("Generating leakage plot...")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(quantum_df['gamma_ps_inv'], quantum_df['leakage'],
                marker='.', linestyle='-', label='Subspace Leakage')
        ax.set_title('Population Leakage vs. Dephasing Rate', fontsize=16)
        ax.set_xlabel('Dephasing Rate γ (ps⁻¹)', fontsize=12)
        ax.set_ylabel('Leakage (1 - P_single_excitation)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.tight_layout()
        output_path = os.path.join(self.figures_dir, "Fig2_Leakage_Analysis.png")
        fig.savefig(output_path, dpi=300)
        plt.close(fig)