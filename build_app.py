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
    
    # Copy necessary resource files to the portable directory
    # Create resources directory structure
    resources_dir = os.path.join(portable_dir, "resources")
    os.makedirs(resources_dir, exist_ok=True)
    
    # Copy dictionary resources
    dict_src = os.path.join(base_dir, "resources", "dictionary")
    dict_dest = os.path.join(resources_dir, "dictionary")
    if os.path.exists(dict_src):
        shutil.copytree(dict_src, dict_dest, dirs_exist_ok=True)
        print(f"Copied dictionary resources to {dict_dest}")
    
    # Copy splash resources
    splash_src = os.path.join(base_dir, "resources", "splash")
    splash_dest = os.path.join(resources_dir, "splash")
    if os.path.exists(splash_src):
        shutil.copytree(splash_src, splash_dest, dirs_exist_ok=True)
        print(f"Copied splash resources to {splash_dest}")
    
    # Copy fonts resources if they exist
    fonts_src = os.path.join(base_dir, "resources", "fonts")
    fonts_dest = os.path.join(resources_dir, "fonts")
    if os.path.exists(fonts_src):
        shutil.copytree(fonts_src, fonts_dest, dirs_exist_ok=True)
        print(f"Copied fonts resources to {fonts_dest}")
    
    # Create a data directory in the portable directory
    data_dir = os.path.join(portable_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f"Created data directory at {data_dir}")
    
    # Copy sinhalawordmap.json to the portable data directory
    wordmap_src = os.path.join(base_dir, "sinhalawordmap.json")
    if os.path.exists(wordmap_src):
        shutil.copy2(wordmap_src, os.path.join(data_dir, "sinhalawordmap.json"))
        print(f"Copied sinhalawordmap.json to {os.path.join(data_dir, 'sinhalawordmap.json')}")
    
    # Create a portable.txt file to indicate this is a portable installation
    portable_marker = os.path.join(portable_dir, "portable.txt")
    with open(portable_marker, 'w') as f:
        f.write("This file indicates that SinhalaWord is running in portable mode.\n")
        f.write("User data will be stored in the 'data' directory next to the executable.\n")
    print(f"Created portable marker file at {portable_marker}")
    
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
        f.write("No installation is required.\n\n")
        f.write("Copyright (c) 2025 L.J.Amila Prasad Perera\n")
        f.write("CC - Free to use by crediting the owner (L.J.Amila Prasad Perera)\n")
    
    print(f"Created README file at {readme_path}")
    
    print("\nBuild completed successfully!")
    print(f"Standalone executable: {exe_path}")
    print(f"Portable version: {portable_dir}")

if __name__ == "__main__":
    main()