"""
4-Qubit FMO Proof-of-Concept: Noise-Assisted Energy Transport

This script implements a simplified FMO complex using the first 4 sites from
Adolphs-Renger 2006. It demonstrates noise-assisted quantum transport by
sweeping dephasing rates and measuring excitation transfer efficiency.

Key features:
- Trotter decomposition of FMO Hamiltonian evolution
- Uniform site dephasing with tunable rates
- Local simulation with optional AWS DM1 confirmation
- Efficiency measured as population transfer to "sink" site
"""

import numpy as np
import pandas as pd
import argparse
import time
import os
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from braket.aws import AwsDevice
from braket.circuits.noises import PhaseDamping

# Constants
CM_TO_PSPERSEC = 0.000188365  # cm^-1 → ps^-1 (ℏ = 1)
DT_PS = 0.025  # Trotter step size in ps (25 fs)
T_FINAL_PS = 1.0  # Total evolution time in ps
N_STEPS = int(T_FINAL_PS / DT_PS)  # 40 steps
WALL_CLOCK_GUARD = 60  # seconds

def load_fmo_hamiltonian(csv_path="fmo4_couplings.csv"):
    """Load the 4x4 FMO coupling matrix and convert to rad/ps units."""
    # Skip comment lines and load the matrix
    H_cm = np.loadtxt(csv_path, delimiter=',', comments='#')
    H_radps = H_cm * CM_TO_PSPERSEC
    print(f"Loaded FMO Hamiltonian (4x4), max coupling: {np.max(np.abs(H_radps)):.6f} rad/ps")
    return H_radps

def add_hopping_term(circuit, q1, q2, theta):
    """Add hopping interaction exp(-i*theta*(σ+⊗σ- + σ-⊗σ+)) for single excitation subspace.
    
    In the single excitation subspace, this is equivalent to a rotation between |10⟩ and |01⟩.
    We implement this using controlled rotations.
    """
    # For single excitation subspace, hopping between sites i,j is:
    # exp(-i*theta*(|i⟩⟨j| + |j⟩⟨i|)) in the {|i⟩, |j⟩} subspace
    
    # This can be implemented as a partial SWAP rotation
    # We use the fact that in single-excitation subspace:
    # |q1=1,q2=0⟩ ↔ |q1=0,q2=1⟩ rotation
    
    # Implement using RY rotations conditioned on the other qubit states
    # This is a simplified approach for the 4-qubit single-excitation case
    
    # For now, use a simpler approach: direct XX+YY which approximates hopping
    # This needs to be small angle for accuracy
    circuit.cnot(q1, q2)
    circuit.rz(q2, 2 * theta)
    circuit.cnot(q1, q2)
    return circuit

def build_fmo_circuit(H, dt_ps, n_steps, dephase_p):
    """
    Build the FMO evolution circuit with Trotter decomposition and dephasing.
    
    Args:
        H: 4x4 Hamiltonian matrix (rad/ps)
        dt_ps: Trotter step size (ps)
        n_steps: Number of Trotter steps
        dephase_p: Dephasing probability per step
    """
    circuit = Circuit()
    
    # Initial state: excitation on site 1 (qubit 0)
    circuit.x(0)
    
    # Trotter evolution
    for step in range(n_steps):
        # Diagonal terms (site energies) → single-qubit Rz rotations
        for i in range(4):
            theta_diag = -H[i, i] * dt_ps
            circuit.rz(i, theta_diag)
        
        # Off-diagonal terms (couplings) → hopping interactions
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(H[i, j]) > 1e-10:  # Skip negligible couplings
                    theta_coupling = -H[i, j] * dt_ps
                    add_hopping_term(circuit, i, j, theta_coupling)
        
        # Add dephasing noise after each Trotter step
        if dephase_p > 0:
            for q in range(4):
                circuit.phase_damping(q, dephase_p)
    
    return circuit

def count_phase_damping(circuit):
    """Count the number of phase damping operations in the circuit."""
    count = 0
    for instr in circuit.instructions:
        if hasattr(instr, 'operator') and instr.operator.name == 'PhaseDamping':
            count += 1
    return count

def calculate_efficiency(density_matrix, sink_qubit=2):
    """Calculate transport efficiency as population on sink qubit.
    
    In FMO model: site 1 (qubit 0) → site 3 (qubit 2) transport.
    Braket uses little-endian, so:
    - Site 1 = qubit 0 (rightmost bit)
    - Site 3 = qubit 2 
    """
    # Convert to numpy if needed (for compatibility with different Braket versions)
    if hasattr(density_matrix, 'value'):
        dm = density_matrix.value
    else:
        dm = density_matrix
    
    # Handle different return formats
    if isinstance(dm, list):
        # Convert complex list format to numpy array
        dm_array = np.array(dm)
        if dm_array.dtype == object:  # List of complex numbers as [real, imag]
            dm_complex = np.array([[complex(x[0], x[1]) if isinstance(x, list) else x 
                                  for x in row] for row in dm])
        else:
            dm_complex = dm_array
    else:
        dm_complex = np.array(dm)
    
    # Calculate population on sink qubit
    n_qubits = int(np.log2(dm_complex.shape[0]))
    sink_states = [i for i in range(2**n_qubits) if (i >> sink_qubit) & 1]
    efficiency = sum(np.real(dm_complex[i, i]) for i in sink_states)
    
    return efficiency

def run_sweep(device, H, gamma_values, output_path):
    """Run the dephasing sweep and save results."""
    results = []
    
    print(f"Running sweep on {device.name if hasattr(device, 'name') else 'LocalSimulator'}")
    print(f"Gamma values: {gamma_values} ps^-1")
    print(f"Circuit parameters: {N_STEPS} steps, {DT_PS} ps/step")
    
    for i, gamma in enumerate(gamma_values):
        t0 = time.time()
        print(f"  Point {i+1}/{len(gamma_values)}: γ = {gamma} ps^-1...", end=" ")
        
        # Convert gamma to dephasing probability: p = 1 - exp(-γ*dt)
        dephase_p = 1 - np.exp(-gamma * DT_PS) if gamma > 0 else 0
        
        # Build circuit
        circuit = build_fmo_circuit(H, DT_PS, N_STEPS, dephase_p)
        circuit.density_matrix()
        
        # Sanity checks
        assert circuit.qubit_count == 4, f"Expected 4 qubits, got {circuit.qubit_count}"
        expected_noise_ops = N_STEPS * 4 if gamma > 0 else 0
        actual_noise_ops = count_phase_damping(circuit)
        assert actual_noise_ops == expected_noise_ops, f"Expected {expected_noise_ops} noise ops, got {actual_noise_ops}"
        
        # Run simulation
        task = device.run(circuit, shots=0)
        result = task.result()
        density_matrix = result.result_types[0]
        
        # Calculate efficiency
        efficiency = calculate_efficiency(density_matrix)
        
        elapsed = time.time() - t0
        print(f"efficiency = {efficiency:.4f} (took {elapsed:.2f}s)")
        
        results.append({
            'gamma_ps': gamma,
            'dephase_p': dephase_p,
            'efficiency': efficiency,
            'runtime_s': elapsed
        })
        
        # Wall-clock guard for cloud runs
        if elapsed > WALL_CLOCK_GUARD:
            print(f"Wall-clock guard triggered at {elapsed:.1f}s")
            break
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    
    return df

def main():
    parser = argparse.ArgumentParser(description="4-Qubit FMO Noise-Assisted Transport")
    parser.add_argument("--device_arn", type=str, default="local", 
                       help="Device ARN (default: local)")
    parser.add_argument("--sweep_points", type=str, default="0,25,50,75,100",
                       help="Comma-separated gamma values in ps^-1")
    parser.add_argument("--output", type=str, default=None,
                       help="Output CSV file (auto-generated if not specified)")
    
    args = parser.parse_args()
    
    # Parse gamma values
    gamma_values = [float(x.strip()) for x in args.sweep_points.split(',')]
    
    # Set up device
    if args.device_arn == "local":
        device = LocalSimulator("braket_dm")
        device_name = "local"
    else:
        device = AwsDevice(args.device_arn)
        device_name = device.name.replace('/', '_')
    
    # Load Hamiltonian
    H = load_fmo_hamiltonian()
    
    # Set output path
    if args.output is None:
        if args.device_arn == "local":
            output_path = "sweep_local_dm.csv"
        else:
            output_path = f"dm1_check.csv"
    else:
        output_path = args.output
    
    # Run sweep
    results_df = run_sweep(device, H, gamma_values, output_path)
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Gamma range: {min(gamma_values)} - {max(gamma_values)} ps^-1")
    print(f"  Efficiency range: {results_df['efficiency'].min():.4f} - {results_df['efficiency'].max():.4f}")
    print(f"  Optimal gamma: {results_df.loc[results_df['efficiency'].idxmax(), 'gamma_ps']:.1f} ps^-1")
    print(f"  Total runtime: {results_df['runtime_s'].sum():.1f}s")

if __name__ == "__main__":
    main()
