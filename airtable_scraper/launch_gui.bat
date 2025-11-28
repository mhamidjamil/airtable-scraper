@echo off
title Airtable Scraper GUI
echo Starting Airtable Scraper GUI...
echo.

cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

:: Run the GUI application
python gui_app.py

pause