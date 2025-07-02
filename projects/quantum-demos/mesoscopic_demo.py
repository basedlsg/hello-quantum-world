import random
import math

def mesoscopic_weirdness():
    print("=== Mesoscopic Twilight Zone ===\n")
    
    print("At 100-10,000 atoms, reality gets WEIRD:")
    print("- Too big for pure quantum behavior")
    print("- Too small for pure classical behavior")
    print("- Result: HYBRID WEIRDNESS!\n")
    
    # Simulate mesoscopic behavior
    atom_counts = [1, 10, 100, 1000, 10000, 100000]
    
    print("Atoms | Quantum Behavior | Classical Behavior | Weird Hybrid Effects")
    print("-" * 75)
    
    for atoms in atom_counts:
        quantum_strength = max(0, 100 - math.log10(atoms) * 20)
        classical_strength = min(100, math.log10(atoms) * 20)
        weirdness = abs(quantum_strength - classical_strength)
        
        if atoms <= 10:
            status = "Pure quantum chaos"
        elif atoms <= 10000:
            status = f"TWILIGHT ZONE - {weirdness:.0f}% weird!"
        else:
            status = "Classical and stable"
            
        print(f"{atoms:>5} | {quantum_strength:>14.0f}% | {classical_strength:>16.0f}% | {status}")
    
    print("\n=== Real Mesoscopic Weirdness Examples ===")
    examples = [
        "Quantum dots: Act like artificial atoms but with 1000+ real atoms",
        "Carbon nanotubes: Sometimes conduct, sometimes don't (quantum lottery)",
        "Superconducting grains: Partially superconducting (impossible!)",
        "Biological molecules: Quantum effects in photosynthesis and smell",
        "Virus particles: Too big for quantum, too small for classical thermodynamics"
    ]
    
    for example in examples:
        print(f"• {example}")
    
    print("\nThis is where physics gets REALLY strange!")

if __name__ == "__main__":
    mesoscopic_weirdness() 