import os
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
from organize_music import organize_music

app = Flask(__name__)

DOWNLOAD_DIR = "/app/downloads"

# DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    files_before = set(os.listdir(DOWNLOAD_DIR))

    try:
        # Decide which tool to use based on the link
        if "spotify" in url.lower():
            # Spotify link -> use SpotDL (mp3 or best default)
            command = [
                'spotdl',
                'download',
                url,
                '--output', DOWNLOAD_DIR
            ]
        elif any(domain in url.lower() for domain in ["youtube.com", "youtu.be", "music.youtube"]):
            # YouTube or YouTube Music -> use yt-dlp
            # Enhanced yt-dlp command with better error handling
            command = [
                'yt-dlp',
                '-x',
                '--audio-format', 'mp3',
                '--ffmpeg-location', '/usr/bin/ffmpeg',
                '-o', os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                '--no-warnings',
                '--extract-flat', 'false',
                url
            ]
        else:
            # Fallback
            command = [
                'spotdl',
                'download',
                url,
                '--output', DOWNLOAD_DIR
            ]

        result = subprocess.run(command, capture_output=True, text=True)

        print("=== Download Command ===")
        print(" ".join(command))
        print("=== STDOUT ===")
        print(result.stdout)
        print("=== STDERR ===")
        print(result.stderr)
        print("Return code:", result.returncode)
        print("========================")

        # Check if download was successful (even with post-processing warnings)
        files_after = set(os.listdir(DOWNLOAD_DIR))
        new_files = list(files_after - files_before)
        
        # Consider it successful if:
        # 1. Return code is 0, OR
        # 2. New files were created (download succeeded even if post-processing had issues)
        download_successful = result.returncode == 0 or len(new_files) > 0
        
        # Check for specific error patterns that indicate actual download failure
        stderr_lower = result.stderr.lower()
        actual_download_failed = any(error in stderr_lower for error in [
            'video unavailable',
            'private video',
            'video not found',
            'unable to download',
            'no video formats found',
            'sign in to confirm',
            'this video is not available'
        ])
        
        if download_successful and not actual_download_failed:
            files_after = set(os.listdir(DOWNLOAD_DIR))
            new_files = list(files_after - files_before)

            # Determine success message based on whether post-processing succeeded
            if result.returncode == 0:
                message = "Download completed successfully!"
            else:
                message = "Download completed! (Note: Audio conversion may need manual processing)"
            
            return jsonify({
                "message": message,
                "files": new_files if new_files else [],
                "success": True,
                "warning": result.returncode != 0
            }), 200
        else:
            # Provide more specific error messages
            if actual_download_failed:
                error_message = "Failed to download: Video may be private, unavailable, or region-restricted"
            elif "ffmpeg" in result.stderr.lower() or "ffprobe" in result.stderr.lower():
                error_message = "Download completed but audio conversion failed. Please try again or contact support."
            else:
                error_message = "Download failed. Please check the URL and try again."
                
            return jsonify({
                "error": error_message,
                "details": result.stderr,
                "success": False
            }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/organize', methods=['POST'])
def organize():
    try:
        organize_music()
        return jsonify({"message": "Music organized successfully"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
