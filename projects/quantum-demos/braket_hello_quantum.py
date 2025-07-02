import boto3
from braket.aws import AwsDevice
from braket.circuits import Circuit
from braket.devices import LocalSimulator

# 1. Build a 2-qubit Bell circuit
c = Circuit()
c.h(0)
c.cnot(0, 1)
c.probability()

# 2. Run on the local simulator
device = LocalSimulator()
print("Local simulator results:", device.run(c, shots=1000).result().measurement_probabilities)

# 3. Run on a quantum device on AWS
try:
    # Get the AWS account ID
    aws_account_id = boto3.client("sts").get_caller_identity()["Account"]
    
    # Specify the S3 bucket for results
    s3_folder = ("amazon-braket-us-west-2-quantum-jobs", "quantum-jobs")

    # Choose the device (using cloud simulator - more cost effective for testing)
    device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")

    # Run the circuit
    task = device.run(c, s3_folder, shots=1000)
    
    # Print the task ID and get the results
    print(f'Created task {task.id}')
    result = task.result()
    
    # Print the results
    print("Cloud device results:", result.measurement_probabilities)
    
except Exception as e:
    print("❌ AWS connection failed:", str(e))
    print("💡 Possible issues:")
    print("   - AWS credentials not configured. Run 'aws configure' in your terminal.")
    print("   - The IAM user/role does not have Braket permissions.")
    print("   - The S3 bucket policy might be incorrect.")
    print("💡 Visit the AWS Braket documentation for setup instructions.") 