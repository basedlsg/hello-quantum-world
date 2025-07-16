def entanglement_creation():
    print("=== How Entanglement is Actually Created ===\n")

    print("NOT through wires or frequencies - through QUANTUM GATES!")

    steps = [
        "1. Start with two separate qubits (not entangled)",
        "2. Apply quantum gates (like CNOT) using precise pulses",
        "3. Gates create quantum correlations between qubits",
        "4. Result: Entangled qubits (no physical connection needed!)",
    ]

    for step in steps:
        print(step)

    print("\nThink of it like:")
    print("• Two coins spinning on separate tables")
    print("• Magic spell links their fates")
    print("• Now when one lands heads, other MUST land heads")
    print("• No wires needed - the correlation is in the quantum state!")


def entanglement_measurement():
    print("\n=== How We Measure Entanglement ===\n")

    print("We can't SEE entanglement directly, but we can PROVE it exists:")

    tests = [
        ("Bell test", "Measure correlations that violate classical physics"),
        ("Quantum tomography", "Reconstruct the full quantum state"),
        ("Fidelity measurement", "Compare to perfect entangled state"),
        ("Concurrence", "Mathematical measure of entanglement strength"),
    ]

    print("Test Method | What it Measures")
    print("-" * 40)
    for test, description in tests:
        print(f"{test:<15} | {description}")

    print("\nKey insight: We measure the EFFECTS of entanglement!")


def entanglement_scale():
    print("\n=== Entanglement Scale Records ===\n")

    records = [
        ("2 particles", "1970s - First demonstrations"),
        ("10 particles", "1990s - Small quantum systems"),
        ("100 particles", "2000s - Quantum computer prototypes"),
        ("1000 particles", "2020s - Current record holders"),
        ("1 million+", "Future goal - Fault-tolerant quantum computers"),
    ]

    print("Scale | Achievement Era")
    print("-" * 30)
    for scale, era in records:
        print(f"{scale:<12} | {era}")

    print("\nChallenges:")
    print("• More particles = exponentially harder to maintain")
    print("• Decoherence destroys entanglement quickly")
    print("• Current record: ~1000 particles for microseconds")


def how_particles_link():
    print("\n=== How Particles Actually 'Link' ===\n")

    print("NOT through physical connections!")
    print("The 'link' is in the QUANTUM STATE itself:")

    print("\nClassical thinking (WRONG):")
    print("• Particle A sends signal to Particle B")
    print("• Information travels between them")
    print("• Physical connection required")

    print("\nQuantum reality:")
    print("• Particles share a single quantum state")
    print("• Measuring one instantly affects the shared state")
    print("• No information travels - the correlation was always there!")
    print("• It's like two parts of the same coin")


if __name__ == "__main__":
    entanglement_creation()
    entanglement_measurement()
    entanglement_scale()
    how_particles_link()
