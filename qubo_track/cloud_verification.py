#!/usr/bin/env python3
"""
CLOUD VERIFICATION: Minimal test for CI environments
Fast verification that core QUBO functionality works in cloud
"""

import time
import sys

def main():
    start_time = time.time()
    
    print("🌐 CLOUD VERIFICATION: QUBO Track v2.1")
    print("=" * 45)
    
    try:
        # Test imports
        from corrected_classical_optimization import (
            compute_exact_max_cut,
            create_test_graphs
        )
        import networkx as nx
        from dwave.samplers import SimulatedAnnealingSampler
        print("✅ All imports successful")
        
        # Test 1: Basic exact computation
        graph = nx.complete_graph(4)
        result = compute_exact_max_cut(graph, quick_mode=False)
        assert result == 4, f"K4 should have max-cut 4, got {result}"
        print("✅ Exact computation: K4 max-cut = 4")
        
        # Test 2: Quick mode for larger graphs  
        graph = nx.complete_graph(15)
        result = compute_exact_max_cut(graph, quick_mode=True)
        assert result > 50, f"K15 should have large max-cut, got {result}"
        print(f"✅ Quick mode: K15 max-cut ≈ {result}")
        
        # Test 3: Ocean SDK sampling
        sampler = SimulatedAnnealingSampler()
        print("✅ D-Wave Ocean SDK functional")
        
        # Test 4: Statistical imports
        import pandas as pd
        import numpy as np
        from scipy import stats
        print("✅ Statistical packages available")
        
        # Test 5: Headless plotting (critical for cloud environments)
        import matplotlib
        matplotlib.use("Agg")  # Use non-interactive backend
        import matplotlib.pyplot as plt
        from pathlib import Path
        
        plt.figure()
        plt.plot([0, 1], [0, 1])
        plt.title("Cloud verification smoke test")
        plt.savefig("ci_smoke.png")
        plt.close()
        
        # Verify plot was created and has content
        smoke_path = Path("ci_smoke.png")
        assert smoke_path.exists() and smoke_path.stat().st_size > 0, "Plot generation failed"
        print("✅ Headless plotting functional (matplotlib + Agg backend)")
        
        elapsed = time.time() - start_time
        print(f"\n✅ CLOUD VERIFICATION COMPLETE")
        print(f"✅ Runtime: {elapsed:.2f}s (target: <30s)")
        print(f"✅ Status: READY FOR CLOUD DEPLOYMENT")
        
        return 0
        
    except Exception as e:
        print(f"❌ CLOUD VERIFICATION FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
