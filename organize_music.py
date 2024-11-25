import os
import shutil
import requests
from flask import Flask, jsonify
from mutagen.easyid3 import EasyID3
import re
import time
from ytmusicapi import YTMusic

# Initialize YTMusic
ytmusic = YTMusic()

# Initialize Flask app
app = Flask(__name__)

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

# Fetch metadata from YouTube Music
def fetch_metadata_from_ytmusic(title, artist):
    try:
        query = f"{title} {artist}"
        search_results = ytmusic.search(query, filter="songs")
        if search_results:
            track = search_results[0]
            metadata = {
                'title': track.get('title', 'Unknown Title'),
                'album': track.get('album', {}).get('name', 'Unknown Album'),
                'artist': ', '.join([a['name'] for a in track.get('artists', [])]),
                'year': track.get('year', ''),
                'genre': track.get('category', 'Unknown Genre'),
                'album_art_url': track.get('thumbnails', [{}])[-1].get('url')  # Get the largest thumbnail
            }
            print(f"Fetched metadata from YouTube Music: {metadata}")
            return metadata
        print(f"No metadata found on YouTube Music for query: {query}")
        return None
    except Exception as e:
        print(f"Error fetching metadata from YouTube Music: {e}")
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

# Fetch and save album cover from YouTube Music
def fetch_and_save_album_cover(album_art_url, album_folder):
    try:
        if album_art_url:
            print(f"Fetching album cover from URL: {album_art_url}")
            response = requests.get(album_art_url, stream=True, timeout=10)
            response.raise_for_status()
            cover_path = os.path.join(album_folder, "cover.jpg")
            with open(cover_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Album cover saved to {cover_path}")
    except Exception as e:
        print(f"Error fetching album cover: {e}")

# Check for duplicates in the target directory
def is_duplicate(target_folder, filename):
    return os.path.exists(os.path.join(target_folder, filename))

# Sanitize folder names for Windows
def sanitize_folder_name(name):
    # Remove or replace invalid characters
    name = name.replace(':', '-').replace('/', '-').replace('\\', '-')
    sanitized = re.sub(r'[^a-zA-Z0-9 _\-\(\)\[\]]', '', name.strip())
    return sanitized.strip()

# Extract the first artist from a list of artists
def get_first_artist(artist):
    for separator in [',', '/']:
        if separator in artist:
            return artist.split(separator)[0].strip()
    return artist.strip()

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

                title = audio.get('title', [os.path.splitext(filename)[0]])[0]
                artist = audio.get('artist', ['Unknown Artist'])[0]
                first_artist = get_first_artist(artist)
                
                # Fetch updated metadata from YouTube Music
                metadata = fetch_metadata_from_ytmusic(title, first_artist)
                if not metadata:
                    # Fallback to MusicBrainz if YouTube Music metadata is not available
                    metadata = fetch_metadata(first_artist, title)
                if metadata:
                    audio['album'] = metadata['album']
                    audio['artist'] = metadata['artist']
                    audio['date'] = metadata['year'] if metadata['year'] else audio.get('date', ['Unknown Year'])[0]
                    audio['genre'] = metadata['genre'] if metadata['genre'] != 'Unknown Genre' else audio.get('genre', ['Unknown Genre'])[0]
                    audio.save()
                    print(f"Updated metadata for {filename}")

                    # Sanitize folder names
                    album_folder = os.path.join(
                        destination_dir, 
                        sanitize_folder_name(metadata['album'])
                    )
                else:
                    # Use existing values if metadata is not found
                    album_folder = os.path.join(
                        destination_dir, 
                        sanitize_folder_name(audio.get('album', ['Unknown Album'])[0])
                    )

                # Create the album folder if it doesn’t exist
                os.makedirs(album_folder, exist_ok=True)
                
                # Check if the file is a duplicate in the target folder
                target_filepath = os.path.join(album_folder, filename)
                if is_duplicate(album_folder, filename):
                    print(f"Duplicate found, skipping {filename}")
                    continue
                
                # Fetch and save high-res album art if available from YouTube Music
                fetch_and_save_album_cover(metadata.get('album_art_url'), album_folder)
                
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
