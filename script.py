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

def get_related_tracks(track_id):
    """Fetch related tracks (SoundCloud radio) for a given track."""
    res = requests.get(
        f"https://api.soundcloud.com/tracks/{track_id}/related",
        params={"client_id": CLIENT_ID},
        headers={"Authorization": f"OAuth {OAUTH_TOKEN}"}
    )
    if res.status_code != 200:
        print(f"Warning: Could not retrieve related tracks for track {track_id}.")
        return []
    return res.json()

def update_proposals_playlist(new_track_ids):
    """Update the proposals playlist with new track IDs."""
    # Get current proposals playlist
    get_res = requests.get(
        f"https://api.soundcloud.com/playlists/{PROPOSALS_PLAYLIST_ID}",
        params={"client_id": CLIENT_ID},
        headers={"Authorization": f"OAuth {OAUTH_TOKEN}"}
    )
    if get_res.status_code != 200:
        raise Exception(f"Failed to retrieve proposals playlist: {get_res.text}")
    prop_data = get_res.json()
    current_tracks = prop_data.get("tracks", [])
    current_track_ids = [t.get("id") for t in current_tracks if t.get("id") is not None]

    # Combine current and new track IDs (avoid duplicates)
    combined_track_ids = current_track_ids.copy()
    added_count = 0
    for tid in new_track_ids:
        if tid not in combined_track_ids:
            combined_track_ids.append(tid)
            added_count += 1

    if added_count > 0:
        payload = {
            "playlist": {
                "tracks": [{"id": tid} for tid in combined_track_ids]
            }
        }
        update_res = requests.put(
            f"https://api.soundcloud.com/playlists/{PROPOSALS_PLAYLIST_ID}",
            headers={
                "Authorization": f"OAuth {OAUTH_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        if update_res.status_code == 200:
            print(f"Added {added_count} new tracks to proposals playlist.")
        else:
            print(f"Failed to update proposals playlist: {update_res.text}")
    else:
        print("No new tracks to add to proposals playlist.")

# ----------------------------
# Main Process
# ----------------------------
def main():
    processed_ids = load_history(HISTORY_FILE)
    new_processed_ids = set()

    # Resolve the source playlist and get its tracks
    playlist_data = resolve_playlist(PLAYLIST_URL)
    playlist_tracks = playlist_data.get("tracks", [])
    print(f"Found {len(playlist_tracks)} tracks in the playlist.")

    proposals_to_add = []

    # Process each track
    for track in playlist_tracks:
        track_id = track.get("id")
        if track_id is None or track_id in processed_ids:
            continue

        related_tracks = get_related_tracks(track_id)
        if not related_tracks:
            print(f"Skipping track {track_id} due to no related tracks.")
            new_processed_ids.add(track_id)
            continue

        # Filter for tracks with fewer than 100 likes
        low_like_tracks = []
        for rel in related_tracks:
            likes = rel.get("likes_count")
            if likes is None:
                likes = rel.get("favoritings_count", 0)
            if likes < 100 and rel.get("id"):
                low_like_tracks.append(rel)

        if low_like_tracks:
            print(f"Track {track_id}: Found {len(low_like_tracks)} low-like tracks.")
            proposals_to_add.extend([rt.get("id") for rt in low_like_tracks])
        else:
            print(f"Track {track_id}: No related tracks with <100 likes found.")

        new_processed_ids.add(track_id)

    # Update proposals playlist if new tracks were found
    if proposals_to_add:
        update_proposals_playlist(proposals_to_add)
    else:
        print("No new low-like tracks found for any source track.")

    # Save processed track IDs to history file
    if new_processed_ids:
        append_to_history(HISTORY_FILE, new_processed_ids)

if __name__ == "__main__":
    main()
