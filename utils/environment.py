import os
import subprocess
import venv

class ProductionEnv:
    """
    Manages the creation of a sandboxed Python virtual environment and the
    installation of dependencies from a locked requirements file.
    """
    def __init__(self, name="venv", python_version="3.10"):
        self.name = name
        self.python_version = python_version
        self.path = os.path.abspath(self.name)
        self.bin_path = os.path.join(self.path, "bin")
        self.python_path = os.path.join(self.bin_path, "python")

    def create(self):
        """Creates the virtual environment if it doesn't already exist."""
        if not os.path.exists(self.path):
            print(f"Creating virtual environment at: {self.path}")
            venv.create(self.path, with_pip=True)
        else:
            print("Virtual environment already exists. Skipping creation.")

    def install_dependencies_from_lockfile(self, lockfile_path):
        """Installs dependencies from a specified pip-tools lockfile."""
        if os.path.exists(lockfile_path):
            print(f"Installing locked dependencies from {lockfile_path}...")
            subprocess.check_call([self.python_path, "-m", "pip", "install", "-r", lockfile_path])
        else:
            raise FileNotFoundError(f"Lockfile not found at: {lockfile_path}") 