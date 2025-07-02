# Experiment Provenance Log

This file is intended to be a log of all cloud-based and computationally intensive experiments run as part of this case study. Maintaining a provenance log is a critical practice for scientific reproducibility, allowing researchers to track the exact parameters, code versions, and outcomes of their work.

Users of this repository are encouraged to add entries to this log when they run the scaling analysis, noisy simulations, or execute tasks on real QPUs.

---

## Log Entry Template

```markdown
**Experiment ID:** [A unique identifier, e.g., Noisy-Sim-01]
**Date:** [Date of execution, e.g., 2025-07-16]
**Script / Notebook:** [Name of the script run, e.g., `run_qaoa_with_noise.py`]
**Git Commit Hash:** [The full git commit hash at the time of execution]
**Description:** [A brief, one-sentence description of the experiment's goal.]

**Parameters:**
- **Graph:** [Description of the graph used, e.g., "4-Node Weighted Cycle"]
- **Simulator/QPU:** [The ARN or name of the device used, e.g., "braket_dm"]
- **Noise Model:** [Description of the noise model, e.g., "Depolarizing(p=0.01) on CNOTs"]
- **Optimization:** [Optimizer and parameters, e.g., "SciPy COBYLA, p=2 layers"]

**Cloud Job IDs / Task ARNs:**
- `[Task ARN if applicable]`

**Results:**
- **Key Metric (Canonical):** [e.g., "Approximation Ratio: 0.059"]
- **Key Metric (Flawed):** [e.g., "Approximation Ratio: 0.059"]
- **Conclusion:** [e.g., "Hypothesis not confirmed; noise dominated optimization."]

**Notes:**
- [Any additional observations, anomalies, or comments.]
```

---

## Example Log Entries

**Experiment ID:** Noisy-Sim-01
**Date:** 2025-07-16
**Script / Notebook:** `run_qaoa_with_noise.py`
**Git Commit Hash:** `[Example: 8a2d1e9bfe2b3c4d5a6f7g8h9i0j1k2l3m4n5o6p]`
**Description:** Initial test of the QAOA optimizers in a noisy environment.

**Parameters:**
- **Graph:** 4-Node Weighted Cycle, weights [1.5, 2.0, 0.5, 1.0]
- **Simulator/QPU:** `braket_dm` (Local Density Matrix Simulator)
- **Noise Model:** Depolarizing(p=0.01) on 2-qubit gates.
- **Optimization:** SciPy COBYLA, p=2 layers.

**Cloud Job IDs / Task ARNs:**
- N/A (Local Simulation)

**Results:**
- **Key Metric (Canonical):** Approximation Ratio: 0.059
- **Key Metric (Flawed):** Approximation Ratio: 0.059
- **Conclusion:** Hypothesis not confirmed. The flawed cost function did not lead to a measurably worse result in this specific noisy instance.

**Notes:**
- The convergence for both optimizers was very similar, suggesting the noise model created a landscape where the cost function error was not the dominant factor. 