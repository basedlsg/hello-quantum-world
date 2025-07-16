
# FMO Noise-Assisted Transport: Project Summary

This document summarizes the key findings of the simulated quantum transport in a 4-site FMO-like complex.

## 1. Quantitative Headline Result

The primary finding is the clear demonstration of noise-assisted transport. After an initial drop, transport efficiency is enhanced by dephasing noise.

- **Minimum Efficiency**: 0.471 at γ = 23.55 ps⁻¹
- **Final Efficiency**: 0.499 at γ = 94.20 ps⁻¹
- **Quantitative Enhancement**: A **+5.9%** relative increase in transport efficiency from the minimum.

**Definition of Efficiency (η):** Efficiency is defined as the population of the target "sink" site at the end of the simulation time (t=1 ps). In our 4-qubit system, this corresponds to the population of the state |1000> (Braket little-endian), which is `ρ_sink,sink(t_final)`.

## 2. Key Validation Figures

The following figures provide visual evidence for the scientific rigor and validity of the simulation.

### Figure 1: Quantum vs. Classical Transport

This plot shows the main result, comparing the efficiency of the quantum simulation against a classical random walk benchmark.

![Main Comparison Plot](final_results/figures/Fig1_Quantum_vs_Classical_Transport_Final.png)

### Figure 2: Subspace Leakage Analysis

This plot confirms that population leakage out of the single-excitation subspace is negligible, ensuring the simulation conserves probability and is physically valid.

![Leakage Plot](final_results/figures/Fig2_Leakage_Analysis.png)

### Figure 3: Numerical Convergence

This plot shows that the simulation results converge as the Trotter time step is reduced.

![Convergence Plot](final_results/figures/Fig3_Convergence_Analysis.png)

## 3. Physical Realism

The dephasing rates (γ) used in this simulation are physically relevant.
