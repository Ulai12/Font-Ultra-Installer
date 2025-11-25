@echo off
title Ultra Font Installer Launcher
echo Starting Ultra Font Installer...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

:: Install dependencies if needed (simple check)
python -c "import PySide6; import qfluentwidgets" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required Python packages...
    pip install PySide6 PySide6-Fluent-Widgets packaging pillow
)

:: Run the application
cd /d "%~dp0"
python src\main.py
pause
