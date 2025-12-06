#!/bin/bash
# Setup script for YouTube Downloader

echo "YouTube Downloader - Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python dependencies."
    exit 1
fi

# Check for FFmpeg
echo ""
echo "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg is already installed: $(ffmpeg -version | head -n 1)"
else
    echo "FFmpeg is not installed."
    echo ""
    echo "Please install FFmpeg:"
    echo "  - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Fedora: sudo dnf install ffmpeg"
    echo "  - Windows: Download from https://ffmpeg.org/download.html"
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x youtube_dl_cli.py
chmod +x youtube_downloader.py

# Create downloads directory
echo ""
echo "Creating downloads directory..."
mkdir -p downloads

echo ""
echo "=================================="
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  python3 youtube_dl_cli.py --help"
echo ""
echo "Example:"
echo "  python3 youtube_dl_cli.py -a 'https://www.youtube.com/watch?v=VIDEO_ID'"
echo ""
