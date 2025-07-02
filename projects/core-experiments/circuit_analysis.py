"""
Circuit Depth and Gate Count Analysis
Investigates whether spatial vs non-spatial fidelity differences are due to 
topology or simply different gate counts/depths.
"""

import numpy as np
from braket.circuits import Circuit, noises
from braket.devices import LocalSimulator
import pandas as pd

def create_spatial_circuit(n_qubits: int) -> Circuit:
    """Create spatial circuit with nearest-neighbor interactions only."""
    circuit = Circuit()
    
    # Initialize all qubits in superposition
    for i in range(n_qubits):
        circuit.h(i)
    
    # Create spatial correlations through nearest-neighbor gates
    for i in range(n_qubits - 1):
        circuit.cnot(i, i + 1)
        
    return circuit

def create_nonspatial_circuit(n_qubits: int) -> Circuit:
    """Create non-spatial circuit with long-range interactions."""
    circuit = Circuit()
    
    # Initialize all qubits in superposition
    for i in range(n_qubits):
        circuit.h(i)
    
    # Create non-spatial correlations through long-range gates
    for i in range(n_qubits):
        for j in range(i + 2, n_qubits):  # Skip nearest neighbors
            circuit.cnot(i, j)
            
    return circuit

def analyze_circuit_properties(circuit: Circuit, circuit_type: str, n_qubits: int):
    """Analyze depth, gate counts, and other properties of a circuit."""
    
    # Count different gate types
    gate_counts = {}
    for instruction in circuit.instructions:
        gate_name = instruction.operator.name
        if gate_name in gate_counts:
            gate_counts[gate_name] += 1
        else:
            gate_counts[gate_name] = 1
    
    # Calculate circuit depth (number of time steps)
    depth = circuit.depth
    
    # Total gate count
    total_gates = len(circuit.instructions)
    
    # CNOT count specifically
    cnot_count = gate_counts.get('CNot', 0)
    h_count = gate_counts.get('H', 0)
    
    return {
        'circuit_type': circuit_type,
        'n_qubits': n_qubits,
        'total_gates': total_gates,
        'cnot_count': cnot_count,
        'h_count': h_count,
        'depth': depth,
        'gate_counts': gate_counts
    }

def main():
    """Analyze circuit properties across qubit counts."""
    print("=== Circuit Depth and Gate Count Analysis ===")
    print("Comparing spatial vs non-spatial circuit properties\n")
    
    results = []
    
    for n_qubits in range(2, 7):  # 2 to 6 qubits
        print(f"--- Analyzing {n_qubits} qubits ---")
        
        # Create both circuit types
        spatial_circuit = create_spatial_circuit(n_qubits)
        nonspatial_circuit = create_nonspatial_circuit(n_qubits)
        
        # Analyze properties
        spatial_props = analyze_circuit_properties(spatial_circuit, 'spatial', n_qubits)
        nonspatial_props = analyze_circuit_properties(nonspatial_circuit, 'nonspatial', n_qubits)
        
        results.extend([spatial_props, nonspatial_props])
        
        # Print comparison
        print(f"Spatial:     Total gates={spatial_props['total_gates']:2d}, "
              f"CNOTs={spatial_props['cnot_count']:2d}, Depth={spatial_props['depth']:2d}")
        print(f"Non-spatial: Total gates={nonspatial_props['total_gates']:2d}, "
              f"CNOTs={nonspatial_props['cnot_count']:2d}, Depth={nonspatial_props['depth']:2d}")
        
        # Calculate ratios
        gate_ratio = nonspatial_props['total_gates'] / spatial_props['total_gates']
        cnot_ratio = nonspatial_props['cnot_count'] / spatial_props['cnot_count'] if spatial_props['cnot_count'] > 0 else float('inf')
        depth_ratio = nonspatial_props['depth'] / spatial_props['depth']
        
        print(f"Ratios (non-spatial/spatial): Gates={gate_ratio:.2f}, CNOTs={cnot_ratio:.2f}, Depth={depth_ratio:.2f}")
        print()
    
    # Save detailed results
    df = pd.DataFrame(results)
    df.to_csv('results/circuit_analysis.csv', index=False)
    print("Detailed results saved to results/circuit_analysis.csv")
    
    # Summary analysis
    print("\n=== CRITICAL ANALYSIS ===")
    spatial_df = df[df['circuit_type'] == 'spatial']
    nonspatial_df = df[df['circuit_type'] == 'nonspatial']
    
    print("Gate count scaling:")
    for i, n_qubits in enumerate(range(2, 7)):
        s_gates = spatial_df.iloc[i]['total_gates']
        ns_gates = nonspatial_df.iloc[i]['total_gates']
        ratio = ns_gates / s_gates
        print(f"  {n_qubits} qubits: {s_gates} vs {ns_gates} gates (ratio: {ratio:.2f})")
    
    print("\nDepth scaling:")
    for i, n_qubits in enumerate(range(2, 7)):
        s_depth = spatial_df.iloc[i]['depth']
        ns_depth = nonspatial_df.iloc[i]['depth']
        ratio = ns_depth / s_depth
        print(f"  {n_qubits} qubits: {s_depth} vs {ns_depth} depth (ratio: {ratio:.2f})")
    
    print("\n*** INTERPRETATION ***")
    print("If ratios increase significantly with qubit count, our fidelity differences")
    print("may be due to circuit complexity (gate count/depth) rather than topology.")
    print("Look for correlation between these ratios and our observed fidelity crossover at 5-6 qubits.")

if __name__ == "__main__":
    main() 