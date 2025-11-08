@echo off
REM Cosik AI Agent - Quick Start Script for Windows
REM This script helps you get started with Cosik quickly

echo ========================================
echo Cosik AI Agent - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
pip show pyautogui >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
    echo.
)

REM Create necessary directories
if not exist "data\memory\" mkdir data\memory
if not exist "data\vector_store\" mkdir data\vector_store
if not exist "data\backups\" mkdir data\backups
if not exist "logs\" mkdir logs

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now run Cosik AI Agent:
echo.
echo   For interactive mode:
echo   python main.py --interactive
echo.
echo   For single command:
echo   python main.py --command "otwórz notepad"
echo.
echo   For help:
echo   python main.py --help
echo.
echo To run tests:
echo   pytest tests/ -v
echo.
echo Press any key to start in interactive mode...
pause >nul

python main.py --interactive
