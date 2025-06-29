import math

def grovers_demo():
    print("=== Grover's Search Explanation ===\n")
    
    # Example: Finding 1 item in 16 items
    database_size = 16
    optimal_iterations = int(math.pi * math.sqrt(database_size) / 4)
    
    print(f"Database size: {database_size} items")
    print(f"Classical search: {database_size//2} tries on average")
    print(f"Grover's search: {optimal_iterations} iterations")
    print(f"Speedup: {(database_size//2) / optimal_iterations:.1f}x faster\n")
    
    print("How Grover's Works:")
    print("1. Start: All items have equal probability (6.25% each)")
    print("2. Iteration 1: Target item probability increases to ~25%")
    print("3. Iteration 2: Target item probability increases to ~75%") 
    print("4. Iteration 3: Target item probability reaches ~94%")
    print("5. Measure: Get the right answer with 94% confidence!\n")
    
    print("Why √N iterations?")
    print("- Each iteration rotates the probability amplitude")
    print("- After √N rotations, target amplitude is maximized")
    print("- It's like tuning a radio to the right frequency!")
    
    # Demonstrate scaling
    print("\n=== Scaling Demonstration ===")
    sizes = [100, 10000, 1000000, 1000000000]
    
    for size in sizes:
        classical = size // 2
        quantum = int(math.pi * math.sqrt(size) / 4)
        speedup = classical / quantum
        print(f"Size: {size:>10,} | Classical: {classical:>8,} | Quantum: {quantum:>6,} | Speedup: {speedup:>6.0f}x")

if __name__ == "__main__":
    grovers_demo() 