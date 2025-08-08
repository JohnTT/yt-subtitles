from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for, abort
import os
import subprocess
import shlex
import whisper
from pathlib import Path

app = Flask(__name__)

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
            <option value="hi">Hindi</option>
            <option value="ge">German</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="cn">Chinese</option>
            <option value="jp">Japanese</option>
            <option value="ko">Korean</option>
            <option value="ro">Romanian</option>
        </select><br><br>

        <button type="submit">Download & Translate</button>
    </form>

    <h3>Translated Videos Ready for Download</h3>
    <ul>
        {% for file in files %}
            <li>
                <a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a>
                <form method="post" action="{{ url_for('delete_file', filename=file) }}" style="display:inline;">
                    <button type="submit" onclick="return confirm('Delete {{ file }}?')">Delete</button>
                </form>
            </li>
        {% else %}
            <li>No files yet.</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

import subprocess
from pathlib import Path

def translate_video(input_path, language):
    input_path = Path(input_path)

    # Ensure output directories exist
    srt_dir = DOWNLOADS_DIR
    srt_dir.mkdir(parents=True, exist_ok=True)
    SUBTITLES_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Run Whisper to create the SRT in videos-downloads
    whisper_cmd = [
        "whisper",
        str(input_path),
        "--model", "large",
        "--language", language,
        "--task", "translate",
        "--output_format", "srt",
        "--output_dir", str(srt_dir),
    ]
    subprocess.run(whisper_cmd, check=True)

    # 2) Locate the generated SRT
    srt_path = srt_dir / (input_path.with_suffix(".srt").name)
    if not srt_path.exists():
        candidates = list(srt_dir.glob(input_path.stem + "*.srt"))
        if not candidates:
            raise FileNotFoundError(f"Could not find SRT for {input_path.name} in {srt_dir}")
        srt_path = candidates[0]

    # 3) Build output file path in videos-subtitles
    output_path = SUBTITLES_DIR / input_path.name

    # 4) Mux SRT into MP4 without burning in
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),   # video
        "-i", str(srt_path),     # subtitles
        "-c", "copy",
        "-c:s", "mov_text",
        "-metadata:s:s:0", f"language={language}",
        str(output_path),
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    app.logger.info(f"Video with subtitles written to {str(output_path)}")

@app.route("/", methods=["GET"])
def index():
    files = [f for f in os.listdir(SUBTITLES_DIR) if (SUBTITLES_DIR / f).is_file()]
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

        # Run translation (creates muxed file in SUBTITLES_DIR)
        translate_video(str(latest_file), language)

        # Delete original download after translation completes
        try:
            latest_file.unlink()
            app.logger.info("Deleted original file: %s", latest_file)
        except Exception as del_err:
            app.logger.error("Failed to delete %s: %s", latest_file, del_err)

        # Delete the corresponding .srt file in videos-downloads
        srt_path = latest_file.with_suffix(".srt")
        try:
            if srt_path.exists():
                srt_path.unlink()
                app.logger.info("Deleted subtitle file: %s", srt_path)
        except Exception as del_err:
            app.logger.error("Failed to delete %s: %s", srt_path, del_err)

    except Exception as e:
        app.logger.error("Error downloading/translating: %s", e)

    return redirect(url_for("index"))

@app.route("/videos-subtitles/<path:filename>")
def download_file(filename):
    target = SUBTITLES_DIR / filename
    if not target.exists():
        app.logger.error("Requested file not found: %s", target)
        abort(404)
    return send_from_directory(str(SUBTITLES_DIR), filename, as_attachment=True)

# NEW: delete route (POST) to remove a translated video safely
@app.post("/videos-subtitles/delete/<path:filename>")
def delete_file(filename):
    # Resolve and ensure the target is within SUBTITLES_DIR (prevent path traversal)
    target = (SUBTITLES_DIR / filename).resolve()
    try:
        target.relative_to(SUBTITLES_DIR.resolve())
    except ValueError:
        app.logger.warning("Blocked path traversal attempt: %s", target)
        abort(400, description="Invalid filename")

    if not target.exists() or not target.is_file():
        app.logger.error("File to delete not found: %s", target)
        abort(404)

    try:
        target.unlink()
        app.logger.info("Deleted translated video: %s", target)
    except Exception as e:
        app.logger.error("Failed to delete %s: %s", target, e)
        abort(500, description="Failed to delete file")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=9000, debug=True)
