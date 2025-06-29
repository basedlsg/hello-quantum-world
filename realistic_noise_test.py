"""
Realistic T1/T2 Noise Model Test
Tests whether gate-count advantages persist under hardware-realistic noise:
- Amplitude damping (T1 = 40 μs) 
- Dephasing (T2 = 60 μs)
- Gate time = 200 ns
"""

import numpy as np
from braket.circuits import Circuit, noises
from braket.devices import LocalSimulator
import pandas as pd
from scipy.linalg import sqrtm

# Hardware-realistic parameters
T1 = 40e-6  # seconds (amplitude damping time)
T2 = 60e-6  # seconds (dephasing time) 
GATE_TIME = 200e-9  # seconds (gate duration)

def fidelity_robust(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Robust fidelity calculation compatible with noise simulations."""
    rho = rho / np.trace(rho)
    sigma = sigma / np.trace(sigma)
    
    if np.allclose(rho, sigma, atol=1e-6):
        return 1.0
    
    overlap = np.real(np.trace(rho @ sigma))
    return max(0.0, min(1.0, overlap))

def create_spatial_circuit_with_realistic_noise(n_qubits: int) -> Circuit:
    """Create spatial circuit with realistic T1/T2 noise after each gate."""
    circuit = Circuit()
    
    # Calculate noise probabilities per gate
    # p_amplitude = 1 - exp(-gate_time/T1)
    # p_dephasing = 1 - exp(-gate_time/T2) 
    p_amplitude = 1 - np.exp(-GATE_TIME / T1)
    p_dephasing = 1 - np.exp(-GATE_TIME / T2)
    
    # Initialize all qubits in superposition
    for i in range(n_qubits):
        circuit.h(i)
        # Add realistic noise after each gate
        circuit.amplitude_damping(i, p_amplitude)
        circuit.phase_damping(i, p_dephasing)
    
    # Create spatial correlations through nearest-neighbor gates
    for i in range(n_qubits - 1):
        circuit.cnot(i, i + 1)
        # Add noise to both qubits involved in CNOT
        circuit.amplitude_damping(i, p_amplitude)
        circuit.amplitude_damping(i + 1, p_amplitude)
        circuit.phase_damping(i, p_dephasing)
        circuit.phase_damping(i + 1, p_dephasing)
        
    return circuit

def create_nonspatial_circuit_with_realistic_noise(n_qubits: int) -> Circuit:
    """Create non-spatial circuit with realistic T1/T2 noise after each gate."""
    circuit = Circuit()
    
    p_amplitude = 1 - np.exp(-GATE_TIME / T1)
    p_dephasing = 1 - np.exp(-GATE_TIME / T2)
    
    # Initialize all qubits in superposition
    for i in range(n_qubits):
        circuit.h(i)
        circuit.amplitude_damping(i, p_amplitude)
        circuit.phase_damping(i, p_dephasing)
    
    # Create non-spatial correlations through long-range gates
    for i in range(n_qubits):
        for j in range(i + 2, n_qubits):  # Skip nearest neighbors
            circuit.cnot(i, j)
            # Add noise to both qubits
            circuit.amplitude_damping(i, p_amplitude)
            circuit.amplitude_damping(j, p_amplitude)
            circuit.phase_damping(i, p_dephasing)
            circuit.phase_damping(j, p_dephasing)
            
    return circuit

def create_ideal_circuit_spatial(n_qubits: int) -> Circuit:
    """Create ideal spatial circuit without noise."""
    circuit = Circuit()
    for i in range(n_qubits):
        circuit.h(i)
    for i in range(n_qubits - 1):
        circuit.cnot(i, i + 1)
    return circuit

def create_ideal_circuit_nonspatial(n_qubits: int) -> Circuit:
    """Create ideal non-spatial circuit without noise."""
    circuit = Circuit()
    for i in range(n_qubits):
        circuit.h(i)
    for i in range(n_qubits):
        for j in range(i + 2, n_qubits):
            circuit.cnot(i, j)
    return circuit

def run_realistic_noise_experiment():
    """Run the experiment with realistic T1/T2 noise models."""
    print("=== Realistic T1/T2 Noise Model Test ===")
    print(f"T1 = {T1*1e6:.1f} μs, T2 = {T2*1e6:.1f} μs, Gate time = {GATE_TIME*1e9:.0f} ns")
    
    device = LocalSimulator("braket_dm")
    results = []
    
    for n_qubits in range(2, 7):
        print(f"\n--- Testing {n_qubits} qubits ---")
        
        # Create ideal circuits
        ideal_spatial = create_ideal_circuit_spatial(n_qubits)
        ideal_nonspatial = create_ideal_circuit_nonspatial(n_qubits)
        
        # Create noisy circuits
        noisy_spatial = create_spatial_circuit_with_realistic_noise(n_qubits)
        noisy_nonspatial = create_nonspatial_circuit_with_realistic_noise(n_qubits)
        
        # Add density matrix measurement
        ideal_spatial.density_matrix()
        ideal_nonspatial.density_matrix()
        noisy_spatial.density_matrix()
        noisy_nonspatial.density_matrix()
        
        # Run simulations
        ideal_spatial_result = device.run(ideal_spatial, shots=0).result().values[0]
        ideal_nonspatial_result = device.run(ideal_nonspatial, shots=0).result().values[0]
        noisy_spatial_result = device.run(noisy_spatial, shots=0).result().values[0]
        noisy_nonspatial_result = device.run(noisy_nonspatial, shots=0).result().values[0]
        
        # Convert to numpy arrays and handle 3D format
        ideal_spatial_dm = np.array(ideal_spatial_result)
        ideal_nonspatial_dm = np.array(ideal_nonspatial_result)
        noisy_spatial_dm = np.array(noisy_spatial_result)
        noisy_nonspatial_dm = np.array(noisy_nonspatial_result)
        
        if ideal_spatial_dm.ndim == 3:
            ideal_spatial_dm = ideal_spatial_dm[:, :, 0]
        if ideal_nonspatial_dm.ndim == 3:
            ideal_nonspatial_dm = ideal_nonspatial_dm[:, :, 0]
        if noisy_spatial_dm.ndim == 3:
            noisy_spatial_dm = noisy_spatial_dm[:, :, 0]
        if noisy_nonspatial_dm.ndim == 3:
            noisy_nonspatial_dm = noisy_nonspatial_dm[:, :, 0]
        
        # Calculate fidelities
        spatial_fidelity = fidelity_robust(ideal_spatial_dm, noisy_spatial_dm)
        nonspatial_fidelity = fidelity_robust(ideal_nonspatial_dm, noisy_nonspatial_dm)
        
        print(f"Spatial fidelity: {spatial_fidelity:.6f}")
        print(f"Non-spatial fidelity: {nonspatial_fidelity:.6f}")
        print(f"Spatial advantage: {spatial_fidelity - nonspatial_fidelity:+.6f}")
        
        results.append({
            'n_qubits': n_qubits,
            'spatial_fidelity': spatial_fidelity,
            'nonspatial_fidelity': nonspatial_fidelity,
            'spatial_advantage': spatial_fidelity - nonspatial_fidelity
        })
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv('results/realistic_noise_test.csv', index=False)
    print("\nResults saved to results/realistic_noise_test.csv")
    
    # Analysis
    print("\n=== ANALYSIS: Realistic Noise vs Depolarizing ===")
    print("Spatial advantage by qubit count:")
    for result in results:
        n = result['n_qubits']
        adv = result['spatial_advantage']
        print(f"  {n} qubits: {adv:+.6f}")
    
    print("\n*** INTERPRETATION ***")
    print("Compare these results to our depolarizing noise results.")
    print("If the spatial advantage pattern changes significantly,")
    print("our findings are noise-model dependent, not universal.")

if __name__ == "__main__":
    run_realistic_noise_experiment() 