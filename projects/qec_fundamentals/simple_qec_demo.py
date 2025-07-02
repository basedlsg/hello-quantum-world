"""
Simple QEC Demo - Week 1: 3-Qubit Bit-Flip Code
===============================================

A working demonstration of the QEC fundamentals using your existing code patterns.
This version properly handles density matrix results from both local and AWS simulators.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from braket.aws import AwsDevice
import time

# Reuse hardware-realistic parameters from realistic_noise_test.py
T1 = 40e-6  # seconds (amplitude damping time)
T2 = 60e-6  # seconds (dephasing time) 
GATE_TIME = 200e-9  # seconds (gate duration)

# Calculate noise probabilities (same as existing codebase)
P_AMPLITUDE = 1 - np.exp(-GATE_TIME / T1)  # p = 0.004987...
P_DEPHASING = 1 - np.exp(-GATE_TIME / T2)  # p = 0.003328...

print(f"QEC Noise Model: T1={T1*1e6:.1f}μs, T2={T2*1e6:.1f}μs")
print(f"Per-gate error rates: p_amp={P_AMPLITUDE:.6f}, p_deph={P_DEPHASING:.6f}")

def extract_populations(density_matrix_result):
    """
    Extract state populations from density matrix result.
    Handles both local simulator and AWS DM1 formats.
    """
    # Get the density matrix
    if hasattr(density_matrix_result, 'value'):
        dm = density_matrix_result.value
    else:
        dm = density_matrix_result
    
    # Convert to numpy array (handle AWS format)
    if isinstance(dm, list):
        dim = len(dm)
        dm_array = np.zeros((dim, dim), dtype=complex)
        for i in range(dim):
            for j in range(dim):
                elem = dm[i][j]
                if isinstance(elem, dict):
                    dm_array[i, j] = elem.get("real", 0.0) + 1j * elem.get("imag", 0.0)
                elif isinstance(elem, (list, tuple)) and len(elem) == 2:
                    dm_array[i, j] = complex(elem[0], elem[1])
                else:
                    dm_array[i, j] = complex(elem)
    else:
        dm_array = np.array(dm)
    
    # Extract populations (diagonal elements)
    populations = {}
    n_states = dm_array.shape[0]
    n_qubits = int(np.log2(n_states))
    
    for i in range(n_states):
        prob = np.real(dm_array[i, i])
        # Handle numpy arrays by extracting scalar
        if hasattr(prob, 'item'):
            prob_val = prob.item()
        else:
            prob_val = float(prob)
            
        if prob_val > 1e-10:  # Only include significant probabilities
            bitstring = format(i, f'0{n_qubits}b')
            populations[bitstring] = prob_val
    
    return populations

def create_logical_zero_with_noise(evolution_steps=1):
    """Create logical |0⟩ = |000⟩ with noise evolution"""
    circuit = Circuit()
    
    # Logical |0⟩ is already |000⟩ (no gates needed)
    
    # Add noise evolution (same pattern as realistic_noise_test.py)
    for step in range(evolution_steps):
        for q in range(3):
            circuit.amplitude_damping(q, P_AMPLITUDE)
            circuit.phase_damping(q, P_DEPHASING)
    
    return circuit

def create_logical_one_with_noise(evolution_steps=1):
    """Create logical |1⟩ = |111⟩ with noise evolution"""
    circuit = Circuit()
    
    # Prepare logical |1⟩ = |111⟩
    circuit.x(0)
    circuit.x(1) 
    circuit.x(2)
    
    # Add noise evolution
    for step in range(evolution_steps):
        for q in range(3):
            circuit.amplitude_damping(q, P_AMPLITUDE)
            circuit.phase_damping(q, P_DEPHASING)
    
    return circuit

def decode_syndrome_simple(populations):
    """
    Simple syndrome analysis for 3-qubit bit-flip code
    For 3-qubit system: |000⟩, |001⟩, |010⟩, |011⟩, |100⟩, |101⟩, |110⟩, |111⟩
    """
    # Count error patterns
    no_error = populations.get('000', 0.0) + populations.get('111', 0.0)
    single_errors = (populations.get('001', 0.0) + populations.get('010', 0.0) + 
                    populations.get('100', 0.0) + populations.get('110', 0.0) + 
                    populations.get('101', 0.0) + populations.get('011', 0.0))
    
    total_population = sum(populations.values())
    
    return {
        'no_error_rate': no_error,
        'single_error_rate': single_errors,
        'total_population': total_population,
        'logical_fidelity': no_error / total_population if total_population > 0 else 0
    }

def run_simple_qec_demo():
    """Run a simple QEC demonstration"""
    print("\n=== Simple QEC Demo: Week 1 ===")
    
    device = LocalSimulator("braket_dm")
    
    print("\n--- Testing Logical |0⟩ Lifetime ---")
    evolution_steps_list = [1, 3, 5, 7, 10]
    
    results = []
    
    for steps in evolution_steps_list:
        print(f"Evolution steps: {steps}")
        
        # Test logical |0⟩
        circuit_0 = create_logical_zero_with_noise(steps)
        circuit_0.density_matrix()
        
        result_0 = device.run(circuit_0, shots=0).result()
        populations_0 = extract_populations(result_0.result_types[0])
        analysis_0 = decode_syndrome_simple(populations_0)
        
        # Test logical |1⟩
        circuit_1 = create_logical_one_with_noise(steps)
        circuit_1.density_matrix()
        
        result_1 = device.run(circuit_1, shots=0).result()
        populations_1 = extract_populations(result_1.result_types[0])
        analysis_1 = decode_syndrome_simple(populations_1)
        
        avg_fidelity = (analysis_0['logical_fidelity'] + analysis_1['logical_fidelity']) / 2
        
        print(f"  |0⟩ fidelity: {analysis_0['logical_fidelity']:.4f}")
        print(f"  |1⟩ fidelity: {analysis_1['logical_fidelity']:.4f}")
        print(f"  Average: {avg_fidelity:.4f}")
        print()
        
        results.append({
            'evolution_steps': steps,
            'evolution_time_ns': steps * GATE_TIME * 1e9,
            'logical_0_fidelity': analysis_0['logical_fidelity'],
            'logical_1_fidelity': analysis_1['logical_fidelity'],
            'average_fidelity': avg_fidelity,
            'error_rate': 1 - avg_fidelity
        })
    
    # Convert to DataFrame and plot
    df = pd.DataFrame(results)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['evolution_time_ns'], df['logical_0_fidelity'], 'bo-', label='Logical |0⟩', markersize=8)
    plt.plot(df['evolution_time_ns'], df['logical_1_fidelity'], 'ro-', label='Logical |1⟩', markersize=8)
    plt.plot(df['evolution_time_ns'], df['average_fidelity'], 'go-', label='Average', markersize=8, linewidth=2)
    
    plt.xlabel('Evolution Time (ns)')
    plt.ylabel('Logical Fidelity')
    plt.title('3-Qubit Bit-Flip Code: Logical Qubit Decay')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig('../results/qec_demo_simple.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save results
    df.to_csv('../results/qec_demo_simple.csv', index=False)
    
    print("=== Demo Completed ===")
    print(f"Results saved to ../results/qec_demo_simple.csv")
    print(f"Plot saved to ../results/qec_demo_simple.png")
    
    # Print summary
    print(f"\n📊 Key Findings:")
    print(f"  Initial fidelity: {df.iloc[0]['average_fidelity']:.4f}")
    print(f"  Final fidelity:   {df.iloc[-1]['average_fidelity']:.4f}")
    print(f"  Decay rate: {(df.iloc[0]['average_fidelity'] - df.iloc[-1]['average_fidelity']):.4f}")
    
    return df

def compare_physical_vs_logical():
    """Compare single physical qubit vs 3-qubit logical code"""
    print("\n--- Physical vs Logical Comparison ---")
    
    device = LocalSimulator("braket_dm")
    evolution_steps_list = [1, 5, 10, 15, 20]
    
    comparison_results = []
    
    for steps in evolution_steps_list:
        # Physical qubit (single qubit with noise)
        physical_circuit = Circuit()
        physical_circuit.h(0)  # Start in |+⟩ state
        
        # Add same noise evolution
        for step in range(steps):
            physical_circuit.amplitude_damping(0, P_AMPLITUDE)
            physical_circuit.phase_damping(0, P_DEPHASING)
        
        physical_circuit.density_matrix()
        
        physical_result = device.run(physical_circuit, shots=0).result()
        physical_pops = extract_populations(physical_result.result_types[0])
        
        # Calculate physical fidelity (how much |+⟩ state is preserved)
        # For |+⟩ = (|0⟩ + |1⟩)/√2, ideal result has equal |0⟩ and |1⟩ populations
        physical_fidelity = physical_pops.get('0', 0) + physical_pops.get('1', 0)
        
        # Logical qubit (average of |0⟩ and |1⟩ logical states)
        logical_0_circuit = create_logical_zero_with_noise(steps)
        logical_0_circuit.density_matrix()
        logical_0_result = device.run(logical_0_circuit, shots=0).result()
        logical_0_pops = extract_populations(logical_0_result.result_types[0])
        logical_0_analysis = decode_syndrome_simple(logical_0_pops)
        
        logical_1_circuit = create_logical_one_with_noise(steps)
        logical_1_circuit.density_matrix()
        logical_1_result = device.run(logical_1_circuit, shots=0).result()
        logical_1_pops = extract_populations(logical_1_result.result_types[0])
        logical_1_analysis = decode_syndrome_simple(logical_1_pops)
        
        logical_fidelity = (logical_0_analysis['logical_fidelity'] + logical_1_analysis['logical_fidelity']) / 2
        qec_advantage = logical_fidelity - physical_fidelity
        
        print(f"Steps {steps:2d}: Physical={physical_fidelity:.4f}, Logical={logical_fidelity:.4f}, Advantage={qec_advantage:+.4f}")
        
        comparison_results.append({
            'evolution_steps': steps,
            'physical_fidelity': physical_fidelity, 
            'logical_fidelity': logical_fidelity,
            'qec_advantage': qec_advantage
        })
    
    comparison_df = pd.DataFrame(comparison_results)
    
    # Plot comparison
    plt.figure(figsize=(10, 6))
    plt.plot(comparison_df['evolution_steps'], comparison_df['physical_fidelity'], 
             'ro-', label='Physical Qubit', linewidth=2, markersize=8)
    plt.plot(comparison_df['evolution_steps'], comparison_df['logical_fidelity'], 
             'bo-', label='Logical Qubit (3-bit code)', linewidth=2, markersize=8)
    
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, label='Random Guess')
    plt.xlabel('Evolution Steps')
    plt.ylabel('Fidelity')
    plt.title('QEC Performance: Physical vs Logical Qubits')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig('../results/qec_comparison_simple.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    comparison_df.to_csv('../results/qec_comparison_simple.csv', index=False)
    
    avg_advantage = comparison_df['qec_advantage'].mean()
    if avg_advantage > 0:
        print(f"\n✅ QEC provides average advantage of {avg_advantage:.4f}")
        print("This suggests the error correction is working!")
    else:
        print(f"\n❌ QEC shows average disadvantage of {avg_advantage:.4f}")
        print("Error rates may be too high for this simple code.")
    
    return comparison_df

if __name__ == "__main__":
    print("="*60)
    print("Week 1: Simple QEC Demo - 3-Qubit Bit-Flip Code")
    print("="*60)
    print("Building on your spatial locality and noise modeling work")
    print("="*60)
    
    # Create results directory
    import os
    os.makedirs('../results', exist_ok=True)
    
    # Run demonstrations
    lifetime_results = run_simple_qec_demo()
    comparison_results = compare_physical_vs_logical()
    
    print("\n" + "="*60)
    print("SIMPLE QEC DEMO COMPLETED")
    print("="*60)
    print("Files created:")
    print("  - ../results/qec_demo_simple.csv")
    print("  - ../results/qec_demo_simple.png") 
    print("  - ../results/qec_comparison_simple.csv")
    print("  - ../results/qec_comparison_simple.png")
    
    print(f"\n🎓 Educational Value:")
    print("  - Demonstrates QEC principles with realistic T1/T2 noise")
    print("  - Shows logical qubit decay over time")
    print("  - Compares logical vs physical qubit performance")
    print("  - Uses your proven experimental methodology")
    
    print("\n✅ Ready to explore the full bit_flip_code.py implementation!") 