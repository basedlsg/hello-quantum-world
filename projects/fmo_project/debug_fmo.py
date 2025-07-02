"""
Debug script to understand FMO efficiency calculation
"""

import numpy as np
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from run_fmo4 import load_fmo_hamiltonian, build_fmo_circuit, calculate_efficiency

def debug_states():
    """Debug the initial and final states."""
    
    device = LocalSimulator("braket_dm")
    H = load_fmo_hamiltonian()
    
    print("=== FMO Debug Analysis ===")
    print(f"Hamiltonian shape: {H.shape}")
    print(f"Hamiltonian (first row): {H[0, :]}")
    print()
    
    # Test with no noise first
    circuit = build_fmo_circuit(H, 0.025, 40, 0.0)
    circuit.density_matrix()
    
    print(f"Circuit depth: {circuit.depth}")
    print(f"Circuit qubit count: {circuit.qubit_count}")
    print()
    
    # Run simulation
    task = device.run(circuit, shots=0)
    result = task.result()
    dm = result.result_types[0].value
    dm_array = np.array(dm)
    
    print("Final density matrix diagonal (populations):")
    for i in range(16):  # 2^4 = 16 states
        state_str = format(i, '04b')  # 4-bit binary
        pop = np.real(dm_array[i, i])
        print(f"  |{state_str}⟩: {pop:.6f}")
    
    print()
    
    # Check individual qubit populations
    print("Individual qubit populations:")
    for q in range(4):
        # States where qubit q is |1⟩
        states_with_q = [i for i in range(16) if (i >> q) & 1]
        pop_q = sum(np.real(dm_array[i, i]) for i in states_with_q)
        print(f"  Qubit {q}: {pop_q:.6f}")
    
    print()
    
    # Test efficiency calculation
    eff = calculate_efficiency(result.result_types[0])
    print(f"Calculated efficiency (sink = qubit 3): {eff:.6f}")
    
    # Test with different sink definitions
    for sink_q in range(4):
        states_with_sink = [i for i in range(16) if (i >> sink_q) & 1]
        eff_sink = sum(np.real(dm_array[i, i]) for i in states_with_sink)
        print(f"  If sink = qubit {sink_q}: efficiency = {eff_sink:.6f}")

def test_initial_state():
    """Test just the initial state preparation."""
    device = LocalSimulator("braket_dm")
    
    print("\n=== Initial State Test ===")
    
    # Just prepare initial state
    circuit = Circuit()
    circuit.x(0)  # In Braket: qubit 0 is rightmost, so this gives |0001⟩
    circuit.density_matrix()
    
    task = device.run(circuit, shots=0)
    result = task.result()
    dm = np.array(result.result_types[0].value)
    
    print("Initial state populations:")
    n_states = dm.shape[0]
    n_qubits = int(np.log2(n_states))
    print(f"System has {n_qubits} qubits, {n_states} states")
    
    for i in range(n_states):
        state_str = format(i, f'0{n_qubits}b')
        pop = np.real(dm[i, i])
        if pop > 1e-10:
            print(f"  |{state_str}⟩: {pop:.6f}")
            # Show which qubits are |1⟩
            active_qubits = [q for q in range(n_qubits) if (i >> q) & 1]
            print(f"    Active qubits: {active_qubits}")

if __name__ == "__main__":
    test_initial_state()
    debug_states() 