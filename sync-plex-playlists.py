"""
This script automates playlist management for your Plex server
using pre-defined variables. Playlists are local (Windows), and
Plex runs in a docker container - though where Plex lives shouldn't
matter as long as the file name in your mp3s *roughly* match the 
file name in your Plex library.

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
from fuzzywuzzy import fuzz
import os
import time
import logging

# Configure logging
logging.basicConfig(filename='C:\\Logs\\plex-playlists-sync.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = 'your-plex-token'
PLEX_LIBRARY_SECTION_ID = 2  # Most common is 2, use the same method of getting your plex-token to retrieve 
local_folder = r"C:\path\to\.m3u8\playlists"  # Replace with your local Windows base path


def normalize_string(s):
    return s.lower().strip() if s else ""

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
    unmatched_tracks = 0
    for track_info in track_infos:
        if len(track_info) == 2:
            artist_name, track_name = track_info
            track_name = track_name.replace('.mp3', '')  # Remove the .mp3 extension

            # Normalize the artist name and track name
            artist_name = normalize_string(artist_name)
            track_name = normalize_string(track_name)

            matched = False
            for track in tracks:
                # Normalize the artist name and track name
                track_artist_name = normalize_string(track.grandparentTitle)
                track_track_name = normalize_string(track.title)

                # Use fuzzy matching to compare the artist name and track name
                if fuzz.token_set_ratio(artist_name, track_artist_name) > 70 and fuzz.token_set_ratio(track_name, track_track_name) > 70:
                    playlist_tracks.append(track)
                    matched = True
                    break

            if not matched:
                unmatched_tracks += 1
                logging.debug(f"Track not matched: Artist - {artist_name}, Track - {track_name}")

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

        logging.info(f"Added {len(playlist_tracks)} tracks to playlist: {playlist_name}")
        logging.info(f"{unmatched_tracks} tracks were not matched for playlist: {playlist_name}")

        return playlist
    else:
        logging.error(f"No matching tracks found for playlist: {playlist_name}")

# Connect to the Plex server
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Store the last modified times of the .m3u files
last_modified_times = {}

# Convert and sync each playlist
for root, dirs, files in os.walk(local_folder):
    for file in files:
        try:
            if file.endswith('.m3u'):
                m3u_playlist_path = os.path.join(root, file)
                m3u8_playlist_path = m3u_playlist_path.replace('.m3u', '.m3u8')

                # Get the last modified time of the .m3u file
                last_modified_time = os.path.getmtime(m3u_playlist_path)

                # If the .m3u file has been modified since the last sync, run the sync
                if m3u_playlist_path not in last_modified_times or last_modified_time > last_modified_times[m3u_playlist_path]:
                    if file.endswith('.m3u8'):
                        m3u_playlist_path = convert_m3u8_to_m3u(m3u8_playlist_path)
                    sync_playlist_with_plex(plex, m3u_playlist_path)

                    # Update the last modified time
                    last_modified_times[m3u_playlist_path] = last_modified_time
        except Exception as e:
            logging.error(f"An error occurred while processing file {file}: {e}")
