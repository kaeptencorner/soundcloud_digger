#!/usr/bin/env python3
import os
import requests

# ----------------------------
# Configuration: Read from Environment
# ----------------------------
CLIENT_ID = os.getenv("SOUNDCLOUD_CLIENT_ID")
OAUTH_TOKEN = os.getenv("SOUNDCLOUD_OAUTH_TOKEN")

if not CLIENT_ID or not OAUTH_TOKEN:
    raise Exception("Missing SoundCloud API credentials. Set SOUNDCLOUD_CLIENT_ID and SOUNDCLOUD_OAUTH_TOKEN.")

# These values can also be stored in your GitHub Secrets and injected as env variables.
PLAYLIST_URL = os.getenv("SOUNDCLOUD_PLAYLIST_URL", "https://soundcloud.com/USER/playlist-name")
PROPOSALS_PLAYLIST_ID = os.getenv("PROPOSALS_PLAYLIST_ID", "1234567890")
try:
    PROPOSALS_PLAYLIST_ID = int(PROPOSALS_PLAYLIST_ID)
except ValueError:
    raise Exception("Invalid PROPOSALS_PLAYLIST_ID. Must be a numeric ID.")

HISTORY_FILE = "processed_tracks.txt"

# ----------------------------
# Helper Functions
# ----------------------------
def load_history(file_path):
    """Load processed track IDs from file."""
    try:
        with open(file_path, "r") as f:
            return {int(line.strip()) for line in f if line.strip().isdigit()}
    except FileNotFoundError:
        return set()

def append_to_history(file_path, track_ids):
    """Append new processed track IDs to history file."""
    with open(file_path, "a") as f:
        for tid in track_ids:
            f.write(f"{tid}\n")

def resolve_playlist(url_or_id):
    """Resolve a SoundCloud playlist by URL or ID."""
    if "soundcloud.com" in url_or_id:
        res = requests.get(
            "https://api.soundcloud.com/resolve",
            params={"url": url_or_id, "client_id": CLIENT_ID},
            headers={"Authorization": f"OAuth {OAUTH_TOKEN}"}
        )
    else:
        res = requests.get(
            f"https://api.soundcloud.com/playlists/{url_or_id}",
            params={"client_id": CLIENT_ID},
            headers={"Authorization": f"OAuth {OAUTH_TOKEN}"}
        )
    if res.status_code != 200:
        raise Exception(f"Failed to retrieve playlist: {res.text}")
    return res.json()

def get_related_tracks(track_i
