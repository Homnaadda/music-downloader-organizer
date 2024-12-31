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
            #
            # -x / --extract-audio: Download & extract only audio
            # --audio-format mp3 : Convert to MP3
            # -o ...             : Output filename pattern
            #
            command = [
                'yt-dlp',
                '-x',
                '--audio-format', 'mp3',
                '-o', os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
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

        if result.returncode == 0:
            files_after = set(os.listdir(DOWNLOAD_DIR))
            new_files = list(files_after - files_before)

            if new_files:
                return jsonify({
                    "message": "Download successful",
                    "files": new_files
                }), 200
            else:
                return jsonify({"error": "No files downloaded"}), 400
        else:
            print(f"Download failed with return code: {result.returncode}")
            return jsonify({
                "error": "Download failed",
                "details": result.stderr
            }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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
