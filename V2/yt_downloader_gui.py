import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
from pathlib import Path
import queue
import logging
from typing import List, Dict, Optional
import webbrowser

# Import our custom modules
from yt_downloader_enhanced import YouTubeDownloaderEnhanced, DownloadItem
from spotify_to_youtube import SpotifyToYouTubeConverter

class YouTubeDownloaderGUI:
    """Production-ready GUI for YouTube Downloader with Spotify integration."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize variables
        self.downloader = None
        self.spotify_converter = None
        self.download_queue = queue.Queue()
        self.is_downloading = False
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI
        self.create_widgets()
        self.load_settings()
        
    def setup_logging(self):
        """Setup logging for the GUI application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('yt_downloader_gui.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_settings_tab()
        self.create_downloader_tab()
        self.create_spotify_tab()
        self.create_batch_tab()
        self.create_queue_tab()
        self.create_logs_tab()
        
    def create_settings_tab(self):
        """Create the settings configuration tab."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # API Keys section
        api_frame = ttk.LabelFrame(settings_frame, text="API Configuration", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # YouTube API Key
        ttk.Label(api_frame, text="YouTube Data API Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.youtube_api_var = tk.StringVar()
        youtube_entry = ttk.Entry(api_frame, textvariable=self.youtube_api_var, width=50, show="*")
        youtube_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W+tk.E)
        
        # Spotify Client ID
        ttk.Label(api_frame, text="Spotify Client ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.spotify_id_var = tk.StringVar()
        spotify_id_entry = ttk.Entry(api_frame, textvariable=self.spotify_id_var, width=50)
        spotify_id_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W+tk.E)
        
        # Spotify Client Secret
        ttk.Label(api_frame, text="Spotify Client Secret:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.spotify_secret_var = tk.StringVar()
        spotify_secret_entry = ttk.Entry(api_frame, textvariable=self.spotify_secret_var, width=50, show="*")
        spotify_secret_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W+tk.E)
        
        api_frame.columnconfigure(1, weight=1)
        
        # Download settings
        download_frame = ttk.LabelFrame(settings_frame, text="Download Settings", padding=10)
        download_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Download path
        ttk.Label(download_frame, text="Download Directory:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.download_path_var = tk.StringVar(value=str(Path.home() / "Downloads" / "YouTube"))
        path_frame = ttk.Frame(download_frame)
        path_frame.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W+tk.E)
        
        ttk.Entry(path_frame, textvariable=self.download_path_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_download_path).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Default media type
        ttk.Label(download_frame, text="Default Media Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.media_type_var = tk.StringVar(value="audio")
        media_combo = ttk.Combobox(download_frame, textvariable=self.media_type_var, values=["audio", "video"], state="readonly")
        media_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        download_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Help", command=self.show_help).pack(side=tk.RIGHT, padx=5)
        
    def create_downloader_tab(self):
        """Create the main downloader tab."""
        downloader_frame = ttk.Frame(self.notebook)
        self.notebook.add(downloader_frame, text="Download")
        
        # Input section
        input_frame = ttk.LabelFrame(downloader_frame, text="Single Download", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="YouTube URL or Search Query:").pack(anchor=tk.W)
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(input_frame, textvariable=self.url_var, width=80)
        url_entry.pack(fill=tk.X, pady=5)
        url_entry.bind('<Return>', lambda e: self.add_single_download())
        
        # Options
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="Type:").pack(side=tk.LEFT)
        self.single_media_var = tk.StringVar(value="audio")
        ttk.Radiobutton(options_frame, text="Audio", variable=self.single_media_var, value="audio").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(options_frame, text="Video", variable=self.single_media_var, value="video").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(options_frame, text="Add to Queue", command=self.add_single_download).pack(side=tk.RIGHT, padx=5)
        ttk.Button(options_frame, text="Download Now", command=self.download_single_now).pack(side=tk.RIGHT, padx=5)
        
        # Search results section
        search_frame = ttk.LabelFrame(downloader_frame, text="Search Results", padding=10)
        search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Search results tree
        columns = ("Title", "Channel", "Duration", "Views", "Status")
        self.search_tree = ttk.Treeview(search_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=150)
        
        # Scrollbars for search results
        search_scroll_y = ttk.Scrollbar(search_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        search_scroll_x = ttk.Scrollbar(search_frame, orient=tk.HORIZONTAL, command=self.search_tree.xview)
        self.search_tree.configure(yscrollcommand=search_scroll_y.set, xscrollcommand=search_scroll_x.set)
        
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        search_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Search results buttons
        search_buttons = ttk.Frame(search_frame)
        search_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(search_buttons, text="Add Selected", command=self.add_selected_search_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_buttons, text="Preview", command=self.preview_selected).pack(side=tk.LEFT, padx=5)
        
    def create_spotify_tab(self):
        """Create the Spotify integration tab."""
        spotify_frame = ttk.Frame(self.notebook)
        self.notebook.add(spotify_frame, text="Spotify")
        
        # Spotify playlist input
        playlist_frame = ttk.LabelFrame(spotify_frame, text="Spotify Playlist", padding=10)
        playlist_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(playlist_frame, text="Spotify Playlist URL:").pack(anchor=tk.W)
        self.spotify_url_var = tk.StringVar()
        spotify_entry = ttk.Entry(playlist_frame, textvariable=self.spotify_url_var, width=80)
        spotify_entry.pack(fill=tk.X, pady=5)
        
        spotify_buttons = ttk.Frame(playlist_frame)
        spotify_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(spotify_buttons, text="Load Playlist", command=self.load_spotify_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(spotify_buttons, text="Convert to YouTube", command=self.convert_spotify_to_youtube).pack(side=tk.LEFT, padx=5)
        ttk.Button(spotify_buttons, text="Add All to Queue", command=self.add_spotify_to_queue).pack(side=tk.RIGHT, padx=5)
        
        # Spotify tracks display
        tracks_frame = ttk.LabelFrame(spotify_frame, text="Playlist Tracks", padding=10)
        tracks_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Track", "Artist", "Album", "YouTube URL", "Status")
        self.spotify_tree = ttk.Treeview(tracks_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.spotify_tree.heading(col, text=col)
            self.spotify_tree.column(col, width=150)
        
        spotify_scroll_y = ttk.Scrollbar(tracks_frame, orient=tk.VERTICAL, command=self.spotify_tree.yview)
        spotify_scroll_x = ttk.Scrollbar(tracks_frame, orient=tk.HORIZONTAL, command=self.spotify_tree.xview)
        self.spotify_tree.configure(yscrollcommand=spotify_scroll_y.set, xscrollcommand=spotify_scroll_x.set)
        
        self.spotify_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        spotify_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        spotify_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_batch_tab(self):
        """Create the batch processing tab."""
        batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(batch_frame, text="Batch")
        
        # File input
        file_frame = ttk.LabelFrame(batch_frame, text="Batch File Input", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill=tk.X, pady=5)
        
        self.batch_file_var = tk.StringVar()
        ttk.Entry(file_input_frame, textvariable=self.batch_file_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_input_frame, text="Browse", command=self.browse_batch_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(file_frame, text="Load from File", command=self.load_batch_file).pack(pady=5)
        
        # Manual input
        manual_frame = ttk.LabelFrame(batch_frame, text="Manual Batch Input", padding=10)
        manual_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(manual_frame, text="Enter URLs/queries (one per line):").pack(anchor=tk.W)
        self.batch_text = scrolledtext.ScrolledText(manual_frame, height=15, width=80)
        self.batch_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        batch_buttons = ttk.Frame(manual_frame)
        batch_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Label(batch_buttons, text="Media Type:").pack(side=tk.LEFT)
        self.batch_media_var = tk.StringVar(value="audio")
        ttk.Radiobutton(batch_buttons, text="Audio", variable=self.batch_media_var, value="audio").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(batch_buttons, text="Video", variable=self.batch_media_var, value="video").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(batch_buttons, text="Add to Queue", command=self.add_batch_to_queue).pack(side=tk.RIGHT, padx=5)
        ttk.Button(batch_buttons, text="Clear", command=lambda: self.batch_text.delete(1.0, tk.END)).pack(side=tk.RIGHT, padx=5)
        
    def create_queue_tab(self):
        """Create the download queue management tab."""
        queue_frame = ttk.Frame(self.notebook)
        self.notebook.add(queue_frame, text="Queue")
        
        # Queue controls
        controls_frame = ttk.Frame(queue_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Start Downloads", command=self.start_downloads).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Pause", command=self.pause_downloads).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Clear Queue", command=self.clear_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Results", command=self.export_results).pack(side=tk.RIGHT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(queue_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(queue_frame, textvariable=self.status_var).pack(pady=5)
        
        # Queue display
        queue_display_frame = ttk.LabelFrame(queue_frame, text="Download Queue", padding=10)
        queue_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("URL/Query", "Type", "Status", "Progress", "File Path")
        self.queue_tree = ttk.Treeview(queue_display_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.queue_tree.heading(col, text=col)
            self.queue_tree.column(col, width=150)
        
        queue_scroll_y = ttk.Scrollbar(queue_display_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        queue_scroll_x = ttk.Scrollbar(queue_display_frame, orient=tk.HORIZONTAL, command=self.queue_tree.xview)
        self.queue_tree.configure(yscrollcommand=queue_scroll_y.set, xscrollcommand=queue_scroll_x.set)
        
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        queue_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        queue_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_logs_tab(self):
        """Create the logs and debugging tab."""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=25, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log controls
        log_controls = ttk.Frame(logs_frame)
        log_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_controls, text="Clear Logs", command=lambda: self.log_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controls, text="Save Logs", command=self.save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controls, text="Refresh", command=self.refresh_logs).pack(side=tk.RIGHT, padx=5)
        
    def browse_download_path(self):
        """Browse for download directory."""
        path = filedialog.askdirectory(initialdir=self.download_path_var.get())
        if path:
            self.download_path_var.set(path)
            
    def browse_batch_file(self):
        """Browse for batch input file."""
        file_path = filedialog.askopenfilename(
            title="Select Batch File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.batch_file_var.set(file_path)
            
    def save_settings(self):
        """Save current settings to file."""
        settings = {
            "youtube_api_key": self.youtube_api_var.get(),
            "spotify_client_id": self.spotify_id_var.get(),
            "spotify_client_secret": self.spotify_secret_var.get(),
            "download_path": self.download_path_var.get(),
            "default_media_type": self.media_type_var.get()
        }
        
        try:
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.initialize_downloaders()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                
                self.youtube_api_var.set(settings.get("youtube_api_key", ""))
                self.spotify_id_var.set(settings.get("spotify_client_id", ""))
                self.spotify_secret_var.set(settings.get("spotify_client_secret", ""))
                self.download_path_var.set(settings.get("download_path", str(Path.home() / "Downloads" / "YouTube")))
                self.media_type_var.set(settings.get("default_media_type", "audio"))
                
                self.initialize_downloaders()
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            
    def initialize_downloaders(self):
        """Initialize downloader instances with current settings."""
        try:
            if self.youtube_api_var.get():
                self.downloader = YouTubeDownloaderEnhanced(
                    self.youtube_api_var.get(),
                    self.download_path_var.get()
                )
                
            if self.spotify_id_var.get() and self.spotify_secret_var.get() and self.youtube_api_var.get():
                self.spotify_converter = SpotifyToYouTubeConverter(
                    self.spotify_id_var.get(),
                    self.spotify_secret_var.get(),
                    self.youtube_api_var.get()
                )
        except Exception as e:
            self.logger.error(f"Failed to initialize downloaders: {e}")
            
    def test_connection(self):
        """Test API connections."""
        if not self.downloader:
            messagebox.showerror("Error", "Please configure and save YouTube API key first!")
            return
            
        try:
            # Test YouTube API
            test_results = self.downloader.search_youtube("test", max_results=1)
            if test_results:
                messagebox.showinfo("Success", "YouTube API connection successful!")
            else:
                messagebox.showwarning("Warning", "YouTube API connected but no results returned.")
                
        except Exception as e:
            messagebox.showerror("Error", f"API connection failed: {e}")
            
    def show_help(self):
        """Show help information."""
        help_text = """
YouTube Downloader Pro - Help

1. Settings Tab:
   - Configure your YouTube Data API key
   - Configure Spotify API credentials (optional)
   - Set download directory and preferences

2. Download Tab:
   - Enter YouTube URLs or search queries
   - Choose audio or video format
   - Preview search results before downloading

3. Spotify Tab:
   - Enter Spotify playlist URLs
   - Convert tracks to YouTube URLs
   - Add entire playlists to download queue

4. Batch Tab:
   - Load URLs from text files
   - Enter multiple URLs manually
   - Process large batches efficiently

5. Queue Tab:
   - Manage download queue
   - Monitor download progress
   - Export results

6. Logs Tab:
   - View detailed logs
   - Debug issues
   - Save logs for support

API Keys Required:
- YouTube Data API v3 key from Google Cloud Console
- Spotify Client ID and Secret from Spotify Developer Dashboard
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x500")
        
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
    def add_single_download(self):
        """Add single URL/query to download queue."""
        if not self.downloader:
            messagebox.showerror("Error", "Please configure YouTube API key first!")
            return
            
        url_or_query = self.url_var.get().strip()
        if not url_or_query:
            messagebox.showwarning("Warning", "Please enter a URL or search query!")
            return
            
        try:
            self.downloader.add_to_queue([url_or_query], self.single_media_var.get())
            self.update_queue_display()
            self.url_var.set("")
            messagebox.showinfo("Success", "Added to download queue!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to queue: {e}")
            
    def download_single_now(self):
        """Download single item immediately."""
        # Implementation for immediate download
        pass
        
    def load_spotify_playlist(self):
        """Load tracks from Spotify playlist."""
        if not self.spotify_converter:
            messagebox.showerror("Error", "Please configure Spotify API credentials first!")
            return
            
        playlist_url = self.spotify_url_var.get().strip()
        if not playlist_url:
            messagebox.showwarning("Warning", "Please enter a Spotify playlist URL!")
            return
            
        try:
            tracks = self.spotify_converter.get_playlist_tracks(playlist_url)
            self.update_spotify_display(tracks)
            messagebox.showinfo("Success", f"Loaded {len(tracks)} tracks from playlist!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlist: {e}")
            
    def convert_spotify_to_youtube(self):
        """Convert Spotify tracks to YouTube URLs."""
        if not self.spotify_converter or not self.spotify_converter.tracks:
            messagebox.showwarning("Warning", "Please load a Spotify playlist first!")
            return
            
        try:
            self.spotify_converter.process_tracks()
            self.update_spotify_display(self.spotify_converter.tracks)
            messagebox.showinfo("Success", "Conversion completed!")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {e}")
            
    def add_spotify_to_queue(self):
        """Add Spotify tracks to download queue."""
        # Implementation for adding Spotify tracks to queue
        pass
        
    def load_batch_file(self):
        """Load URLs from batch file."""
        file_path = self.batch_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid batch file!")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.batch_text.delete(1.0, tk.END)
            self.batch_text.insert(1.0, content)
            messagebox.showinfo("Success", "Batch file loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load batch file: {e}")
            
    def add_batch_to_queue(self):
        """Add batch items to download queue."""
        if not self.downloader:
            messagebox.showerror("Error", "Please configure YouTube API key first!")
            return
            
        content = self.batch_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Please enter URLs or queries!")
            return
            
        items = [line.strip() for line in content.split('\n') if line.strip()]
        
        try:
            self.downloader.add_to_queue(items, self.batch_media_var.get())
            self.update_queue_display()
            messagebox.showinfo("Success", f"Added {len(items)} items to queue!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add batch to queue: {e}")
            
    def start_downloads(self):
        """Start processing download queue."""
        if not self.downloader or not self.downloader.download_queue:
            messagebox.showwarning("Warning", "Download queue is empty!")
            return
            
        if self.is_downloading:
            messagebox.showwarning("Warning", "Downloads are already in progress!")
            return
            
        self.is_downloading = True
        threading.Thread(target=self.process_downloads, daemon=True).start()
        
    def process_downloads(self):
        """Process downloads in background thread."""
        try:
            def progress_callback(current, total, item):
                progress = (current / total) * 100
                self.root.after(0, lambda: self.progress_var.set(progress))
                self.root.after(0, lambda: self.status_var.set(f"Processing {current}/{total}: {item[:50]}..."))
                
            results = self.downloader.process_queue(progress_callback)
            
            self.root.after(0, lambda: self.status_var.set(f"Completed: {results['completed']}, Failed: {results['failed']}"))
            self.root.after(0, self.update_queue_display)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {e}"))
        finally:
            self.is_downloading = False
            
    def pause_downloads(self):
        """Pause downloads."""
        self.is_downloading = False
        self.status_var.set("Paused")
        
    def clear_queue(self):
        """Clear download queue."""
        if self.downloader:
            self.downloader.clear_queue()
            self.update_queue_display()
            messagebox.showinfo("Success", "Queue cleared!")
            
    def export_results(self):
        """Export download results."""
        if not self.downloader:
            messagebox.showwarning("Warning", "No downloader instance!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.downloader.export_results(file_path)
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
                
    def update_queue_display(self):
        """Update the queue display tree."""
        if not self.downloader:
            return
            
        # Clear existing items
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        # Add current queue items
        for item in self.downloader.download_queue:
            self.queue_tree.insert("", tk.END, values=(
                item.url_or_query[:50] + "..." if len(item.url_or_query) > 50 else item.url_or_query,
                item.media_type,
                item.status,
                "",  # Progress placeholder
                item.file_path[:50] + "..." if len(item.file_path) > 50 else item.file_path
            ))
            
    def update_spotify_display(self, tracks):
        """Update the Spotify tracks display."""
        # Clear existing items
        for item in self.spotify_tree.get_children():
            self.spotify_tree.delete(item)
            
        # Add tracks
        for track in tracks:
            self.spotify_tree.insert("", tk.END, values=(
                track.title[:30] + "..." if len(track.title) > 30 else track.title,
                track.artist[:20] + "..." if len(track.artist) > 20 else track.artist,
                track.album[:20] + "..." if len(track.album) > 20 else track.album,
                track.youtube_url[:40] + "..." if track.youtube_url and len(track.youtube_url) > 40 else track.youtube_url or "",
                track.verification_status
            ))
            
    def add_selected_search_result(self):
        """Add selected search result to queue."""
        # Implementation for adding selected search results
        pass
        
    def preview_selected(self):
        """Preview selected video in browser."""
        # Implementation for previewing videos
        pass
        
    def save_logs(self):
        """Save logs to file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Logs",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {e}")
                
    def refresh_logs(self):
        """Refresh logs display."""
        try:
            if os.path.exists("yt_downloader_gui.log"):
                with open("yt_downloader_gui.log", 'r', encoding='utf-8') as f:
                    content = f.read()
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(1.0, content)
                self.log_text.see(tk.END)
        except Exception as e:
            self.logger.error(f"Failed to refresh logs: {e}")

def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

