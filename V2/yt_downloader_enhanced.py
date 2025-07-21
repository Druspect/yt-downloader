import os
import json
import re
import sys
import subprocess
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import yt_dlp
from googleapiclient.discovery import build
from termcolor import colored
from mutagen.easyid3 import EasyID3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yt_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DownloadItem:
    """Represents a single download item with metadata."""
    url_or_query: str
    media_type: str = 'audio'  # 'audio' or 'video'
    quality: str = 'best'
    status: str = 'pending'  # 'pending', 'processing', 'completed', 'failed'
    error_message: str = ''
    file_path: str = ''
    title: str = ''
    duration: str = ''
    view_count: int = 0
    
@dataclass
class QualityInfo:
    """Represents quality information for a video."""
    format_id: str
    ext: str
    resolution: str
    filesize: Optional[int]
    fps: Optional[int]
    vcodec: str
    acodec: str
    
class YouTubeDownloaderEnhanced:
    """Enhanced YouTube downloader with batch processing and quality verification."""
    
    def __init__(self, api_key: str, download_path: str):
        self.api_key = api_key
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.download_queue: List[DownloadItem] = []
        
    def validate_youtube_url(self, url: str) -> bool:
        """Validate if a URL is a valid YouTube URL."""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(youtube_regex.match(url))
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get video information using YouTube API."""
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if response['items']:
                return response['items'][0]
            return None
        except Exception as e:
            logger.error(f"Error fetching video info for {video_id}: {e}")
            return None
    
    def get_available_qualities(self, url: str) -> List[QualityInfo]:
        """Get available quality options for a video."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'listformats': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                quality_list = []
                for fmt in formats:
                    if fmt.get('vcodec') != 'none' or fmt.get('acodec') != 'none':
                        quality_info = QualityInfo(
                            format_id=fmt.get('format_id', ''),
                            ext=fmt.get('ext', ''),
                            resolution=fmt.get('resolution', 'audio only'),
                            filesize=fmt.get('filesize'),
                            fps=fmt.get('fps'),
                            vcodec=fmt.get('vcodec', 'none'),
                            acodec=fmt.get('acodec', 'none')
                        )
                        quality_list.append(quality_info)
                
                return quality_list
        except Exception as e:
            logger.error(f"Error getting qualities for {url}: {e}")
            return []
    
    def verify_url_accessibility(self, url: str) -> Tuple[bool, str]:
        """Verify if a YouTube URL is accessible and downloadable."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'simulate': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return True, "URL is accessible"
                else:
                    return False, "Unable to extract video information"
                    
        except yt_dlp.DownloadError as e:
            return False, f"Download error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def search_youtube(self, query: str, max_results: int = 15) -> List[Dict]:
        """Search YouTube for videos and return results with quality verification."""
        try:
            search_response = self.youtube.search().list(
                q=query,
                type='video',
                part='id,snippet',
                maxResults=max_results,
                order='relevance'
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Verify accessibility
                is_accessible, message = self.verify_url_accessibility(video_url)
                
                video_info = {
                    'title': item['snippet']['title'],
                    'id': video_id,
                    'url': video_url,
                    'channel': item['snippet']['channelTitle'],
                    'description': item['snippet']['description'][:200] + '...',
                    'accessible': is_accessible,
                    'access_message': message
                }
                
                # Get additional info from API
                api_info = self.get_video_info(video_id)
                if api_info:
                    video_info.update({
                        'duration': api_info['contentDetails']['duration'],
                        'view_count': int(api_info['statistics'].get('viewCount', 0)),
                        'like_count': int(api_info['statistics'].get('likeCount', 0))
                    })
                
                videos.append(video_info)
            
            # Sort by view count (descending)
            videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)
            return videos
            
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    def add_to_queue(self, items: List[str], media_type: str = 'audio', quality: str = 'best'):
        """Add items to download queue with validation."""
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            download_item = DownloadItem(
                url_or_query=item,
                media_type=media_type,
                quality=quality
            )
            
            # Validate if it's a URL
            if self.validate_youtube_url(item):
                is_accessible, message = self.verify_url_accessibility(item)
                if not is_accessible:
                    download_item.status = 'failed'
                    download_item.error_message = f"URL validation failed: {message}"
                    logger.warning(f"Invalid URL {item}: {message}")
            
            self.download_queue.append(download_item)
            logger.info(f"Added to queue: {item}")
    
    def load_batch_from_file(self, file_path: str) -> List[str]:
        """Load batch items from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                items = [line.strip() for line in f.readlines() if line.strip()]
            logger.info(f"Loaded {len(items)} items from {file_path}")
            return items
        except Exception as e:
            logger.error(f"Error loading batch file {file_path}: {e}")
            return []
    
    def download_single_item(self, item: DownloadItem) -> bool:
        """Download a single item from the queue."""
        item.status = 'processing'
        
        try:
            # If it's not a URL, search for it
            if not self.validate_youtube_url(item.url_or_query):
                search_results = self.search_youtube(item.url_or_query, max_results=5)
                if not search_results:
                    item.status = 'failed'
                    item.error_message = 'No search results found'
                    return False
                
                # Use the first accessible result
                accessible_results = [r for r in search_results if r['accessible']]
                if not accessible_results:
                    item.status = 'failed'
                    item.error_message = 'No accessible videos found in search results'
                    return False
                
                video_url = accessible_results[0]['url']
                item.title = accessible_results[0]['title']
            else:
                video_url = item.url_or_query
            
            # Set up yt-dlp options
            output_template = str(self.download_path / '%(title)s.%(ext)s')
            
            ydl_opts = {
                'format': self._get_format_selector(item.media_type, item.quality),
                'outtmpl': output_template,
                'noplaylist': True,
                'extractaudio': item.media_type == 'audio',
                'audioformat': 'mp3' if item.media_type == 'audio' else None,
                'audioquality': '192' if item.media_type == 'audio' else None,
                'retries': 3,
                'fragment_retries': 3,
                'ignoreerrors': False,
                'no_warnings': False
            }
            
            if item.media_type == 'audio':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            # Download the media
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                expected_filename = ydl.prepare_filename(info)
                
                # Check if file already exists
                if os.path.exists(expected_filename):
                    logger.info(f"File already exists: {expected_filename}")
                    item.file_path = expected_filename
                    item.status = 'completed'
                    return True
                
                # Download the file
                ydl.download([video_url])
                
                # Update item info
                item.title = info.get('title', '')
                item.duration = info.get('duration_string', '')
                item.view_count = info.get('view_count', 0)
                item.file_path = expected_filename
                item.status = 'completed'
                
                logger.info(f"Successfully downloaded: {item.title}")
                return True
                
        except Exception as e:
            item.status = 'failed'
            item.error_message = str(e)
            logger.error(f"Error downloading {item.url_or_query}: {e}")
            return False
    
    def _get_format_selector(self, media_type: str, quality: str) -> str:
        """Get format selector string for yt-dlp."""
        if media_type == 'audio':
            return 'bestaudio/best'
        elif quality == 'best':
            return 'bestvideo+bestaudio/best'
        elif quality == 'worst':
            return 'worstvideo+worstaudio/worst'
        else:
            # Assume quality is a specific format
            return quality
    
    def process_queue(self, progress_callback=None) -> Dict[str, int]:
        """Process all items in the download queue."""
        results = {'completed': 0, 'failed': 0, 'total': len(self.download_queue)}
        
        for i, item in enumerate(self.download_queue):
            if item.status == 'failed':
                results['failed'] += 1
                continue
                
            if progress_callback:
                progress_callback(i + 1, results['total'], item.url_or_query)
            
            success = self.download_single_item(item)
            if success:
                results['completed'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def get_queue_status(self) -> Dict:
        """Get current status of the download queue."""
        status = {
            'total': len(self.download_queue),
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0
        }
        
        for item in self.download_queue:
            status[item.status] += 1
        
        return status
    
    def clear_queue(self):
        """Clear the download queue."""
        self.download_queue.clear()
        logger.info("Download queue cleared")
    
    def export_results(self, file_path: str):
        """Export download results to a JSON file."""
        results = []
        for item in self.download_queue:
            results.append({
                'url_or_query': item.url_or_query,
                'media_type': item.media_type,
                'quality': item.quality,
                'status': item.status,
                'error_message': item.error_message,
                'file_path': item.file_path,
                'title': item.title,
                'duration': item.duration,
                'view_count': item.view_count
            })
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results exported to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting results: {e}")

def install_dependencies():
    """Install required dependencies."""
    packages = {
        'google-api-python-client': 'googleapiclient',
        'termcolor': 'termcolor',
        'mutagen': 'mutagen',
        'yt-dlp': 'yt_dlp'
    }
    
    print(colored("Checking and installing dependencies...", 'yellow'))
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(colored(f"{package_name} is already installed.", 'green'))
        except ImportError:
            print(colored(f"{package_name} not found. Installing...", 'yellow'))
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
                print(colored(f"Successfully installed {package_name}.", 'green'))
            except subprocess.CalledProcessError as e:
                print(colored(f"Failed to install {package_name}: {e}", 'red'))
                sys.exit(1)

def main():
    """Main function for command-line usage."""
    install_dependencies()
    
    # Get API key and download path
    api_key = input(colored("Enter your YouTube Data API key: ", 'cyan'))
    download_path = input(colored("Enter download directory: ", 'cyan'))
    
    # Initialize downloader
    downloader = YouTubeDownloaderEnhanced(api_key, download_path)
    
    while True:
        print(colored("\n=== YouTube Downloader Enhanced ===", 'green'))
        print(colored("1. Add single URL/query", 'white'))
        print(colored("2. Load batch from file", 'white'))
        print(colored("3. Add multiple items (manual entry)", 'white'))
        print(colored("4. View queue status", 'white'))
        print(colored("5. Process queue", 'white'))
        print(colored("6. Clear queue", 'white'))
        print(colored("7. Export results", 'white'))
        print(colored("8. Exit", 'white'))
        
        choice = input(colored("Select option: ", 'cyan'))
        
        if choice == '1':
            item = input(colored("Enter YouTube URL or search query: ", 'cyan'))
            media_type = input(colored("Media type (audio/video) [audio]: ", 'cyan')) or 'audio'
            downloader.add_to_queue([item], media_type)
            
        elif choice == '2':
            file_path = input(colored("Enter file path: ", 'cyan'))
            items = downloader.load_batch_from_file(file_path)
            if items:
                media_type = input(colored("Media type (audio/video) [audio]: ", 'cyan')) or 'audio'
                downloader.add_to_queue(items, media_type)
                
        elif choice == '3':
            print(colored("Enter items (one per line, empty line to finish):", 'cyan'))
            items = []
            while True:
                item = input()
                if not item:
                    break
                items.append(item)
            if items:
                media_type = input(colored("Media type (audio/video) [audio]: ", 'cyan')) or 'audio'
                downloader.add_to_queue(items, media_type)
                
        elif choice == '4':
            status = downloader.get_queue_status()
            print(colored(f"Queue Status: {status}", 'yellow'))
            
        elif choice == '5':
            if not downloader.download_queue:
                print(colored("Queue is empty!", 'red'))
                continue
                
            def progress_callback(current, total, item):
                print(colored(f"Processing {current}/{total}: {item}", 'blue'))
            
            results = downloader.process_queue(progress_callback)
            print(colored(f"Download completed: {results}", 'green'))
            
        elif choice == '6':
            downloader.clear_queue()
            print(colored("Queue cleared!", 'yellow'))
            
        elif choice == '7':
            file_path = input(colored("Enter export file path: ", 'cyan'))
            downloader.export_results(file_path)
            
        elif choice == '8':
            break
            
        else:
            print(colored("Invalid option!", 'red'))

if __name__ == "__main__":
    main()

