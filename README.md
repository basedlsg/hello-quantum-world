# Hello Quantum World 🌍⚛️

A beginner-friendly introduction to quantum computing using Amazon Braket. This project demonstrates how to create and run quantum circuits both locally and on AWS cloud infrastructure.

## 🚀 What This Project Does

This project creates a **Bell State** - one of the most fundamental quantum circuits that demonstrates:
- **Quantum Superposition**: A qubit can be in multiple states simultaneously
- **Quantum Entanglement**: Two qubits become correlated in a way that measuring one instantly affects the other

The circuit creates two qubits that are perfectly correlated - when you measure them, they'll always be in the same state (both 0 or both 1) with roughly 50/50 probability.

## 📋 Prerequisites

1. **AWS Account**: Sign up at [aws.amazon.com](https://aws.amazon.com)
2. **Python 3.8+**: Download from [python.org](https://python.org)
3. **AWS Credentials**: You'll need an AWS Access Key and Secret Key

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hello-quantum-world.git
cd hello-quantum-world
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials
```bash
aws configure
```
When prompted, enter:
- **AWS Access Key ID**: Your access key from AWS IAM
- **AWS Secret Access Key**: Your secret key from AWS IAM  
- **Default region**: `us-west-2` (recommended for Braket)
- **Output format**: `json`

### 4. Set Up Amazon Braket Permissions
1. Go to the [AWS Braket Console](https://console.aws.amazon.com/braket/home?#/permissions?tab=executionRoles)
2. Create the `AWSServiceRoleForAmazonBraket` service role
3. Ensure your IAM user has Braket permissions

## 🎯 Usage

### Run the Main Example
```bash
python hello_quantum_world.py
```

This will:
1. ✅ Run the Bell circuit on a **local simulator** (free, instant)
2. ✅ Run the same circuit on **AWS cloud simulator** (small cost, more powerful)

### List Available Quantum Devices
```bash
python list_devices.py
```

This shows all available quantum computers and simulators on Amazon Braket.

### Advanced Usage
```bash
python braket_hello_quantum.py
```

This version includes S3 bucket configuration for running on actual quantum hardware (QPUs).

## 📊 Expected Results

When you run the Bell circuit, you should see results like:
```
=== Local Simulator ===
Local simulator results: {'00': 0.496, '11': 0.504}

=== AWS Cloud Simulator ===
Task created with ID: arn:aws:braket:us-west-2:123456789:quantum-task/...
Cloud simulator results: {'00': 0.522, '11': 0.478}
```

The results show **quantum entanglement** - the qubits are always measured in the same state!

## 🧠 Understanding the Quantum Circuit

```python
# Create a 2-qubit Bell circuit
c = Circuit()
c.h(0)        # Put qubit 0 in superposition (50% chance of 0 or 1)
c.cnot(0, 1)  # Entangle qubit 1 with qubit 0
c.probability()  # Measure the probability distribution
```

**What happens:**
1. **H Gate**: Creates superposition - qubit 0 becomes 50% |0⟩ + 50% |1⟩
2. **CNOT Gate**: Creates entanglement - if qubit 0 is |1⟩, flip qubit 1
3. **Result**: The qubits become perfectly correlated

## 💰 Cost Information

- **Local Simulator**: Free
- **AWS Cloud Simulators**: ~$0.075 per minute
- **Quantum Hardware (QPUs)**: $0.30-$35.00 per shot (expensive!)

Start with simulators for learning and development.

## 🔧 Troubleshooting

### "Unable to locate credentials"
- Run `aws configure` and enter your AWS credentials
- Verify credentials with: `aws sts get-caller-identity`

### "AWSServiceRoleForAmazonBraket role doesn't exist"
- Visit the [Braket Permissions page](https://console.aws.amazon.com/braket/home?#/permissions?tab=executionRoles)
- Create the required service role

### "Device not found"
- Run `python list_devices.py` to see available devices
- Update the device ARN in your script

## 📚 Learn More

- [Amazon Braket Documentation](https://docs.aws.amazon.com/braket/)
- [Quantum Computing Basics](https://aws.amazon.com/braket/quantum-computing/)
- [Braket Python SDK](https://github.com/aws/amazon-braket-sdk-python)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Next Steps

Once you have this working:
1. Try modifying the circuit (add more qubits, different gates)
2. Explore quantum algorithms (Grover's search, Shor's algorithm)
3. Run on real quantum hardware when ready
4. Build quantum machine learning applications

Welcome to the quantum world! 🚀⚛️ 