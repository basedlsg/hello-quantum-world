"""AWS Braket Cost Projection Tool
Estimates costs for scaling experiments while managing free-tier budget.
"""

import pandas as pd

# AWS Braket pricing (as of 2024)
PRICING = {
    "SV1": 0.075,  # $ per minute
    "DM1": 0.075,  # $ per minute
    "TN1": 0.275,  # $ per minute
    "free_tier_minutes": 60,  # Free tier allowance per month
}


def estimate_simulation_time(n_qubits: int, simulator: str = "DM1") -> float:
    """Estimate simulation time in minutes based on qubit count and simulator."""
    # Empirical scaling estimates based on circuit complexity
    if simulator == "SV1":
        # State vector scales as 2^n in memory, roughly exponential in time
        base_time = 0.1  # minutes for 2 qubits
        scaling_factor = 1.8  # empirical
        time_minutes = base_time * (scaling_factor ** (n_qubits - 2))

    elif simulator == "DM1":
        # Density matrix scales as 4^n in memory, steeper scaling
        base_time = 0.2  # minutes for 2 qubits
        scaling_factor = 3.5  # empirical
        time_minutes = base_time * (scaling_factor ** (n_qubits - 2))

    elif simulator == "TN1":
        # Tensor network can handle larger systems but slower per operation
        base_time = 0.5  # minutes for 2 qubits
        scaling_factor = 2.2  # empirical
        time_minutes = base_time * (scaling_factor ** (n_qubits - 2))

    return time_minutes


def calculate_experiment_cost(
    max_qubits: int,
    trials_per_size: int = 3,
    noise_levels: int = 3,
    simulator: str = "DM1",
) -> dict:
    """Calculate total cost for scaling experiment."""
    total_minutes = 0
    cost_breakdown = []

    for n_qubits in range(2, max_qubits + 1):
        # Each experiment runs both spatial and non-spatial circuits
        circuits_per_trial = 2

        # Time per trial
        time_per_trial = (
            estimate_simulation_time(n_qubits, simulator) * circuits_per_trial
        )

        # Total time for this qubit count
        total_time_n = time_per_trial * trials_per_size * noise_levels
        total_minutes += total_time_n

        # Cost calculation
        cost_n = total_time_n * PRICING[simulator]

        cost_breakdown.append(
            {
                "n_qubits": n_qubits,
                "time_per_trial_min": time_per_trial,
                "total_time_min": total_time_n,
                "cost_usd": cost_n,
            }
        )

    # Free tier calculation
    free_tier_used = min(total_minutes, PRICING["free_tier_minutes"])
    billable_minutes = max(0, total_minutes - PRICING["free_tier_minutes"])

    total_cost = billable_minutes * PRICING[simulator]

    return {
        "total_minutes": total_minutes,
        "free_tier_minutes": free_tier_used,
        "billable_minutes": billable_minutes,
        "total_cost_usd": total_cost,
        "breakdown": cost_breakdown,
    }


def find_optimal_strategy(budget_usd: float = 5.0) -> dict:
    """Find the maximum scale achievable within budget."""
    strategies = []

    for max_qubits in range(6, 15):  # Test up to 14 qubits
        for simulator in ["SV1", "DM1", "TN1"]:
            for trials in [1, 2, 3]:
                for noise_levels in [1, 2, 3]:

                    cost_analysis = calculate_experiment_cost(
                        max_qubits, trials, noise_levels, simulator
                    )

                    if cost_analysis["total_cost_usd"] <= budget_usd:
                        strategies.append(
                            {
                                "max_qubits": max_qubits,
                                "simulator": simulator,
                                "trials": trials,
                                "noise_levels": noise_levels,
                                "total_cost": cost_analysis["total_cost_usd"],
                                "total_minutes": cost_analysis["total_minutes"],
                                "scientific_value": max_qubits
                                * trials
                                * noise_levels,  # Heuristic
                            }
                        )

    # Sort by scientific value (more qubits, trials, noise levels = better)
    strategies.sort(key=lambda x: x["scientific_value"], reverse=True)

    return strategies


def main():
    """Run cost projection analysis."""
    print("=== AWS Braket Cost Projection ===")
    print(f"Free tier: {PRICING['free_tier_minutes']} minutes/month")
    print(
        f"Pricing: SV1=${PRICING['SV1']}/min, DM1=${PRICING['DM1']}/min, TN1=${PRICING['TN1']}/min"
    )

    # Test current experiment scaling
    print("\n--- Current Experiment Scaling (DM1) ---")
    for max_qubits in [6, 8, 10, 12]:
        cost_analysis = calculate_experiment_cost(
            max_qubits, trials_per_size=3, noise_levels=2, simulator="DM1"
        )
        print(
            f"{max_qubits} qubits: {cost_analysis['total_minutes']:.1f} min, "
            f"${cost_analysis['total_cost_usd']:.2f}"
        )

    # Find optimal strategies
    print("\n--- Optimal Strategies (Budget: $5) ---")
    strategies = find_optimal_strategy(budget_usd=5.0)

    print("Top 5 strategies:")
    for i, strategy in enumerate(strategies[:5]):
        print(
            f"{i+1}. {strategy['max_qubits']} qubits, {strategy['simulator']}, "
            f"{strategy['trials']} trials, {strategy['noise_levels']} noise levels"
        )
        print(
            f"   Cost: ${strategy['total_cost']:.2f}, Time: {strategy['total_minutes']:.1f} min"
        )

    # Save detailed breakdown
    if strategies:
        best_strategy = strategies[0]
        detailed_cost = calculate_experiment_cost(
            best_strategy["max_qubits"],
            best_strategy["trials"],
            best_strategy["noise_levels"],
            best_strategy["simulator"],
        )

        df = pd.DataFrame(detailed_cost["breakdown"])
        df.to_csv("results/cost_projection.csv", index=False)
        print("\nDetailed breakdown saved to results/cost_projection.csv")

        print("\n*** RECOMMENDED STRATEGY ***")
        print(f"Max qubits: {best_strategy['max_qubits']}")
        print(f"Simulator: {best_strategy['simulator']}")
        print(f"Trials per size: {best_strategy['trials']}")
        print(f"Noise levels: {best_strategy['noise_levels']}")
        print(f"Total cost: ${best_strategy['total_cost']:.2f}")
        print(
            f"Free tier usage: {min(detailed_cost['total_minutes'], 60):.1f}/60 minutes"
        )


if __name__ == "__main__":
    main()
