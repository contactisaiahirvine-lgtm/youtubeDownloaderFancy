#!/bin/bash
# Force clear all caches and restart fresh

set -e  # Exit on error

echo "🧹 Cleaning up YouTube Downloader Fancy..."
echo ""

# Kill any running Electron processes
echo "1. Killing any running Electron processes..."
pkill -9 electron 2>/dev/null || echo "   No Electron processes found"
pkill -9 Electron 2>/dev/null || true
sleep 1

# Clear Electron cache
echo "2. Clearing Electron cache..."
rm -rf ~/.config/youtube-downloader-fancy 2>/dev/null || true
rm -rf ~/.config/Electron 2>/dev/null || true
rm -rf ~/Library/Application\ Support/youtube-downloader-fancy 2>/dev/null || true
rm -rf ~/Library/Application\ Support/Electron 2>/dev/null || true

# Clear node_modules
echo "3. Clearing node_modules..."
cd "$(dirname "$0")"
rm -rf node_modules 2>/dev/null || true

# Reinstall dependencies
echo "4. Reinstalling dependencies..."
npm install

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Starting app in development mode..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the app
npm run dev
