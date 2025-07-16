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

def to_ndarray(x: object) -> np.ndarray:
    """
    Convert AWS DM1 density-matrix payload (nested lists / object dtype)
    to a proper complex128 ndarray.
    
    Provided by user based on forensic analysis of AWS DM1 return types.
    """
    # Force numpy to allocate a real ND-array instead of an object array.
    arr = np.asarray(x, dtype=np.complex128)
    
    # Collapse the superfluous length-1 dimension that DM1 sometimes adds.
    return arr if arr.ndim == 2 else arr.squeeze() 

def dm1_to_numpy(raw: list) -> np.ndarray:
    """
    Convert the density-matrix payload returned by AWS DM1
    (e.g., list[list[dict(real, imag)]] or list[list[list[real, imag]]])
    to a proper complex128 ndarray.
    Works for shots=0 (single matrix). Squeezes any length-1 axis.

    This function was originally based on forensic analysis of the AWS DM1
    simulator's return type and has been updated to handle format variations.
    """
    if isinstance(raw, np.ndarray):  # Handle local simulator pass-through
        mat = raw
    else:
        dim = len(raw)
        mat = np.empty((dim, dim), dtype=np.complex128)
        for i, row in enumerate(raw):
            for j, elem in enumerate(row):
                if isinstance(elem, dict):
                    # Handles {'real': ..., 'imag': ...} format
                    mat[i, j] = elem.get("real", 0.0) + 1j * elem.get("imag", 0.0)
                elif isinstance(elem, (list, tuple)) and len(elem) == 2:
                    # Handles [real, imag] or (real, imag) format
                    mat[i, j] = complex(elem[0], elem[1])
                else:
                    # Handles raw numeric types (e.g., float, complex)
                    mat[i, j] = complex(elem)

    # Squeeze to handle potential (d,d,1) shapes
    return np.squeeze(mat) 