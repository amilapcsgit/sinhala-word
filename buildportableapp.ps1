# This script builds the standalone executable using PyInstaller.

# Activate the virtual environment
. .\.venv\Scripts\activate

# Run PyInstaller command
# --noconfirm: Overwrite output directory without asking
# --onefile: Create a single executable file
# --add-data "source;destination": Include data and resources
# --name sinhalaword: Set the name of the executable to sinhalaword.exe
# run.py: The main script file
pyinstaller --noconfirm --onefile --add-data "data;data" --add-data "resources;resources" --name sinhalaword run.py

# Deactivate the virtual environment (optional, but good practice)
deactivate

Write-Host "Build process finished. Check the 'dist' folder for sinhalaword.exe"
