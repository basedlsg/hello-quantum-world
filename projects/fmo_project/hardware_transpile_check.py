# hardware_transpile_check.py
#
# This script checks the feasibility of running the FMO experiment on
# real quantum hardware. It builds the circuit for the optimal noise
# level and transpiles it for a specific hardware target (IonQ Aria)
# to determine the required gate counts.

import numpy as np
import logging
from braket.aws import AwsDevice

# Import the circuit-building logic from our main script
from run_fmo_polished import build_evolution_circuit, get_scaled_hamiltonian

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Starting Hardware Transpilation Check...")

    # --- Target Device ---
    # We choose IonQ Aria as a representative high-fidelity device.
    # Note: This does not run a job, it only accesses the device's properties.
    try:
        # Using a region where Aria-1 is available
        device = AwsDevice("arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1")
        logging.info(f"Targeting hardware: {device.name}")
    except Exception as e:
        logging.error(f"Could not access AWS Device properties: {e}")
        logging.error("Please ensure your AWS credentials and Braket permissions are configured.")
        exit(1)

    # --- Circuit Construction ---
    # We build the circuit at the optimal dephasing rate found in simulation,
    # as this is the most scientifically interesting case to run on hardware.
    H = get_scaled_hamiltonian()
    T_FINAL_PS = 1.0
    N_STEPS = 40
    
    # From simulation, the optimal gamma was found to be around 37 ps^-1
    OPTIMAL_GAMMA_PS_INV = 37.68

    logging.info(f"Building circuit for optimal gamma = {OPTIMAL_GAMMA_PS_INV:.2f} ps⁻¹...")
    circuit = build_evolution_circuit(
        H,
        evolution_time=T_FINAL_PS,
        n_steps=N_STEPS,
        gamma=OPTIMAL_GAMMA_PS_INV
    )
    logging.info("Circuit built successfully.")

    # --- Transpilation and Analysis ---
    logging.info("Transpiling circuit for IonQ Aria's native gate set...")
    try:
        transpiled_circuit = device.transpile(circuit)
        
        # A robust way to count native gates
        native_counts = {}
        for instr in transpiled_circuit.instructions:
            gate_name = instr.operator.name
            native_counts[gate_name] = native_counts.get(gate_name, 0) + 1
            
        # Log the results
        print("\n" + "="*50)
        print("  Hardware Feasibility Report: IonQ Aria")
        print("="*50)
        print(f"  Qubit Count: {transpiled_circuit.qubit_count}")
        print(f"  Circuit Depth: {transpiled_circuit.depth}")
        print("\n  Native Gate Counts:")
        
        if not native_counts:
            print("    No native gates found in transpiled circuit.")
        else:
            for gate, count in sorted(native_counts.items()):
                print(f"    - {gate}: {count}")
            
        print("\n" + "="*50)
        logging.info("✅ Transpilation check complete.")

    except Exception as e:
        logging.error(f"Failed to transpile the circuit: {e}")
        logging.error("This can happen if the device is offline or if the circuit contains unsupported operations.")
        
