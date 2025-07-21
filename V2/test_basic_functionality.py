#!/usr/bin/env python3
"""
Basic functionality tests for YouTube Downloader Pro
"""

import os
import sys
import tempfile
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import yt_dlp
        print("✓ yt-dlp imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import yt-dlp: {e}")
        return False
    
    try:
        from googleapiclient.discovery import build
        print("✓ Google API client imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Google API client: {e}")
        return False
    
    try:
        import spotipy
        print("✓ Spotipy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import spotipy: {e}")
        return False
    
    try:
        from termcolor import colored
        print("✓ Termcolor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import termcolor: {e}")
        return False
    
    try:
        from mutagen.easyid3 import EasyID3
        print("✓ Mutagen imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import mutagen: {e}")
        return False
    
    return True

def test_module_imports():
    """Test that our custom modules can be imported."""
    print("\nTesting custom module imports...")
    
    try:
        from yt_downloader_enhanced import YouTubeDownloaderEnhanced, DownloadItem
        print("✓ Enhanced downloader imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import enhanced downloader: {e}")
        return False
    
    try:
        from spotify_to_youtube import SpotifyToYouTubeConverter, SpotifyTrack
        print("✓ Spotify converter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Spotify converter: {e}")
        return False
    
    try:
        import tkinter as tk
        print("✓ Tkinter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import tkinter: {e}")
        return False
    
    return True

def test_url_validation():
    """Test URL validation functionality."""
    print("\nTesting URL validation...")
    
    try:
        from yt_downloader_enhanced import YouTubeDownloaderEnhanced
        
        # Create a temporary downloader instance (without API key for testing)
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = YouTubeDownloaderEnhanced("dummy_key", temp_dir)
            
            # Test valid URLs
            valid_urls = [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://youtu.be/dQw4w9WgXcQ",
                "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "www.youtube.com/watch?v=dQw4w9WgXcQ"
            ]
            
            for url in valid_urls:
                if downloader.validate_youtube_url(url):
                    print(f"✓ Valid URL recognized: {url}")
                else:
                    print(f"✗ Valid URL not recognized: {url}")
                    return False
            
            # Test invalid URLs
            invalid_urls = [
                "https://www.google.com",
                "not a url",
                "https://vimeo.com/123456",
                ""
            ]
            
            for url in invalid_urls:
                if not downloader.validate_youtube_url(url):
                    print(f"✓ Invalid URL correctly rejected: {url}")
                else:
                    print(f"✗ Invalid URL incorrectly accepted: {url}")
                    return False
        
        return True
    except Exception as e:
        print(f"✗ URL validation test failed: {e}")
        return False

def test_video_id_extraction():
    """Test video ID extraction from URLs."""
    print("\nTesting video ID extraction...")
    
    try:
        from yt_downloader_enhanced import YouTubeDownloaderEnhanced
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = YouTubeDownloaderEnhanced("dummy_key", temp_dir)
            
            test_cases = [
                ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
                ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
                ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
                ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ")
            ]
            
            for url, expected_id in test_cases:
                extracted_id = downloader.extract_video_id(url)
                if extracted_id == expected_id:
                    print(f"✓ Correct ID extracted from {url}: {extracted_id}")
                else:
                    print(f"✗ Incorrect ID extracted from {url}: {extracted_id} (expected {expected_id})")
                    return False
        
        return True
    except Exception as e:
        print(f"✗ Video ID extraction test failed: {e}")
        return False

def test_download_item_creation():
    """Test DownloadItem dataclass creation."""
    print("\nTesting DownloadItem creation...")
    
    try:
        from yt_downloader_enhanced import DownloadItem
        
        # Test basic creation
        item = DownloadItem("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        if item.url_or_query == "https://www.youtube.com/watch?v=dQw4w9WgXcQ":
            print("✓ Basic DownloadItem created successfully")
        else:
            print("✗ Basic DownloadItem creation failed")
            return False
        
        # Test with all parameters
        item = DownloadItem(
            url_or_query="test query",
            media_type="video",
            quality="720p",
            status="completed",
            error_message="",
            file_path="/path/to/file.mp4",
            title="Test Video",
            duration="3:45",
            view_count=1000000
        )
        
        if (item.media_type == "video" and 
            item.quality == "720p" and 
            item.status == "completed"):
            print("✓ Full DownloadItem created successfully")
        else:
            print("✗ Full DownloadItem creation failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ DownloadItem creation test failed: {e}")
        return False

def test_spotify_track_creation():
    """Test SpotifyTrack dataclass creation."""
    print("\nTesting SpotifyTrack creation...")
    
    try:
        from spotify_to_youtube import SpotifyTrack
        
        track = SpotifyTrack(
            title="Never Gonna Give You Up",
            artist="Rick Astley",
            album="Whenever You Need Somebody",
            spotify_url="https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
        )
        
        if (track.title == "Never Gonna Give You Up" and 
            track.artist == "Rick Astley" and
            track.verification_status == "pending"):
            print("✓ SpotifyTrack created successfully")
            return True
        else:
            print("✗ SpotifyTrack creation failed")
            return False
    except Exception as e:
        print(f"✗ SpotifyTrack creation test failed: {e}")
        return False

def test_file_operations():
    """Test basic file operations."""
    print("\nTesting file operations...")
    
    try:
        # Test creating download directory
        test_dir = Path(tempfile.gettempdir()) / "yt_downloader_test"
        test_dir.mkdir(exist_ok=True)
        
        if test_dir.exists():
            print("✓ Directory creation successful")
        else:
            print("✗ Directory creation failed")
            return False
        
        # Test file writing
        test_file = test_dir / "test.txt"
        test_file.write_text("test content")
        
        if test_file.exists() and test_file.read_text() == "test content":
            print("✓ File operations successful")
        else:
            print("✗ File operations failed")
            return False
        
        # Cleanup
        test_file.unlink()
        test_dir.rmdir()
        
        return True
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("YouTube Downloader Pro - Basic Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_module_imports,
        test_url_validation,
        test_video_id_extraction,
        test_download_item_creation,
        test_spotify_track_creation,
        test_file_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"Test {test.__name__} failed!")
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The application should work correctly.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed correctly.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

