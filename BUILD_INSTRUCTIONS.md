# SinhalaWord Build Instructions

This document provides instructions on how to build the SinhalaWord application into a standalone executable, a portable version, and an installer.

## Prerequisites

1. Python 3.8 or higher
2. PyInstaller (`pip install pyinstaller`)
3. NSIS (Nullsoft Scriptable Install System) - Optional, for creating the installer

## Building the Application

### Automatic Build (Recommended)

1. Run the `build.bat` file by double-clicking it or running it from the command line:
   ```
   build.bat
   ```

   This will:
   - Build the standalone executable
   - Create a portable version
   - Create an installer (if NSIS is installed)

### Manual Build

1. Build the application using PyInstaller:
   ```
   python build_app.py
   ```

2. (Optional) Create an installer using NSIS:
   ```
   makensis installer.nsi
   ```

## Output Files

After the build process completes, you will find:

1. Standalone executable:
   ```
   dist/SinhalaWord.exe
   ```

2. Portable version:
   ```
   dist/SinhalaWord_Portable/
   ```
   **Important:** To ensure the application runs in portable mode (saving data locally), always run `SinhalaWord.exe` or `SinhalaWord.bat` from within the `SinhalaWord_Portable` directory.

3. Installer (if NSIS is installed):
   ```
   dist/SinhalaWord_Setup.exe
   ```

## Installing NSIS

If you want to create an installer, you need to install NSIS:

1. Download NSIS from https://nsis.sourceforge.io/Download
2. Install NSIS
3. Make sure the NSIS installation directory is added to your PATH environment variable

## Troubleshooting

If you encounter any issues during the build process:

1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

2. Check that the paths in the spec file are correct
3. Ensure that the icon and splash image files exist in the specified locations