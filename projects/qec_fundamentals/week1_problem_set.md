# Week 1 Problem Set: 3-Qubit Bit-Flip Code Fundamentals

**Course**: QEC Fundamentals with AWS Braket  
**Week**: 1 of 8  
**Prerequisites**: Completed spatial locality experiments, familiar with T1/T2 noise models  
**Time Estimate**: 4-6 hours  
**AWS Budget**: $0.00-0.50 (primarily local simulation)

## 🎯 Learning Objectives

By completing this problem set, you will:
- **Implement** 3-qubit bit-flip error correction from first principles
- **Analyze** syndrome detection and error identification
- **Compare** logical vs physical qubit performance under realistic noise
- **Investigate** QEC advantage thresholds and resource overhead
- **Apply** your existing noise modeling expertise to QEC

## 📚 Background Reading

### **Required**
- Your `final_experiment_report.md`: Methodology for controlling confounding variables
- Your `realistic_noise_test.py`: T1/T2 noise implementation patterns
- Nielsen & Chuang Chapter 10.1-10.3: QEC Basics

### **Recommended**
- Your `final_parity_check_experiment.py`: Systematic experimental design
- Gottesman: "Stabilizer Codes and Quantum Error Correction" (Sections 1-2)

---

## Problem 1: Syndrome Table Verification (25 points)

### **Context**
The 3-qubit bit-flip code uses syndrome measurements to identify error locations. Your task is to verify the syndrome detection works correctly.

### **Background Theory**
For the encoding |0⟩ₗ = |000⟩, |1⟩ₗ = |111⟩, syndrome measurements are:
- S₁ = q₀ ⊕ q₁ (parity of first two qubits)
- S₂ = q₁ ⊕ q₂ (parity of last two qubits)

### **Task 1.1: Manual Syndrome Calculation (10 points)**

Complete this syndrome lookup table:

| State After Error | S₁ | S₂ | Error Location |
|-------------------|----|----|----------------|
| \|000⟩ (no error) | 0  | 0  | None           |
| \|100⟩ (X₀ error) | ?  | ?  | ?              |
| \|010⟩ (X₁ error) | ?  | ?  | ?              |
| \|001⟩ (X₂ error) | ?  | ?  | ?              |

**Deliverable**: Complete table with calculations shown

### **Task 1.2: Circuit Implementation (10 points)**

Modify the `create_syndrome_detection_circuit()` function to handle arbitrary data qubit indices:

```python
def create_syndrome_detection_circuit_general(data_qubits: List[int], 
                                            syndrome_qubits: List[int]) -> Circuit:
    """
    Create syndrome detection for any qubit layout
    
    Args:
        data_qubits: [q0, q1, q2] - the 3 data qubits
        syndrome_qubits: [s1, s2] - the 2 syndrome qubits
    
    Returns:
        Circuit implementing S1 = q0⊕q1, S2 = q1⊕q2
    """
    # YOUR IMPLEMENTATION HERE
    pass
```

**Deliverable**: Complete function implementation

### **Task 1.3: Syndrome Verification (5 points)**

Write a test that verifies syndrome detection for all single-qubit errors:

```python
def test_syndrome_detection():
    """Test syndrome detection for all possible single-qubit errors"""
    # Test no error case
    # Test single X error on each qubit
    # Verify syndrome patterns match lookup table
    pass
```

**Deliverable**: Working test function with assertion statements

---

## Problem 2: Noise Threshold Investigation (30 points)

### **Context**
QEC only provides advantage when physical error rates are below a certain threshold. Your task is to find this threshold using your existing noise model.

### **Background**
From your `realistic_noise_test.py`, you have:
```python
T1, T2, GATE_TIME = 40e-6, 60e-6, 200e-9
P_AMPLITUDE = 1 - np.exp(-GATE_TIME / T1)
P_DEPHASING = 1 - np.exp(-GATE_TIME / T2)
```

### **Task 2.1: Noise Scaling Study (15 points)**

Implement a function to scale noise strength and find the QEC threshold:

```python
def find_qec_threshold(noise_scale_range: np.ndarray, 
                      evolution_steps: int = 10) -> pd.DataFrame:
    """
    Find the noise level where QEC advantage disappears
    
    Args:
        noise_scale_range: [0.1, 0.5, 1.0, 2.0, 5.0] - multipliers for base noise
        evolution_steps: Number of evolution steps per test
    
    Returns:
        DataFrame with noise_scale, physical_fidelity, logical_fidelity, qec_advantage
    """
    results = []
    
    for scale in noise_scale_range:
        # Scale your existing noise probabilities
        scaled_p_amp = P_AMPLITUDE * scale
        scaled_p_deph = P_DEPHASING * scale
        
        # Create physical qubit circuit
        # Create logical qubit circuit
        # Run both with scaled noise
        # Calculate QEC advantage = logical_fidelity - physical_fidelity
        
        # YOUR IMPLEMENTATION HERE
        
    return pd.DataFrame(results)
```

**Deliverable**: Complete function implementation

### **Task 2.2: Threshold Analysis (10 points)**

Run the threshold study and create a publication-quality plot:

```python
# Run threshold study
threshold_data = find_qec_threshold(
    noise_scale_range=np.array([0.1, 0.5, 1.0, 2.0, 5.0]),
    evolution_steps=10
)

# Plot results (follow style from your existing experiments)
plt.figure(figsize=(10, 6))
# Plot physical vs logical fidelity vs noise scale
# Add horizontal line at QEC advantage = 0
# Include error bars if multiple runs
# Save to results/week1/threshold_analysis.png
```

**Deliverable**: Plot showing QEC advantage vs noise scale, with threshold clearly marked

### **Task 2.3: Critical Analysis (5 points)**

Based on your results, answer:
1. At what noise scale does QEC advantage disappear?
2. How does this compare to theoretical predictions?
3. What are the implications for real quantum hardware?

**Deliverable**: 200-word analysis with specific numbers from your results

---

## Problem 3: Resource Overhead Analysis (25 points)

### **Context**
QEC requires additional qubits and operations. You'll quantify this overhead using your systematic analysis approach.

### **Task 3.1: Operation Counting (15 points)**

Implement operation counting for logical vs physical qubits:

```python
def count_circuit_resources(circuit: Circuit) -> Dict[str, int]:
    """
    Count quantum operations in a circuit
    
    Returns:
        Dictionary with counts of different gate types
    """
    resources = {
        'total_gates': 0,
        'two_qubit_gates': 0,
        'single_qubit_gates': 0,
        'noise_operations': 0,
        'measurement_operations': 0,
        'qubits_used': circuit.qubit_count
    }
    
    # YOUR IMPLEMENTATION HERE
    # Count each type of operation
    
    return resources

def compare_logical_vs_physical_overhead(evolution_steps: int = 10) -> pd.DataFrame:
    """
    Compare resource requirements for logical vs physical qubits
    """
    # Create physical qubit circuit
    physical_circuit = create_single_qubit_evolution(evolution_steps)
    
    # Create logical qubit circuit  
    logical_circuit = create_logical_qubit_evolution(evolution_steps)
    
    # Count resources for both
    physical_resources = count_circuit_resources(physical_circuit)
    logical_resources = count_circuit_resources(logical_circuit)
    
    # Calculate overhead ratios
    overhead_analysis = {}
    for key in physical_resources:
        if physical_resources[key] > 0:
            overhead_ratio = logical_resources[key] / physical_resources[key]
            overhead_analysis[f'{key}_overhead'] = overhead_ratio
    
    return pd.DataFrame([overhead_analysis])
```

**Deliverable**: Complete implementation with overhead analysis

### **Task 3.2: Scaling Study (10 points)**

Study how overhead scales with evolution time:

```python
# Test overhead for different evolution times
evolution_range = [1, 5, 10, 15, 20]
overhead_results = []

for steps in evolution_range:
    overhead_data = compare_logical_vs_physical_overhead(steps)
    overhead_data['evolution_steps'] = steps
    overhead_results.append(overhead_data)

overhead_df = pd.concat(overhead_results, ignore_index=True)

# Plot overhead vs evolution time
# Save results to CSV
```

**Deliverable**: Plot showing overhead scaling and CSV with complete data

---

## Problem 4: Advanced QEC Analysis (20 points)

### **Context**
Apply your advanced analysis skills to understand QEC performance in detail.

### **Task 4.1: Error Pattern Analysis (10 points)**

Analyze which error patterns occur most frequently:

```python
def analyze_error_patterns(num_trials: int = 1000, 
                          evolution_steps: int = 10) -> Dict[str, float]:
    """
    Statistical analysis of error patterns in 3-qubit code
    
    Returns:
        Dictionary with frequencies of each error pattern
    """
    error_frequencies = {
        'no_error': 0,
        'single_errors': {'q0': 0, 'q1': 0, 'q2': 0},
        'double_errors': {'q0q1': 0, 'q0q2': 0, 'q1q2': 0},
        'triple_error': 0,
        'uncorrectable': 0
    }
    
    # Run many trials with noise
    # Classify error patterns based on syndrome measurements
    # Calculate frequencies
    
    # YOUR IMPLEMENTATION HERE
    
    return error_frequencies
```

**Deliverable**: Statistical analysis of error patterns with visualization

### **Task 4.2: Fidelity Decay Models (10 points)**

Fit mathematical models to logical qubit decay:

```python
def fit_decay_models(fidelity_data: pd.DataFrame) -> Dict[str, any]:
    """
    Fit exponential and power-law decay models to fidelity data
    
    Models:
    - Exponential: F(t) = F₀ * exp(-t/τ)
    - Power law: F(t) = F₀ * (t/τ)^(-α)
    
    Returns:
        Fit parameters and goodness-of-fit metrics
    """
    from scipy.optimize import curve_fit
    
    # Define model functions
    def exponential_decay(t, F0, tau):
        return F0 * np.exp(-t / tau)
    
    def power_law_decay(t, F0, tau, alpha):
        return F0 * (t / tau) ** (-alpha)
    
    # Fit both models to your fidelity vs time data
    # Calculate R² values
    # Compare model quality
    
    # YOUR IMPLEMENTATION HERE
    
    return fit_results
```

**Deliverable**: Model comparison with fit parameters and R² values

---

## 🔬 Experimental Protocol

### **Setup**
1. Ensure your environment has all dependencies from existing experiments
2. Create `results/week1/` directory for outputs
3. Set random seed for reproducibility: `np.random.seed(1337)`

### **Execution Order**
1. **Problem 1**: Verify syndrome detection works correctly
2. **Problem 2**: Find QEC threshold (can use local simulation)
3. **Problem 3**: Quantify resource overhead
4. **Problem 4**: Advanced analysis (optional AWS validation)

### **Budget Guidelines**
- **Local Simulation**: Free, use for development and most testing
- **AWS DM1 Validation**: ≤$0.50, use only for final verification
- **Track Costs**: Use your existing cost tracking methodology

---

## 📊 Deliverables

### **Required Submissions**
1. **Completed Code**: All functions implemented and tested
2. **Results Data**: CSV files with experimental data
3. **Plots**: Publication-quality figures (PNG, 300 DPI)
4. **Analysis Report**: 2-page summary of findings
5. **Cost Report**: AWS usage summary

### **Grading Rubric** (100 points total)

| Component | Points | Criteria |
|-----------|--------|----------|
| **Problem 1**: Syndrome Verification | 25 | Correct syndrome table, working circuit, passing tests |
| **Problem 2**: Threshold Analysis | 30 | Complete threshold study, quality plot, insightful analysis |
| **Problem 3**: Resource Overhead | 25 | Accurate operation counting, scaling analysis, clear visualization |
| **Problem 4**: Advanced Analysis | 20 | Statistical rigor, model fitting, professional presentation |

### **Bonus Opportunities** (+10 points each)
- **AWS Validation**: Run key experiments on DM1 simulator
- **Creative Extension**: Investigate novel QEC aspects
- **Code Quality**: Exceptional documentation and testing
- **Community Contribution**: Share insights on course forum

---

## 🎓 Learning Assessment

### **Self-Check Questions**
After completing this problem set, you should be able to:
1. Explain why the 3-qubit code can correct any single-qubit error
2. Calculate syndrome patterns for arbitrary error configurations
3. Determine when QEC provides advantage over uncoded qubits
4. Quantify the resource overhead of error correction
5. Apply your noise modeling expertise to QEC analysis

### **Next Week Preparation**
- Review your syndrome detection implementation
- Understand limitations of bit-flip-only codes
- Prepare for phase-flip errors in 5-qubit Shor code

---

## 🤝 Collaboration Guidelines

### **Individual Work Required**
- All code implementations
- Analysis and interpretations
- Written responses

### **Collaboration Encouraged**
- Debugging assistance
- Conceptual discussions
- Plot styling and presentation tips

### **Resources Available**
- Your existing experiment codebases
- Course forum for questions
- Office hours for detailed help
- AWS documentation for troubleshooting

---

## 🔗 Connection to Your Research

This problem set builds directly on your expertise:
- **Noise Modeling**: Same T1/T2 approach from `realistic_noise_test.py`
- **Systematic Analysis**: Same methodology as `final_parity_check_experiment.py`
- **Cost Management**: Same budget tracking as your AWS studies
- **Educational Approach**: Same problem-solving style as existing problem sets

Your spatial locality findings also apply: gate count and operation type matter more than specific topology for QEC overhead.

---

**🎯 Ready to Start?**

```bash
cd qec_fundamentals
python bit_flip_code.py --device local_dm --max-steps 5
# Use this as your baseline, then tackle the problems!
```

**Questions?** Reference your existing experiments - you already have all the patterns needed for success! 