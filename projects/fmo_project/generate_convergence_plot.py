# generate_convergence_plot.py
#
# This script generates a plot to visually demonstrate the numerical convergence
# of the FMO simulation with respect to the Trotter step size (dt).

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os

from braket.devices import LocalSimulator
from run_fmo_polished import get_scaled_hamiltonian, build_evolution_circuit, extract_populations

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DATA_DIR = "final_results/data"
FIGURES_DIR = "final_results/figures"
plt.style.use('seaborn-v0_8-colorblind')

if __name__ == "__main__":
    logging.info("--- Generating Convergence Analysis Plot ---")

    # --- Load main results to find the two most interesting gamma values ---
    try:
        df_main = pd.read_csv(os.path.join(DATA_DIR, "quantum_transport_results.csv"))
    except FileNotFoundError:
        logging.error("Main quantum results not found. Please run `bash run_all.sh` first.")
        exit(1)

    # We will test convergence at two points:
    # 1. Zero noise (coherent regime)
    # 2. The point of minimum efficiency (where transport is least effective)
    gamma_zero = 0.0
    gamma_min_eff = df_main.loc[df_main['efficiency'].idxmin(), 'gamma_ps_inv']
    
    # --- Simulation Parameters ---
    H = get_scaled_hamiltonian()
    T_FINAL_PS = 1.0
    device = LocalSimulator("braket_dm")
    
    # We will vary the number of Trotter steps
    n_steps_range = [10, 20, 40, 60, 80, 100, 150, 200, 250, 300]
    
    convergence_results = []
    
    for gamma in [gamma_zero, gamma_min_eff]:
        logging.info(f"Testing convergence for γ = {gamma:.2f} ps⁻¹...")
        for n_steps in n_steps_range:
            dt = T_FINAL_PS / n_steps
            circuit = build_evolution_circuit(H, T_FINAL_PS, n_steps, gamma)
            circuit.density_matrix()
            task = device.run(circuit, shots=0)
            eff, _, _ = extract_populations(task.result().result_types[0])
            convergence_results.append({
                "gamma": gamma,
                "n_steps": n_steps,
                "dt": dt,
                "efficiency": eff
            })
    
    df_conv = pd.DataFrame(convergence_results)

    # --- Create the Plot ---
    logging.info("Plotting convergence results...")
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
    output_path = os.path.join(FIGURES_DIR, "Fig3_Convergence_Analysis.png")
    fig.savefig(output_path, dpi=300)
    logging.info(f"Convergence plot saved to {output_path}")
    plt.close(fig)

    logging.info("--- ✅ Convergence analysis complete. ---") 