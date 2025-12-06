@echo off
REM Setup script for YouTube Downloader (Windows)

echo YouTube Downloader - Setup Script
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

REM Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies.
    pause
    exit /b 1
)

REM Check for FFmpeg
echo.
echo Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo FFmpeg is already installed
) else (
    echo FFmpeg is not installed.
    echo.
    echo Please install FFmpeg:
    echo   1. Download from https://ffmpeg.org/download.html
    echo   2. Extract the files
    echo   3. Add the bin folder to your PATH environment variable
    echo.
)

REM Create downloads directory
echo.
echo Creating downloads directory...
if not exist downloads mkdir downloads

echo.
echo ==================================
echo Setup complete!
echo.
echo Usage:
echo   python youtube_dl_cli.py --help
echo.
echo Example:
echo   python youtube_dl_cli.py -a "https://www.youtube.com/watch?v=VIDEO_ID"
echo.
pause
