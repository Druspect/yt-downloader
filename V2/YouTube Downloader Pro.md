# YouTube Downloader Pro

A comprehensive, production-ready YouTube downloader with Spotify playlist integration, batch processing, quality verification, and a modern GUI interface.

## Features

### 🎵 Core Functionality
- **YouTube Downloads**: Download audio (MP3) or video files from YouTube
- **Search Integration**: Search YouTube directly within the app
- **Quality Selection**: Choose from available quality options
- **Metadata Editing**: Automatic metadata tagging for audio files

### 🎧 Spotify Integration
- **Playlist Conversion**: Convert Spotify playlists to YouTube URLs
- **Automatic Matching**: Find YouTube equivalents for Spotify tracks
- **Verification**: Verify URL accessibility and quality
- **Batch Processing**: Process entire playlists at once

### 📋 Batch Processing
- **File Input**: Load URLs from text files
- **Manual Entry**: Enter multiple URLs in the interface
- **Queue Management**: Add, remove, and reorder downloads
- **Progress Tracking**: Real-time progress monitoring

### 🖥️ User Interface
- **Modern GUI**: Clean, intuitive Tkinter interface
- **Tabbed Layout**: Organized workflow with dedicated tabs
- **Real-time Logs**: Built-in logging and debugging
- **Settings Management**: Persistent configuration storage

### 🔧 Production Features
- **Error Handling**: Robust error recovery and reporting
- **Logging**: Comprehensive logging system
- **Configuration**: Persistent settings storage
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.7 or higher
- Internet connection
- YouTube Data API v3 key
- Spotify API credentials (optional, for Spotify features)

### Quick Setup

1. **Clone or download the project files**
2. **Run the setup script**:
   ```bash
   python setup.py
   ```
3. **Start the application**:
   ```bash
   python yt_downloader_gui.py
   ```

### Manual Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create directories**:
   ```bash
   mkdir -p ~/Downloads/YouTube
   mkdir logs
   ```

## API Setup

### YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key for use in the application

### Spotify API (Optional)

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Note down Client ID and Client Secret
4. Add redirect URI: `http://localhost:8080/callback`

## Usage

### First Time Setup

1. **Launch the application**:
   ```bash
   python yt_downloader_gui.py
   ```

2. **Configure API keys**:
   - Go to the "Settings" tab
   - Enter your YouTube Data API key
   - Enter Spotify credentials (if using Spotify features)
   - Set your preferred download directory
   - Click "Save Settings"

3. **Test connection**:
   - Click "Test Connection" to verify API setup

### Downloading Videos

#### Single Downloads
1. Go to the "Download" tab
2. Enter a YouTube URL or search query
3. Select audio or video format
4. Click "Add to Queue" or "Download Now"

#### Batch Downloads
1. Go to the "Batch" tab
2. Either:
   - Load URLs from a text file, or
   - Enter URLs manually (one per line)
3. Select media type (audio/video)
4. Click "Add to Queue"

#### Spotify Playlists
1. Go to the "Spotify" tab
2. Enter a Spotify playlist URL
3. Click "Load Playlist"
4. Click "Convert to YouTube" to find YouTube equivalents
5. Click "Add All to Queue" to add to download queue

### Managing Downloads

1. Go to the "Queue" tab
2. Review queued downloads
3. Click "Start Downloads" to begin processing
4. Monitor progress in real-time
5. Export results when complete

## File Structure

```
youtube-downloader-pro/
├── yt_downloader_enhanced.py    # Enhanced downloader core
├── spotify_to_youtube.py        # Spotify integration
├── yt_downloader_gui.py         # GUI application
├── yt_loader.py                 # Original script (reference)
├── requirements.txt             # Python dependencies
├── setup.py                     # Setup script
├── README.md                    # This file
├── settings.json               # User settings (created after first run)
└── logs/                       # Log files directory
```

## Configuration

Settings are stored in `settings.json` and include:

```json
{
  "youtube_api_key": "your_api_key_here",
  "spotify_client_id": "your_client_id_here",
  "spotify_client_secret": "your_client_secret_here",
  "download_path": "/path/to/downloads",
  "default_media_type": "audio"
}
```

## Troubleshooting

### Common Issues

**"API key not working"**
- Verify the API key is correct
- Ensure YouTube Data API v3 is enabled
- Check API quotas in Google Cloud Console

**"No search results"**
- Check internet connection
- Verify API key configuration
- Try different search terms

**"Download fails with 403 error"**
- Update yt-dlp: `pip install -U yt-dlp`
- Check if video is available in your region
- Verify video is not private or deleted

**"Spotify playlist not loading"**
- Verify Spotify API credentials
- Ensure playlist is public
- Check playlist URL format

### Logging

- Check the "Logs" tab in the application
- Log files are saved in the `logs/` directory
- Enable verbose logging for debugging

### Getting Help

1. Check the logs for error messages
2. Verify all API keys are configured correctly
3. Ensure all dependencies are installed
4. Try with a simple test case first

## Advanced Usage

### Command Line Interface

The enhanced downloader can also be used from command line:

```bash
python yt_downloader_enhanced.py
```

### Spotify Converter Standalone

```bash
python spotify_to_youtube.py
```

### Batch File Format

Create a text file with one URL or search query per line:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
Never Gonna Give You Up Rick Astley
https://www.youtube.com/watch?v=oHg5SJYRHA0
```

## Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Structure

- `yt_downloader_enhanced.py`: Core downloading logic
- `spotify_to_youtube.py`: Spotify integration
- `yt_downloader_gui.py`: GUI interface
- `setup.py`: Installation and setup

### Testing

Run basic tests:

```bash
python -m pytest tests/  # If test suite exists
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Uses [Google YouTube Data API](https://developers.google.com/youtube/v3)
- Spotify integration via [Spotipy](https://spotipy.readthedocs.io/)
- GUI built with Python Tkinter

## Disclaimer

This tool is for educational and personal use only. Please respect copyright laws and YouTube's Terms of Service. The developers are not responsible for any misuse of this software.

## Version History

### v2.0.0 (Current)
- Added Spotify playlist integration
- Implemented batch processing
- Created modern GUI interface
- Added quality verification
- Enhanced error handling and logging

### v1.0.0 (Original)
- Basic YouTube downloading
- Command-line interface
- Single video processing

