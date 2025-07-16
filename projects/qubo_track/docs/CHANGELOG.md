# CHANGELOG - QUBO Track

## v2.1 (Production-Grade) - 2024-07-02

### 🚀 Production Readiness Improvements
- **True dependency lockfile**: `requirements_locked.txt` with exact Ocean SDK sub-package versions
- **Headless plotting**: Added matplotlib smoke test for cloud environments (Agg backend)
- **Faster CI**: Removed redundant `pip install safety` (now in lockfile)
- **Conservative quick mode**: Reduced exact computation limit to 8 nodes (from 12) for CI safety
- **Local CI reproduction**: Added `run_ci.sh` script for developers
- **Enhanced security**: All Ocean sub-packages (`dwave-*`, `dimod`) pinned exactly

### 🔧 Technical Improvements
- **CI runtime**: ~30 seconds (down from potential 5+ minutes)
- **Dependency drift protection**: No version ranges - all packages exactly pinned
- **Cloud deployment ready**: Headless plotting verified in CI
- **Memory documentation**: Consistent RAM usage estimates across files

---

## v2.0 (Statistical Rigor) - 2024-06-XX

### 🧪 Scientific Integrity Restoration
- **Fixed false claims**: Removed all "quantum annealing advantage" terminology
- **Proper baselines**: TabuSampler vs SimulatedAnnealingSampler (both classical)
- **Statistical validation**: 20 trials with confidence intervals and significance testing
- **Effect size**: Added Cohen's d interpretation with NaN-safe handling
- **Multiple comparison correction**: Holm-Bonferroni method
- **Exact optimum**: Brute force enumeration for ≤10 nodes with quality normalization

### 📊 Enhanced Analysis
- **Random seeding**: Per-trial reproducibility with `np.random.seed()`
- **Error bars**: Standard error of mean (SEM) in visualizations
- **Runtime management**: `--quick` flag using Tabu approximation for >10 nodes
- **File safety**: Deprecated old files with RuntimeError guards

### 🧪 Testing Infrastructure
- **Unit tests**: `test_exact_optimum.py` with verified K3, K4, K6, P4, C4 cases
- **Comprehensive tests**: `test_comprehensive.py` with CSV schema and NaN statistics validation
- **CI pipeline**: GitHub Actions with dependency verification and security audit

---

## v1.0 (Corrected Classical) - 2024-06-XX

### ✅ Initial Scientific Fixes
- **Honest terminology**: "Classical SA vs Classical Optimization" 
- **Fixed baselines**: Replaced greedy approximation with TabuSampler
- **Statistical basics**: 20 trials with mean/std reporting
- **Exact optimum**: Basic brute force implementation
- **Quality normalization**: `cut_value / exact_optimum` metric

### 📝 Documentation
- **CORRECTED_QUBO_SUMMARY.md**: Honest assessment without false claims
- **SCIENTIFIC_INTEGRITY_VERIFICATION.md**: Detailed fix documentation

---

## v0.0 (Original - DEPRECATED)

### ❌ Scientific Issues (Fixed)
- **Misleading claims**: "39% quantum annealing advantage" 
- **Wrong terminology**: Called `SimulatedAnnealingSampler` "quantum annealing"
- **Weak baselines**: Compared against trivial greedy approximation
- **No statistical validation**: Single runs without confidence intervals
- **Missing ground truth**: No exact optimum calculation

**Status**: All files from this version are deprecated with RuntimeError guards. 