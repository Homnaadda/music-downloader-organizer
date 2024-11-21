import os
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
from organize_music import organize_music

app = Flask(__name__)

# Ensure downloads directory exists
DOWNLOAD_DIR = '/app/downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    # Get the URL from the request
    url = request.form.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Get the list of files before download
    files_before = set(os.listdir(DOWNLOAD_DIR))
    
    try:
        # Run spotdl command to download
        result = subprocess.run([
            'spotdl', 
            'download', 
            url, 
            '--output', 
            DOWNLOAD_DIR
        ], capture_output=True, text=True)
        
        # Check if download was successful
        if result.returncode == 0:
            # Get the list of files after download
            files_after = set(os.listdir(DOWNLOAD_DIR))
            # Get the newly downloaded files by comparing before and after
            new_files = list(files_after - files_before)

            if new_files:
                return jsonify({
                    "message": "Download successful", 
                    "files": new_files
                }), 200
            else:
                return jsonify({"error": "No files downloaded"}), 400
        else:
            return jsonify({
                "error": "Download failed", 
                "details": result.stderr
            }), 500
    
    except Exception as e:
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
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
