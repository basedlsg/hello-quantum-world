# plot_final_results.py
#
# This script generates the final, publication-quality figures for the FMO
# project. It reads the data from the quantum and classical simulations
# and creates a comparative plot to highlight the noise-assisted transport
# phenomenon.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DATA_DIR = "final_results/data"
FIGURES_DIR = "final_results/figures"
os.makedirs(FIGURES_DIR, exist_ok=True)

# Use a color-blind friendly and aesthetically pleasing style
plt.style.use('seaborn-v0_8-colorblind')

# --- Main Plotting Function ---
def create_comparison_plot(quantum_df, classical_df, aws_df=None):
    """
    Creates and saves the main figure comparing quantum and classical transport.
    Optionally overlays AWS validation points.
    """
    logging.info("Generating main comparison plot...")
    
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot Quantum Results (Local Simulation)
    ax.plot(quantum_df['gamma_ps_inv'], quantum_df['efficiency'],
            marker='o', linestyle='-', label='Quantum Transport (Local DM Simulator)')

    # Plot Classical Results
    ax.plot(classical_df['gamma_ps_inv'], classical_df['classical_efficiency'],
            marker='s', linestyle='--', label='Classical Random Walk (Benchmark)')

    # Plot AWS Validation Points if available
    if aws_df is not None and not aws_df.empty:
        # Match colors for clarity
        q_color = ax.get_lines()[0].get_color()
        ax.plot(aws_df['gamma_ps_inv'], aws_df['aws_efficiency'],
                'X', markersize=14, mew=2.5,
                label='Quantum Transport (AWS DM1 Cloud Sim)',
                linestyle='none', c=q_color, zorder=10,
                markeredgecolor='white')

    # --- Formatting and Labels ---
    ax.set_title('Noise-Assisted Transport in an FMO-like System', fontsize=18, weight='bold')
    ax.set_xlabel('Dephasing Rate γ (ps⁻¹)', fontsize=14)
    ax.set_ylabel('Transport Efficiency to Sink', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.6)
    ax.tick_params(axis='both', which='major', labelsize=12)

    # --- Annotations for Key Results ---
    # Find the point of minimum efficiency (where noise is most destructive)
    min_idx = quantum_df['efficiency'].idxmin()
    min_gamma = quantum_df.loc[min_idx, 'gamma_ps_inv']
    min_eff = quantum_df.loc[min_idx, 'efficiency']

    # Efficiency at the highest noise level
    final_eff = quantum_df['efficiency'].iloc[-1]
    
    # Calculate the enhancement percentage
    enhancement = (final_eff - min_eff) / min_eff * 100
    
    ax.annotate(f'Noise-Assisted Enhancement:\nη rises from {min_eff:.3f} to {final_eff:.3f}\n(a {enhancement:+.1f}% increase)',
                xy=(quantum_df['gamma_ps_inv'].iloc[-1], final_eff),
                xytext=(min_gamma - 10, final_eff + 0.15),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8, connectionstyle="arc3,rad=0.2"),
                bbox=dict(boxstyle="round,pad=0.4", fc="lightgoldenrodyellow", ec="gray", alpha=0.9),
                fontsize=11, weight='bold')

    # Annotate the minimum
    ax.annotate(f'Minimum η = {min_eff:.3f}',
                xy=(min_gamma, min_eff),
                xytext=(min_gamma, min_eff - 0.12),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                ha='center',
                fontsize=10)

    plt.tight_layout()

    # Save the figure
    output_path = os.path.join(FIGURES_DIR, "Fig1_Quantum_vs_Classical_Transport_Final.png")
    fig.savefig(output_path, dpi=300)
    logging.info(f"Final figure saved to {output_path}")
    plt.close(fig)

def create_leakage_plot(quantum_df):
    """
    Creates and saves a figure showing the population leakage from the
    single-excitation subspace vs. the dephasing rate.
    """
    logging.info("Generating leakage plot...")
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(quantum_df['gamma_ps_inv'], quantum_df['leakage'],
            marker='.', linestyle='-', label='Subspace Leakage')
    
    ax.set_title('Population Leakage vs. Dephasing Rate', fontsize=16)
    ax.set_xlabel('Dephasing Rate γ (ps⁻¹)', fontsize=12)
    ax.set_ylabel('Leakage (1 - P_single_excitation)', fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Use scientific notation for the y-axis as leakage is very small
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    plt.tight_layout()
    
    output_path = os.path.join(FIGURES_DIR, "Fig2_Leakage_Analysis.png")
    fig.savefig(output_path, dpi=300)
    logging.info(f"Leakage plot saved to {output_path}")
    plt.close(fig)

# --- Execution ---
if __name__ == "__main__":
    logging.info("--- Generating Final Publication Figure ---")
    
    # Define data paths
    quantum_data_path = os.path.join(DATA_DIR, "quantum_transport_results.csv")
    classical_data_path = os.path.join(DATA_DIR, "classical_transport_results.csv")
    aws_data_path = os.path.join(DATA_DIR, "aws_validation_results.csv")
    
    try:
        df_quantum = pd.read_csv(quantum_data_path)
        df_classical = pd.read_csv(classical_data_path)
    except FileNotFoundError as e:
        logging.error(f"Critical data file not found: {e}. Please run `bash run_all.sh` first.")
        exit(1)

    # Load AWS data if it exists, but don't fail if it doesn't
    df_aws = None
    try:
        df_aws = pd.read_csv(aws_data_path)
        logging.info("Successfully loaded AWS validation data.")
    except FileNotFoundError:
        logging.warning("AWS validation data not found. Plotting local & classical results only.")

    # Create the main plot
    create_comparison_plot(df_quantum, df_classical, df_aws)

    # Create the leakage analysis plot
    create_leakage_plot(df_quantum)

    logging.info("--- ✅ Plotting process complete. ---")
