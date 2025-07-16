import sys
import os
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.environment import ProductionEnv
from utils.repro import set_all_seeds
from fmo import FMOProject
import argparse
import logging
import subprocess

def main():
    """
    Main entry point for the FMO project.
    """
    parser = argparse.ArgumentParser(description="Run the FMO simulation project.")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run a quick version of the simulation for testing.",
    )
    args = parser.parse_args()

    # Set all random seeds for reproducibility
    set_all_seeds()

    # Setup environment
    env = ProductionEnv(name="fmo_env")
    env.create()
    
    # Generate lockfile if it doesn't exist
    lockfile = "projects/fmo_project/requirements_locked.txt"
    if not os.path.exists(lockfile):
        print("Lockfile not found, generating...")
        requirements_file = "projects/fmo_project/requirements_production.txt"
        subprocess.check_call([
            "pip-compile",
            requirements_file,
            "--output-file",
            lockfile
        ])
    
    env.install_dependencies_from_lockfile(lockfile)

    # Run the analysis
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    project = FMOProject(quick=args.quick)
    project.run_full_analysis()

    print("FMO project analysis complete.")

if __name__ == "__main__":
    main() 