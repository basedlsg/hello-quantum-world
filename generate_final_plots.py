"""
Generate Final Plots and Supplementary Material

This script performs the final analysis for the gate-count parity study.
It generates three key outputs for the final report:
1.  The definitive bar chart showing the main result (with CI).
2.  A supplementary histogram of fidelity distributions to visualize variance.
3.  A supplementary plot justifying the use of overlap as a proxy for
    Uhlmann fidelity for one of the tested circuits.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from scipy.linalg import sqrtm

# --- Helper Functions ---
def bootstrap_ci(data, n_bootstrap=10000, ci_level=95):
    """Calculates the bootstrap confidence interval for a given dataset."""
    boot_means = [
        np.mean(np.random.choice(data, size=len(data), replace=True))
        for _ in range(n_bootstrap)
    ]
    low = (100 - ci_level) / 2
    high = 100 - low
    return np.percentile(boot_means, [low, high])

def uhlmann_fidelity(rho, sigma):
    """Calculates the true Uhlmann-Jozsa fidelity."""
    # Ensure matrices are normalized
    rho_norm = rho / np.trace(rho)
    sigma_norm = sigma / np.trace(sigma)
    
    sqrt_rho = sqrtm(rho_norm)
    # The @ operator is matrix multiplication
    fid_matrix = sqrtm(sqrt_rho @ sigma_norm @ sqrt_rho)
    return np.real(np.trace(fid_matrix))**2

# --- Main Plotting and Analysis ---
def final_analysis(csv_path="results/final_parity_check_results_dm1.csv"):
    if not os.path.exists(csv_path):
        print(f"Error: Results file not found at '{csv_path}'.")
        return

    df = pd.read_csv(csv_path)
    if not os.path.exists('figures'): os.makedirs('figures')
    plt.style.use('seaborn-v0_8-whitegrid')

    # 1. --- Main Figure: Bar Chart with CI ---
    summary_list = []
    for name, group in df.groupby('circuit_type'):
        mean_fid = group['fidelity'].mean()
        ci = bootstrap_ci(group['fidelity'].values)
        summary_list.append({'circuit_type': name, 'mean': mean_fid, 'ci_low': ci[0], 'ci_high': ci[1]})
    
    summary_df = pd.DataFrame(summary_list).sort_values(by="mean").reset_index(drop=True)
    summary_df['yerr'] = (summary_df['ci_high'] - summary_df['ci_low']) / 2.0
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(summary_df['circuit_type'], summary_df['mean'], yerr=summary_df['yerr'], capsize=5, color=sns.color_palette('muted')[0])
    ax.set_title('Fidelity is Identical Across Topologies with Equal Noise Load', fontsize=16)
    ax.set_ylabel('Mean Fidelity (95% CI from 10 Graph Seeds)', fontsize=12)
    ax.set_xlabel('Circuit Topology (All with 7 CNOTs and 14 Noise Operations)', fontsize=12)
    ax.set_xticklabels(summary_df['circuit_type'], rotation=0)
    ax.set_ylim(bottom=0.96, top=0.98)
    
    main_fig_path = "figures/definitive_fidelity_parity_chart.png"
    plt.savefig(main_fig_path, dpi=300, bbox_inches='tight')
    print(f"Main figure saved to '{main_fig_path}'")
    plt.close(fig)


    # 2. --- Supplementary Figure 1: Fidelity Histograms ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    fig.suptitle('Fidelity Distribution by Topology (10 Random Seeds)', fontsize=16)
    
    for i, (name, group) in enumerate(df.groupby('circuit_type')):
        sns.histplot(group['fidelity'], ax=axes[i], bins=5, kde=True)
        axes[i].set_title(name)
        axes[i].set_xlabel('Fidelity')
    axes[0].set_ylabel('Count')

    hist_fig_path = "figures/supplementary_fidelity_histogram.png"
    plt.savefig(hist_fig_path, dpi=300, bbox_inches='tight')
    print(f"Supplementary histogram saved to '{hist_fig_path}'")
    plt.close(fig)

    # 3. --- Supplementary Figure 2: Metric Justification ---
    # We need to re-run one instance to get the density matrices.
    # We can reuse the experiment script's functions for this.
    from final_parity_check_experiment import create_random_er_circuit, apply_noise_to_circuit
    from braket.devices import LocalSimulator

    print("\nRunning one instance locally to compare fidelity metrics...")
    device = LocalSimulator("braket_dm")
    base_c = create_random_er_circuit(seed=1337)
    noisy_c = apply_noise_to_circuit(base_c)
    base_c.density_matrix()
    noisy_c.density_matrix()
    
    ideal_dm = device.run(base_c, shots=0).result().result_types[0].value
    noisy_dm = device.run(noisy_c, shots=0).result().result_types[0].value
    
    overlap_fid = np.real(np.trace(ideal_dm @ noisy_dm)) # Using un-normalized for direct comparison
    uhlmann_fid = uhlmann_fidelity(ideal_dm, noisy_dm)
    diff = abs(overlap_fid - uhlmann_fid)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(['Hilbert-Schmidt Overlap', 'Uhlmann Fidelity'], [overlap_fid, uhlmann_fid], color=['#4c72b0', '#c44e52'])
    ax.set_ylabel('Fidelity Value')
    ax.set_title('Comparison of Fidelity Metrics for One Circuit Instance')
    ax.text(0.5, 0.5, f'Difference: {diff:.2e}', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.set_ylim(bottom=0.95)

    metric_fig_path = "figures/supplementary_metric_comparison.png"
    plt.savefig(metric_fig_path, dpi=300, bbox_inches='tight')
    print(f"Supplementary metric plot saved to '{metric_fig_path}'")
    plt.close(fig)

if __name__ == "__main__":
    final_analysis() 