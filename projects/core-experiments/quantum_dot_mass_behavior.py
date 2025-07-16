def electron_mass_behavior():
    print("=== Electrons vs The Collective ===\n")

    print("YES! Electrons remain individual, but the COLLECTIVE behaves like an atom:")
    print("• Individual electrons = Still electrons")
    print("• Confined space = Creates collective quantum states")
    print("• Collective behavior = Acts like a giant artificial atom")
    print("• The DOT (confined region) has atom-like properties\n")

    print("Think of it like an orchestra:")
    print("• Individual musicians = Still individual people")
    print("• Orchestra as a whole = Creates symphonic behavior")
    print("• Conductor (confinement) = Coordinates the collective")
    print("• Result = Music that no individual could create alone")


def box_size_effects():
    print("\n=== What Happens with Different Box Sizes? ===\n")

    box_sizes = [
        ("Smaller than atom", "0.01 nm", "Super-atomic behavior - even more confined"),
        ("Atom-sized", "0.1 nm", "Atom-like behavior - discrete energy levels"),
        ("10x atom size", "1 nm", "Molecule-like behavior - more energy levels"),
        ("100x atom size", "10 nm", "Quantum dot - tunable properties"),
        ("1000x atom size", "100 nm", "Bulk material - continuous energy levels"),
        ("Macroscopic", "1 mm+", "Classical behavior - no quantum effects"),
    ]

    print("Box Size | Dimension | Behavior")
    print("-" * 50)
    for size, dimension, behavior in box_sizes:
        print(f"{size:<15} | {dimension:<9} | {behavior}")

    print("\nKey insight: Bigger boxes = More energy levels = Less atom-like!")
    print("There's a sweet spot where confinement creates useful artificial atoms.")


def quantum_size_effects():
    print("\n=== The Quantum Size Effect ===\n")

    print("As box gets bigger:")
    print("1. More allowed energy states")
    print("2. Energy levels get closer together")
    print("3. Eventually becomes continuous (classical)")
    print("4. Loses special quantum properties")

    print("\nAs box gets smaller:")
    print("1. Fewer allowed energy states")
    print("2. Energy levels spread farther apart")
    print("3. More atom-like behavior")
    print("4. Eventually: single energy level (useless)")

    print("\nThe magic happens in the 1-10 nm range!")


if __name__ == "__main__":
    electron_mass_behavior()
    box_size_effects()
    quantum_size_effects()
