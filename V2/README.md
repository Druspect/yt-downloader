# YouTube Downloader v2

This folder contains an enhanced downloader with optional GUI and Spotify playlist support.

## Features
- Search and download YouTube audio or video
- Batch processing of multiple URLs or search terms
- Optional GUI built with Tkinter
- Spotify playlist conversion to YouTube
- Basic logging and quality selection

## Setup
1. Ensure Python 3.7+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the setup helper (optional) to create directories and shortcuts:
   ```bash
   python setup.py
   ```

## Usage
- **Command line**
  ```bash
  python yt_downloader_enhanced.py
  ```
- **GUI**
  ```bash
  python yt_downloader_gui.py
  ```

An API key for YouTube Data API v3 is required and will be requested on first run. Spotify credentials are only needed for playlist conversion.
