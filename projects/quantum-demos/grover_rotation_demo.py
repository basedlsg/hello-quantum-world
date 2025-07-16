import math


def grover_rotation_explanation():
    print("=== Grover's Algorithm: The Real Magic ===\n")

    print("It's NOT testing frequencies - it's ROTATING probability amplitudes!")
    print("Think of it like a compass needle finding magnetic north.\n")

    # Simulate Grover's algorithm for 4 items
    N = 4  # Database size
    target_item = 2  # We're looking for item #2

    print(f"Database: {N} items")
    print(f"Looking for: Item #{target_item}")
    print(f"Optimal iterations: {math.pi * math.sqrt(N) / 4:.0f}\n")

    # Initial state: all items equally likely
    amplitudes = [0.5, 0.5, 0.5, 0.5]  # All start with equal amplitude

    print("Iteration | Item 0 | Item 1 | Item 2* | Item 3 | Target Probability")
    print("-" * 65)
    print(
        f"Start     | {amplitudes[0]:>5.2f}  | {amplitudes[1]:>5.2f}  | {amplitudes[2]:>5.2f}   | {amplitudes[3]:>5.2f}  | {amplitudes[target_item]**2:>14.1%}"
    )

    # Grover iterations
    for iteration in range(1, 4):
        # Oracle: flip the sign of target item
        amplitudes[target_item] *= -1

        # Diffusion: reflect around average
        avg = sum(amplitudes) / len(amplitudes)
        amplitudes = [2 * avg - amp for amp in amplitudes]

        probability = amplitudes[target_item] ** 2
        print(
            f"Iter {iteration}     | {amplitudes[0]:>5.2f}  | {amplitudes[1]:>5.2f}  | {amplitudes[2]:>5.2f}   | {amplitudes[3]:>5.2f}  | {probability:>14.1%}"
        )

    print("\n=== The Magic Explained ===")
    print("1. Oracle marks the target (flips its sign)")
    print("2. Diffusion rotates ALL amplitudes toward the target")
    print("3. Each iteration increases target probability")
    print("4. After √N iterations, target probability is maximized!")
    print("\nIt's like a GPS that gets more accurate with each recalculation!")


def why_sqrt_n():
    print("\n=== Why √N? The Geometry! ===")
    print("Grover's algorithm works in 2D rotation space:")
    print("- X-axis: 'Wrong answers' amplitude")
    print("- Y-axis: 'Right answer' amplitude")
    print("- Each iteration rotates by a fixed angle")
    print("- After √N rotations, you've rotated 90 degrees to the target!")
    print("\nIt's pure geometry - not random searching!")


if __name__ == "__main__":
    grover_rotation_explanation()
    why_sqrt_n()
