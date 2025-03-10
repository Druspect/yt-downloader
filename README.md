# YouTube Downloader

A Python script to download audio (MP3) or video files from YouTube by searching or using direct URLs. Features include metadata editing for audio files and robust error handling.

-----------------------------------------------------------------------------------------

## Features
- Search YouTube for the top 15 videos by view count.
- Download audio (MP3) or video files.
- Edit artist and song metadata for MP3s.
- Automatic dependency installation.
- Verbose error reporting for failed downloads.
  
-----------------------------------------------------------------------------------------

## Prerequisites
- Python 3.6 or higher
- A YouTube Data API key (see [GETTING_API_KEY.md](docs/GETTING_API_KEY.md))

-----------------------------------------------------------------------------------------

## Installation

**Clone the Repository**:
- git clone https://github.com/yourusername/youtube-downloader.git
- cd youtube-downloader
- Install Dependencies: The script will attempt to install dependencies automatically on first run. 
  
Add Your YouTube API Key:
- Open youtube_downloader.py in a text editor.
- Find API_KEY = "" (around line 150).
- Replace "" with your API key (e.g., API_KEY = "YOUR_API_KEY_HERE").
- Save the file. See GETTING_API_KEY.md for instructions.

-----------------------------------------------------------------------------------------
## Usage
Run the Script:
- python youtube_downloader.py

## Follow Prompts:
- Enter a folder path to save files.
- Enter a song name or YouTube URL (or "done" to exit).
- Select a video from the search results (if searching).
- Choose to download audio or video.
- Edit metadata if downloading audio.

-----------------------------------------------------------------------------------------

## Troubleshooting
- Download Fails: Update yt-dlp with pip install -U yt-dlp if you encounter HTTP errors (e.g., 403 Forbidden).
- API Key Issues: Ensure your key is valid and has quota remaining.

-----------------------------------------------------------------------------------------

## License
This project is licensed under the MIT License - see LICENSE for details.

-----------------------------------------------------------------------------------------

## Acknowledgments
Built with yt-dlp and Google API Client.
