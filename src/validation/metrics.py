"""
Quantum Information Theory Metrics
"""
import numpy as np
from scipy.linalg import sqrtm

def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """
    Calculates the Uhlmann-Jozsa fidelity between two density matrices.

    F(rho, sigma) = (Tr[sqrt(sqrt(rho) * sigma * sqrt(rho))])^2

    Args:
        rho: A density matrix (Hermitian, trace-1).
        sigma: A density matrix (Hermitian, trace-1).

    Returns:
        The fidelity between rho and sigma.
    """
    # Validate inputs
    if not np.allclose(np.trace(rho), 1.0) or not np.allclose(np.trace(sigma), 1.0):
        raise ValueError("Density matrices must have a trace of 1.")
    if not np.allclose(rho, rho.conj().T) or not np.allclose(sigma, sigma.conj().T):
        raise ValueError("Density matrices must be Hermitian.")

    # Calculate fidelity
    sqrt_rho = sqrtm(rho)
    # The @ operator is equivalent to np.matmul
    inner_matrix = sqrtm(sqrt_rho @ sigma @ sqrt_rho)
    
    # Fidelity is the squared trace of the resulting matrix.
    # The result should be real, but we take np.real to discard tiny imaginary
    # parts from numerical precision errors.
    fid = float(np.real(np.trace(inner_matrix))**2)
    
    return fid 