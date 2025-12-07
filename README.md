# YouTube Downloader Fancy 🎬

A beautiful, modern desktop application for downloading YouTube videos and audio, built with Electron.

![YouTube Downloader Fancy](screenshot.png)

## Features ✨

- **🖼️ Beautiful Modern UI** - Sleek, user-friendly interface with a gradient design
- **📥 Easy URL Management** - Add URLs through a dedicated modal window
- **🎵 Audio Track Selection** - Choose specific audio tracks for videos with multiple languages
- **📊 Real-time Progress** - View download progress with thumbnails, progress bars, speed, and ETA
- **📁 Custom Output Folder** - Choose where your downloads are saved
- **🎯 Quality Control** - Select video quality (4K, 1080p, 720p, etc.) and format (MP4, WebM, MKV)
- **🎧 Audio-Only Downloads** - Extract audio in MP3, M4A, OPUS, or AAC formats
- **⚙️ Advanced Settings** - Embed thumbnails, metadata, and more
- **🔄 Download Management** - Pause, retry, or cancel downloads
- **📋 Multiple Downloads** - Queue and manage multiple downloads simultaneously

## Screenshots

### Main Window
The main window displays your download queue with beautiful thumbnails and real-time progress indicators.

### Add URL Modal
A clean, focused interface for adding YouTube URLs with video preview.

## Installation

### Prerequisites

1. **Node.js** (v14 or higher)
   - Download from [nodejs.org](https://nodejs.org/)

2. **Python 3.7+**
   - Download from [python.org](https://www.python.org/)

3. **FFmpeg**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo dnf install ffmpeg` (Fedora)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/youtubeDownloaderFancy.git
   cd youtubeDownloaderFancy
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   cd youtubeDownloader
   pip install -r requirements.txt
   cd ..
   ```

4. **Verify Python setup** (Optional but recommended)
   ```bash
   # Check Python version
   python3 --version
   # Should show Python 3.7 or higher

   # Check FFmpeg
   ffmpeg -version

   # Test the bridge script
   python3 youtubeDownloader/electron_bridge.py get-info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   # Should return JSON with video info
   ```

## Usage

### Running the Application

```bash
npm start
```

For development mode (with DevTools):
```bash
npm run dev
```

### Using the Application

1. **Launch the app** using `npm start`

2. **Click "Add URL"** button to open the URL input modal

3. **Paste a YouTube URL**
   - Single video URL
   - Playlist URL
   - Multiple URLs (one per line)

4. **Click "Get Info"** (optional) to preview video details and available audio tracks

5. **Click "Add to Downloads"** to add the video to your download queue

6. **Configure settings** (optional)
   - Select output folder
   - Choose video quality or audio bitrate
   - Select format (MP4, WebM, MKV for video; MP3, M4A, OPUS for audio)
   - Advanced: Select specific audio track, embed thumbnail/metadata

7. **Watch the progress** in real-time with thumbnails and progress bars

8. **Access your downloads** by clicking the folder icon when complete

## Configuration

### Output Folder
By default, downloads are saved to `~/Downloads/YouTube`. You can change this by clicking the "Browse" button in the Settings sidebar.

### Download Settings

- **Download Type**: Video + Audio or Audio Only
- **Quality**:
  - Video: Best, 4K, 1440p, 1080p, 720p, 480p
  - Audio: 320kbps, 256kbps, 192kbps, 128kbps
- **Format**:
  - Video: MP4, WebM, MKV
  - Audio: MP3, M4A, OPUS, AAC

### Advanced Settings

- **Audio Track**: Select specific language audio track (for videos with multiple audio tracks)
- **Embed Thumbnail**: Add video thumbnail to the file metadata
- **Embed Metadata**: Include video title, author, and other metadata

## Keyboard Shortcuts

- **Ctrl/Cmd + Enter** (in Add URL modal): Get video info

## Building for Production

### Package for your platform

```bash
# Install electron-builder
npm install --save-dev electron-builder

# Add to package.json scripts:
"build": "electron-builder"

# Build
npm run build
```

### Platform-specific builds

```bash
# Windows
npm run build -- --win

# macOS
npm run build -- --mac

# Linux
npm run build -- --linux
```

## Project Structure

```
youtubeDownloaderFancy/
├── main.js                    # Electron main process
├── index.html                 # Main window UI
├── add-url.html              # Add URL modal UI
├── renderer.js               # Main window logic
├── add-url-renderer.js       # Add URL modal logic
├── styles.css                # Global styles
├── package.json              # Node.js dependencies
├── youtubeDownloader/        # Python backend
│   ├── electron_bridge.py    # Electron-Python bridge (JSON communication)
│   ├── youtube_downloader.py # YouTube download logic
│   ├── youtube_dl_cli.py     # CLI interface
│   └── requirements.txt      # Python dependencies
└── README.md                 # This file
```

## Technical Details

### Technologies Used

- **Electron** - Desktop application framework
- **Node.js** - JavaScript runtime
- **Python** - Backend processing
- **yt-dlp** - YouTube download library
- **FFmpeg** - Audio/video processing

### IPC Communication

The app uses Electron's IPC (Inter-Process Communication) to communicate between:
- **Renderer process (UI) ↔ Main process (Electron)**: Uses Electron IPC for UI events
- **Main process ↔ Python backend**: Spawns Python child processes that communicate via JSON

The `electron_bridge.py` script acts as a bridge, receiving commands from Electron and returning:
- Video information (title, thumbnail, duration, available audio tracks)
- Real-time download progress (percentage, speed, ETA)
- Completion/error status

## Troubleshooting

### Downloads not starting

1. Make sure Python is installed and accessible from command line
2. Verify FFmpeg is installed: `ffmpeg -version`
3. Check that Python dependencies are installed: `pip list | grep yt-dlp`

### Permission errors

- Make sure you have write permissions to the output folder
- Try selecting a different output folder

### Video info not loading

- Check your internet connection
- Verify the YouTube URL is correct and the video is publicly accessible
- Some videos may be region-locked or age-restricted

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided for educational purposes. Please respect copyright laws and YouTube's terms of service when using this tool.

## Credits

Built with:
- [Electron](https://www.electronjs.org/) - Desktop app framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Media processing

## Disclaimer

This tool is for personal use only. Always respect content creators' rights and YouTube's terms of service. Do not use this tool to download copyrighted content without permission.
