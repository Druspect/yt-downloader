import os
import webbrowser
import subprocess
import sys
import re
import pip
from googleapiclient.discovery import build
from termcolor import colored
from mutagen.easyid3 import EasyID3

# Function to install missing dependencies
def install_dependencies():
    """Attempt to install required Python packages if they are not already installed."""
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
            print(colored(f"{package_name} not found. Attempting to install...", 'yellow'))
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
                print(colored(f"Successfully installed {package_name}.", 'green'))
            except subprocess.CalledProcessError as e:
                print(colored(f"Failed to install {package_name}: {str(e)}. Please install it manually.", 'red'))
                print(colored(f"Run: pip install {package_name}", 'red'))
                sys.exit(1)

    # Special case for yt-dlp executable
    try:
        subprocess.run(["yt-dlp", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(colored("yt-dlp executable is already installed.", 'green'))
    except FileNotFoundError:
        print(colored("yt-dlp executable not found. Attempting to install via pip...", 'yellow'))
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp'])
            print(colored("Successfully installed yt-dlp.", 'green'))
        except subprocess.CalledProcessError as e:
            print(colored(f"Failed to install yt-dlp: {str(e)}. Please install it manually from https://github.com/yt-dlp/yt-dlp", 'red'))
            sys.exit(1)

# Function to check for required dependencies
def check_dependencies():
    """Ensure all required dependencies are installed."""
    try:
        import googleapiclient
    except ImportError:
        print(colored("googleapiclient is not installed.", 'red'))
        sys.exit(1)
    try:
        import termcolor
    except ImportError:
        print(colored("termcolor is not installed.", 'red'))
        sys.exit(1)
    try:
        subprocess.run(["yt-dlp", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(colored("yt-dlp is not installed.", 'red'))
        sys.exit(1)
    try:
        import mutagen
    except ImportError:
        print(colored("mutagen is not installed.", 'red'))
        sys.exit(1)

# Function to print a styled header
def print_header(text):
    """Print a cyan-colored header with borders."""
    print(colored("=" * 50, 'cyan'))
    print(colored(text.center(50), 'cyan'))
    print(colored("=" * 50, 'cyan'))

# Function to print a styled section
def print_section(text):
    """Print a yellow-colored section with borders."""
    print(colored("-" * 50, 'yellow'))
    print(colored(text, 'yellow'))
    print(colored("-" * 50, 'yellow'))

# Function to sanitize filenames
def sanitize_filename(name):
    """Replace invalid characters in filenames with underscores."""
    return re.sub(r'[^\w\-_\. ]', '_', name)

# Function to extract artist and song from title
def extract_metadata(title):
    """Attempt to split the title into artist and song."""
    parts = title.split(" - ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "Unknown Artist", title

# Function to search YouTube for top videos
def get_top_videos(youtube, query, max_results=15):
    """Retrieve the top 15 YouTube videos based on a search query."""
    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            order="viewCount",
            maxResults=max_results
        )
        response = request.execute()
        videos = []
        for item in response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            videos.append({
                'title': title,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            })
        return videos
    except Exception as e:
        print(colored(f"Search failed: {str(e)}", 'red'))
        return []

# Function to download file with yt-dlp
def download_file(url, output_path, download_type, verbose=False):
    """Download audio or video using yt-dlp."""
    cmd = ["yt-dlp", "-o", output_path, url]
    if download_type == 'audio':
        cmd.extend(["-x", "--audio-format", "mp3"])
    if verbose:
        cmd.append("--verbose")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr

# Main function to run the downloader
def main():
    """Main program logic for the YouTube Downloader."""
    # Install and check dependencies
    install_dependencies()
    check_dependencies()
    
    # Welcome message
    print_header("Welcome to the YouTube Downloader!")
    print_section("Download audio or video from YouTube with ease.")
    
    # Hardcoded YouTube API key (replace with your own)
    API_KEY = ""  # Replace with your YouTube Data API key
    if not API_KEY:
        print(colored("Error: No YouTube Data API key found.", 'red'))
        print(colored("Please add your API key to the 'API_KEY' variable in the script.", 'red'))
        print(colored("See the guide for obtaining a key at: [insert guide location or URL]", 'red'))
        sys.exit(1)
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Get folder path for saving files
    folder = input(colored("Enter the folder path to save files: ", 'green'))
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(colored(f"Created folder: {folder}", 'green'))
    else:
        print(colored(f"Using existing folder: {folder}", 'green'))
    
    # Get default album name for audio metadata
    default_album = input(colored("Enter default album name (default: 'YouTube Downloads'): ", 'green')) or "YouTube Downloads"
    
    # Main loop for downloading
    while True:
        song = input(colored("Enter a song name or YouTube URL (or 'done' to finish): ", 'green'))
        if song.lower() == 'done':
            break
        
        if song.startswith('http'):
            # Handle direct URL
            result = subprocess.run(["yt-dlp", "--get-title", song], capture_output=True, text=True)
            if result.returncode == 0:
                title = result.stdout.strip()
                selected_video = {'title': title, 'url': song}
            else:
                print(colored("Failed to get video title. Please check the URL.", 'red'))
                continue
        else:
            # Search for videos
            videos = get_top_videos(youtube, song)
            if not videos:
                print(colored(f"No videos found for: {song}", 'red'))
                continue
            
            print_section("Top 15 search results:")
            for i, video in enumerate(videos, 1):
                print(colored(f"{i}. {video['title']}", 'white'))
            
            choice = input(colored("Enter the number of the correct video (or 'skip'): ", 'green'))
            if choice.lower() == 'skip':
                continue
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= 15:
                    selected_video = videos[choice_num - 1]
                else:
                    print(colored("Invalid number. Please enter 1-15.", 'red'))
                    continue
            except ValueError:
                print(colored("Invalid input. Enter a number or 'skip'.", 'red'))
                continue
        
        # Display selected video
        print(colored(f"Selected: {selected_video['title']}", 'green'))
        
        # Extract and edit metadata
        artist, song_title = extract_metadata(selected_video['title'])
        print(colored(f"Extracted Artist: {artist}", 'yellow'))
        print(colored(f"Extracted Song: {song_title}", 'yellow'))
        edit = input(colored("Edit artist and song name? (yes/no): ", 'green'))
        if edit.lower() == 'yes':
            artist = input(colored("Enter artist name: ", 'green'))
            song_title = input(colored("Enter song title: ", 'green'))
        
        # Open video for confirmation
        webbrowser.open(selected_video['url'])
        print(colored("Video playing in browser. Confirm it’s correct.", 'yellow'))
        
        # Confirm download
        confirm = input(colored("Download this? (yes/no): ", 'green'))
        if confirm.lower() != 'yes':
            print(colored("Skipping download.", 'yellow'))
            continue
        
        # Choose download type
        download_type = input(colored("Download audio or video? (audio/video): ", 'green')).lower()
        if download_type not in ['audio', 'video']:
            print(colored("Invalid choice. Skipping download.", 'red'))
            continue
        
        # Set output path
        if download_type == 'audio':
            output_filename = f"{sanitize_filename(song_title)}.mp3"
            extension = ".mp3"
        else:
            output_filename = f"{sanitize_filename(song_title)}.%(ext)s"
            extension = ".%(ext)s"
        
        output_path = os.path.join(folder, output_filename)
        counter = 1
        base_filename = output_filename.split('.')[0]
        while os.path.exists(output_path):
            output_filename = f"{base_filename}_{counter}{extension}"
            output_path = os.path.join(folder, output_filename)
            counter += 1
        
        # Attempt download
        success, error_msg = download_file(selected_video['url'], output_path, download_type, verbose=True)
        if success:
            if download_type == 'audio':
                try:
                    audio = EasyID3(output_path)
                    audio['title'] = song_title
                    audio['artist'] = artist
                    audio['album'] = default_album
                    audio.save()
                    print(colored(f"Audio downloaded and metadata set: {output_filename}", 'green'))
                except Exception as e:
                    print(colored(f"Metadata setting failed: {str(e)}", 'red'))
            else:
                print(colored(f"Video downloaded: {output_filename}", 'green'))
        else:
            print(colored(f"{download_type.capitalize()} download failed: {error_msg}", 'red'))
            retry = input(colored("Retry with verbose output? (yes/no): ", 'green'))
            if retry.lower() == 'yes':
                success, error_msg = download_file(selected_video['url'], output_path, download_type, verbose=True)
                if success:
                    print(colored(f"{download_type.capitalize()} downloaded successfully on retry!", 'green'))
                else:
                    print(colored(f"Retry failed: {error_msg}", 'red'))
    
    # Farewell message
    print_header("All downloads complete!")
    print_header("Enjoy your music and videos!")

if __name__ == "__main__":
    main()
