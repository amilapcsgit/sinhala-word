@echo off
echo Building SinhalaWord Application...

REM Run the Python build script
python -m pip install pyinstaller --upgrade
python build_app.py

REM Check if NSIS is installed
where makensis > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Building installer with NSIS...
    makensis installer.nsi
    echo Installer created at dist\SinhalaWord_Setup.exe
) else (
    echo NSIS not found. Skipping installer creation.
    echo To create an installer, please install NSIS from https://nsis.sourceforge.io/Download
)

echo.
echo Build process completed!
echo Standalone executable: dist\SinhalaWord.exe
echo Portable version: dist\SinhalaWord_Portable\
if %ERRORLEVEL% EQU 0 (
    echo Installer: dist\SinhalaWord_Setup.exe
)

pause