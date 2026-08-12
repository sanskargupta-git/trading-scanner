@echo off
title Ultimate Pro Trading Scanner
echo ============================================
echo   ULTIMATE PRO TRADING SCANNER
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python is not installed or not on PATH.
    echo     Install it from https://python.org and tick "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [1/2] Installing dependencies ^(first run takes a minute^)...
python -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo [!] Could not install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo [2/2] Starting the scanner...
echo.
echo     Open http://localhost:5000 in your browser.
echo     The tables fill in after about 15 seconds on first load.
echo     Press Ctrl+C here to stop.
echo.
python trading_scanner.py
pause
