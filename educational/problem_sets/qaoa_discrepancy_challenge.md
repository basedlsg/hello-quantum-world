# Problem Set: The Great QAOA Mystery
## Graduate Quantum Computing Course - Reproducibility Module

**Course**: CS/PHYS 8803 - Quantum Algorithm Implementation and Reproducibility  
**Instructor**: [Your Name]  
**Due Date**: [Two weeks from assignment]  
**Total Points**: 100  

---

## Background Story

You are a graduate student working in a quantum computing research lab. Your advisor has handed you two QAOA (Quantum Approximate Optimization Algorithm) implementations that were developed by different research groups to solve the same MaxCut problem. Both groups claim their results are correct, but when you run them, they produce different expected cut values for identical quantum circuits.

This is based on a **real case study** where an independent verification committee found significant discrepancies in QAOA results, leading to a forensic investigation that revealed important insights about quantum algorithm implementation.

Your mission: **Investigate the discrepancy, identify its source, and propose a solution.**

---

## Learning Objectives

By completing this problem set, you will:

1. Experience real-world reproducibility challenges in quantum computing
2. Develop systematic debugging skills for quantum algorithms  
3. Understand the importance of implementation details in scientific computing
4. Practice collaborative problem-solving techniques used in research
5. Gain appreciation for reproducibility protocols in quantum computing

---

## Setup Instructions

```bash
# Clone the repository
git clone https://github.com/quantum-reproducibility/qaoa-case-study.git
cd qaoa-case-study

# Install dependencies
pip install -r requirements.txt

# Verify setup
python -m pytest tests/ -v
```

---

## Part A: Reproduce the Discrepancy (20 points)

### A.1 Initial Investigation (10 points)

Run both QAOA implementations with the following parameters:

```python
from src.maxcut_implementations.original_maxcut import OriginalMaxCut
from src.maxcut_implementations.verification_maxcut import VerificationMaxCut

# Initialize both implementations
original = OriginalMaxCut()
verification = VerificationMaxCut()

# Test parameters from the case study
test_cases = [
    {'gamma': 0.5, 'beta': 0.5},
    {'gamma': 1.0, 'beta': 0.5}, 
    {'gamma': 0.5, 'beta': 1.0}
]
```

**Tasks:**
1. Calculate the expected cut values for each parameter combination using both implementations
2. Document the observed differences in a table
3. Calculate the relative error between the two methods

**Deliverable:** A markdown report (`part_a_reproduction.md`) with:
- Table of results showing discrepancies
- Screenshots of code execution
- Initial hypothesis about the source of differences

### A.2 Quantum Circuit Verification (10 points)

Before diving deeper, verify whether the quantum circuits themselves are identical.

**Tasks:**
1. Generate the QAOA circuits for both implementations
2. Compare gate sequences, parameters, and circuit depths
3. Verify that the probability distributions from quantum simulation are identical

**Deliverable:** Code analysis showing circuit comparison results.

**Expected Finding:** The quantum circuits should be identical - the discrepancy is not in the quantum part!

---

## Part B: Forensic Analysis (30 points)

### B.1 Implementation Deep Dive (15 points)

Now investigate the MaxCut calculation methods in detail.

**Tasks:**
1. Trace through the `calculate_cut_value()` method for both implementations
2. Test the same bitstring (e.g., "101") with both methods
3. Document step-by-step calculations for each method
4. Identify specific differences in the calculation approaches

**Guiding Questions:**
- How does each method count edges in the cut?
- Are there any scaling factors applied?
- Do they handle edge cases differently?
- What data structures are used (lookup tables vs. direct calculation)?

**Deliverable:** Detailed analysis document (`forensic_analysis.md`) with:
- Step-by-step calculation traces
- Identification of key algorithmic differences
- Evidence supporting your hypothesis

### B.2 Statistical Analysis (15 points)

Perform a comprehensive comparison across all possible bitstrings.

**Tasks:**
1. Calculate cut values for all 8 possible bitstrings (000, 001, ..., 111)
2. Determine which bitstrings agree vs. disagree between methods
3. Calculate the overall agreement rate
4. Analyze the pattern of disagreements

**Expected Results:**
- Agreement rate should be 37.5% (3 out of 8 bitstrings)
- Specific bitstrings that agree: those with cut value = 0 in both methods
- Pattern: Disagreements occur when scaling factors matter

**Deliverable:** Statistical analysis with visualizations showing agreement patterns.

---

## Part C: Resolution and Standardization (30 points)

### C.1 Root Cause Analysis (15 points)

Based on your forensic analysis, identify the exact source of the discrepancy.

**Tasks:**
1. Determine which implementation follows standard MaxCut definition
2. Identify any non-standard modifications (e.g., scaling factors)
3. Explain why these differences matter for QAOA expectation values
4. Assess which method should be considered "correct"

**Expected Discovery:**
- Original method uses 0.5 scaling factor
- Verification method uses standard MaxCut definition (no scaling)
- The scaling factor causes systematic differences in expectation values

**Deliverable:** Root cause analysis report with recommendations.

### C.2 Standardized Implementation (15 points)

Create a standardized MaxCut implementation that resolves the discrepancy.

**Tasks:**
1. Implement a `StandardizedMaxCut` class that follows best practices
2. Ensure it agrees with the verification method (reference standard)
3. Add comprehensive documentation explaining the calculation method
4. Include error handling and input validation

**Requirements:**
- Use direct edge counting method
- No arbitrary scaling factors
- Clear, documented code
- Comprehensive docstrings

**Deliverable:** 
- `src/maxcut_implementations/standardized_maxcut.py`
- Unit tests demonstrating agreement with verification method

---

## Part D: Reproducibility Protocol (20 points)

### D.1 Verification Protocol Design (10 points)

Design a protocol to prevent similar issues in future quantum algorithm implementations.

**Tasks:**
1. Create a checklist for quantum algorithm implementation verification
2. Design unit tests that would have caught this discrepancy
3. Propose community standards for MaxCut calculation
4. Develop guidelines for documenting implementation details

**Deliverable:** Reproducibility protocol document (`reproducibility_protocol.md`).

### D.2 Community Contribution (10 points)

Contribute to the broader quantum computing community.

**Tasks:**
1. Write unit tests for your standardized implementation
2. Create a reference implementation guide
3. Propose improvements to existing quantum software libraries
4. Document lessons learned for other researchers

**Deliverable:** 
- Comprehensive test suite (`tests/test_standardized_maxcut.py`)
- Community contribution proposal (`community_recommendations.md`)

---

## Bonus Challenges (Optional, +10 points each)

### Bonus 1: Extended Graph Analysis
Test your findings on larger graphs (4-node, 5-node) to verify the scaling factor hypothesis.

### Bonus 2: Literature Review
Research similar reproducibility issues in quantum computing literature and compare with this case study.

### Bonus 3: Automated Detection
Create a tool that automatically detects potential implementation discrepancies in quantum algorithms.

---

## Submission Guidelines

### Required Files
```
submission/
├── reports/
│   ├── part_a_reproduction.md
│   ├── forensic_analysis.md
│   ├── root_cause_analysis.md
│   └── reproducibility_protocol.md
├── code/
│   ├── standardized_maxcut.py
│   └── analysis_scripts/
├── tests/
│   └── test_standardized_maxcut.py
└── README.md (summary of your findings)
```

### Grading Rubric

| Component | Excellent (A) | Good (B) | Satisfactory (C) | Needs Work (D/F) |
|-----------|---------------|----------|------------------|------------------|
| **Reproduction** | Accurately reproduces all discrepancies with clear documentation | Reproduces most discrepancies with good documentation | Reproduces some discrepancies with basic documentation | Fails to reproduce or poor documentation |
| **Analysis** | Identifies exact source with compelling evidence | Identifies likely source with good evidence | Identifies general area with some evidence | Fails to identify source or weak evidence |
| **Resolution** | Creates robust standardized solution with excellent documentation | Creates good solution with clear documentation | Creates basic solution with adequate documentation | Solution doesn't work or poor documentation |
| **Protocol** | Comprehensive, practical protocol that would prevent similar issues | Good protocol with most important elements | Basic protocol covering key points | Incomplete or impractical protocol |

### Academic Integrity

This is based on a real case study, but you must do your own analysis. You may:
- Discuss approaches with classmates
- Use online resources for background information
- Consult documentation and textbooks

You may NOT:
- Copy code from other students
- Share detailed analysis findings before submission
- Use automated tools to solve the problem for you

---

## Hints and Tips

### Getting Started
1. Start by running both implementations and documenting the differences
2. Don't assume the quantum circuits are different - check this first!
3. Focus on the MaxCut calculation methods, not the quantum simulation

### Debugging Strategy
1. Test with simple cases first (e.g., bitstring "000" vs "111")
2. Trace through calculations step by step
3. Look for scaling factors, different edge counting methods, or data structure differences
4. Use the debug functions provided in both implementations

### Common Pitfalls
- Don't get lost in quantum circuit details - the issue is in classical post-processing
- Don't assume one method is "obviously" wrong - both have internal logic
- Don't overlook simple differences like scaling factors
- Don't forget to test edge cases in your standardized implementation

### Success Indicators
- You should find exactly 37.5% agreement rate between methods
- The discrepancy should be systematic, not random
- Your standardized implementation should match the verification method
- Your analysis should explain why this discrepancy matters for QAOA

---

## Resources

### Required Reading
- [Quantum Approximate Optimization Algorithm (QAOA) Tutorial](https://qiskit.org/textbook/ch-applications/qaoa.html)
- [MaxCut Problem Definition](https://en.wikipedia.org/wiki/Maximum_cut)
- Original case study reports (in `reports/` directory)

### Recommended Reading
- "Reproducible Research in Computational Science" - Peng (2011)
- "The Practice of Reproducible Research" - Kitzes et al. (2017)
- AWS Braket documentation on QAOA

### Technical Resources
- Python debugging tools (`pdb`, `ipdb`)
- Jupyter notebooks for interactive analysis
- Matplotlib/Seaborn for visualization
- NetworkX for graph analysis

---

## Questions and Support

### Office Hours
- Tuesdays 2-4 PM, [Location]
- Thursdays 10-12 PM, [Location]
- Or by appointment

### Discussion Forum
Use the course discussion forum for:
- Clarification questions about the problem statement
- Technical setup issues
- General debugging strategies

Do NOT post:
- Specific analysis findings
- Code solutions
- Detailed implementation discussions

### Contact
- Email: [instructor@university.edu]
- Course website: [course_url]

---

**"The most exciting phrase to hear in science, the one that heralds new discoveries, is not 'Eureka!' but 'That's funny...'"** - Isaac Asimov

This problem set is designed to give you that "That's funny..." moment that leads to deeper understanding. Embrace the mystery, enjoy the investigation, and remember that even "failed" reproductions can lead to valuable scientific insights!

---

*This problem set is based on the real Quantum Computing Reproducibility Case Study. The discrepancy you're investigating actually happened and was resolved through the forensic analysis techniques you'll practice here.* 