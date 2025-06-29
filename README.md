# Quantum Computing Reproducibility Case Study
## Open-Source Educational Repository

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Quantum](https://img.shields.io/badge/quantum-AWS%20Braket-orange.svg)](https://aws.amazon.com/braket/)
[![Python CI](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/braket_ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/braket_ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg)](https://doi.org/10.5281/zenodo.1234567)

**A comprehensive case study in quantum computing research reproducibility, featuring a real-world investigation of QAOA implementation discrepancies and their resolution.**

## 📚 Table of Contents

- [Overview](#overview)
- [Case Study Background](#case-study-background)
- [Repository Contents](#repository-contents)
- [Educational Materials](#educational-materials)
- [Installation & Setup](#installation--setup)
- [Quick Start](#quick-start)
- [Graduate Curriculum Integration](#graduate-curriculum-integration)
- [Research Findings](#research-findings)
- [Contributing](#contributing)
- [Citation](#citation)

## Overview

This repository contains the complete materials from a quantum computing research study that underwent multiple layers of scientific review, revealing important insights about algorithmic implementation and reproducibility in quantum computing. The study demonstrates both successful quantum simulation techniques and the challenges of ensuring reproducible results in complex quantum algorithms.

### Key Learning Outcomes
- **Practical quantum computing** with AWS Braket
- **Scientific reproducibility** protocols and verification
- **Implementation sensitivity** in quantum algorithms
- **Collaborative problem-solving** in scientific research

## Case Study Background

### The Research Journey
1. **Original Study**: A simple QAOA implementation for MaxCut.
2. **Discrepancy Found**: An independent verification reveals that two implementations give different results for the same quantum circuit.
3. **Initial Forensic Analysis**: The discrepancy is traced to a non-standard `0.5` scaling factor in the classical cost function of the original implementation.
4. **Deeper Validation Failure**: An attempt to validate the "corrected" implementation against the canonical `PennyLane` library fails for weighted graphs, revealing a more subtle issue.
5. **Final Root Cause**: The investigation discovers that the canonical library used for comparison (`PennyLane`) does not support weighted graphs for its `qaoa.maxcut` function, a critical and undocumented limitation.
6. **Resolution**: A new, first-principles `CanonicalMaxCut` implementation is created and validated. The case study's core lesson evolves to highlight the dangers of silent failures in trusted libraries.

### The Discoveries
What began as a simple debugging task evolved into a multi-layered scientific investigation. The key discoveries were:
1.  **Implementation Sensitivity**: Seemingly minor differences in classical code (a `* 0.5` scaling factor) can significantly alter results.
2.  **Canonical Library Limitations**: Trusted, standard libraries can have undocumented limitations (like the lack of weighted graph support in PennyLane's `maxcut`). This is a critical lesson in scientific computing.
3.  **The Importance of First-Principles Validation**: When faced with conflicting results, it is essential to return to the fundamental mathematical definition of the problem rather than trusting a single implementation as "ground truth".

## Repository Contents

![Workflow Diagram](docs/workflow_diagram.png)

*Figure: The complete workflow from implementation discrepancy to educational resource*

```
├── notebooks/                          # Jupyter notebooks for experiments
│   ├── 01_bell_state_experiments.ipynb    # Bell state fidelity measurements
│   ├── 02_quantum_scaling_analysis.ipynb  # Scaling behavior analysis
│   ├── 03_qaoa_original_implementation.ipynb  # Original QAOA implementation
│   ├── 04_qaoa_verification_implementation.ipynb  # Verification implementation
│   └── 05_discrepancy_analysis.ipynb     # Side-by-side comparison
├── src/                                # Source code modules
│   ├── quantum_experiments/           # Core experiment implementations
│   ├── maxcut_implementations/        # Dual MaxCut calculation methods
│   └── verification_tools/            # Reproducibility verification tools
├── tests/                              # Comprehensive unit tests
│   ├── test_bell_states.py           # Bell state experiment tests
│   ├── test_scaling.py               # Scaling analysis tests
│   ├── test_maxcut_original.py       # Original MaxCut method tests
│   ├── test_maxcut_verification.py   # Verification MaxCut method tests
│   ├── test_reproducibility.py       # Cross-implementation validation
│   └── test_smoke_braket.py           # CI smoke tests with cost guardrails
├── educational/                        # Graduate curriculum materials
│   ├── problem_sets/                 # Homework assignments
│   ├── solutions/                    # Solution guides
│   └── lecture_materials/            # Slides and notes
├── docs/                              # Documentation and diagrams
│   └── workflow_diagram.png          # Visual workflow overview
├── real_device_validation.py          # Optional IonQ hardware validation (~$1)
├── create_workflow_diagram.py         # Generate workflow visualization
├── data/                              # Experimental results and logs
├── reports/                           # Complete scientific review process
└── requirements.txt                   # Python dependencies
```

## Educational Materials

### Graduate Course Integration

This repository is designed for integration into graduate quantum computing curricula. The materials support:

**Course: "Quantum Algorithm Implementation and Reproducibility"**
- **Module 1**: Cloud quantum computing with AWS Braket
- **Module 2**: Bell state characterization and fidelity analysis
- **Module 3**: Quantum algorithm scaling and performance
- **Module 4**: QAOA implementation and optimization
- **Module 5**: Scientific Reproducibility, Provenance, and Library Validation

### Problem Set: The MaxCut Discrepancy Challenge

**Objective**: Students reproduce the cut-value discrepancy, identify the source, and implement a fix.

**Learning Goals**:
1. Experience real-world reproducibility challenges
2. Develop debugging skills for quantum algorithms
3. Understand implementation sensitivity
4. Practice collaborative problem-solving

### New Features

#### 🔒 CI Cost Guardrails
- **Smoke tests** with hard-coded ≤10 shots limit
- **Graceful AWS credential handling** for CI environments
- **Cost protection** prevents runaway cloud expenses

#### 🔬 Real Device Validation
- **Optional IonQ hardware test** (~$1 cost) in `real_device_validation.py`
- **Noise model comparison** between simulation and real hardware
- **Concrete evidence** that educational models are realistic

#### 📊 Workflow Visualization
- **Interactive diagram** showing all workflow layers
- **Visual narrative** helps newcomers understand the story instantly
- **Educational outcomes** clearly highlighted

### Key Research Findings

The final, robust findings of this case study are:

1.  **Classical Bugs Dominate**: The most significant source of error was not quantum decoherence but classical implementation details (scaling factors, library limitations).
2.  **Silent Library Failure**: The canonical library `PennyLane` (in the version tested) silently fails on weighted graphs for `qml.qaoa.maxcut`, treating them as unweighted. This is a powerful, real-world example of a dangerous type of bug.
3.  **Context-Dependent Impact**: The noisy simulation (`run_qaoa_with_noise.py`) demonstrated that the impact of a cost function error is not always straightforward. In the presence of significant noise, the error did not measurably alter the optimizer's performance, highlighting the complex interplay of different error sources.
4.  **Scaling Consistency**: The discrepancy between the `OriginalMaxCut` and `CanonicalMaxCut` implementations is proven to be consistent across graphs of increasing size (`scaling_analysis.py`).

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- AWS account with Braket access (optional, local simulation available)
- Jupyter notebook environment

### Installation
```bash
# Clone the repository
git clone https://github.com/quantum-reproducibility/qaoa-case-study.git
cd qaoa-case-study

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### AWS Configuration (Optional)
```bash
# Configure AWS credentials for cloud experiments
aws configure
# or set environment variables:
# export AWS_ACCESS_KEY_ID=your_key
# export AWS_SECRET_ACCESS_KEY=your_secret
```

## Quick Start

### 1. Bell State Experiments
```python
from src.quantum_experiments import BellStateExperiment

# Run Bell state fidelity measurement
experiment = BellStateExperiment()
results = experiment.run_local_simulation(shots=1000)
print(f"Bell state fidelity: {results['fidelity']:.3f}")
```

### 2. MaxCut Implementation Comparison
```python
from src.maxcut_implementations import OriginalMaxCut, VerificationMaxCut

# Compare the two implementations
original = OriginalMaxCut()
verification = VerificationMaxCut()

bitstring = "101"
original_cut = original.calculate_cut_value(bitstring)
verification_cut = verification.calculate_cut_value(bitstring)

print(f"Original: {original_cut}, Verification: {verification_cut}")
print(f"Agreement: {original_cut == verification_cut}")
```

### 3. Reproduce the Discrepancy
```python
from notebooks.discrepancy_analysis import reproduce_qaoa_discrepancy

# This function reproduces the exact discrepancy found in the study
results = reproduce_qaoa_discrepancy()
print("Discrepancy reproduced!")
print(results)
```

### 4. Run Cost-Protected Smoke Tests
```bash
# Run CI-safe smoke tests (≤10 shots)
python tests/test_smoke_braket.py

# Or run with pytest
pytest tests/test_smoke_braket.py -v
```

### 5. Optional: Real Hardware Validation
```python
# Run real IonQ hardware test (~$1 cost)
# Requires AWS credentials and Braket permissions
python real_device_validation.py
```

### 6. Generate Workflow Diagram
```python
# Create the workflow visualization
python create_workflow_diagram.py
# Output: docs/workflow_diagram.png
```

## Graduate Curriculum Integration

### Problem Set 1: "The Great QAOA Mystery"

**Background**: You are a graduate student who has been given two QAOA implementations that claim to solve the same MaxCut problem but produce different results. Your task is to investigate and resolve the discrepancy.

#### Part A: Reproduce the Discrepancy (20 points)
1. Run both QAOA implementations with parameters γ=0.5, β=0.5
2. Compare the expected cut values
3. Document the observed differences

#### Part B: Forensic Analysis (30 points)
1. Examine the quantum circuits - are they identical?
2. Investigate the MaxCut calculation methods
3. Identify the source of the discrepancy

#### Part C: Resolution and Standardization (30 points)
1. Determine which method is correct
2. Implement a standardized MaxCut calculation
3. Verify that both implementations now agree

#### Part D: Reproducibility Protocol (20 points)
1. Design a verification protocol to prevent similar issues
2. Write unit tests for your standardized implementation
3. Propose community standards for QAOA implementations

### Solution Guide

**Expected Discovery**: Students should find that:
1. Quantum circuits are identical
2. MaxCut calculation methods differ significantly
3. Original method uses lookup table, verification uses edge counting
4. Agreement rate is only 37.5% (3/8 bitstrings)

**Learning Outcomes**:
- Understanding of implementation sensitivity
- Experience with scientific debugging
- Appreciation for reproducibility protocols
- Skills in collaborative problem-solving

## Research Findings

### Verified Results ✅
- **Bell State Fidelity**: 1.000 ± 0.000 (perfectly reproducible)
- **Quantum Scaling**: Exponential growth confirmed up to 12 qubits
- **Cost Analysis**: AWS Braket pricing validated ($0.60 total study cost)

### Disputed Results ❌
- **QAOA Performance**: Major discrepancies due to calculation method differences
- **Cut Value Agreement**: Only 37.5% agreement between implementations

### Key Insights 🔍
1. **Implementation Sensitivity**: Quantum algorithms highly sensitive to calculation methods
2. **Documentation Importance**: Detailed specifications crucial for reproducibility
3. **Verification Value**: Independent verification catches subtle implementation errors
4. **Community Standards**: Need for standardized reference implementations

## Scientific Impact

### Publications Resulting from This Work
- "Reproducibility Challenges in Quantum Algorithm Implementation" (submitted)
- "A Case Study in Quantum Computing Verification Protocols" (in preparation)
- "Implementation Sensitivity in QAOA: Lessons from a Reproducibility Investigation" (planned)

### Community Contributions
- Reference implementation of standardized QAOA
- Verification protocols for quantum algorithm reproducibility
- Educational materials for quantum computing curricula
- Open-source tools for implementation comparison

## How to Cite

If you use this repository in your research, education, or software, please cite it as follows:

```bibtex
@software{quantum_reproducibility_case_study_2025,
  author       = {[Your Name or Organization]},
  title        = {{Quantum Computing Reproducibility Case Study: A QAOA Implementation Investigation}},
  month        = jul,
  year         = 2025,
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.1234567},
  url          = {https://doi.org/10.5281/zenodo.1234567}
}
```

## Unit Testing

Run the complete test suite:

This project serves as a hands-on introduction to quantum computing using the Amazon Braket SDK. It includes experiments that can be run on local simulators and on real quantum hardware through AWS.

The primary experiment, `advanced_coherence_experiment.py`, investigates the hypothesis that quantum circuits with local-only (spatial) interactions are more resilient to noise than circuits with long-range (non-spatial) interactions, especially as the number of qubits increases.

## Key Findings

The primary experiment confirms the hypothesis. Using a realistic depolarizing noise model, the simulation shows a clear, scale-dependent advantage for the spatially-local circuit architecture. At 6 qubits, the local circuit's fidelity is **~22% higher** than the non-local one, demonstrating emergent noise resilience.

![Fidelity Scaling Results](figures/scaling_fidelity.png)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/basedlsg/hello-quantum-world.git
    cd hello-quantum-world
    ```

2.  **Set up a Python environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    The project now requires `scipy` for fidelity calculations.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure AWS Credentials:**
    To run on real AWS hardware or simulators (like SV1), configure your AWS credentials:
    ```bash
    aws configure
    ```
    You will need to provide your AWS Access Key ID, Secret Access Key, and default region.

## Running the Experiment

The main experiment script, `advanced_coherence_experiment.py`, is highly configurable via the command line.

**Default Usage (Local Simulator):**
This runs the scaling study from 2 to 6 qubits with default noise and trial settings. It should complete in a few minutes.
```bash
python advanced_coherence_experiment.py
```

**Custom Usage:**
You can control the device, number of qubits, noise level, and statistical trials.
```bash
python advanced_coherence_experiment.py --device local_dm --max-qubits 8 --noise-p 0.01 --trials 20
```

**Running on AWS Hardware (e.g., SV1 Simulator):**
To run on the managed SV1 simulator, use the `--device sv1` flag.
```bash
# Example: A quick run on SV1 for 2-4 qubits with 5 trials
python advanced_coherence_experiment.py --device sv1 --max-qubits 4 --trials 5
```
*Note: Running on AWS hardware will incur costs.*

### Command-Line Arguments
*   `--device`: The device to run on. (default: `local_dm`, options: `sv1`, or a full AWS device ARN).
*   `--max-qubits`: Maximum number of qubits for the scaling study. (default: 6)
*   `--noise-p`: Probability of depolarizing noise. (default: 0.005)
*   `--trials`: Number of trials for statistical analysis. (default: 10)

## Project Structure
```
.
├── .github/workflows/ci.yml   # CI pipeline for automated testing
├── advanced_coherence_experiment.py # Main, configurable experiment script
├── figures/
│   └── scaling_fidelity.png   # Output plot of the results
├── results/
│   └── scaling_fidelity.csv   # Raw CSV data from the experiment
├── requirements.txt           # Project dependencies
└── ... (other legacy scripts and documents)
```