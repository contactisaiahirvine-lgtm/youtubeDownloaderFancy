#!/bin/bash
# Verification script for YouTube Downloader Fancy

echo "🔍 Verifying YouTube Downloader Fancy Installation..."
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this from the project root directory."
    exit 1
fi

echo "✅ Found package.json"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installed: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js 14+"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python installed: $PYTHON_VERSION"
else
    echo "❌ Python3 not found. Please install Python 3.7+"
    exit 1
fi

# Check FFmpeg
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -1)
    echo "✅ FFmpeg installed: $FFMPEG_VERSION"
else
    echo "⚠️  FFmpeg not found. Download functionality may not work."
fi

# Check yt-dlp
if python3 -c "import yt_dlp" 2>/dev/null; then
    echo "✅ yt-dlp installed"
else
    echo "❌ yt-dlp not found. Installing..."
    pip3 install -r youtubeDownloader/requirements.txt
fi

# Check node_modules
if [ -d "node_modules" ]; then
    echo "✅ node_modules found"
else
    echo "⚠️  node_modules not found. Installing..."
    npm install
fi

# Test Python bridge
echo ""
echo "🧪 Testing Python bridge..."
BRIDGE_TEST=$(python3 youtubeDownloader/electron_bridge.py get-info "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 2>&1)

if echo "$BRIDGE_TEST" | grep -q '"success"'; then
    if echo "$BRIDGE_TEST" | grep -q '"success":true'; then
        echo "✅ Python bridge working (video info fetched)"
    else
        echo "⚠️  Python bridge returned success:false (network issue?)"
    fi
else
    echo "❌ Python bridge test failed"
    echo "Error output:"
    echo "$BRIDGE_TEST" | head -20
fi

# Check for via.placeholder references (should be none)
echo ""
echo "🔍 Checking for outdated code..."
if grep -r "via.placeholder" --include="*.js" --include="*.html" . 2>/dev/null; then
    echo "❌ Found via.placeholder references - code may be outdated"
else
    echo "✅ No via.placeholder references found"
fi

# Check for simulateDownload (should be none)
if grep -r "simulateDownload" --include="*.js" . 2>/dev/null; then
    echo "❌ Found simulateDownload function - code may be outdated"
else
    echo "✅ No simulateDownload function found"
fi

# Verify key files exist
echo ""
echo "📁 Verifying key files..."
FILES=(
    "main.js"
    "index.html"
    "add-url.html"
    "renderer.js"
    "add-url-renderer.js"
    "styles.css"
    "youtubeDownloader/electron_bridge.py"
    "DEBUG.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "📋 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count checks
TOTAL=0
PASSED=0

# This is a simplified summary
echo ""
echo "To run the app:"
echo "  npm run dev     # Development mode with DevTools"
echo "  npm start       # Production mode"
echo ""
echo "To clear cache:"
echo "  rm -rf ~/.config/youtube-downloader-fancy"
echo ""
echo "For troubleshooting, see DEBUG.md"
