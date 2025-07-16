from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.devices import LocalSimulator

# 1. Build a 2-qubit Bell circuit
c = Circuit()
c.h(0)
c.cnot(0, 1)
c.probability()

# 2. Run on the local simulator
print("=== Local Simulator ===")
device = LocalSimulator()
result = device.run(c, shots=1000).result()
print("Local simulator results:", result.measurement_probabilities)

# 3. Run on AWS cloud simulator (simpler approach)
print("\n=== AWS Cloud Simulator ===")
try:
    # Use the cloud simulator
    device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")

    # Run the circuit (this approach doesn't require S3 bucket configuration)
    task = device.run(c, shots=1000)

    print(f"Task created with ID: {task.id}")
    print("Waiting for results...")

    # Get the results
    result = task.result()
    print("Cloud simulator results:", result.measurement_probabilities)

except Exception as e:
    print("❌ AWS cloud simulator failed:", str(e))
    print("💡 You may need to:")
    print("   1. Visit https://console.aws.amazon.com/braket/home?#/permissions")
    print("   2. Create the AWSServiceRoleForAmazonBraket role")
    print("   3. Ensure your IAM user has Braket permissions")
