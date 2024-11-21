# Music Downloader and Organizer Docker container

Welcome to the official Guithub repository for the **Music Downloader and Organizer** application! This containerized application is designed to simplify the downloading and organization of music tracks from various sources, including Spotify and other online repositories.

## Features
- **Download Music from Spotify and Other Sources**: Utilizing `spotdl` to easily download tracks, albums, and playlists from Spotify.
- **Organize Your Music Library**: Automatically organize downloaded music based on metadata using `mutagen` for ID3 tag handling and MusicBrainz for album and artist data.
- **Web Interface for Easy Control**: Includes a web interface built with Flask to allow users to input Spotify URLs for downloading and organizing music.

## What's Inside
This image contains:
- **Python 3.9 Slim**: A lightweight Python runtime to keep the image size manageable.
- **Flask**: For the web interface that facilitates music download and organization.
- **SpotDL**: A powerful tool for downloading Spotify tracks, albums, and playlists.
- **Mutagen**: A Python library used for handling ID3 metadata in music files, enabling automatic metadata editing.
- **MusicBrainz API**: To fetch album and artist information to enhance metadata.

## How to Use This Image
To use this application, you need to run it with Docker. You can use the Dockerhub image or make your own. Here's a simple command to get started:

```bash
git clone
```
```bash
docker build your-image-name .
```

```bash
docker run -d \
  --name music-downloader \
  -p 5000:5000 \
  -v /path/to/your/music:/app/downloads \
  shivachaudhary18/music-downloader:latest
```

Replace `/path/to/your/music` with the directory where you want to save your downloaded music.

Once the container is running, you can access the web interface by opening `http://localhost:5000` in your browser.

### Organizing Music
The image also provides an **Organize Music** feature that utilizes a script to arrange your music based on artist and album. The downloaded music files will be automatically categorized into artist and album folders.

## Acknowledgements
We would like to extend our gratitude to the creators of the following open-source tools used in this project:
- **SpotDL**: Thank you to the developers of SpotDL for providing such a convenient way to download Spotify tracks. Find out more about it at [SpotDL GitHub](https://github.com/spotDL/spotify-downloader).
- **Mutagen**: For its simple and effective way to manipulate ID3 tags in MP3 files. More about it at [Mutagen GitHub](https://github.com/quodlibet/mutagen).
- **MusicBrainz**: For providing a free and open music metadata database. Learn more at [MusicBrainz](https://musicbrainz.org).

## License
This project is distributed under the MIT license, allowing for free, open use with attribution.

## Issues and Contributions
If you encounter any issues with this image or have ideas for improvements, please feel free to create an issue or submit a pull request on the project's GitHub repository.

Thank you for using this image, and we hope it helps make managing your music library easier!

