import sys
import os
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from projects.qec_fundamentals.qec import QECProject
from braket.aws import AwsDevice
import argparse
import logging

def run_hardware_benchmark(project, device_arn, dry_run=False):
    """
    Runs a specified QEC project's circuits on real quantum hardware.
    """
    logging.info(f"--- Starting Hardware Benchmark on {device_arn} ---")
    device = AwsDevice(device_arn)

    # Get the circuits from the QEC project
    # For now, let's test a simple 3-qubit logical |+> state
    circuit = project._create_logical_state_circuit("3_qubit", "|+>")
    
    # Add syndrome detection to make it a meaningful circuit
    data_qubits = list(range(3))
    syndrome_qubits = list(range(3, 5))
    syndrome_circuit = project._create_syndrome_detection_circuit("3_qubit", data_qubits, syndrome_qubits)
    circuit.add_circuit(syndrome_circuit)

    logging.info("Transpiling circuit for the target device...")
    transpiled_circuit = device.transpile(circuit)
    logging.info("Transpilation complete.")
    
    print("\n--- Transpiled Circuit Summary ---")
    print(f"Depth: {transpiled_circuit.depth}")
    print(f"Gate Count: {len(transpiled_circuit.instructions)}")
    print("---------------------------------\n")

    if not dry_run:
        logging.info(f"Submitting circuit to {device.name}...")
        task = device.run(transpiled_circuit, shots=100)
        logging.info(f"Task {task.id} created. Waiting for results...")
        
        result = task.result()
        logging.info("Task complete.")
        
        # In a real benchmark, we would analyze the results here.
        # For now, we just print the measurement counts.
        print(result.measurement_counts)
    logging.info("--- Hardware Benchmark Complete ---")

def main():
    parser = argparse.ArgumentParser(description="Run QEC hardware benchmarks.")
    parser.add_argument(
        "--device",
        type=str,
        default="arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
        help="The ARN of the AWS Braket device to run on.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Transpile the circuit for the device without running it.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # We can reuse the QECProject to build our circuits
    qec_project = QECProject()
    
    run_hardware_benchmark(qec_project, args.device, dry_run=args.dry_run)

if __name__ == "__main__":
    main() 