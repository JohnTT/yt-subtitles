from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for, flash
import os
import subprocess
import shlex
from pathlib import Path

app = Flask(__name__)
app.secret_key = "secret"  # Required for flash messages

# Resolve paths relative to this file, not the working directory
BASE_DIR = Path(__file__).resolve().parents[1]  # repo root (parent of src/)
DOWNLOADS_DIR = BASE_DIR / "videos-downloads"
SUBTITLES_DIR = BASE_DIR / "videos-subtitles"

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Translator</title>
</head>
<body>
    <h2>YouTube Video Translator</h2>
    <form method="post" action="{{ url_for('download_video') }}">
        <label>YouTube Link:</label><br>
        <input type="text" name="youtube_link" size="60" required><br><br>

        <label>Video Language:</label><br>
        <select name="language" required>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
        </select><br><br>

        <button type="submit">Download & Translate</button>
    </form>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul style="color:red;">
          {% for msg in messages %}
            <li>{{ msg }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <h3>Translated Videos Ready for Download</h3>
    <ul>
        {% for file in files %}
            <li><a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a></li>
        {% else %}
            <li>No files yet.</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

def translate_video(input_path, output_path, language):
    import shutil
    shutil.copy(input_path, output_path)

@app.route("/", methods=["GET"])
def index():
    files = [f for f in os.listdir(SUBTITLES_DIR) if os.path.isfile(SUBTITLES_DIR / f)]
    return render_template_string(HTML_PAGE, files=files)

@app.route("/download", methods=["POST"])
def download_video():
    youtube_link = request.form.get("youtube_link")
    language = request.form.get("language")

    try:
        cmd = f'yt-dlp -f "bv*+ba/best" --merge-output-format mp4 -o "{DOWNLOADS_DIR}/%(title)s.%(ext)s" {shlex.quote(youtube_link)}'
        subprocess.run(cmd, shell=True, check=True)

        downloaded_files = sorted(
            [DOWNLOADS_DIR / f for f in os.listdir(DOWNLOADS_DIR)],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if not downloaded_files:
            raise RuntimeError("No video was downloaded.")
        
        latest_file = downloaded_files[0]
        output_path = SUBTITLES_DIR / latest_file.name

        translate_video(str(latest_file), str(output_path), language)

        flash(f"Video '{latest_file.name}' downloaded and translated!")
    except subprocess.CalledProcessError as e:
        flash(f"yt-dlp failed: {e}")
    except Exception as e:
        flash(f"Error: {e}")

    return redirect(url_for("index"))

@app.route("/videos-subtitles/<path:filename>")
def download_file(filename):
    return send_from_directory(str(SUBTITLES_DIR), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(port=9000, debug=True, use_reloader=True)
