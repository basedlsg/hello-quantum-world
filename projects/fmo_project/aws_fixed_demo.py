"""
Fixed AWS FMO Demonstration - handles numpy scalar formatting correctly
"""

import numpy as np
import pandas as pd
from braket.circuits import Circuit
from braket.devices import LocalSimulator

def create_transport_hamiltonian():
    """Create a Hamiltonian optimized for demonstrating noise-assisted transport."""
    H = np.array([
        [0.0,  0.4,  0.0,  0.0],   # Site 0 → Site 1
        [0.4,  0.2,  0.5,  0.0],   # Site 1 ↔ Site 2 (stronger forward)
        [0.0,  0.5,  0.1,  0.3],   # Site 2 → Site 3
        [0.0,  0.0,  0.3,  0.0]    # Site 3 (sink)
    ])
    return H

def build_evolution_circuit(H, evolution_time=2.0, n_steps=20, gamma=0.0):
    """Build quantum circuit for FMO evolution in single-excitation subspace."""
    circuit = Circuit()
    
    # Initial state: |0001⟩ (excitation on site 0, rightmost in Braket's convention)
    circuit.x(0)
    
    dt = evolution_time / n_steps
    
    for step in range(n_steps):
        # Diagonal evolution (site energies)
        for i in range(4):
            if abs(H[i, i]) > 1e-8:
                circuit.rz(i, -H[i, i] * dt)
        
        # Off-diagonal evolution (hopping terms)
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(H[i, j]) > 1e-8:
                    theta = H[i, j] * dt
                    circuit.cnot(i, j)
                    circuit.ry(j, 2 * theta)
                    circuit.cnot(i, j)
        
        # Dephasing noise
        if gamma > 0:
            p_dephase = 1 - np.exp(-gamma * dt)
            for q in range(4):
                circuit.phase_damping(q, p_dephase)
    
    return circuit

def extract_single_excitation_populations(density_matrix):
    """Extract populations from the single-excitation subspace only."""
    dm = np.array(density_matrix.value if hasattr(density_matrix, 'value') else density_matrix)
    
    # Single-excitation basis states: [1, 2, 4, 8] for sites [0, 1, 2, 3]
    single_exc_states = [1, 2, 4, 8]
    populations = []
    
    for state_idx in single_exc_states:
        pop = float(np.real(dm[state_idx, state_idx]))  # Convert to Python float
        populations.append(pop)
    
    total_single_exc = sum(populations)
    return populations, total_single_exc

def aws_confirmation(device_arn="arn:aws:braket:::device/quantum-simulator/amazon/dm1"):
    """Run 3-point confirmation on AWS DM1."""
    print(f"=== AWS DM1 Confirmation ===")
    
    from braket.aws import AwsDevice
    import time
    
    device = AwsDevice(device_arn)
    H = create_transport_hamiltonian()
    
    # Test 3 key points
    test_gammas = [0.0, 1.0, 2.0]
    results = []
    total_cost_time = 0
    
    for gamma in test_gammas:
        print(f"AWS DM1: γ = {gamma:.1f}...", end=" ", flush=True)
        
        t0 = time.time()
        
        circuit = build_evolution_circuit(H, evolution_time=2.0, n_steps=20, gamma=gamma)
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        populations, total_se = extract_single_excitation_populations(result.result_types[0])
        efficiency = populations[3]  # Already converted to float
        
        elapsed = time.time() - t0
        total_cost_time += elapsed
        
        print(f"efficiency = {efficiency:.4f} ({elapsed:.1f}s)")
        
        results.append({
            'gamma': gamma,
            'efficiency': efficiency,
            'runtime_s': elapsed,
            'total_single_exc': total_se
        })
        
        # Safety check
        if total_cost_time > 180:
            print("Safety limit reached")
            break
    
    df_aws = pd.DataFrame(results)
    df_aws.to_csv("aws_dm1_confirmation.csv", index=False)
    
    print(f"AWS confirmation completed: {total_cost_time:.1f}s total")
    print(f"Results saved to aws_dm1_confirmation.csv")
    
    return df_aws

def run_local_demo():
    """Run local demonstration first."""
    print("=== Local Demonstration ===")
    
    H = create_transport_hamiltonian()
    device = LocalSimulator("braket_dm")
    
    # Quick 3-point local test
    test_gammas = [0.0, 1.0, 2.0]
    local_results = []
    
    for gamma in test_gammas:
        circuit = build_evolution_circuit(H, evolution_time=2.0, n_steps=20, gamma=gamma)
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        populations, total_se = extract_single_excitation_populations(result.result_types[0])
        efficiency = populations[3]
        
        print(f"Local: γ = {gamma:.1f} → efficiency = {efficiency:.4f}")
        local_results.append({'gamma': gamma, 'efficiency': efficiency})
    
    return pd.DataFrame(local_results)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--device_arn", type=str, 
                       default="arn:aws:braket:::device/quantum-simulator/amazon/dm1")
    
    args = parser.parse_args()
    
    # Run local demo first
    df_local = run_local_demo()
    
    # Run AWS confirmation
    print(f"\n🚀 Starting AWS DM1 confirmation...")
    df_aws = aws_confirmation(args.device_arn)
    
    # Compare results
    print(f"\n=== Comparison ===")
    for _, row in df_aws.iterrows():
        gamma = row['gamma']
        aws_eff = row['efficiency']
        local_eff = df_local[df_local['gamma'] == gamma]['efficiency'].iloc[0]
        diff = abs(aws_eff - local_eff) / local_eff * 100
        
        print(f"γ = {gamma:.1f}: Local = {local_eff:.4f}, AWS = {aws_eff:.4f}, Diff = {diff:.1f}%")
    
    print(f"\n✅ AWS DM1 Confirmation Complete!")
    print(f"📊 Results saved to: aws_dm1_confirmation.csv")
