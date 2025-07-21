import os
import json
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from termcolor import colored

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("spotify_to_youtube.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SpotifyTrack:
    """Represents a Spotify track with relevant metadata."""
    title: str
    artist: str
    album: str
    spotify_url: str
    youtube_url: Optional[str] = None
    youtube_title: Optional[str] = None
    verification_status: str = "pending"  # "pending", "found", "not_found", "verified"

class SpotifyToYouTubeConverter:
    """Converts Spotify playlist tracks to YouTube URLs with verification."""

    def __init__(self, spotify_client_id: str, spotify_client_secret: str, youtube_api_key: str):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret
        ))
        self.youtube = build("youtube", "v3", developerKey=youtube_api_key)
        self.tracks: List[SpotifyTrack] = []

    def get_playlist_tracks(self, playlist_url: str) -> List[SpotifyTrack]:
        """Fetches all tracks from a Spotify playlist URL."""
        try:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            results = self.sp.playlist_items(playlist_id)
            tracks = results["items"]
            while results["next"]:
                results = self.sp.next(results)
                tracks.extend(results["items"])

            spotify_tracks = []
            for item in tracks:
                track = item["track"]
                if track:
                    title = track["name"]
                    artist = track["artists"][0]["name"] if track["artists"] else "Unknown Artist"
                    album = track["album"]["name"] if track["album"] else "Unknown Album"
                    spotify_url = track["external_urls"]["spotify"]
                    spotify_tracks.append(SpotifyTrack(title, artist, album, spotify_url))
            logger.info(f"Found {len(spotify_tracks)} tracks in Spotify playlist.")
            self.tracks = spotify_tracks
            return spotify_tracks
        except Exception as e:
            logger.error(f"Error fetching Spotify playlist tracks: {e}")
            return []

    def search_youtube_for_track(self, track: SpotifyTrack) -> Optional[Tuple[str, str]]:
        """Searches YouTube for a given Spotify track and returns the best URL and title."""
        query = f"{track.title} {track.artist}"
        try:
            search_response = self.youtube.search().list(
                q=query,
                type="video",
                part="id,snippet",
                maxResults=5  # Get a few results to pick the best one
            ).execute()

            videos = search_response.get("items", [])
            if not videos:
                track.verification_status = "not_found"
                logger.warning(f"No YouTube video found for: {query}")
                return None

            # Simple heuristic: pick the first result for now, can be improved with more advanced matching
            best_video = videos[0]
            video_id = best_video["id"]["videoId"]
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            youtube_title = best_video["snippet"]["title"]

            track.youtube_url = youtube_url
            track.youtube_title = youtube_title
            track.verification_status = "found"
            logger.info(f"Found YouTube URL for '{query}': {youtube_url}")
            return youtube_url, youtube_title

        except Exception as e:
            logger.error(f"Error searching YouTube for '{query}': {e}")
            track.verification_status = "not_found"
            return None

    def process_tracks(self):
        """Processes all Spotify tracks to find their YouTube counterparts."""
        for track in self.tracks:
            if track.verification_status == "pending":
                self.search_youtube_for_track(track)

    def export_youtube_urls(self, file_path: str):
        """Exports the found YouTube URLs to a text file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for track in self.tracks:
                    if track.youtube_url:
                        f.write(f"{track.youtube_url}\n")
            logger.info(f"YouTube URLs exported to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting YouTube URLs: {e}")

    def export_full_results(self, file_path: str):
        """Exports full results (Spotify track info + YouTube URL) to a JSON file."""
        results = []
        for track in self.tracks:
            results.append({
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "spotify_url": track.spotify_url,
                "youtube_url": track.youtube_url,
                "youtube_title": track.youtube_title,
                "verification_status": track.verification_status
            })
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Full results exported to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting full results: {e}")

def main():
    """Main function for command-line usage of Spotify to YouTube converter."""
    print(colored("\n=== Spotify to YouTube Converter ===", "green"))

    spotify_client_id = os.getenv("SPOTIPY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")

    if not spotify_client_id or not spotify_client_secret or not youtube_api_key:
        print(colored("Please set SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and YOUTUBE_API_KEY environment variables.", "red"))
        print(colored("You can get Spotify API credentials from https://developer.spotify.com/dashboard/applications", "yellow"))
        print(colored("You can get YouTube API key from https://console.developers.google.com/apis/credentials", "yellow"))
        return

    converter = SpotifyToYouTubeConverter(spotify_client_id, spotify_client_secret, youtube_api_key)

    while True:
        playlist_url = input(colored("Enter Spotify playlist URL (or 'q' to quit): ", "cyan"))
        if playlist_url.lower() == 'q':
            break

        if not playlist_url:
            print(colored("Playlist URL cannot be empty.", "red"))
            continue

        print(colored(f"Fetching tracks from playlist: {playlist_url}", "blue"))
        converter.get_playlist_tracks(playlist_url)

        if not converter.tracks:
            print(colored("No tracks found or error fetching playlist.", "yellow"))
            continue

        print(colored("Searching YouTube for each track...", "blue"))
        converter.process_tracks()

        output_file_txt = input(colored("Enter filename to export YouTube URLs (e.g., youtube_urls.txt): ", "cyan"))
        if output_file_txt:
            converter.export_youtube_urls(output_file_txt)

        output_file_json = input(colored("Enter filename to export full results (e.g., full_results.json): ", "cyan"))
        if output_file_json:
            converter.export_full_results(output_file_json)

        print(colored("\nProcessing complete.", "green"))

if __name__ == "__main__":
    main()


