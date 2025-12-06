#!/usr/bin/env python3
"""
YouTube Downloader CLI - Command-line interface for downloading YouTube videos
"""

import argparse
import sys
from pathlib import Path
from colorama import Fore, Style, init
from youtube_downloader import YouTubeDownloader

init(autoreset=True)


def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║           YouTube Downloader v1.0                        ║
║  Download videos and audio from YouTube with ease       ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)


def read_urls_from_file(file_path: str) -> list:
    """
    Read URLs from a text file (one URL per line).

    Args:
        file_path: Path to the file containing URLs

    Returns:
        List of URLs
    """
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except Exception as e:
        print(f"{Fore.RED}Error reading file {file_path}: {str(e)}{Style.RESET_ALL}")
        return []


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Download videos and audio from YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download a single video
  python youtube_dl_cli.py https://www.youtube.com/watch?v=VIDEO_ID

  # Download audio only (MP3)
  python youtube_dl_cli.py -a https://www.youtube.com/watch?v=VIDEO_ID

  # Download multiple videos
  python youtube_dl_cli.py URL1 URL2 URL3

  # Download from a playlist
  python youtube_dl_cli.py -p https://www.youtube.com/playlist?list=PLAYLIST_ID

  # Download videos from a file (one URL per line)
  python youtube_dl_cli.py -f urls.txt

  # Specify output format and quality
  python youtube_dl_cli.py -q 720p -F mp4 URL

  # Download audio with specific quality
  python youtube_dl_cli.py -a -q 320 URL
        """
    )

    parser.add_argument(
        'urls',
        nargs='*',
        help='YouTube URL(s) to download'
    )

    parser.add_argument(
        '-a', '--audio',
        action='store_true',
        help='Download audio only (default: MP3)'
    )

    parser.add_argument(
        '-p', '--playlist',
        action='store_true',
        help='Download entire playlist'
    )

    parser.add_argument(
        '-f', '--file',
        type=str,
        metavar='FILE',
        help='Read URLs from a text file (one URL per line)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='downloads',
        metavar='DIR',
        help='Output directory (default: downloads)'
    )

    parser.add_argument(
        '-F', '--format',
        type=str,
        metavar='FORMAT',
        help='Output format (mp4, webm, mkv for video; mp3, m4a, opus for audio)'
    )

    parser.add_argument(
        '-q', '--quality',
        type=str,
        metavar='QUALITY',
        help='Quality (best, 1080p, 720p, 480p for video; 128, 192, 256, 320 for audio bitrate)'
    )

    parser.add_argument(
        '--start',
        type=int,
        default=1,
        metavar='N',
        help='Playlist: start from video N (default: 1)'
    )

    parser.add_argument(
        '--end',
        type=int,
        metavar='N',
        help='Playlist: end at video N'
    )

    parser.add_argument(
        '-i', '--info',
        action='store_true',
        help='Show video information without downloading'
    )

    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Hide banner'
    )

    args = parser.parse_args()

    # Print banner
    if not args.no_banner:
        print_banner()

    # Collect URLs
    urls = []
    if args.file:
        urls = read_urls_from_file(args.file)
        if not urls:
            print(f"{Fore.RED}No valid URLs found in file{Style.RESET_ALL}")
            sys.exit(1)
    elif args.urls:
        urls = args.urls
    else:
        parser.print_help()
        sys.exit(1)

    # Initialize downloader
    downloader = YouTubeDownloader(output_dir=args.output)

    # Show info only
    if args.info:
        for url in urls:
            print(f"\n{Fore.CYAN}Getting info for: {url}{Style.RESET_ALL}")
            info = downloader.get_video_info(url)
            if info:
                print(f"{Fore.GREEN}Title:{Style.RESET_ALL} {info['title']}")
                print(f"{Fore.GREEN}Uploader:{Style.RESET_ALL} {info['uploader']}")
                print(f"{Fore.GREEN}Duration:{Style.RESET_ALL} {info['duration']} seconds")
                print(f"{Fore.GREEN}Views:{Style.RESET_ALL} {info['view_count']:,}")
        sys.exit(0)

    # Determine format and quality
    if args.audio:
        format_type = args.format or 'mp3'
        quality = args.quality or '192'
    else:
        format_type = args.format or 'mp4'
        quality = args.quality or 'best'

    # Download based on mode
    try:
        if args.playlist:
            # Playlist mode
            if len(urls) > 1:
                print(f"{Fore.YELLOW}Warning: Multiple URLs provided with -p flag. Only the first URL will be treated as a playlist.{Style.RESET_ALL}")

            success = downloader.download_playlist(
                playlist_url=urls[0],
                audio_only=args.audio,
                format_type=format_type,
                quality=quality,
                start_index=args.start,
                end_index=args.end
            )

            if success:
                print(f"\n{Fore.GREEN}All downloads completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Files saved to: {Path(args.output).absolute()}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Playlist download failed{Style.RESET_ALL}")
                sys.exit(1)

        elif len(urls) > 1:
            # Multiple videos mode
            results = downloader.download_multiple(
                urls=urls,
                audio_only=args.audio,
                format_type=format_type,
                quality=quality
            )

            failed = [url for url, success in results.items() if not success]
            if failed:
                print(f"\n{Fore.YELLOW}Some downloads failed:{Style.RESET_ALL}")
                for url in failed:
                    print(f"  {Fore.RED}✗ {url}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}Files saved to: {Path(args.output).absolute()}{Style.RESET_ALL}")

        else:
            # Single video mode
            if args.audio:
                success = downloader.download_audio(
                    url=urls[0],
                    format_type=format_type,
                    quality=quality
                )
            else:
                success = downloader.download_video(
                    url=urls[0],
                    format_type=format_type,
                    quality=quality
                )

            if success:
                print(f"\n{Fore.GREEN}Download completed successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}File saved to: {Path(args.output).absolute()}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}Download failed{Style.RESET_ALL}")
                sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Download interrupted by user{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
