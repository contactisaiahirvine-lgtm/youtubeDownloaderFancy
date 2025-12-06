# YouTube Downloader

A powerful, cross-platform command-line tool for downloading YouTube videos and audio. Supports single videos, multiple videos, and entire playlists with various quality and format options.

## Features

- **Video Downloads**: Download videos in MP4, WebM, MKV, and other formats
- **Audio Downloads**: Extract audio in MP3, M4A, OPUS, and other formats
- **Multiple Downloads**: Download multiple videos at once from a list of URLs
- **Playlist Support**: Download entire playlists with a single command
- **Quality Control**: Choose video quality (1080p, 720p, etc.) or audio bitrate (128, 192, 320 kbps)
- **Progress Tracking**: Real-time download progress with speed and ETA
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Batch Processing**: Read URLs from a file for bulk downloads

## Requirements

- Python 3.7 or higher
- FFmpeg (for audio conversion and video merging)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Extract and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (Fedora):**
```bash
sudo dnf install ffmpeg
```

## Usage

### Basic Usage

Download a single video:
```bash
python youtube_dl_cli.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Audio-Only Downloads

Download audio only (MP3 format):
```bash
python youtube_dl_cli.py -a "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download audio in different format and quality:
```bash
python youtube_dl_cli.py -a -F m4a -q 320 "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Multiple Videos

Download multiple videos at once:
```bash
python youtube_dl_cli.py "URL1" "URL2" "URL3"
```

Download from a text file (one URL per line):
```bash
python youtube_dl_cli.py -f urls.txt
```

**Example urls.txt:**
```
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.youtube.com/watch?v=VIDEO_ID2
https://www.youtube.com/watch?v=VIDEO_ID3
# This is a comment - lines starting with # are ignored
```

### Playlist Downloads

Download entire playlist:
```bash
python youtube_dl_cli.py -p "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

Download specific range from playlist:
```bash
python youtube_dl_cli.py -p --start 5 --end 10 "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Video Quality and Format

Download in specific quality:
```bash
python youtube_dl_cli.py -q 1080p "https://www.youtube.com/watch?v=VIDEO_ID"
python youtube_dl_cli.py -q 720p "https://www.youtube.com/watch?v=VIDEO_ID"
```

Download in specific format:
```bash
python youtube_dl_cli.py -F webm "https://www.youtube.com/watch?v=VIDEO_ID"
python youtube_dl_cli.py -F mkv -q best "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Custom Output Directory

Specify output directory:
```bash
python youtube_dl_cli.py -o /path/to/downloads "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Get Video Information

View video information without downloading:
```bash
python youtube_dl_cli.py -i "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Command-Line Options

```
usage: youtube_dl_cli.py [-h] [-a] [-p] [-f FILE] [-o DIR] [-F FORMAT]
                         [-q QUALITY] [--start N] [--end N] [-i] [--no-banner]
                         [urls ...]

positional arguments:
  urls                  YouTube URL(s) to download

optional arguments:
  -h, --help            show this help message and exit
  -a, --audio           Download audio only (default: MP3)
  -p, --playlist        Download entire playlist
  -f FILE, --file FILE  Read URLs from a text file (one URL per line)
  -o DIR, --output DIR  Output directory (default: downloads)
  -F FORMAT, --format FORMAT
                        Output format (mp4, webm, mkv for video;
                        mp3, m4a, opus for audio)
  -q QUALITY, --quality QUALITY
                        Quality (best, 1080p, 720p, 480p for video;
                        128, 192, 256, 320 for audio bitrate)
  --start N             Playlist: start from video N (default: 1)
  --end N               Playlist: end at video N
  -i, --info            Show video information without downloading
  --no-banner           Hide banner
```

## Examples

### Example 1: Download a Music Video as MP3
```bash
python youtube_dl_cli.py -a -q 320 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Example 2: Download Multiple Videos in 720p
```bash
python youtube_dl_cli.py -q 720p "URL1" "URL2" "URL3"
```

### Example 3: Download Playlist Audio Only
```bash
python youtube_dl_cli.py -p -a "https://www.youtube.com/playlist?list=PLxxxxxx"
```

### Example 4: Download from File with Custom Output
```bash
python youtube_dl_cli.py -f my_videos.txt -o ~/Videos/YouTube
```

### Example 5: Download Specific Videos from Playlist
```bash
python youtube_dl_cli.py -p --start 1 --end 5 "https://www.youtube.com/playlist?list=PLxxxxxx"
```

## Using as a Python Module

You can also use the downloader in your Python scripts:

```python
from youtube_downloader import YouTubeDownloader

# Initialize downloader
downloader = YouTubeDownloader(output_dir="my_downloads")

# Download a video
downloader.download_video("https://www.youtube.com/watch?v=VIDEO_ID", format_type="mp4", quality="1080p")

# Download audio
downloader.download_audio("https://www.youtube.com/watch?v=VIDEO_ID", format_type="mp3", quality="320")

# Download multiple videos
urls = ["URL1", "URL2", "URL3"]
downloader.download_multiple(urls, audio_only=False)

# Download playlist
downloader.download_playlist("https://www.youtube.com/playlist?list=PLAYLIST_ID", audio_only=True)

# Get video information
info = downloader.get_video_info("https://www.youtube.com/watch?v=VIDEO_ID")
print(f"Title: {info['title']}")
```

## Supported Formats

### Video Formats
- MP4 (default)
- WebM
- MKV
- And other formats supported by FFmpeg

### Audio Formats
- MP3 (default)
- M4A
- OPUS
- AAC
- And other formats supported by FFmpeg

### Video Quality Options
- `best` - Best available quality (default)
- `2160p` - 4K (2160p)
- `1440p` - 2K (1440p)
- `1080p` - Full HD
- `720p` - HD
- `480p` - SD
- `360p` - Low quality

### Audio Quality Options (bitrate in kbps)
- `320` - Highest quality
- `256` - High quality
- `192` - Medium quality (default)
- `128` - Low quality

## Troubleshooting

### FFmpeg Not Found

If you get an error about FFmpeg not being found:
1. Make sure FFmpeg is installed
2. Verify it's in your system PATH by running `ffmpeg -version`
3. On Windows, you may need to restart your terminal after adding FFmpeg to PATH

### Download Errors

If downloads fail:
1. Check your internet connection
2. Verify the URL is correct and the video is publicly accessible
3. Some videos may be region-locked or age-restricted
4. Try updating yt-dlp: `pip install --upgrade yt-dlp`

### Permission Errors

If you get permission errors when writing files:
- Make sure you have write permissions to the output directory
- Try specifying a different output directory with `-o`

## Notes

- Downloaded files are saved to the `downloads` folder by default
- Playlists are numbered automatically (e.g., "1 - Video Title.mp4")
- The tool respects YouTube's terms of service - use responsibly
- Some videos may not be available for download due to restrictions

## License

This project is provided as-is for educational purposes. Please respect copyright laws and YouTube's terms of service when using this tool.

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The best YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - For audio/video processing
- [colorama](https://github.com/tartley/colorama) - For colored terminal output
