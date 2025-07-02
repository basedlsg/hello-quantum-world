# classical_benchmark.py
#
# This script runs a classical random walk simulation on the same
# 4-site FMO-like network. The goal is to provide a baseline to
# demonstrate that the noise-assisted enhancement observed in the
# quantum model is a non-classical effect.

import numpy as np
import pandas as pd
from scipy.linalg import expm
import os
import logging

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DATA_DIR = "final_results/data"
os.makedirs(DATA_DIR, exist_ok=True)

# Import the Hamiltonian from the polished quantum script to ensure consistency
from run_fmo_polished import get_scaled_hamiltonian

# --- Classical Rate Matrix Construction ---
def build_classical_rate_matrix(H, gamma):
    """
    Builds a classical rate matrix (Liouvillian) for the random walk.

    Args:
        H (np.ndarray): The coherent Hamiltonian (couplings).
        gamma (float): The dephasing rate (incoherent hopping).

    Returns:
        np.ndarray: The 4x4 classical rate matrix.
    """
    n_sites = H.shape[0]
    L = np.zeros((n_sites, n_sites))

    for i in range(n_sites):
        for j in range(n_sites):
            if i == j:
                continue
            
            # Coherent part (from Hamiltonian couplings) - proportional to H_ij^2
            # This is a standard way to model coherent transfer rates classically.
            coherent_rate = (H[i, j]**2) * 0.1 # Small factor to scale contribution
            
            # Incoherent part (from dephasing) - proportional to gamma
            # This models noise-induced hopping between connected sites.
            incoherent_rate = gamma * (1.0 if abs(H[i,j]) > 1e-9 else 0.0)

            rate = coherent_rate + incoherent_rate
            
            L[j, i] = rate  # Rate from site i to site j
            L[i, i] -= rate # Rate of leaving site i

    return L

# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Starting Classical Random Walk Benchmark...")

    # Use the same parameters as the quantum simulation for a fair comparison
    H = get_scaled_hamiltonian()
    T_FINAL_PS = 1.0
    
    # Use the same gamma range
    CM_TO_PS_INV = 0.1884
    gamma_values_cm = np.linspace(0, 500, 26)
    gamma_values_ps_inv = gamma_values_cm * CM_TO_PS_INV
    
    results = []

    logging.info(f"Running classical simulation for {len(gamma_values_ps_inv)} dephasing rates...")
    print("-" * 50)
    print(f"{'γ (ps⁻¹)':>12} | {'Classical Efficiency':>20}")
    print("-" * 50)

    # Initial condition: population is entirely at site 0
    P0 = np.zeros(4)
    P0[0] = 1.0

    for gamma in gamma_values_ps_inv:
        # Build the rate matrix for the current noise level
        L = build_classical_rate_matrix(H, gamma)
        
        # Propagate the initial state in time: P(t) = exp(L*t) * P(0)
        P_t = expm(L * T_FINAL_PS) @ P0
        
        # Classical efficiency is the population at the sink (site 3)
        classical_efficiency = P_t[3]
        
        print(f"{gamma:>12.2f} | {classical_efficiency:>20.4f}")
        
        results.append({
            "gamma_ps_inv": gamma,
            "classical_efficiency": classical_efficiency
        })

    # Save results to CSV
    df_classical = pd.DataFrame(results)
    output_path = os.path.join(DATA_DIR, "classical_transport_results.csv")
    df_classical.to_csv(output_path, index=False)
    
    logging.info(f"Classical benchmark complete. Results saved to {output_path}")
    print("-" * 50) 