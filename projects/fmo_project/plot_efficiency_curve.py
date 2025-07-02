"""
Plot FMO Transport Efficiency vs Dephasing Rate

This script loads the sweep results and creates publication-quality plots
showing the noise-assisted transport phenomenon.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_efficiency_curve(csv_path="sweep_local_dm.csv", dm1_path="dm1_check.csv"):
    """Plot efficiency vs gamma with optional DM1 confirmation points."""
    
    # Load local simulation data
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run the sweep first.")
        return
    
    df_local = pd.read_csv(csv_path)
    
    # Set up the plot
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Plot local simulation curve
    plt.plot(df_local['gamma_ps'], df_local['efficiency'], 'b-o', 
             label='Local Simulation', linewidth=2, markersize=6)
    
    # Add DM1 confirmation points if available
    if os.path.exists(dm1_path):
        df_dm1 = pd.read_csv(dm1_path)
        plt.plot(df_dm1['gamma_ps'], df_dm1['efficiency'], 'rs', 
                 label='AWS DM1 Confirmation', markersize=8, markeredgewidth=2)
        print(f"Added {len(df_dm1)} DM1 confirmation points")
    
    # Formatting
    plt.xlabel('Dephasing Rate γ (ps⁻¹)', fontsize=12)
    plt.ylabel('Transport Efficiency (Population at Sink)', fontsize=12)
    plt.title('FMO Noise-Assisted Transport (4-Qubit Model)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    # Add annotations
    max_idx = df_local['efficiency'].idxmax()
    max_gamma = df_local.loc[max_idx, 'gamma_ps']
    max_eff = df_local.loc[max_idx, 'efficiency']
    
    plt.annotate(f'Peak: γ = {max_gamma:.1f} ps⁻¹\nEfficiency = {max_eff:.3f}',
                xy=(max_gamma, max_eff), xytext=(max_gamma + 20, max_eff + 0.02),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                fontsize=10, ha='left',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Set reasonable axis limits
    plt.xlim(-5, max(df_local['gamma_ps']) + 10)
    plt.ylim(0, max(df_local['efficiency']) * 1.1)
    
    # Save the plot
    output_path = "efficiency_vs_gamma_4Q.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {output_path}")
    
    # Show summary statistics
    print(f"\nSummary Statistics:")
    print(f"  Gamma range: {df_local['gamma_ps'].min():.1f} - {df_local['gamma_ps'].max():.1f} ps⁻¹")
    print(f"  Efficiency range: {df_local['efficiency'].min():.4f} - {df_local['efficiency'].max():.4f}")
    print(f"  Peak efficiency: {max_eff:.4f} at γ = {max_gamma:.1f} ps⁻¹")
    
    # Check for noise enhancement
    gamma_zero_eff = df_local[df_local['gamma_ps'] == 0]['efficiency'].iloc[0]
    enhancement = (max_eff - gamma_zero_eff) / gamma_zero_eff * 100
    print(f"  Enhancement over noiseless: {enhancement:.1f}%")
    
    if enhancement >= 3.0:
        print(f"  ✅ SUCCESS: Enhancement ≥ 3% threshold!")
    else:
        print(f"  ⚠️  Enhancement below 3% threshold")
    
    plt.show()
    
    return df_local

def plot_comparison_histogram(csv_path="sweep_local_dm.csv", dm1_path="dm1_check.csv"):
    """Create a histogram comparing local vs DM1 results."""
    
    if not os.path.exists(csv_path) or not os.path.exists(dm1_path):
        print("Both local and DM1 data needed for comparison histogram")
        return
    
    df_local = pd.read_csv(csv_path)
    df_dm1 = pd.read_csv(dm1_path)
    
    # Merge on gamma values for comparison
    df_merged = pd.merge(df_local, df_dm1, on='gamma_ps', suffixes=('_local', '_dm1'))
    
    if len(df_merged) == 0:
        print("No matching gamma values between local and DM1 data")
        return
    
    # Calculate differences
    df_merged['diff'] = df_merged['efficiency_dm1'] - df_merged['efficiency_local']
    df_merged['rel_diff_pct'] = df_merged['diff'] / df_merged['efficiency_local'] * 100
    
    plt.figure(figsize=(8, 5))
    plt.hist(df_merged['rel_diff_pct'], bins=5, alpha=0.7, color='green', edgecolor='black')
    plt.xlabel('Relative Difference (%)', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title('Local vs DM1 Efficiency Comparison', fontsize=14)
    plt.axvline(0, color='red', linestyle='--', label='Perfect Agreement')
    plt.legend()
    
    plt.savefig("dm1_comparison_histogram.png", dpi=300, bbox_inches='tight')
    print(f"Comparison histogram saved to dm1_comparison_histogram.png")
    
    print(f"\nDM1 vs Local Comparison:")
    print(f"  Mean relative difference: {df_merged['rel_diff_pct'].mean():.2f}%")
    print(f"  Max absolute difference: {df_merged['rel_diff_pct'].abs().max():.2f}%")
    
    plt.show()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Plot FMO efficiency curves")
    parser.add_argument("--local_data", type=str, default="sweep_local_dm.csv")
    parser.add_argument("--dm1_data", type=str, default="dm1_check.csv")
    parser.add_argument("--comparison", action="store_true", 
                       help="Also create comparison histogram")
    
    args = parser.parse_args()
    
    # Main efficiency plot
    df = plot_efficiency_curve(args.local_data, args.dm1_data)
    
    # Optional comparison histogram
    if args.comparison:
        plot_comparison_histogram(args.local_data, args.dm1_data)

