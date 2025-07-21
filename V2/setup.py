#!/usr/bin/env python3
"""
Setup script for YouTube Downloader Pro
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ All requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    try:
        # Create downloads directory
        downloads_dir = Path.home() / "Downloads" / "YouTube"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        print("✓ Directories created successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to create directories: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut (Windows/Linux)."""
    try:
        if sys.platform == "win32":
            # Windows shortcut
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "YouTube Downloader Pro.lnk")
            target = os.path.join(os.getcwd(), "yt_downloader_gui.py")
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
        elif sys.platform.startswith("linux"):
            # Linux desktop entry
            desktop_entry = f"""[Desktop Entry]
Name=YouTube Downloader Pro
Comment=Download YouTube videos and audio with Spotify integration
Exec={sys.executable} "{os.path.join(os.getcwd(), 'yt_downloader_gui.py')}"
Icon={os.path.join(os.getcwd(), 'icon.png')}
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Video;
"""
            desktop_path = Path.home() / "Desktop" / "YouTube Downloader Pro.desktop"
            with open(desktop_path, 'w') as f:
                f.write(desktop_entry)
            os.chmod(desktop_path, 0o755)
            
        print("✓ Desktop shortcut created!")
        return True
    except Exception as e:
        print(f"⚠ Could not create desktop shortcut: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 50)
    print("YouTube Downloader Pro - Setup")
    print("=" * 50)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python yt_downloader_gui.py' to start the application")
        print("2. Configure your API keys in the Settings tab")
        print("3. Start downloading!")
        print("\nAPI Keys needed:")
        print("- YouTube Data API v3 key from Google Cloud Console")
        print("- Spotify Client ID and Secret from Spotify Developer Dashboard")
    else:
        print("✗ Setup completed with errors!")
        print("Please check the error messages above and try again.")
    print("=" * 50)

if __name__ == "__main__":
    main()

