# Production-Grade Quantum Error Correction Fundamentals

This project provides a robust and reproducible framework for exploring the fundamentals of Quantum Error Correction (QEC). It implements and rigorously compares the 3-qubit bit-flip code and the 5-qubit Shor code under a realistic, hardware-inspired noise model.

## Scientific Goal

The primary objective is to investigate the performance of different QEC codes in a controlled, simulated environment. The project is built around two key analyses:

1.  **Logical vs. Physical Qubit Performance**: A direct comparison of the fidelity of a single, unprotected "physical" qubit versus a protected "logical" qubit using the 3-qubit code.
2.  **Controlled Code Comparison**: A statistically rigorous, noise-normalized comparison between the 3-qubit and 5-qubit codes to determine if and when the more resource-intensive code provides a tangible advantage.

## Structure

The project has been refactored into a production-grade Python application with a clear and maintainable structure:

- `main.py`: The main entry point for the entire project.
- `qec.py`: Contains the core logic in two main classes:
    - `QECProject`: Encapsulates all the scientific logic, including the definitions of the QEC codes, the noise model, the experimental workflows, and the statistical analysis.
    - `ProductionEnv`: A utility class for creating a sandboxed Python virtual environment and managing dependencies via `pip-tools`.
- `requirements_production.txt`: High-level Python dependencies.
- `requirements_locked.txt`: A fully-pinned, locked list of all dependencies for maximum reproducibility.
- `test_qec.py`: A CI-friendly smoke test that verifies the core functionality.
- `final_results/data/`: This directory contains the output CSV data from the simulations.

## How to Run

To run the full analysis pipeline:
```bash
python3 projects/qec_fundamentals/main.py
```

To run a quick version for testing:
```bash
python3 projects/qec_fundamentals/main.py --quick
```

## How to Test

To run the smoke test:
```bash
python3 -m unittest projects/qec_fundamentals/test_qec.py
```
