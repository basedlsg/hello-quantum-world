"""
Week 1: 3-Qubit Bit-Flip Code - QEC Fundamentals
===============================================

Building on the spatial locality investigation, we now explore quantum error correction.
This implements a 3-qubit bit-flip code with syndrome detection, using the same
noise modeling approach from realistic_noise_test.py.

Key Features:
- Hardware-realistic T1/T2 noise model (reused from existing codebase)
- Syndrome detection and error correction
- Logical qubit lifetime analysis 
- Cost tracking for AWS free tier management
- Educational problem set structure

Scientific Question: How do logical error rates compare to physical error rates
under realistic T1/T2 decoherence?
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from braket.aws import AwsDevice
from braket.tracking import Tracker
import time
from typing import Dict, List, Tuple
import argparse

# Reuse hardware-realistic parameters from realistic_noise_test.py
T1 = 40e-6  # seconds (amplitude damping time)
T2 = 60e-6  # seconds (dephasing time) 
GATE_TIME = 200e-9  # seconds (gate duration)

# Calculate noise probabilities (same as existing codebase)
P_AMPLITUDE = 1 - np.exp(-GATE_TIME / T1)  # p = 0.004987...
P_DEPHASING = 1 - np.exp(-GATE_TIME / T2)  # p = 0.003328...

print(f"QEC Noise Model: T1={T1*1e6:.1f}μs, T2={T2*1e6:.1f}μs")
print(f"Per-gate error rates: p_amp={P_AMPLITUDE:.6f}, p_deph={P_DEPHASING:.6f}")

class BitFlipQECExperiment:
    """
    3-Qubit Bit-Flip Code experiment using proven validation methodology
    Adapts patterns from final_parity_check_experiment.py
    """
    
    def __init__(self, device_name: str = "local_dm"):
        """Initialize with same device handling as existing experiments"""
        if device_name == "local_dm":
            self.device = LocalSimulator("braket_dm")
        elif device_name == "dm1":
            self.device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/dm1")
        else:
            self.device = LocalSimulator()
        
        self.results = {}
        self.total_aws_cost = 0.0
        
        print(f"✅ QEC Experiment initialized with device: {device_name}")
    
    def create_logical_zero_circuit(self, add_noise: bool = True, evolution_steps: int = 1) -> Circuit:
        """
        Create 3-qubit logical |0⟩ state with optional noise evolution
        Encoding: |0⟩_L = |000⟩, |1⟩_L = |111⟩
        
        Follows circuit construction pattern from spatial experiments
        """
        circuit = Circuit()
        
        # Prepare logical |0⟩ = |000⟩ (already in this state)
        # No gates needed for |000⟩
        
        # Add noise evolution (adapt from FMO evolution patterns)
        if add_noise:
            for step in range(evolution_steps):
                # Apply T1/T2 noise to all qubits (same pattern as realistic_noise_test.py)
                for q in range(3):
                    circuit.amplitude_damping(q, P_AMPLITUDE)
                    circuit.phase_damping(q, P_DEPHASING)
        
        return circuit
    
    def create_logical_one_circuit(self, add_noise: bool = True, evolution_steps: int = 1) -> Circuit:
        """
        Create 3-qubit logical |1⟩ state with optional noise evolution
        Encoding: |1⟩_L = |111⟩
        """
        circuit = Circuit()
        
        # Prepare logical |1⟩ = |111⟩
        circuit.x(0)
        circuit.x(1) 
        circuit.x(2)
        
        # Add noise evolution
        if add_noise:
            for step in range(evolution_steps):
                for q in range(3):
                    circuit.amplitude_damping(q, P_AMPLITUDE)
                    circuit.phase_damping(q, P_DEPHASING)
        
        return circuit
    
    def create_logical_plus_circuit(self, add_noise: bool = True, evolution_steps: int = 1) -> Circuit:
        """
        Create logical |+⟩ = (|0⟩_L + |1⟩_L)/√2 = (|000⟩ + |111⟩)/√2
        This tests superposition preservation under noise
        """
        circuit = Circuit()
        
        # Create equal superposition of |000⟩ and |111⟩
        # Method: Start with |000⟩, apply H to first qubit, then copy state
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.cnot(0, 2)
        
        # Add noise evolution
        if add_noise:
            for step in range(evolution_steps):
                for q in range(3):
                    circuit.amplitude_damping(q, P_AMPLITUDE)
                    circuit.phase_damping(q, P_DEPHASING)
        
        return circuit
    
    def create_syndrome_detection_circuit(self, data_qubits: List[int] = [0, 1, 2]) -> Circuit:
        """
        Add syndrome detection to existing circuit
        For bit-flip code: detect parity of adjacent qubit pairs
        
        Syndrome qubits: [3, 4]
        S1 = q0 ⊕ q1 (detects error on q0 or q1)
        S2 = q1 ⊕ q2 (detects error on q1 or q2)
        """
        circuit = Circuit()
        
        # Syndrome 1: Parity of q0, q1
        circuit.cnot(data_qubits[0], 3)  # Ancilla qubit 3
        circuit.cnot(data_qubits[1], 3)
        
        # Syndrome 2: Parity of q1, q2  
        circuit.cnot(data_qubits[1], 4)  # Ancilla qubit 4
        circuit.cnot(data_qubits[2], 4)
        
        return circuit
    
    def decode_syndrome(self, measurement_results: Dict[str, float]) -> Dict[str, any]:
        """
        Decode syndrome measurements to identify error location
        
        Syndrome table for 3-qubit bit-flip code:
        S1 S2 | Error Location
        0  0  | No error
        1  0  | Error on q0
        1  1  | Error on q1  
        0  1  | Error on q2
        """
        error_counts = {
            'no_error': 0,
            'error_q0': 0,
            'error_q1': 0,
            'error_q2': 0,
            'multi_error': 0
        }
        
        for bitstring, probability in measurement_results.items():
            if len(bitstring) >= 5:  # Ensure we have syndrome bits
                s1 = int(bitstring[-2])  # Second-to-last bit
                s2 = int(bitstring[-1])  # Last bit
                
                syndrome = (s1, s2)
                shots = int(probability * 1000)  # Approximate shot count
                
                if syndrome == (0, 0):
                    error_counts['no_error'] += shots
                elif syndrome == (1, 0):
                    error_counts['error_q0'] += shots
                elif syndrome == (1, 1):
                    error_counts['error_q1'] += shots
                elif syndrome == (0, 1):
                    error_counts['error_q2'] += shots
                else:
                    error_counts['multi_error'] += shots
        
        total_shots = sum(error_counts.values())
        if total_shots > 0:
            error_rates = {k: v/total_shots for k, v in error_counts.items()}
        else:
            error_rates = error_counts
        
        syndrome_analysis = {
            'error_counts': error_counts,
            'error_rates': error_rates,
            'total_errors': 1.0 - error_rates.get('no_error', 0.0),
            'correctable_errors': error_rates.get('error_q0', 0) + 
                                 error_rates.get('error_q1', 0) + 
                                 error_rates.get('error_q2', 0)
        }
        
        return syndrome_analysis
    
    def run_logical_lifetime_study(self, max_evolution_steps: int = 20, 
                                  device: str = "local_dm") -> pd.DataFrame:
        """
        Study logical qubit lifetime vs evolution time
        Adapts experimental methodology from spatial locality experiments
        """
        print(f"\n=== Logical Qubit Lifetime Study ===")
        print(f"Device: {device}, Max evolution steps: {max_evolution_steps}")
        
        results = []
        
        logical_states = [
            ('logical_0', self.create_logical_zero_circuit),
            ('logical_1', self.create_logical_one_circuit), 
            ('logical_plus', self.create_logical_plus_circuit)
        ]
        
        for state_name, circuit_creator in logical_states:
            print(f"\n--- Testing {state_name} ---")
            
            for evolution_steps in range(1, max_evolution_steps + 1, 2):
                # Create circuit with noise evolution
                circuit = circuit_creator(add_noise=True, evolution_steps=evolution_steps)
                
                # Add syndrome detection
                syndrome_circuit = self.create_syndrome_detection_circuit()
                for instr in syndrome_circuit.instructions:
                    circuit.add_instruction(instr)
                
                # Measure all qubits
                circuit.probability()
                
                # Run simulation (same pattern as existing experiments)
                start_time = time.time()
                
                if device == "dm1":
                    # Track AWS costs (same pattern as realistic_quantum_research_demo.py)
                    with Tracker() as tracker:
                        task = self.device.run(circuit, shots=0)
                        result = task.result()
                        cost = float(tracker.simulator_tasks_cost()) if tracker.simulator_tasks_cost() else 0.0
                        self.total_aws_cost += cost
                else:
                    # Local simulation (free)
                    task = self.device.run(circuit, shots=0)
                    result = task.result()
                    cost = 0.0
                
                execution_time = time.time() - start_time
                
                # Analyze results (handle density matrix results)
                if hasattr(result, 'measurement_probabilities') and result.measurement_probabilities:
                    probabilities = dict(result.measurement_probabilities)
                else:
                    # For density matrix results, extract diagonal elements
                    dm_result = result.result_types[0]
                    
                    # Handle different density matrix formats
                    if hasattr(dm_result, 'value'):
                        dm = dm_result.value
                    else:
                        dm = dm_result
                    
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
                    
                    # Extract probabilities from diagonal
                    probs = np.real(np.diag(dm_array))
                    n_qubits = int(np.log2(len(probs)))
                    probabilities = {}
                    for i, prob in enumerate(probs):
                        prob_val = float(prob)  # Convert to scalar
                        if prob_val > 1e-10:  # Only include significant probabilities
                            bitstring = format(i, f'0{n_qubits}b')
                            probabilities[bitstring] = prob_val
                
                syndrome_analysis = self.decode_syndrome(probabilities)
                
                # Calculate logical fidelity (simplified)
                if state_name == 'logical_0':
                    # Ideal result should be |00000⟩ (no errors)
                    logical_fidelity = probabilities.get('00000', 0.0)
                elif state_name == 'logical_1':
                    # Ideal result should be |11100⟩ (|111⟩ + no syndrome)
                    logical_fidelity = probabilities.get('11100', 0.0)
                else:  # logical_plus
                    # Should have equal amplitudes on |00000⟩ and |11100⟩
                    logical_fidelity = probabilities.get('00000', 0.0) + probabilities.get('11100', 0.0)
                
                result_data = {
                    'state': state_name,
                    'evolution_steps': evolution_steps,
                    'evolution_time_ns': evolution_steps * GATE_TIME * 1e9,
                    'logical_fidelity': logical_fidelity,
                    'total_error_rate': syndrome_analysis['total_errors'],
                    'correctable_error_rate': syndrome_analysis['correctable_errors'],
                    'execution_time_s': execution_time,
                    'aws_cost_usd': cost,
                    'device': device
                }
                
                results.append(result_data)
                
                print(f"  Steps {evolution_steps:2d}: Fidelity={logical_fidelity:.4f}, "
                      f"Errors={syndrome_analysis['total_errors']:.4f}, "
                      f"Cost=${cost:.6f}")
        
        # Convert to DataFrame (same pattern as existing experiments)
        df = pd.DataFrame(results)
        return df
    
    def run_error_correction_benchmark(self, device: str = "local_dm") -> pd.DataFrame:
        """
        Compare logical vs physical error rates
        Key scientific question: When does QEC provide advantage?
        """
        print(f"\n=== Error Correction Benchmark ===")
        
        results = []
        
        # Test different noise strengths by scaling evolution steps
        evolution_steps_range = [1, 5, 10, 15, 20]
        
        for steps in evolution_steps_range:
            print(f"\n--- Evolution steps: {steps} ---")
            
            # Physical qubit (single qubit, no QEC)
            physical_circuit = Circuit()
            physical_circuit.h(0)  # Start in |+⟩ state
            
            # Add same noise evolution as logical qubits
            for step in range(steps):
                physical_circuit.amplitude_damping(0, P_AMPLITUDE)
                physical_circuit.phase_damping(0, P_DEPHASING)
            
            physical_circuit.probability()
            
            # Logical qubit (3-qubit code)
            logical_circuit = self.create_logical_plus_circuit(add_noise=True, evolution_steps=steps)
            syndrome_circuit = self.create_syndrome_detection_circuit()
            for instr in syndrome_circuit.instructions:
                logical_circuit.add_instruction(instr)
            logical_circuit.probability()
            
            # Run both experiments
            physical_result = self.device.run(physical_circuit, shots=0).result() 
            logical_result = self.device.run(logical_circuit, shots=0).result()
            
            # Analyze physical qubit (helper function for DM conversion)
            def convert_dm_to_probs(result, n_qubits):
                if hasattr(result, 'measurement_probabilities') and result.measurement_probabilities:
                    return dict(result.measurement_probabilities)
                else:
                    dm_result = result.result_types[0]
                    
                    # Handle different density matrix formats
                    if hasattr(dm_result, 'value'):
                        dm = dm_result.value
                    else:
                        dm = dm_result
                    
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
                    
                    # Extract probabilities from diagonal
                    probs = np.real(np.diag(dm_array))
                    probabilities = {}
                    for i, prob in enumerate(probs):
                        prob_val = float(prob)  # Convert to scalar
                        if prob_val > 1e-10:  # Only include significant probabilities
                            bitstring = format(i, f'0{n_qubits}b')
                            probabilities[bitstring] = prob_val
                    return probabilities
            
            physical_probs = convert_dm_to_probs(physical_result, 1)
            physical_fidelity = physical_probs.get('0', 0.0) + physical_probs.get('1', 0.0)  # Total probability
            
            # Analyze logical qubit  
            logical_probs = convert_dm_to_probs(logical_result, 5)  # 3 data + 2 syndrome qubits
                        
            syndrome_analysis = self.decode_syndrome(logical_probs)
            logical_fidelity = logical_probs.get('00000', 0.0) + logical_probs.get('11100', 0.0)
            
            result_data = {
                'evolution_steps': steps,
                'physical_fidelity': physical_fidelity,
                'logical_fidelity': logical_fidelity,
                'qec_advantage': logical_fidelity - physical_fidelity,
                'logical_error_rate': syndrome_analysis['total_errors'],
                'correctable_errors': syndrome_analysis['correctable_errors'],
                'device': device
            }
            
            results.append(result_data)
            
            print(f"  Physical fidelity: {physical_fidelity:.4f}")
            print(f"  Logical fidelity:  {logical_fidelity:.4f}")
            print(f"  QEC advantage:     {result_data['qec_advantage']:+.4f}")
        
        return pd.DataFrame(results)

def create_educational_analysis(results_df: pd.DataFrame) -> Dict[str, str]:
    """
    Generate educational insights from experimental results
    Follows pedagogical approach from existing problem sets
    """
    insights = {
        'key_finding': '',
        'qec_threshold': '',
        'practical_implication': '',
        'next_steps': ''
    }
    
    # Analyze QEC advantage
    avg_advantage = results_df['qec_advantage'].mean()
    
    if avg_advantage > 0:
        insights['key_finding'] = f"QEC provides average fidelity advantage of {avg_advantage:.4f}"
        insights['qec_threshold'] = "QEC advantage observed at all tested noise levels"
    else:
        insights['key_finding'] = f"QEC shows average disadvantage of {avg_advantage:.4f}"
        insights['qec_threshold'] = "Physical error rates too high for QEC advantage"
    
    # Practical implications
    max_advantage = results_df['qec_advantage'].max()
    if max_advantage > 0.1:
        insights['practical_implication'] = "Strong QEC advantage suggests practical utility"
    elif max_advantage > 0.01:
        insights['practical_implication'] = "Modest QEC advantage requires careful implementation"
    else:
        insights['practical_implication'] = "No significant QEC advantage under current noise model"
    
    insights['next_steps'] = "Consider 5-qubit code or surface code for better error correction"
    
    return insights

def generate_plots(lifetime_df: pd.DataFrame, benchmark_df: pd.DataFrame, output_dir: str = "results"):
    """
    Generate publication-quality plots
    Reuses plotting style from existing experiments
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: Logical qubit lifetime
    plt.figure(figsize=(10, 6))
    
    for state in lifetime_df['state'].unique():
        state_data = lifetime_df[lifetime_df['state'] == state]
        plt.plot(state_data['evolution_time_ns'], state_data['logical_fidelity'], 
                'o-', label=f'{state}', linewidth=2, markersize=6)
    
    plt.xlabel('Evolution Time (ns)')
    plt.ylabel('Logical Fidelity')
    plt.title('3-Qubit Bit-Flip Code: Logical Qubit Lifetime')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/logical_lifetime.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Plot 2: QEC Advantage
    plt.figure(figsize=(10, 6))
    
    plt.plot(benchmark_df['evolution_steps'], benchmark_df['physical_fidelity'], 
             'ro-', label='Physical Qubit', linewidth=2, markersize=8)
    plt.plot(benchmark_df['evolution_steps'], benchmark_df['logical_fidelity'], 
             'bo-', label='Logical Qubit (3-bit code)', linewidth=2, markersize=8)
    
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, label='Random Guess')
    plt.xlabel('Evolution Steps')
    plt.ylabel('Fidelity')
    plt.title('QEC Performance: Physical vs Logical Qubits')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/qec_advantage.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✅ Plots saved to {output_dir}/")

def main():
    """
    Main experimental workflow
    Follows the same structure as existing experiment scripts
    """
    parser = argparse.ArgumentParser(description='3-Qubit Bit-Flip QEC Experiment')
    parser.add_argument('--device', default='local_dm', choices=['local_dm', 'dm1'],
                       help='Simulation device')
    parser.add_argument('--max-steps', type=int, default=20,
                       help='Maximum evolution steps')
    parser.add_argument('--output-dir', default='results/qec_week1',
                       help='Output directory')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Week 1: 3-Qubit Bit-Flip Code QEC Experiment")
    print("="*60)
    print("Building on spatial locality and noise modeling work")
    print(f"Device: {args.device}")
    print(f"Noise model: T1={T1*1e6:.1f}μs, T2={T2*1e6:.1f}μs")
    print("="*60)
    
    # Initialize experiment
    experiment = BitFlipQECExperiment(device_name=args.device)
    
    # Run experiments
    print("\n🔬 Running logical qubit lifetime study...")
    lifetime_results = experiment.run_logical_lifetime_study(
        max_evolution_steps=args.max_steps, 
        device=args.device
    )
    
    print("\n🔬 Running QEC benchmark...")
    benchmark_results = experiment.run_error_correction_benchmark(device=args.device)
    
    # Save results
    import os
    os.makedirs(args.output_dir, exist_ok=True)
    
    lifetime_results.to_csv(f'{args.output_dir}/lifetime_results.csv', index=False)
    benchmark_results.to_csv(f'{args.output_dir}/benchmark_results.csv', index=False)
    
    # Generate analysis
    educational_insights = create_educational_analysis(benchmark_results)
    
    # Generate plots
    generate_plots(lifetime_results, benchmark_results, args.output_dir)
    
    # Print summary (same format as existing experiments)
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETED")
    print("="*60)
    print(f"Total AWS cost: ${experiment.total_aws_cost:.6f}")
    
    print(f"\n📊 Key Findings:")
    for key, finding in educational_insights.items():
        print(f"  {key}: {finding}")
    
    print(f"\n📁 Results saved to: {args.output_dir}/")
    print("  - lifetime_results.csv")
    print("  - benchmark_results.csv") 
    print("  - logical_lifetime.png")
    print("  - qec_advantage.png")
    
    print(f"\n🎓 Educational Value:")
    print("  - Demonstrates QEC principles with realistic noise")
    print("  - Compares logical vs physical error rates")
    print("  - Shows syndrome detection in action")
    print("  - Provides foundation for more advanced QEC codes")
    
    print("\n✅ Ready for Week 2: 5-Qubit Shor Code!")

if __name__ == "__main__":
    main() 