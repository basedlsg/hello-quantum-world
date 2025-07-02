#!/bin/bash
#
# run_all.sh
#
# This script runs the complete, polished analysis for the FMO
# noise-assisted transport project. It ensures full reproducibility
# by setting up a clean environment, running all simulations and
# checks, and generating all final figures.
#

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
PYTHON_ENV_NAME="fmo_env"
PYTHON_VERSION="3.10"
REQUIREMENTS_FILE="requirements.txt"
# Corrected package list: AWS provider is included in the SDK.
PACKAGES_TO_INSTALL="amazon-braket-sdk numpy pandas scipy matplotlib seaborn"
FINAL_RESULTS_DIR="final_results"
MAIN_SCRIPT="run_fmo_polished.py"
CLASSICAL_SCRIPT="classical_benchmark.py"
PLOT_SCRIPT="plot_final_results.py"
HW_SCRIPT="hardware_transpile_check.py"

# --- Script Start ---
echo "=========================================================="
echo "  FMO Noise-Assisted Transport: Full Analysis Pipeline"
echo "=========================================================="

# 1. Environment Setup
echo -e "\n[1/5] Setting up Python virtual environment..."
if [ -d "$PYTHON_ENV_NAME" ]; then
    echo "  > Environment '$PYTHON_ENV_NAME' already exists. Removing for a clean start."
    rm -rf $PYTHON_ENV_NAME
fi
echo "  > Creating new environment..."
python$PYTHON_VERSION -m venv $PYTHON_ENV_NAME

# Activate the environment
source $PYTHON_ENV_NAME/bin/activate
echo "  > Installing latest compatible packages..."
pip install -q --upgrade pip
pip install -q $PACKAGES_TO_INSTALL

echo "  > Freezing working versions to $REQUIREMENTS_FILE..."
pip freeze | grep -E "amazon-braket-sdk|numpy|pandas|scipy|matplotlib" > $REQUIREMENTS_FILE

echo "  > Environment setup complete."

# 2. Run Simulations & Checks
echo -e "\n[2/5] Running Quantum Simulation and Validation Checks..."
# The main script will perform the primary simulation, the dt/2 convergence
# check, and the stability test, saving results to CSV files.
python $MAIN_SCRIPT

# 3. Run Classical Benchmark
echo -e "\n[3/5] Running Classical Random Walk Benchmark..."
python $CLASSICAL_SCRIPT

# 4. Generate All Final Figures
echo -e "\n[4/6] Generating all final figures..."
python $PLOT_SCRIPT

# 5. Generate Convergence Plot
echo -e "\n[5/6] Generating convergence analysis plot..."
python generate_convergence_plot.py

# 6. Hardware Feasibility Check
echo -e "\n[6/7] Running Hardware Transpilation Check..."
python $HW_SCRIPT

# 7. Generate Final Report
echo -e "\n[7/7] Generating final summary report..."
python generate_report.py

# --- Completion ---
echo -e "\n========================================================"
echo "  ✅ PIPELINE COMPLETE"
echo "  Final figures are in: 'final_results/figures/'"
echo "  Final report is: 'results_summary.md'"
echo "========================================================"

# Deactivate the environment
deactivate 