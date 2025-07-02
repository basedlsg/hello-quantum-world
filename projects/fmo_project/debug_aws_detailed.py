"""
Detailed debug of AWS density matrix structure
"""

import numpy as np
from braket.circuits import Circuit
from braket.aws import AwsDevice

def debug_aws_dm_detailed():
    """Debug AWS density matrix in detail."""
    circuit = Circuit()
    circuit.x(0)  # |0001⟩
    circuit.phase_damping(0, 0.1)  # Add some noise
    circuit.density_matrix()
    
    print("=== AWS DM1 Detailed Debug ===")
    try:
        device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/dm1")
        task = device.run(circuit, shots=0)
        result = task.result()
        dm_result = result.result_types[0]
        
        print(f"dm_result type: {type(dm_result)}")
        print(f"dm_result hasattr value: {hasattr(dm_result, 'value')}")
        
        if hasattr(dm_result, 'value'):
            dm_raw = dm_result.value
            print(f"dm_raw type: {type(dm_raw)}")
            print(f"dm_raw length: {len(dm_raw)}")
            print(f"dm_raw[0] type: {type(dm_raw[0])}")
            print(f"dm_raw[0] length: {len(dm_raw[0])}")
            print(f"dm_raw[1][1]: {dm_raw[1][1]} (type: {type(dm_raw[1][1])})")
            
            # Convert to numpy
            dm_np = np.array(dm_raw)
            print(f"dm_np shape: {dm_np.shape}")
            print(f"dm_np dtype: {dm_np.dtype}")
            print(f"dm_np[1,1]: {dm_np[1,1]} (type: {type(dm_np[1,1])})")
            
            # Try to extract real part
            real_part = np.real(dm_np[1,1])
            print(f"real_part: {real_part} (type: {type(real_part)})")
            print(f"real_part shape: {getattr(real_part, 'shape', 'no shape')}")
            
            # Different conversion methods
            try:
                method1 = float(real_part)
                print(f"float(real_part): {method1}")
            except Exception as e:
                print(f"float(real_part) failed: {e}")
                
            try:
                method2 = real_part.item()
                print(f"real_part.item(): {method2}")
            except Exception as e:
                print(f"real_part.item() failed: {e}")
                
            try:
                method3 = np.asscalar(real_part)
                print(f"np.asscalar(real_part): {method3}")
            except Exception as e:
                print(f"np.asscalar(real_part) failed: {e}")
        
    except Exception as e:
        print(f"AWS error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_aws_dm_detailed()
