#!/usr/bin/env python3
"""
YouTube Downloader - Download videos and audio from YouTube
Supports single videos, multiple videos, and playlists
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import yt_dlp
from colorama import Fore, Style, init

init(autoreset=True)


class YouTubeDownloader:
    """
    A comprehensive YouTube downloader that supports:
    - Single video downloads
    - Multiple video downloads
    - Playlist downloads
    - Audio-only (MP3) downloads
    - Video downloads (MP4/other formats)
    """

    def __init__(self, output_dir: str = "downloads"):
        """
        Initialize the YouTube downloader.

        Args:
            output_dir: Directory where downloads will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def _get_progress_hooks(self):
        """Return progress hook for download tracking."""
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    percent = d.get('_percent_str', 'N/A')
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    print(f"\r{Fore.CYAN}Downloading: {percent} at {speed} ETA: {eta}{Style.RESET_ALL}", end='')
                except:
                    pass
            elif d['status'] == 'finished':
                print(f"\r{Fore.GREEN}Download completed! Processing...{Style.RESET_ALL}")

        return [progress_hook]

    def download_video(
        self,
        url: str,
        format_type: str = "mp4",
        quality: str = "best"
    ) -> bool:
        """
        Download a single video.

        Args:
            url: YouTube video URL
            format_type: Output format (mp4, webm, mkv, etc.)
            quality: Video quality (best, 720p, 1080p, etc.)

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Fore.YELLOW}Downloading video: {url}{Style.RESET_ALL}")

        ydl_opts = {
            'format': self._get_video_format_string(quality),
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'progress_hooks': self._get_progress_hooks(),
            'merge_output_format': format_type,
            'postprocessor_args': [
                '-c:v', 'copy',
                '-c:a', 'aac',
            ],
            'quiet': False,
            'no_warnings': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"{Fore.GREEN}✓ Successfully downloaded video{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ Error downloading video: {str(e)}{Style.RESET_ALL}")
            return False

    def download_audio(
        self,
        url: str,
        format_type: str = "mp3",
        quality: str = "192"
    ) -> bool:
        """
        Download audio only.

        Args:
            url: YouTube video URL
            format_type: Audio format (mp3, m4a, opus, etc.)
            quality: Audio bitrate in kbps (128, 192, 256, 320)

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Fore.YELLOW}Downloading audio: {url}{Style.RESET_ALL}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'progress_hooks': self._get_progress_hooks(),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_type,
                'preferredquality': quality,
            }],
            'quiet': False,
            'no_warnings': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"{Fore.GREEN}✓ Successfully downloaded audio{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ Error downloading audio: {str(e)}{Style.RESET_ALL}")
            return False

    def download_multiple(
        self,
        urls: List[str],
        audio_only: bool = False,
        format_type: str = None,
        quality: str = None
    ) -> Dict[str, bool]:
        """
        Download multiple videos or audio files.

        Args:
            urls: List of YouTube URLs
            audio_only: If True, download audio only
            format_type: Output format
            quality: Quality setting

        Returns:
            Dictionary mapping URLs to success status
        """
        print(f"\n{Fore.CYAN}Starting batch download of {len(urls)} items...{Style.RESET_ALL}\n")

        results = {}
        for i, url in enumerate(urls, 1):
            print(f"\n{Fore.MAGENTA}[{i}/{len(urls)}]{Style.RESET_ALL}")

            if audio_only:
                fmt = format_type or "mp3"
                qual = quality or "192"
                success = self.download_audio(url, fmt, qual)
            else:
                fmt = format_type or "mp4"
                qual = quality or "best"
                success = self.download_video(url, fmt, qual)

            results[url] = success

        # Print summary
        successful = sum(1 for v in results.values() if v)
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Completed: {successful}/{len(urls)} successful{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

        return results

    def download_playlist(
        self,
        playlist_url: str,
        audio_only: bool = False,
        format_type: str = None,
        quality: str = None,
        start_index: int = 1,
        end_index: Optional[int] = None
    ) -> bool:
        """
        Download an entire playlist.

        Args:
            playlist_url: YouTube playlist URL
            audio_only: If True, download audio only
            format_type: Output format
            quality: Quality setting
            start_index: Start from this video in playlist (1-indexed)
            end_index: End at this video in playlist (inclusive, optional)

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Fore.YELLOW}Downloading playlist: {playlist_url}{Style.RESET_ALL}")

        if audio_only:
            fmt = format_type or "mp3"
            qual = quality or "192"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
                'progress_hooks': self._get_progress_hooks(),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': fmt,
                    'preferredquality': qual,
                }],
                'quiet': False,
                'no_warnings': False,
            }
        else:
            fmt = format_type or "mp4"
            qual = quality or "best"
            ydl_opts = {
                'format': self._get_video_format_string(qual),
                'outtmpl': str(self.output_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
                'progress_hooks': self._get_progress_hooks(),
                'merge_output_format': fmt,
                'quiet': False,
                'no_warnings': False,
            }

        # Add playlist range if specified
        if end_index:
            ydl_opts['playlist_items'] = f'{start_index}-{end_index}'
        elif start_index > 1:
            ydl_opts['playlist_items'] = f'{start_index}-'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                if 'entries' in info:
                    num_videos = len(list(info['entries']))
                    print(f"{Fore.CYAN}Found {num_videos} videos in playlist{Style.RESET_ALL}\n")

                ydl.download([playlist_url])

            print(f"{Fore.GREEN}✓ Successfully downloaded playlist{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ Error downloading playlist: {str(e)}{Style.RESET_ALL}")
            return False

    def _get_video_format_string(self, quality: str) -> str:
        """
        Get the format string for yt-dlp based on quality.

        Args:
            quality: Quality descriptor (best, 1080p, 720p, etc.)

        Returns:
            Format string for yt-dlp
        """
        quality_map = {
            'best': 'bestvideo+bestaudio/best',
            '2160p': 'bestvideo[height<=2160]+bestaudio/best',
            '1440p': 'bestvideo[height<=1440]+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best',
            '720p': 'bestvideo[height<=720]+bestaudio/best',
            '480p': 'bestvideo[height<=480]+bestaudio/best',
            '360p': 'bestvideo[height<=360]+bestaudio/best',
        }

        return quality_map.get(quality.lower(), 'bestvideo+bestaudio/best')

    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a video without downloading it.

        Args:
            url: YouTube video URL

        Returns:
            Dictionary with video information or None if error
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'description': info.get('description'),
                }
        except Exception as e:
            print(f"{Fore.RED}Error getting video info: {str(e)}{Style.RESET_ALL}")
            return None


if __name__ == "__main__":
    print(f"{Fore.CYAN}YouTube Downloader{Style.RESET_ALL}")
    print("Use youtube_dl_cli.py for command-line interface\n")
