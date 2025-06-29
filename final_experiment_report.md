# Final Experiment Report: Spatial vs. Non-Spatial Quantum Coherence

## 1. Introduction & Hypothesis

This report details the findings of a computational experiment designed to test the hypothesis that quantum systems with **spatially local interactions** are inherently more resilient to decoherence than systems with non-local (or "non-spatial") interactions.

The core idea, proposed during our discussions, was that the stability observed in the classical world emerges from spatially-constrained quantum phenomena. We hypothesized that by mimicking this spatial locality in a quantum circuit, we might observe greater stability compared to a standard, non-spatially-aware circuit like a Greenberger–Horne–Zeilinger (GHZ) state, which relies on fragile, long-range entanglement.

## 2. Experimental Design

To test this hypothesis, we developed a Python script (`spatial_coherence_experiment.py`) using the AWS Braket SDK's local simulator. The experiment was designed to directly address the feedback from a mock scientific committee review.

### 2.1. Circuit Definitions

We defined two types of quantum circuits:

-   **Spatial Circuit:** Entanglement was established only between **adjacent qubits** (e.g., `CNOT(0,1)`, `CNOT(1,2)`). This represents a system with local, nearest-neighbor interactions, acting as a proxy for physical spatial relationships.
-   **Non-Spatial Circuit:** Entanglement was established between **all non-adjacent qubit pairs** (e.g., `CNOT(0,2)`, `CNOT(0,3)`, `CNOT(1,3)`). This represents a system with non-local interactions, similar to a GHZ state.

### 2.2. Experimental Phases

The experiment was conducted in three phases:

1.  **Phase 1: Coherence vs. Noise:** Both circuit types were subjected to increasing levels of simulated environmental noise. We measured their final state fidelity to see which one degraded faster.
2.  **Phase 2: Scaling Study:** The number of qubits was increased from 2 to 6 with a fixed level of noise to see if any stability advantage for the spatial circuit emerged at a larger scale.
3.  **Phase 3: Statistical Analysis:** The core experiment was repeated multiple times to ensure the results were statistically significant and not due to random chance.

## 3. Results

The experiment was executed successfully. The numerical output provided a clear, unambiguous answer to our research question *within the constraints of this simulation*.

### 3.1. Key Observations

-   **No Significant Difference:** Across all three phases, the measured fidelities of the spatial and non-spatial circuits were nearly identical.
-   **Statistical Insignificance:** The minor differences that were observed were smaller than the statistical error margins (standard deviation), meaning they are not statistically significant.
-   **Null Result:** The experiment **failed to provide evidence** supporting the hypothesis that the spatial circuit is more resilient to noise. As noise and qubit count increased, both systems lost coherence at a similar rate.

| Phase                       | Finding                                                                              | Conclusion                                             |
| --------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| **1. Coherence vs. Noise**  | Both circuits showed >99.5% fidelity; difference was negligible.                      | No advantage for spatial circuit.                      |
| **2. Scaling Study**        | Both circuits degraded similarly as qubit count increased.                           | No emergent advantage at larger scale.                 |
| **3. Statistical Analysis** | Average fidelities were statistically identical; differences were within error margin. | The null result is statistically robust.               |

## 4. Conclusion & Future Work

This investigation serves as a perfect example of the scientific method in action. We began with a creative and intuitive hypothesis, refined it based on critical feedback, and designed a rigorous experiment to test it. The result was a **null finding**, which in science is not a failure, but a valuable piece of knowledge. We have learned that, at least within this specific theoretical model, circuit topology alone does not confer the expected resilience.

### 4.1. Limitations

It is crucial to acknowledge the limitations of this experiment:

-   **Simplified Models:** We used a very basic noise model and a circuit-based proxy for "spatial" effects. Real-world quantum systems have much more complex error channels and genuine 3D spatial properties.
-   **Scale:** The simulation was limited to a small number of qubits. It's theoretically possible that the hypothesized effect only appears at a much larger scale.

### 4.2. Future Directions

This null result points toward more refined research questions:

1.  **Advanced Models:** Would a more sophisticated simulation, using physically accurate noise models from real QPUs and modeling 3D qubit positions, yield a different result?
2.  **Different Architectures:** Would this effect be more pronounced in a different qubit modality, like neutral atoms, where spatial position is a key degree of freedom?

This concludes our formal investigation into this specific hypothesis. 