# Final Experiment Report: The Dominance of Gate Count over Topology in Quantum Circuit Fidelity

## 1. Abstract

We investigate the hypothesis that spatially local quantum circuits are inherently more robust to noise than non-local or random circuits. Initial experiments, which did not control for gate count, showed a misleading "spatial advantage." However, a definitive follow-up experiment, enforcing strict gate-count and noise-load parity across all circuit topologies, **invalidates this hypothesis**. Our results demonstrate that, for a 6-qubit system with 7 CNOTs under a standard T1/T2 noise model, the total number of noisy two-qubit operations is the primary driver of circuit fidelity, while the specific topology (`spatial`, `non-spatial`, or `random`) has no statistically significant impact. This work serves as a case study in the critical importance of controlling for confounding variables in quantum benchmarking.

## 2. The Definitive Experiment: Enforcing Parity

To correct for a confounding variable in our initial study, we designed a new, rigorous experiment to isolate the impact of topology.

### 2.1. Methodology

-   **Constant Gate Count & Noise Load:** Three classes of 6-qubit circuits were generated, each with an identical budget of **7 CNOT gates**. The spatial circuit was padded with logically-neutral `CNOT;CNOT` pairs to ensure the number of noisy operations was identical across all topologies.
-   **Realistic Noise Model:** A standard T1/T2 noise model was applied after every `CNot` gate. (See Appendix 5.2 for details).
-   **Fidelity Metric:** We use the Hilbert–Schmidt overlap `Tr[ρσ]` as a numerically stable upper-bound proxy for the true Uhlmann fidelity. For the small depolarising rates used, this is a high-quality estimate (see Appendix 5.4).
-   **Statistical Rigor:** 10 unique, seeded instances of the random and non-spatial circuits were run on the AWS DM1 simulator to gather statistics.

### 2.2. Results: Hypothesis Invalidated

The results of the parity-check experiment were decisive. Once the CNOT count and noise load were equalized, any fidelity advantage between the topologies vanished.

![Definitive Fidelity Comparison Chart](figures/definitive_fidelity_parity_chart.png)
*Figure 1: Mean fidelities are identical across all topologies. The 95% CI, calculated from 10 random graph seeds, reflects the low variance between different random topologies, not stochastic simulator noise.*

## 3. Conclusion

The hypothesis that spatial locality provides intrinsic noise resilience is, under this model, **unsupported**. The fidelity of a quantum circuit appears to be overwhelmingly determined by the quantity of entangling operations, not their topological arrangement. This suggests that efforts to improve device performance should focus on reducing the raw error rates of two-qubit gates, as architectural choices about qubit connectivity may offer little intrinsic benefit for noise resilience on their own.

---

## 4. Appendix: Reproducibility Details

### 4.1. Core Information
-   **Code:** `final_parity_check_experiment.py`, `generate_final_plots.py`
-   **Results Data:** `results/final_parity_check_results_dm1.csv`
-   **Random Seed:** `1337`
-   **Device:** AWS Braket DM1 Simulator (`arn:aws:braket:::device/quantum-simulator/amazon/dm1`)
-   **Braket SDK Version:** `braket-sdk~=1.60.0`

### 4.2. Noise Model Implementation
The T1/T2 noise was applied using built-in Braket SDK methods, immediately following each `CNot` gate. Four Kraus operators were applied per CNOT: an amplitude damping and a phase damping channel on both the control and target qubits.

```python
# T1/T2 Noise Parameters
T1, T2, GATE_TIME = 40e-6, 60e-6, 200e-9
P_AMPLITUDE = 1 - np.exp(-GATE_TIME / T1)  # p = 0.004987...
P_DEPHASING = 1 - np.exp(-GATE_TIME / T2)  # p = 0.003328...

# For each qubit `q` involved in the CNot gate:
noisy_c.amplitude_damping(q, P_AMPLITUDE)
noisy_c.phase_damping(q, P_DEPHASING)
```

### 4.3. Fidelity Distribution (Supplementary Figure 1)
The histogram below shows the distribution of the raw fidelity values for the 10 random seeds of each non-deterministic topology. The tight clustering confirms the low variance observed in the main result.

![Fidelity Distribution Histogram](figures/supplementary_fidelity_histogram.png)

### 4.4. Fidelity Metric Justification (Supplementary Figure 2)
The plot below shows that for a representative circuit from this study, the difference between the computationally-intensive Uhlmann fidelity and the Hilbert-Schmidt overlap we use as a proxy is negligible, justifying our choice of metric.

![Fidelity Metric Comparison](figures/supplementary_metric_comparison.png)
