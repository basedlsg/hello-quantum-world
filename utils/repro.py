import random
import numpy as np
import os

def set_all_seeds(seed=1337):
    """
    Sets the random seed for all relevant libraries to ensure reproducibility.
    
    Args:
        seed (int): The seed value to use.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    
    # Check for other libraries and set seeds if they are installed
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass # PyTorch not installed
        
    print(f"🌱 All random seeds set to {seed} for reproducibility.") 