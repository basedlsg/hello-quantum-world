"""
Minimal FMO 4-Site Proof-of-Concept

This version focuses on getting the basic physics right with a simple implementation.
We'll use a much smaller Hamiltonian and shorter evolution to ensure we can see the dynamics.
"""

import numpy as np
import pandas as pd
from braket.circuits import Circuit
from braket.devices import LocalSimulator

def create_simple_fmo_hamiltonian():
    """Create a simplified FMO-like Hamiltonian with smaller energy scales."""
    # Simplified 4-site system with smaller energies for clearer dynamics
    # Units: arbitrary (will be scaled for reasonable circuit depths)
    H = np.array([
        [0.0,  0.1,  0.02, 0.01],   # Site 0 (start)
        [0.1,  0.05, 0.08, 0.03],   # Site 1
        [0.02, 0.08, 0.03, 0.15],   # Site 2 
        [0.01, 0.03, 0.15, 0.0]     # Site 3 (target sink)
    ])
    return H

def build_minimal_circuit(H, evolution_time=0.5, n_steps=10):
    """Build a minimal circuit for single-excitation evolution."""
    circuit = Circuit()
    
    # Start with excitation on site 0 (qubit 0)
    circuit.x(0)
    
    dt = evolution_time / n_steps
    
    # Very simple Trotter evolution
    for step in range(n_steps):
        # Diagonal terms (site energies)
        for i in range(4):
            theta = -H[i, i] * dt
            circuit.rz(i, theta)
        
        # Off-diagonal terms - use a simple approach
        # For small angles, we can approximate the hopping with basic rotations
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(H[i, j]) > 1e-6:
                    # Simple hopping approximation using controlled gates
                    theta = H[i, j] * dt
                    if abs(theta) < 0.3:  # Keep angles small
                        # Implement |i⟩⟨j| + |j⟩⟨i| interaction
                        # Use CNOT + RY to create controlled transitions
                        circuit.cnot(i, j)
                        circuit.ry(j, 2 * theta)
                        circuit.cnot(i, j)
    
    return circuit

def analyze_populations(density_matrix):
    """Analyze the population distribution."""
    dm = np.array(density_matrix.value if hasattr(density_matrix, 'value') else density_matrix)
    
    populations = {}
    total_single_excitation = 0
    
    print("State populations:")
    for i in range(16):  # 2^4 states
        pop = np.real(dm[i, i])
        if pop > 1e-6:
            state_str = format(i, '04b')
            print(f"  |{state_str}⟩: {pop:.4f}")
            
            # Count single-excitation states
            n_excitations = bin(i).count('1')
            if n_excitations == 1:
                total_single_excitation += pop
                qubit_excited = int(np.log2(i))  # Which qubit is excited
                populations[qubit_excited] = pop
    
    print(f"\nSingle-excitation subspace population: {total_single_excitation:.4f}")
    print("Individual site populations:")
    for site in range(4):
        pop = populations.get(site, 0.0)
        print(f"  Site {site}: {pop:.4f}")
    
    return populations

def test_minimal_evolution():
    """Test the minimal evolution approach."""
    print("=== Minimal FMO Evolution Test ===")
    
    H = create_simple_fmo_hamiltonian()
    print("Simplified Hamiltonian:")
    print(H)
    print()
    
    device = LocalSimulator("braket_dm")
    
    # Test different evolution times
    evolution_times = [0.1, 0.5, 1.0, 2.0]
    
    results = []
    
    for t in evolution_times:
        print(f"--- Evolution time: {t:.1f} ---")
        
        circuit = build_minimal_circuit(H, evolution_time=t, n_steps=20)
        circuit.density_matrix()
        
        print(f"Circuit depth: {circuit.depth}")
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        populations = analyze_populations(result.result_types[0])
        
        # Calculate efficiency (population at site 3)
        efficiency = populations.get(3, 0.0)
        print(f"Transport efficiency to site 3: {efficiency:.4f}")
        print()
        
        results.append({
            'evolution_time': t,
            'efficiency_site3': efficiency,
            'population_site0': populations.get(0, 0.0),
            'population_site1': populations.get(1, 0.0),
            'population_site2': populations.get(2, 0.0),
        })
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv("minimal_evolution_test.csv", index=False)
    print("Results saved to minimal_evolution_test.csv")
    
    return df

def test_with_noise():
    """Test the same evolution with added dephasing noise."""
    print("\n=== Testing with Dephasing Noise ===")
    
    H = create_simple_fmo_hamiltonian()
    device = LocalSimulator("braket_dm")
    
    # Fixed evolution time
    t_evolution = 1.0
    gamma_values = [0.0, 1.0, 2.0, 5.0, 10.0]  # Dephasing rates
    
    results = []
    
    for gamma in gamma_values:
        print(f"--- Dephasing rate γ = {gamma:.1f} ---")
        
        circuit = build_minimal_circuit(H, evolution_time=t_evolution, n_steps=20)
        
        # Add dephasing noise
        if gamma > 0:
            # Simple uniform dephasing
            dephase_p = 1 - np.exp(-gamma * 0.05)  # dt = 0.05
            for q in range(4):
                circuit.phase_damping(q, dephase_p)
        
        circuit.density_matrix()
        
        task = device.run(circuit, shots=0)
        result = task.result()
        
        populations = analyze_populations(result.result_types[0])
        efficiency = populations.get(3, 0.0)
        
        print(f"Efficiency with γ = {gamma:.1f}: {efficiency:.4f}")
        print()
        
        results.append({
            'gamma': gamma,
            'efficiency': efficiency
        })
    
    df = pd.DataFrame(results)
    df.to_csv("noise_test_results.csv", index=False)
    print("Noise test results saved to noise_test_results.csv")
    
    return df

if __name__ == "__main__":
    # Test basic evolution
    df1 = test_minimal_evolution()
    
    # Test with noise
    df2 = test_with_noise()
    
    print("\n=== Summary ===")
    print("Basic evolution - efficiency vs time:")
    for _, row in df1.iterrows():
        print(f"  t={row['evolution_time']:.1f}: efficiency={row['efficiency_site3']:.3f}")
    
    print("\nWith noise - efficiency vs gamma:")
    for _, row in df2.iterrows():
        print(f"  γ={row['gamma']:.1f}: efficiency={row['efficiency']:.3f}")
    
    # Check for noise-assisted transport
    max_eff_idx = df2['efficiency'].idxmax()
    max_gamma = df2.loc[max_eff_idx, 'gamma']
    max_eff = df2.loc[max_eff_idx, 'efficiency']
    noiseless_eff = df2[df2['gamma'] == 0]['efficiency'].iloc[0]
    
    enhancement = (max_eff - noiseless_eff) / noiseless_eff * 100 if noiseless_eff > 0 else 0
    
    print(f"\nNoise-assisted transport analysis:")
    print(f"  Noiseless efficiency: {noiseless_eff:.3f}")
    print(f"  Maximum efficiency: {max_eff:.3f} at γ = {max_gamma:.1f}")
    print(f"  Enhancement: {enhancement:.1f}%")
    
    if enhancement > 5:
        print("  ✅ Noise-assisted transport observed!")
    else:
        print("  ⚠️  No significant noise enhancement") 