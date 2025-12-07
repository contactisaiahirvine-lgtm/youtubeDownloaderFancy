#!/usr/bin/env python3
"""
Electron Bridge - Bridge between Electron and YouTube Downloader
Communicates via JSON for seamless integration with the Electron app
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yt_dlp


class ElectronBridge:
    """Bridge class for Electron-Python communication."""

    def __init__(self, output_dir: str = "downloads"):
        """Initialize the bridge."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def send_json(self, data: Dict[str, Any]):
        """Send JSON data to Electron via stdout."""
        print(json.dumps(data), flush=True)

    def send_error(self, error: str, details: Optional[str] = None):
        """Send error message to Electron."""
        self.send_json({
            'type': 'error',
            'error': error,
            'details': details
        })

    def send_progress(self, progress: int, speed: str = '', eta: str = ''):
        """Send download progress to Electron."""
        self.send_json({
            'type': 'progress',
            'progress': progress,
            'speed': speed,
            'eta': eta
        })

    def send_complete(self, filename: str):
        """Send completion message to Electron."""
        self.send_json({
            'type': 'complete',
            'filename': filename
        })

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get detailed video information including thumbnails and audio tracks.

        Args:
            url: YouTube video URL

        Returns:
            Dictionary with video information
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Extract audio track information
                audio_tracks = []
                if 'requested_formats' in info:
                    # For videos with separate audio/video streams
                    for fmt in info.get('formats', []):
                        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                            lang = fmt.get('language', 'unknown')
                            lang_name = fmt.get('language_preference', lang)
                            if lang and lang != 'unknown':
                                audio_tracks.append({
                                    'id': lang,
                                    'language': lang.upper() if len(lang) == 2 else lang.title(),
                                    'description': f"{lang_name} audio"
                                })

                # Remove duplicates
                seen = set()
                unique_tracks = []
                for track in audio_tracks:
                    track_id = track['id']
                    if track_id not in seen:
                        seen.add(track_id)
                        unique_tracks.append(track)

                # Add default auto track
                if not unique_tracks:
                    unique_tracks = [{
                        'id': 'auto',
                        'language': 'Auto (Default)',
                        'description': 'Default audio track'
                    }]
                else:
                    unique_tracks.insert(0, {
                        'id': 'auto',
                        'language': 'Auto (Default)',
                        'description': 'Default audio track'
                    })

                # Get best thumbnail
                thumbnail = None
                if 'thumbnails' in info and info['thumbnails']:
                    # Get the highest quality thumbnail
                    thumbnails = sorted(
                        info['thumbnails'],
                        key=lambda x: x.get('preference', 0) or 0,
                        reverse=True
                    )
                    thumbnail = thumbnails[0]['url'] if thumbnails else None

                return {
                    'success': True,
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration', 0),
                    'thumbnail': thumbnail or info.get('thumbnail'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:200],  # First 200 chars
                    'audioTracks': unique_tracks
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def download_video(
        self,
        url: str,
        format_type: str = 'mp4',
        quality: str = 'best',
        audio_only: bool = False,
        audio_track: str = 'auto',
        embed_thumbnail: bool = False,
        embed_metadata: bool = True
    ):
        """
        Download video with progress updates.

        Args:
            url: YouTube video URL
            format_type: Output format
            quality: Video quality or audio bitrate
            audio_only: Download audio only
            audio_track: Preferred audio track language
            embed_thumbnail: Embed thumbnail in file
            embed_metadata: Embed metadata in file
        """
        def progress_hook(d):
            """Hook for progress updates."""
            if d['status'] == 'downloading':
                try:
                    # Extract progress information
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)

                    if total > 0:
                        progress = int((downloaded / total) * 100)
                    else:
                        # Fallback to percent string if available
                        percent_str = d.get('_percent_str', '0%')
                        progress = int(float(percent_str.strip('%').strip()))

                    speed = d.get('_speed_str', 'N/A').strip()
                    eta = d.get('_eta_str', 'N/A').strip()

                    self.send_progress(progress, speed, eta)

                except Exception as e:
                    # If we can't parse progress, send a generic update
                    pass

            elif d['status'] == 'finished':
                self.send_progress(100, '0 B/s', '0s')

        try:
            if audio_only:
                # Audio download options
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': format_type,
                        'preferredquality': quality,
                    }],
                    'quiet': True,
                    'no_warnings': True,
                }

                # Add thumbnail embedding if requested
                if embed_thumbnail:
                    ydl_opts['postprocessors'].append({
                        'key': 'EmbedThumbnail',
                    })
                    ydl_opts['writethumbnail'] = True

            else:
                # Video download options
                quality_map = {
                    'best': 'bestvideo+bestaudio/best',
                    '2160p': 'bestvideo[height<=2160]+bestaudio/best',
                    '1440p': 'bestvideo[height<=1440]+bestaudio/best',
                    '1080p': 'bestvideo[height<=1080]+bestaudio/best',
                    '720p': 'bestvideo[height<=720]+bestaudio/best',
                    '480p': 'bestvideo[height<=480]+bestaudio/best',
                    '360p': 'bestvideo[height<=360]+bestaudio/best',
                }

                format_string = quality_map.get(quality, 'bestvideo+bestaudio/best')

                # Add audio track preference if specified and not auto
                if audio_track and audio_track != 'auto':
                    format_string = f'{format_string}[language={audio_track}]'

                ydl_opts = {
                    'format': format_string,
                    'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'merge_output_format': format_type,
                    'quiet': True,
                    'no_warnings': True,
                }

                # Add thumbnail embedding if requested
                if embed_thumbnail:
                    ydl_opts['writethumbnail'] = True
                    ydl_opts['postprocessors'] = [{
                        'key': 'EmbedThumbnail',
                    }]

            # Add metadata embedding
            if embed_metadata:
                if 'postprocessors' not in ydl_opts:
                    ydl_opts['postprocessors'] = []
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                })

            # Perform download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Get the filename of the downloaded file
                if audio_only:
                    filename = ydl.prepare_filename(info)
                    # Replace extension with the audio format
                    filename = Path(filename).with_suffix(f'.{format_type}')
                else:
                    filename = ydl.prepare_filename(info)

                self.send_complete(str(filename))

        except Exception as e:
            self.send_error('Download failed', str(e))


def main():
    """Main entry point for the bridge."""
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No command specified'}))
        sys.exit(1)

    command = sys.argv[1]
    bridge = ElectronBridge()

    if command == 'get-info':
        # Get video info
        if len(sys.argv) < 3:
            print(json.dumps({'error': 'No URL specified'}))
            sys.exit(1)

        url = sys.argv[2]
        info = bridge.get_video_info(url)
        print(json.dumps(info))

    elif command == 'download':
        # Download video
        if len(sys.argv) < 3:
            print(json.dumps({'error': 'No options specified'}))
            sys.exit(1)

        try:
            options = json.loads(sys.argv[2])

            bridge.output_dir = Path(options.get('outputFolder', 'downloads'))
            bridge.output_dir.mkdir(exist_ok=True)

            bridge.download_video(
                url=options['url'],
                format_type=options.get('format', 'mp4'),
                quality=options.get('quality', 'best'),
                audio_only=options.get('audioOnly', False),
                audio_track=options.get('audioTrack', 'auto'),
                embed_thumbnail=options.get('embedThumbnail', False),
                embed_metadata=options.get('embedMetadata', True)
            )
        except json.JSONDecodeError as e:
            print(json.dumps({'error': 'Invalid JSON options', 'details': str(e)}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({'error': 'Download failed', 'details': str(e)}))
            sys.exit(1)

    else:
        print(json.dumps({'error': f'Unknown command: {command}'}))
        sys.exit(1)


if __name__ == '__main__':
    main()
