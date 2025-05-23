#!/usr/bin/env python
"""
Build script for SinhalaWord application.
This script builds both a standalone executable and a portable version.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Main build function."""
    print("Building SinhalaWord application...")
    
    # Get the base directory
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Run PyInstaller with our spec file
    # Try to find PyInstaller in the user's site-packages
    pyinstaller_path = os.path.join(os.path.expanduser("~"), "appdata", "local", "packages", 
                                   "pythonsoftwarefoundation.python.3.10_qbz5n2kfra8p0", 
                                   "localcache", "local-packages", "python310", "scripts", "pyinstaller.exe")
    
    if os.path.exists(pyinstaller_path):
        cmd = [pyinstaller_path, "--clean", "sinhalaword.spec"]
    else:
        # Fallback to using python -m pyinstaller
        cmd = [sys.executable, "-m", "pyinstaller", "--clean", "sinhalaword.spec"]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=base_dir)
    
    if result.returncode != 0:
        print("Error: PyInstaller failed to build the application.")
        return
    
    # Create portable version directory
    portable_dir = os.path.join(base_dir, "dist", "SinhalaWord_Portable")
    os.makedirs(portable_dir, exist_ok=True)
    
    # Copy the executable to the portable directory
    exe_path = os.path.join(base_dir, "dist", "SinhalaWord.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, portable_dir)
        print(f"Copied executable to {portable_dir}")
    
    # Create a batch file to run the application
    batch_path = os.path.join(portable_dir, "SinhalaWord.bat")
    with open(batch_path, 'w') as f:
        f.write('@echo off\n')
        f.write('start "" "%~dp0\\SinhalaWord.exe"\n')
    
    print(f"Created batch file at {batch_path}")
    
    # Create a README file
    readme_path = os.path.join(portable_dir, "README.txt")
    with open(readme_path, 'w') as f:
        f.write("SinhalaWord Portable\n")
        f.write("=================\n\n")
        f.write("This is a portable version of SinhalaWord application.\n")
        f.write("To run the application, double-click on SinhalaWord.exe or SinhalaWord.bat.\n\n")
        f.write("No installation is required.\n")
    
    print(f"Created README file at {readme_path}")
    
    print("\nBuild completed successfully!")
    print(f"Standalone executable: {exe_path}")
    print(f"Portable version: {portable_dir}")

if __name__ == "__main__":
    main()