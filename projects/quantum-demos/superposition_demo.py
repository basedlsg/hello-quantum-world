from braket.circuits import Circuit
from braket.devices import LocalSimulator

# Demonstration: How we KNOW superposition exists
print("=== Proving Superposition Exists ===\n")

# Test 1: Classical bit (always gives same result)
print("Classical bit test:")
for i in range(5):
    c = Circuit()
    c.x(0)  # Classical bit flip (always 1)
    c.probability()

    device = LocalSimulator()
    result = device.run(c, shots=100).result()
    print(f"Run {i+1}: {result.measurement_probabilities}")

print("\n" + "=" * 50 + "\n")

# Test 2: Quantum superposition (shows interference)
print("Quantum superposition test:")
print("H gate puts qubit in 50/50 superposition")
for i in range(5):
    c = Circuit()
    c.h(0)  # Hadamard gate creates superposition
    c.probability()

    device = LocalSimulator()
    result = device.run(c, shots=100).result()
    print(f"Run {i+1}: {result.measurement_probabilities}")

print("\n" + "=" * 50 + "\n")

# Test 3: Quantum interference (PROOF of superposition)
print("Quantum interference test (the smoking gun!):")
print("H-H sequence should give 100% |0⟩ due to interference")
for i in range(5):
    c = Circuit()
    c.h(0)  # Create superposition
    c.h(0)  # Interfere with itself - should cancel back to |0⟩
    c.probability()

    device = LocalSimulator()
    result = device.run(c, shots=100).result()
    print(f"Run {i+1}: {result.measurement_probabilities}")

print("\nIf we get 100% |0⟩, superposition MUST have existed!")
print("Classical physics can't explain this interference pattern.")
