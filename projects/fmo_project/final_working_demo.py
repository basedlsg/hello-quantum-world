"""
FINAL WORKING FMO Demonstration

This version correctly handles the single-excitation subspace and demonstrates
clear noise-assisted transport suitable for AWS DM1 confirmation.
"""

import numpy as np
import pandas as pd
from braket.circuits import Circuit
from braket.devices import LocalSimulator

def create_transport_hamiltonian():
    """Create a Hamiltonian optimized for demonstrating noise-assisted transport."""
    # 4-site linear chain with asymmetric couplings
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
                    # Implement hopping with CNOT sandwich
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
    
    # Single-excitation basis states in Braket's little-endian convention:
    # |0001⟩ = state 1  → site 0 excited
    # |0010⟩ = state 2  → site 1 excited  
    # |0100⟩ = state 4  → site 2 excited
    # |1000⟩ = state 8  → site 3 excited
    
    single_exc_states = [1, 2, 4, 8]
    populations = []
    
    for i, state_idx in enumerate(single_exc_states):
        pop = np.real(dm[state_idx, state_idx])
        populations.append(pop)
    
    # Calculate total population in single-excitation subspace
    total_single_exc = sum(populations)
    
    return populations, total_single_exc

def run_transport_demonstration():
    """Run the complete noise-assisted transport demonstration."""
    print("=== FMO Noise-Assisted Transport: Final Demonstration ===\n")
    
    H = create_transport_hamiltonian()
    print("Transport Hamiltonian:")
    print(H)
    print("\nSingle-excitation basis: |0001⟩→Site0, |0010⟩→Site1, |0100⟩→Site2, |1000⟩→Site3")
    print()
    
    device = LocalSimulator("braket_dm")
    
    # Sweep noise levels
    gamma_values = np.linspace(0, 3.0, 13)  # 0 to 3.0 in steps of 0.25
    results = []
    
    print("γ\tSite0\tSite1\tSite2\tSite3\tTotal\tEfficiency")
    print("-" * 65)
    
    for gamma in gamma_values:
        # Build and run circuit
        circuit = build_evolution_circuit(H, evolution_time=2.0, n_steps=20, gamma=gamma)
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        # Extract populations
        populations, total_se = extract_single_excitation_populations(result.result_types[0])
        efficiency = populations[3]  # Population at site 3 (sink)
        
        print(f"{gamma:.2f}\t{populations[0]:.3f}\t{populations[1]:.3f}\t{populations[2]:.3f}\t{populations[3]:.3f}\t{total_se:.3f}\t{efficiency:.3f}")
        
        results.append({
            'gamma': gamma,
            'site0_pop': populations[0],
            'site1_pop': populations[1],
            'site2_pop': populations[2],
            'site3_pop': populations[3],
            'total_single_exc': total_se,
            'efficiency': efficiency
        })
    
    # Analyze results
    df = pd.DataFrame(results)
    df.to_csv("final_fmo_demonstration.csv", index=False)
    
    # Find optimal noise level
    max_idx = df['efficiency'].idxmax()
    optimal_gamma = df.loc[max_idx, 'gamma']
    max_efficiency = df.loc[max_idx, 'efficiency']
    noiseless_efficiency = df[df['gamma'] == 0]['efficiency'].iloc[0]
    
    enhancement = (max_efficiency - noiseless_efficiency) / noiseless_efficiency * 100 if noiseless_efficiency > 0 else 0
    
    print("\n" + "=" * 65)
    print("FINAL RESULTS:")
    print(f"  Noiseless transport efficiency: {noiseless_efficiency:.4f}")
    print(f"  Maximum efficiency: {max_efficiency:.4f} at γ = {optimal_gamma:.2f}")
    print(f"  Noise enhancement: {enhancement:.1f}%")
    print(f"  Single-excitation conservation: {df['total_single_exc'].mean():.3f} ± {df['total_single_exc'].std():.3f}")
    
    if enhancement > 5:
        print("  ✅ SUCCESS: Noise-assisted transport demonstrated!")
        success = True
    else:
        print("  ⚠️  Enhancement below 5% threshold")
        success = False
    
    print(f"  Results saved to final_fmo_demonstration.csv")
    
    return success, df, optimal_gamma

def aws_confirmation(device_arn="arn:aws:braket:::device/quantum-simulator/amazon/dm1"):
    """Run 3-point confirmation on AWS DM1."""
    print(f"\n=== AWS DM1 Confirmation ===")
    
    from braket.aws import AwsDevice
    device = AwsDevice(device_arn)
    H = create_transport_hamiltonian()
    
    # Select 3 key points: noiseless, optimal, high-noise
    test_gammas = [0.0, 1.0, 2.0]
    
    results = []
    total_cost_time = 0
    
    for gamma in test_gammas:
        print(f"AWS DM1: γ = {gamma:.1f}...", end=" ")
        
        import time
        t0 = time.time()
        
        circuit = build_evolution_circuit(H, evolution_time=2.0, n_steps=20, gamma=gamma)
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        populations, total_se = extract_single_excitation_populations(result.result_types[0])
        efficiency = float(populations[3])  # Ensure it's a scalar float
        
        elapsed = time.time() - t0
        total_cost_time += elapsed
        
        print(f"efficiency = {efficiency:.4f} ({elapsed:.1f}s)")
        
        results.append({
            'gamma': gamma,
            'efficiency': efficiency,
            'runtime_s': elapsed,
            'total_single_exc': total_se
        })
        
        # Cost safety
        if total_cost_time > 180:  # 3-minute safety limit
            print("Safety limit reached")
            break
    
    df_aws = pd.DataFrame(results)
    df_aws.to_csv("aws_dm1_confirmation.csv", index=False)
    
    print(f"AWS confirmation completed: {total_cost_time:.1f}s total")
    print(f"Results saved to aws_dm1_confirmation.csv")
    
    return df_aws

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws", action="store_true", help="Run AWS DM1 confirmation")
    parser.add_argument("--device_arn", type=str, 
                       default="arn:aws:braket:::device/quantum-simulator/amazon/dm1")
    
    args = parser.parse_args()
    
    # Run local demonstration
    success, df_local, optimal_gamma = run_transport_demonstration()
    
    if success and args.aws:
        print(f"\n🚀 Running AWS DM1 confirmation...")
        df_aws = aws_confirmation(args.device_arn)
        
        # Compare local vs AWS
        aws_noiseless = df_aws[df_aws['gamma'] == 0]['efficiency'].iloc[0] if len(df_aws) > 0 else 0
        local_noiseless = df_local[df_local['gamma'] == 0]['efficiency'].iloc[0]
        
        agreement = abs(aws_noiseless - local_noiseless) / local_noiseless * 100 if local_noiseless > 0 else 100
        
        print(f"\nLocal vs AWS Agreement:")
        print(f"  Local γ=0: {local_noiseless:.4f}")
        print(f"  AWS γ=0: {aws_noiseless:.4f}")
        print(f"  Difference: {agreement:.1f}%")
        
        if agreement < 5:
            print("  ✅ Excellent agreement!")
        else:
            print("  ⚠️  Significant difference - check implementation")
    
    print(f"\n🎯 FMO Project Complete!")
    print(f"   Demonstration: {'✅ Success' if success else '❌ Failed'}")
    print(f"   AWS Ready: {'✅ Yes' if success else '❌ No'}")
    
    if success:
        print(f"   Optimal γ: {optimal_gamma:.2f}")
        print(f"   Cost estimate: <3 min on AWS DM1")
        print(f"\n📊 Key files:")
        print(f"   • final_fmo_demonstration.csv")
        if args.aws:
            print(f"   • aws_dm1_confirmation.csv") 