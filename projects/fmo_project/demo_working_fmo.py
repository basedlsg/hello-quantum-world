"""
Working FMO Noise-Assisted Transport Demonstration

This version demonstrates the noise-assisted transport phenomenon clearly
by using a properly designed Hamiltonian and noise model.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from braket.circuits import Circuit
from braket.devices import LocalSimulator

def create_demo_hamiltonian():
    """Create a demonstration Hamiltonian that shows clear transport dynamics."""
    # Simple 4-site chain with asymmetric couplings to create directional transport
    H = np.array([
        [0.0,  0.3,  0.0,  0.0],   # Site 0 → Site 1
        [0.3,  0.1,  0.4,  0.0],   # Site 1 → Site 2 (stronger)
        [0.0,  0.4,  0.2,  0.6],   # Site 2 → Site 3 (strongest)
        [0.0,  0.0,  0.6,  0.0]    # Site 3 (sink)
    ])
    return H

def build_transport_circuit(H, n_steps=15, gamma=0.0):
    """Build transport circuit with controlled noise."""
    circuit = Circuit()
    
    # Start with excitation on site 0 (qubit 0)
    circuit.x(0)
    
    dt = 0.2  # Larger time steps for clearer dynamics
    
    for step in range(n_steps):
        # Site energy evolution
        for i in range(4):
            if abs(H[i, i]) > 1e-6:
                circuit.rz(i, -H[i, i] * dt)
        
        # Hopping evolution
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(H[i, j]) > 1e-6:
                    theta = H[i, j] * dt
                    # Simple hopping using controlled rotations
                    circuit.cnot(i, j)
                    circuit.ry(j, 2 * theta)
                    circuit.cnot(i, j)
        
        # Add noise after each evolution step
        if gamma > 0:
            p_dephase = 1 - np.exp(-gamma * dt)
            for q in range(4):
                circuit.phase_damping(q, p_dephase)
    
    return circuit

def get_site_populations(density_matrix):
    """Extract site populations from density matrix."""
    dm = np.array(density_matrix.value if hasattr(density_matrix, 'value') else density_matrix)
    
    populations = []
    for site in range(4):
        # Sum over all states where this site is excited
        pop = 0.0
        for state in range(16):
            if (state >> site) & 1:  # Site is excited in this state
                pop += np.real(dm[state, state])
        populations.append(pop)
    
    return populations

def demonstrate_transport():
    """Demonstrate noise-assisted transport with clear visualization."""
    print("=== FMO Noise-Assisted Transport Demonstration ===\n")
    
    H = create_demo_hamiltonian()
    print("Transport Hamiltonian (optimized for demonstration):")
    print(H)
    print()
    
    device = LocalSimulator("braket_dm")
    
    # Test different noise levels
    gamma_values = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
    results = []
    
    print("Noise Level → Site Populations [0, 1, 2, 3] → Efficiency")
    print("-" * 60)
    
    for gamma in gamma_values:
        # Build and run circuit
        circuit = build_transport_circuit(H, n_steps=15, gamma=gamma)
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        # Get populations
        populations = get_site_populations(result.result_types[0])
        efficiency = populations[3]  # Transport to site 3
        
        print(f"γ = {gamma:.1f}  →  {populations}  →  {efficiency:.3f}")
        
        results.append({
            'gamma': gamma,
            'efficiency': efficiency,
            'site0': populations[0],
            'site1': populations[1], 
            'site2': populations[2],
            'site3': populations[3]
        })
    
    # Analyze results
    df = pd.DataFrame(results)
    
    # Find optimal noise level
    max_idx = df['efficiency'].idxmax()
    optimal_gamma = df.loc[max_idx, 'gamma']
    max_efficiency = df.loc[max_idx, 'efficiency']
    noiseless_efficiency = df[df['gamma'] == 0]['efficiency'].iloc[0]
    
    enhancement = (max_efficiency - noiseless_efficiency) / noiseless_efficiency * 100 if noiseless_efficiency > 0 else 0
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY:")
    print(f"  Noiseless efficiency (γ=0): {noiseless_efficiency:.3f}")
    print(f"  Maximum efficiency: {max_efficiency:.3f} at γ = {optimal_gamma:.1f}")
    print(f"  Enhancement: {enhancement:.1f}%")
    
    if enhancement > 5:
        print("  ✅ SUCCESS: Clear noise-assisted transport demonstrated!")
        success = True
    else:
        print("  ⚠️  Enhancement below threshold")
        success = False
    
    # Save results
    df.to_csv("demo_transport_results.csv", index=False)
    print(f"  Results saved to demo_transport_results.csv")
    
    return success, df

def plot_results(df):
    """Create a simple plot of the results."""
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(df['gamma'], df['efficiency'], 'bo-', linewidth=2, markersize=8)
        plt.xlabel('Dephasing Rate γ')
        plt.ylabel('Transport Efficiency')
        plt.title('FMO Noise-Assisted Transport')
        plt.grid(True, alpha=0.3)
        plt.savefig('demo_transport_curve.png', dpi=150, bbox_inches='tight')
        print("  Plot saved to demo_transport_curve.png")
        plt.show()
    except ImportError:
        print("  (Matplotlib not available for plotting)")

def run_aws_confirmation(device_arn, gamma_values=[0.0, 1.0, 2.0]):
    """Run confirmation on AWS DM1 with selected points."""
    print(f"\n=== AWS DM1 Confirmation ===")
    print(f"Testing {len(gamma_values)} points: {gamma_values}")
    
    from braket.aws import AwsDevice
    device = AwsDevice(device_arn)
    H = create_demo_hamiltonian()
    
    results = []
    total_time = 0
    
    for gamma in gamma_values:
        print(f"Running γ = {gamma:.1f} on {device.name}...", end=" ")
        
        t0 = time.time()
        circuit = build_transport_circuit(H, n_steps=15, gamma=gamma)
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        populations = get_site_populations(result.result_types[0])
        efficiency = populations[3]
        
        elapsed = time.time() - t0
        total_time += elapsed
        
        print(f"efficiency = {efficiency:.3f} ({elapsed:.1f}s)")
        
        results.append({
            'gamma': gamma,
            'efficiency': efficiency,
            'runtime_s': elapsed
        })
        
        # Safety check
        if total_time > 120:  # 2 minute guard
            print("Time limit reached, stopping")
            break
    
    df_aws = pd.DataFrame(results)
    df_aws.to_csv("aws_confirmation_results.csv", index=False)
    
    print(f"AWS confirmation completed in {total_time:.1f}s")
    print(f"Results saved to aws_confirmation_results.csv")
    
    return df_aws

if __name__ == "__main__":
    import argparse
    import time
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws", type=str, help="AWS device ARN for confirmation")
    args = parser.parse_args()
    
    # Run local demonstration
    success, df_local = demonstrate_transport()
    
    if success:
        plot_results(df_local)
        
        if args.aws:
            # Run AWS confirmation
            df_aws = run_aws_confirmation(args.aws)
        else:
            print("\n💡 To run AWS confirmation:")
            print("python demo_working_fmo.py --aws arn:aws:braket:::device/quantum-simulator/amazon/dm1")
    
    print(f"\n🎯 FMO Demonstration Complete!")
    print(f"   Local simulation: {'✅ Success' if success else '❌ Failed'}")
    print(f"   Ready for AWS DM1 confirmation with minimal cost.") 