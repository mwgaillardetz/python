# Script to scan an m3u file, and if the track does not
# exist in the playlist then the track and it's parent
# folder are deleted.

import os
import shutil
import logging

from datetime import datetime

def parse_m3u(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    tracks = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return tracks

def delete_tracks_and_empty_dirs(dir_path, tracks):
    root_dir = os.path.abspath(dir_path)  # Use dir_path here
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if dirpath == root_dir:
            continue
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(full_path, root_dir).replace("\\", "/")
            if relative_path not in tracks:
                if os.path.exists(full_path):
                    message = f"Track {relative_path} not found in .m3u file, deleting..."
                    print(message)
                    logging.info(message)
                    os.remove(full_path)
                else:
                    message = f"Track {relative_path} does not exist on disk"
                    print(message)
                    logging.warning(message)

# Set up logging
logging.basicConfig(filename='C:\\logs\\remove-old-tracks.log', level=logging.INFO)

try:
    playlist_dir = 'playlist\\directory'
    m3u_files = [f for f in os.listdir(playlist_dir) if f.endswith('.m3u')]
    root_dir = 'playlist\\directory'

    # Run your functions for each .m3u file
    for m3u_file in m3u_files:
        playlist_path = os.path.join(playlist_dir, m3u_file)
        tracks = parse_m3u(playlist_path)
        delete_tracks_and_empty_dirs(playlist_path.rsplit('.', 1)[0], tracks)
        logging.info(f'Script completed successfully at {datetime.now()}')

except Exception as e:
    logging.error(f'An error occurred at {datetime.now()}: {e}', exc_info=True)
