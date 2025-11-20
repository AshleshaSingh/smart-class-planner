@echo off
REM Build script for Smart Class Planner Windows Installer
REM This script creates a standalone Windows executable and installer

echo ========================================
echo Smart Class Planner - Build Script
echo ========================================
echo.

REM Check if .venv exists, otherwise use venv
if exist ".venv" (
    echo Activating .venv virtual environment...
    call .venv\Scripts\activate.bat
) else if exist "venv" (
    echo Activating venv virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

REM Install/upgrade dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "installer_output" rmdir /s /q installer_output

REM Build executable with PyInstaller
echo.
echo Building executable with PyInstaller...
pyinstaller --clean smart_class_planner.spec

REM Check if build was successful
if not exist "dist\SmartClassPlanner\SmartClassPlanner.exe" (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo PyInstaller build completed successfully!
echo ========================================
echo.
echo Executable location: dist\SmartClassPlanner\SmartClassPlanner.exe
echo.

REM Check if Inno Setup is installed
set "ISCC_PATH="
where iscc >nul 2>nul
REM Note: This path may vary based on developer's Inno Setup installation location
if %errorlevel% equ 0 (
    set "ISCC_PATH=iscc"
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if defined ISCC_PATH (
    echo Building installer with Inno Setup...
    "%ISCC_PATH%" installer.iss

    if exist "installer_output\SmartClassPlanner_Setup_1.0.0.exe" (
        echo.
        echo ========================================
        echo Installer created successfully!
        echo ========================================
        echo.
        echo Installer location: installer_output\SmartClassPlanner_Setup_1.0.0.exe
    ) else (
        echo.
        echo WARNING: Inno Setup compilation may have failed.
        echo Please check the error messages above.
    )
) else (
    echo.
    echo NOTE: Inno Setup not found in PATH.
    echo To create the installer, please:
    echo   1. Download and install Inno Setup from https://jrsoftware.org/isinfo.php
    REM Note: This path may vary based on developer's Inno Setup installation location
    echo   2. Run: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    echo.
    echo Alternatively, you can distribute the standalone executable from:
    echo   dist\SmartClassPlanner\
)

echo.
echo Build process completed!
echo.
pause
