import os
import shutil
import requests
from mutagen.easyid3 import EasyID3
import re
import time

# Fetch album metadata from MusicBrainz
def fetch_metadata(artist, album):
    try:
        url = "https://musicbrainz.org/ws/2/release/"
        params = {
            'query': f'artist:{artist} AND release:{album}',
            'fmt': 'json',
            'limit': 1
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        if data.get('releases'):
            release = data['releases'][0]
            metadata = {
                'album': release.get('title', album),
                'artist': artist,
                'year': release.get('date', '').split('-')[0] if 'date' in release else '',
                'genre': release.get('genres', [{'name': 'Unknown'}])[0]['name'],
                'id': release.get('id')
            }
            return metadata
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metadata for {artist} - {album}: {e}")
        return None

# Fetch album cover art from Cover Art Archive
def fetch_album_cover(release_id):
    try:
        cover_art_url = f"http://coverartarchive.org/release/{release_id}/front"
        response = requests.get(cover_art_url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching cover art: {e}")
        return None

# Check for duplicates in the target directory
def is_duplicate(target_folder, filename):
    return os.path.exists(os.path.join(target_folder, filename))

# Sanitize folder names for Windows
def sanitize_folder_name(name):
    # Remove or replace invalid characters
    return re.sub(r'[<>:"/\\|?*]', '', name)

# Organize music by album, update metadata, download album art, and check for duplicates
def organize_and_update_metadata(source_dir, destination_dir):
    # Convert destination_dir to an absolute path
    destination_dir = os.path.abspath(destination_dir)
    
    for filename in os.listdir(source_dir):
        if filename.endswith('.mp3'):
            filepath = os.path.join(source_dir, filename)
            try:
                # Load existing metadata
                try:
                    audio = EasyID3(filepath)
                except Exception as e:
                    print(f"Error loading metadata for {filename}: {e}")
                    continue

                album = audio.get('album', ['Unknown Album'])[0]
                artist = audio.get('artist', ['Unknown Artist'])[0]
                
                # Fetch updated metadata
                metadata = fetch_metadata(artist, album)
                if metadata:
                    # Update metadata if available
                    audio['album'] = metadata['album']
                    audio['artist'] = metadata['artist']
                    if metadata['year']:
                        audio['date'] = metadata['year']
                    if metadata['genre']:
                        audio['genre'] = metadata['genre']
                    audio.save()
                    print(f"Updated metadata for {filename}")

                    # Sanitize folder names
                    album_folder = os.path.join(
                        destination_dir, 
                        sanitize_folder_name(metadata['artist']),
                        sanitize_folder_name(metadata['album'])
                    )
                else:
                    # Use existing values if metadata is not found
                    album_folder = os.path.join(
                        destination_dir, 
                        sanitize_folder_name(artist), 
                        sanitize_folder_name(album)
                    )

                # Create the album folder if it doesn’t exist
                os.makedirs(album_folder, exist_ok=True)
                
                # Check if the file is a duplicate in the target folder
                target_filepath = os.path.join(album_folder, filename)
                if is_duplicate(album_folder, filename):
                    print(f"Duplicate found, skipping {filename}")
                    continue
                
                # Fetch and save high-res album art if available
                if metadata and 'id' in metadata:
                    cover = fetch_album_cover(metadata['id'])
                    if cover:
                        cover_path = os.path.join(album_folder, "cover.jpg")
                        with open(cover_path, "wb") as f:
                            f.write(cover)
                        print(f"Downloaded cover for {metadata['album']}")
                
                # Move the file to the album folder if no duplicate exists
                shutil.move(filepath, target_filepath)
                print(f"Moved {filename} to {album_folder}")
                
            except Exception as e:
                print(f"Could not process {filename}: {e}")

# Flask endpoint function
def organize_music():
    source_directory = '/app/downloads'
    destination_directory = '/app/downloads/organized'
    organize_and_update_metadata(source_directory, destination_directory)
