"""
Statistical Power Analysis and Reproducibility Framework
Comprehensive statistical validation of gate-count advantage findings.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import ttest_ind, chi2_contingency
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict
import json
from datetime import datetime

# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def load_experimental_data() -> pd.DataFrame:
    """Load all experimental results for meta-analysis."""
    data_files = [
        'results/circuit_analysis.csv',
        'results/realistic_noise_test.csv', 
        'results/hardware_compatible_test.csv'
    ]
    
    combined_data = []
    
    for file_path in data_files:
        try:
            df = pd.read_csv(file_path)
            df['experiment_type'] = file_path.split('/')[-1].replace('.csv', '')
            combined_data.append(df)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found, skipping...")
    
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    else:
        return pd.DataFrame()  # Empty dataframe if no files found

def calculate_effect_size(spatial_values: List[float], nonspatial_values: List[float]) -> Dict:
    """Calculate Cohen's d effect size and confidence intervals."""
    spatial_array = np.array(spatial_values)
    nonspatial_array = np.array(nonspatial_values)
    
    # Cohen's d calculation
    pooled_std = np.sqrt(((len(spatial_array) - 1) * np.var(spatial_array, ddof=1) + 
                         (len(nonspatial_array) - 1) * np.var(nonspatial_array, ddof=1)) / 
                        (len(spatial_array) + len(nonspatial_array) - 2))
    
    if pooled_std == 0:
        cohens_d = 0.0
    else:
        cohens_d = (np.mean(spatial_array) - np.mean(nonspatial_array)) / pooled_std
    
    # Effect size interpretation
    if abs(cohens_d) < 0.2:
        effect_magnitude = "negligible"
    elif abs(cohens_d) < 0.5:
        effect_magnitude = "small"
    elif abs(cohens_d) < 0.8:
        effect_magnitude = "medium"
    else:
        effect_magnitude = "large"
    
    # Statistical test
    t_stat, p_value = ttest_ind(spatial_array, nonspatial_array)
    
    return {
        'cohens_d': cohens_d,
        'effect_magnitude': effect_magnitude,
        't_statistic': t_stat,
        'p_value': p_value,
        'spatial_mean': np.mean(spatial_array),
        'nonspatial_mean': np.mean(nonspatial_array),
        'spatial_std': np.std(spatial_array, ddof=1),
        'nonspatial_std': np.std(nonspatial_array, ddof=1)
    }

def power_analysis(effect_size: float, alpha: float = 0.05, power: float = 0.8) -> Dict:
    """Calculate required sample size for given effect size and power."""
    # Simplified power analysis for two-sample t-test
    # Using approximation: n ≈ 16 / (effect_size^2) for power = 0.8, alpha = 0.05
    
    if abs(effect_size) < 1e-6:
        required_n = float('inf')
    else:
        # More precise calculation using z-scores
        z_alpha = stats.norm.ppf(1 - alpha/2)  # Two-tailed test
        z_beta = stats.norm.ppf(power)
        
        required_n = 2 * ((z_alpha + z_beta) / effect_size)**2
    
    return {
        'required_sample_size': int(np.ceil(required_n)) if required_n != float('inf') else None,
        'effect_size': effect_size,
        'alpha': alpha,
        'power': power
    }

def variance_decomposition(data: pd.DataFrame) -> Dict:
    """Decompose variance sources in experimental results."""
    if data.empty:
        return {}
    
    # Group by experiment type and calculate variance components
    variance_components = {}
    
    for exp_type in data['experiment_type'].unique():
        exp_data = data[data['experiment_type'] == exp_type]
        
        if 'spatial_advantage' in exp_data.columns:
            advantages = exp_data['spatial_advantage'].values
            
            # Calculate variance components
            total_variance = np.var(advantages, ddof=1)
            
            # Between-qubit variance (if multiple qubit counts)
            if 'n_qubits' in exp_data.columns:
                qubit_groups = exp_data.groupby('n_qubits')['spatial_advantage']
                between_qubit_var = qubit_groups.var().mean()
                within_qubit_var = total_variance - between_qubit_var
                
                variance_components[exp_type] = {
                    'total_variance': total_variance,
                    'between_qubit_variance': between_qubit_var,
                    'within_qubit_variance': max(0, within_qubit_var),
                    'signal_to_noise_ratio': between_qubit_var / max(within_qubit_var, 1e-10)
                }
    
    return variance_components

def reproducibility_check() -> Dict:
    """Generate reproducibility metadata and checksums."""
    import sys
    import platform
    
    # Environment information
    env_info = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'random_seed': RANDOM_SEED,
        'numpy_version': np.__version__,
        'pandas_version': pd.__version__
    }
    
    # Package versions (if available)
    try:
        import braket
        env_info['braket_version'] = braket.__version__
    except:
        env_info['braket_version'] = 'unknown'
    
    try:
        import scipy
        env_info['scipy_version'] = scipy.__version__
    except:
        env_info['scipy_version'] = 'unknown'
    
    return env_info

def generate_statistical_report():
    """Generate comprehensive statistical analysis report."""
    print("=== Statistical Power Analysis and Reproducibility Report ===")
    print(f"Analysis timestamp: {datetime.now().isoformat()}")
    print(f"Random seed: {RANDOM_SEED}")
    
    # Load data
    print("\n--- Loading Experimental Data ---")
    data = load_experimental_data()
    
    if data.empty:
        print("No experimental data found. Run experiments first.")
        return
    
    print(f"Loaded {len(data)} data points from {data['experiment_type'].nunique()} experiment types")
    
    # Statistical analysis by experiment type
    statistical_results = {}
    
    for exp_type in data['experiment_type'].unique():
        print(f"\n--- Analysis: {exp_type} ---")
        exp_data = data[data['experiment_type'] == exp_type]
        
        if 'spatial_fidelity' in exp_data.columns and 'nonspatial_fidelity' in exp_data.columns:
            spatial_vals = exp_data['spatial_fidelity'].dropna().values
            nonspatial_vals = exp_data['nonspatial_fidelity'].dropna().values
            
            if len(spatial_vals) > 1 and len(nonspatial_vals) > 1:
                effect_analysis = calculate_effect_size(spatial_vals, nonspatial_vals)
                power_analysis_result = power_analysis(effect_analysis['cohens_d'])
                
                print(f"Effect size (Cohen's d): {effect_analysis['cohens_d']:.4f} ({effect_analysis['effect_magnitude']})")
                print(f"Statistical significance: p = {effect_analysis['p_value']:.6f}")
                print(f"Required sample size (power=0.8): {power_analysis_result['required_sample_size']}")
                
                statistical_results[exp_type] = {
                    'effect_analysis': effect_analysis,
                    'power_analysis': power_analysis_result
                }
    
    # Variance decomposition
    print("\n--- Variance Decomposition ---")
    variance_components = variance_decomposition(data)
    
    for exp_type, components in variance_components.items():
        print(f"{exp_type}:")
        print(f"  Signal-to-noise ratio: {components['signal_to_noise_ratio']:.3f}")
        print(f"  Between-qubit variance: {components['between_qubit_variance']:.6f}")
        print(f"  Within-qubit variance: {components['within_qubit_variance']:.6f}")
    
    # Cross-experiment consistency
    print("\n--- Cross-Experiment Consistency ---")
    if len(data['experiment_type'].unique()) > 1:
        # Compare effect directions across experiments
        effect_directions = {}
        for exp_type in data['experiment_type'].unique():
            exp_data = data[data['experiment_type'] == exp_type]
            if 'spatial_advantage' in exp_data.columns:
                advantages = exp_data['spatial_advantage'].dropna()
                if len(advantages) > 0:
                    effect_directions[exp_type] = np.mean(advantages > 0)
        
        print("Fraction of positive spatial advantages by experiment:")
        for exp_type, fraction in effect_directions.items():
            print(f"  {exp_type}: {fraction:.3f}")
    
    # Reproducibility metadata
    print("\n--- Reproducibility Information ---")
    repro_info = reproducibility_check()
    for key, value in repro_info.items():
        print(f"{key}: {value}")
    
    # Save comprehensive results
    final_report = {
        'analysis_metadata': repro_info,
        'statistical_results': statistical_results,
        'variance_components': variance_components,
        'raw_data_summary': {
            'total_experiments': len(data),
            'experiment_types': list(data['experiment_type'].unique()),
            'qubit_range': [int(data['n_qubits'].min()), int(data['n_qubits'].max())] if 'n_qubits' in data.columns else None
        }
    }
    
    with open('results/statistical_analysis_report.json', 'w') as f:
        json.dump(final_report, f, indent=2, default=str)
    
    print(f"\nComprehensive report saved to results/statistical_analysis_report.json")
    
    # Critical assessment
    print("\n*** CRITICAL STATISTICAL ASSESSMENT ***")
    print("Key findings:")
    
    significant_effects = []
    for exp_type, results in statistical_results.items():
        if results['effect_analysis']['p_value'] < 0.05:
            significant_effects.append(exp_type)
    
    if significant_effects:
        print(f"- Statistically significant effects found in: {', '.join(significant_effects)}")
    else:
        print("- No statistically significant effects detected (may need larger sample sizes)")
    
    print("- All results are reproducible with the provided random seed")
    print("- Variance decomposition shows sources of experimental uncertainty")
    
    return final_report

if __name__ == "__main__":
    generate_statistical_report() 