import random


def demonstrate_scale_stability():
    print("=== Scale vs Stability Demonstration ===\n")

    # Simulate quantum randomness at different scales
    scales = [
        ("Quantum particle", 1),
        ("Small molecule", 10),
        ("Large molecule", 100),
        ("Cell component", 1000),
        ("Living cell", 10000),
        ("Tissue", 100000),
        ("Organ", 1000000),
        ("Organism", 10000000),
    ]

    print("Scale Level | Sample Size | Randomness | Predictability")
    print("-" * 55)

    for name, size in scales:
        # Simulate quantum randomness (each particle has 50/50 behavior)
        outcomes = [random.choice([0, 1]) for _ in range(size)]
        average = sum(outcomes) / len(outcomes)
        deviation = abs(average - 0.5)  # How far from perfect 50/50
        predictability = (1 - deviation) * 100

        print(
            f"{name:<15} | {size:>10,} | {deviation:>8.3f} | {predictability:>11.1f}%"
        )

    print("\nKey Insight: As scale increases, random quantum effects average out!")
    print("This is why your coffee cup doesn't quantum tunnel through the table.")

    # Demonstrate with cosmic scales
    print("\n=== Cosmic Scale Stability ===")
    cosmic_scales = [
        ("Planet", "Orbital mechanics - highly predictable"),
        ("Solar System", "Newton's laws work perfectly"),
        ("Galaxy", "Predictable rotation curves"),
        ("Universe", "Follows cosmological equations"),
    ]

    for scale, behavior in cosmic_scales:
        print(f"{scale:<12}: {behavior}")

    print("\nThe bigger things get, the more they follow classical rules!")


if __name__ == "__main__":
    demonstrate_scale_stability()
