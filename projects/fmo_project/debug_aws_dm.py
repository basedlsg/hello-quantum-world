"""
Debug AWS density matrix structure
"""

import numpy as np
from braket.circuits import Circuit
from braket.devices import LocalSimulator
from braket.aws import AwsDevice

def create_simple_circuit():
    """Create a simple test circuit."""
    circuit = Circuit()
    circuit.x(0)  # |0001⟩
    circuit.density_matrix()
    return circuit

def debug_density_matrix_structure():
    """Debug the density matrix structure differences."""
    circuit = create_simple_circuit()
    
    # Test local first
    print("=== Local Simulator ===")
    local_device = LocalSimulator("braket_dm")
    local_task = local_device.run(circuit, shots=0)
    local_result = local_task.result()
    local_dm = local_result.result_types[0]
    
    print(f"Local DM type: {type(local_dm)}")
    print(f"Local DM hasattr value: {hasattr(local_dm, 'value')}")
    if hasattr(local_dm, 'value'):
        print(f"Local DM.value type: {type(local_dm.value)}")
        print(f"Local DM.value shape: {local_dm.value.shape}")
        print(f"Local DM[1,1]: {local_dm.value[1,1]} (type: {type(local_dm.value[1,1])})")
    else:
        print(f"Local DM direct type: {type(local_dm)}")
        print(f"Local DM shape: {local_dm.shape}")
        print(f"Local DM[1,1]: {local_dm[1,1]} (type: {type(local_dm[1,1])})")
    
    print("\n=== AWS DM1 Simulator ===")
    try:
        aws_device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/dm1")
        aws_task = aws_device.run(circuit, shots=0)
        aws_result = aws_task.result()
        aws_dm = aws_result.result_types[0]
        
        print(f"AWS DM type: {type(aws_dm)}")
        print(f"AWS DM hasattr value: {hasattr(aws_dm, 'value')}")
        if hasattr(aws_dm, 'value'):
            print(f"AWS DM.value type: {type(aws_dm.value)}")
            print(f"AWS DM.value shape: {aws_dm.value.shape}")
            print(f"AWS DM[1,1]: {aws_dm.value[1,1]} (type: {type(aws_dm.value[1,1])})")
        else:
            print(f"AWS DM direct type: {type(aws_dm)}")
            print(f"AWS DM shape: {aws_dm.shape}")
            print(f"AWS DM[1,1]: {aws_dm[1,1]} (type: {type(aws_dm[1,1])})")
            
    except Exception as e:
        print(f"AWS error: {e}")

if __name__ == "__main__":
    debug_density_matrix_structure()
