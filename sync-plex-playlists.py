"""
This script automates playlist management for your Plex server
using pre-defined variables:

It connects to your Plex server using a provided URL and token.
Scours through local folders (defined as 'local_folder'), processing .m3u
and .m3u8 playlist files. Converts .m3u8 files to .m3u format, filtering
out unnecessary lines and removing the original .m3u8 files. Extracts
artist and track names from each line of .m3u files. Retrieves tracks
from a designated section of the Plex library, matching them with .m3u
file contents. Creates new playlists on the Plex server, naming them
after the corresponding .m3u files (minus the extension), and populates
them with matched tracks. Existing playlists are emptied before new tracks
are added. Logs error messages if no matching tracks are found or if an
error occurs during processing.

Utilizing the plexapi library for Plex server interaction and the os and
logging libraries for file and logging operations, this script streamlines
your playlist management tasks effortlessly.
"""

from plexapi.server import PlexServer
from plexapi.playlist import Playlist
import os
import time
import logging

# Define these variables before running the script:
PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'your-plex-token'
PLEX_LIBRARY_SECTION_ID = #2 is most common, can be found in the xml used to find plex_token
local_folder = r"C:\your\playlist\folder\location"

def convert_m3u8_to_m3u(m3u8_playlist_path):
    m3u_playlist_path = m3u8_playlist_path.replace('.m3u8', '.m3u')

    with open(m3u8_playlist_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(m3u_playlist_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if line.strip() and not line.startswith('#'):
                file.write(line)
            else:
                file.write(line)

    # Remove the original .m3u8 file
    os.remove(m3u8_playlist_path)

    return m3u_playlist_path

def sync_playlist_with_plex(plex, playlist_path):
    with open(playlist_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    track_infos = [line.strip().split(' - ', 1) for line in lines if line.strip() and not line.startswith('#')]

    # Get the list of all tracks in the music library
    artists = plex.library.sectionByID(PLEX_LIBRARY_SECTION_ID).all()
    tracks = [track for artist in artists for album in artist.albums() for track in album.tracks()]

    # Find the tracks that match the artist name and track name in the M3U file
    playlist_tracks = []
    for track_info in track_infos:
        if len(track_info) == 2:
            artist_name, track_name = track_info
            track_name = track_name.replace('.mp3', '')  # Remove the .mp3 extension
            for track in tracks:
                if track.title == track_name and track.grandparentTitle == artist_name:
                    playlist_tracks.append(track)
                    break

    playlist_name = os.path.basename(playlist_path).replace('.m3u', '')
    if playlist_tracks:
        # Check if a playlist with the same name already exists
        existing_playlists = plex.playlists()
        for playlist in existing_playlists:
            if playlist.title == playlist_name:
                # If a playlist with the same name exists, remove all tracks from the playlist
                playlist.removeItems(playlist.items())
                break
        else:
            # If a playlist with the same name doesn't exist, create a new playlist
            playlist = Playlist.create(plex, playlist_name, items=playlist_tracks)

        # Add the new tracks to the playlist
        playlist.addItems(playlist_tracks)
        return playlist
    else:
        logging.error(f"No matching tracks found for playlist: {playlist_name}")

# Connect to the Plex server
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Convert and sync each playlist
for root, dirs, files in os.walk(local_folder):
    for file in files:
        try:
            if file.endswith('.m3u8'):
                m3u8_playlist_path = os.path.join(root, file)
                m3u_playlist_path = convert_m3u8_to_m3u(m3u8_playlist_path)
                sync_playlist_with_plex(plex, m3u_playlist_path)
            elif file.endswith('.m3u'):
                m3u_playlist_path = os.path.join(root, file)
                m3u8_playlist_path = m3u_playlist_path.replace('.m3u', '.m3u8')
                if not os.path.exists(m3u8_playlist_path) or os.path.getmtime(m3u_playlist_path) > os.path.getmtime(m3u8_playlist_path):
                    sync_playlist_with_plex(plex, m3u_playlist_path)
        except Exception as e:
            logging.error(f"An error occurred while processing file {file}: {e}")