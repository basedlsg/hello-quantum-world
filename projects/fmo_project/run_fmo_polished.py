# run_fmo_polished.py
#
# The canonical script for the FMO noise-assisted transport demonstration.
# This script performs the main quantum simulation and includes rigorous
# validation checks for population conservation, subspace leakage, and
# numerical convergence.

import numpy as np
import pandas as pd
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import os
import logging

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create directories for results
DATA_DIR = "final_results/data"
FIGURES_DIR = "final_results/figures"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# --- Hamiltonian Definition ---
def get_scaled_hamiltonian():
    """
    Returns the 4x4 FMO-like Hamiltonian.

    The couplings and site energies are scaled down from the original
    Adolphs-Renger 2006 Hamiltonian. This is necessary to ensure the
    Trotterized evolution is stable and accurate for the chosen time step (dt),
    preventing numerical artifacts and keeping the total gate count reasonable.
    The original literature values are in cm^-1; we use dimensionless units here
    and will convert back for the final analysis.

    Returns:
        np.ndarray: The 4x4 Hamiltonian matrix.
    """
    # Scaling factor applied to original literature values
    SCALE_FACTOR = 0.1

    # Site energies (diagonal) and couplings (off-diagonal)
    # Scaled from Adolphs & Renger (2006), sites 1-4.
    H_matrix = np.array([
        [280.0, -106.0,    8.4,    5.7],
        [-106.0, 420.0,   41.0,   -9.1],
        [8.4,    41.0,   210.0,  -63.0],
        [5.7,    -9.1,   -63.0,  320.0]
    ]) * SCALE_FACTOR

    return H_matrix

# --- Core Simulation Logic ---
def build_evolution_circuit(H, evolution_time, n_steps, gamma=0.0):
    """Builds the quantum circuit for the FMO time evolution."""
    circuit = Circuit()
    # Initial state: excitation on site 0 (|0001> in Braket's little-endian convention)
    circuit.x(0)
    
    dt = evolution_time / n_steps
    
    for _ in range(n_steps):
        # Diagonal part of Hamiltonian (site energies)
        for i in range(4):
            if abs(H[i, i]) > 1e-9:
                circuit.rz(i, -H[i, i] * dt)
        
        # Off-diagonal part (couplings) using the native XY gate for stability
        # The hopping term is H_ij * (X_i*X_j + Y_i*Y_j)/2.
        # The Braket xy(theta) gate implements exp(-i*theta/2 * (X*X+Y*Y)).
        # By comparing exponents, the correct theta is H_ij*dt.
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(H[i, j]) > 1e-9:
                    # The factor of 2 was erroneous and has been removed.
                    theta = H[i, j] * dt
                    circuit.xy(i, j, theta)
        
        # Add dephasing noise channel
        if gamma > 0:
            # Probability of dephasing for a given gamma and time step dt
            p_dephase = 1 - np.exp(-gamma * dt)
            for q in range(4):
                circuit.phase_damping(q, p_dephase)
    
    return circuit

def extract_populations(dm_result):
    """Extracts key population metrics from a density matrix result."""
    dm = np.array(dm_result.value)
    
    # Single-excitation basis states (indices for a 4-qubit system)
    # |0001> = 1, |0010> = 2, |0100> = 4, |1000> = 8
    se_indices = [1, 2, 4, 8]
    
    # Populations of the single-excitation states
    pop_single_states = [np.real(dm[i, i]) for i in se_indices]
    
    # Total population in the single-excitation subspace
    total_pop_single = sum(pop_single_states)
    
    # Total population in the entire system (should be ~1.0)
    total_pop_system = np.trace(dm).real
    
    # Leakage is the population that has escaped the single-excitation subspace
    leakage = 1.0 - total_pop_single
    
    # Conservation error is how much the total probability deviates from 1
    conservation_error = 1.0 - total_pop_system
    
    # Efficiency is the population at the sink (site 3)
    efficiency = pop_single_states[3]
    
    return efficiency, leakage, conservation_error

# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Starting Polished FMO Simulation...")

    # Simulation parameters
    H = get_scaled_hamiltonian()
    T_FINAL_PS = 1.0      # Total evolution time in picoseconds
    N_STEPS = 100         # Increased steps to reduce Trotter error
    DT_PS = T_FINAL_PS / N_STEPS
    
    # Conversion factor: 1 cm^-1 = 0.1884 ps^-1
    # This factor converts dimensionless Hamiltonian units to ps^-1
    # and dimensionless gamma to a rate in ps^-1.
    CM_TO_PS_INV = 0.1884
    
    gamma_values_cm = np.linspace(0, 500, 26) # Dephasing rate in cm^-1
    gamma_values_ps_inv = gamma_values_cm * CM_TO_PS_INV # Dephasing rate in ps^-1

    device = LocalSimulator("braket_dm")
    results = []

    logging.info(f"Running simulation for {len(gamma_values_ps_inv)} dephasing rates...")
    print("-" * 80)
    print(f"{'γ (ps⁻¹)':>12} | {'Efficiency':>12} | {'Leakage':>12} | {'Pop Error':>12}")
    print("-" * 80)

    for gamma in gamma_values_ps_inv:
        circuit = build_evolution_circuit(H, evolution_time=T_FINAL_PS, n_steps=N_STEPS, gamma=gamma)
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        dm_result = task.result().result_types[0]
        
        eff, leak, pop_err = extract_populations(dm_result)
        
        # Validation asserts
        assert leak < 0.015, f"Leakage {leak:.4f} exceeded 1.5% at gamma={gamma:.2f}"
        assert abs(pop_err) < 1e-6, f"Population error {pop_err:.4e} too high at gamma={gamma:.2f}"
        
        print(f"{gamma:>12.2f} | {eff:>12.4f} | {leak:>12.3e} | {pop_err:>12.3e}")
        
        results.append({
            "gamma_ps_inv": gamma,
            "efficiency": eff,
            "leakage": leak,
            "population_error": pop_err,
            "dt_ps": DT_PS
        })

    # Save detailed results to CSV
    df_results = pd.DataFrame(results)
    output_path = os.path.join(DATA_DIR, "quantum_transport_results.csv")
    df_results.to_csv(output_path, index=False)
    
    logging.info(f"Simulation complete. Detailed results saved to {output_path}")

    # --- Convergence Check ---
    logging.info("Performing dt/2 convergence check...")
    
    n_steps_fine = N_STEPS * 2 # This will now be 200 steps
    gamma_optimal_idx = df_results['efficiency'].idxmax()
    gamma_optimal = df_results.loc[gamma_optimal_idx, 'gamma_ps_inv']

    # Run at original dt
    eff_dt1 = df_results.loc[gamma_optimal_idx, 'efficiency']
    
    # Run at dt/2
    circuit_fine = build_evolution_circuit(H, evolution_time=T_FINAL_PS, n_steps=n_steps_fine, gamma=gamma_optimal)
    circuit_fine.density_matrix()
    task_fine = device.run(circuit_fine, shots=0)
    eff_dt2, _, _ = extract_populations(task_fine.result().result_types[0])

    convergence_error = abs(eff_dt1 - eff_dt2)
    logging.info(f"Convergence check at optimal gamma={gamma_optimal:.2f} ps^-1:")
    logging.info(f"  Efficiency (dt): {eff_dt1:.6f}")
    logging.info(f"  Efficiency (dt/2): {eff_dt2:.6f}")
    logging.info(f"  Absolute Error: {convergence_error:.6f}")
    
    assert convergence_error < 0.01, f"Convergence error {convergence_error:.4f} failed <1% threshold."
    logging.info("✅ Convergence check passed.")

    # --- AWS Cloud Validation Step ---
    try:
        from braket.aws import AwsDevice
        import time
        
        logging.info("--- Starting AWS DM1 Cloud Validation ---")
        
        device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/dm1")
        logging.info(f"Successfully connected to target device: {device.name}")
        
        # Use the same optimal gamma from the local run
        aws_validation_gammas = sorted(list(set([0.0, gamma_optimal, df_results['gamma_ps_inv'].iloc[-5]])))
        aws_results = []

        logging.info(f"Running AWS validation for γ values: {[f'{g:.2f}' for g in aws_validation_gammas]}")

        for gamma in aws_validation_gammas:
            logging.info(f"Submitting AWS task for γ = {gamma:.2f} ps⁻¹...")
            circuit = build_evolution_circuit(H, evolution_time=T_FINAL_PS, n_steps=N_STEPS, gamma=gamma)
            circuit.density_matrix()
            
            task = device.run(circuit, shots=0)
            logging.info(f"  > Task created: {task.id}. Waiting for completion...")
            result = task.result()
            
            # Robustly handle AWS DM format
            dm_raw = result.result_types[0].value
            if isinstance(dm_raw, list):
                dm_shape = len(dm_raw)
                dm_aws = np.zeros((dm_shape, dm_shape), dtype=complex)
                for i in range(dm_shape):
                    for j in range(dm_shape):
                        dm_aws[i, j] = complex(dm_raw[i][j][0], dm_raw[i][j][1])
                # Indices: |0001>=1, |0010>=2, |0100>=4, |1000>=8. Site 3 is index 8.
                aws_eff = np.real(dm_aws[8, 8])
            else:
                aws_eff, _, _ = extract_populations(result.result_types[0])
                
            aws_results.append({ "gamma_ps_inv": gamma, "aws_efficiency": aws_eff })

        df_aws = pd.DataFrame(aws_results)
        aws_output_path = os.path.join(DATA_DIR, "aws_validation_results.csv")
        df_aws.to_csv(aws_output_path, index=False)
        logging.info(f"--- ✅ AWS Validation Complete ---")
        logging.info(f"AWS validation results saved to {aws_output_path}")

    except Exception as e:
        logging.warning(f"AWS Cloud Validation failed: {e}")
        logging.warning("Skipping AWS step. This may be due to missing credentials, permissions, or other errors.")

    print("-" * 80)
    logging.info("Polished FMO simulation finished successfully.")
