# YouTube Video Translator

This project provides a web interface to download YouTube videos, automatically translate their audio to English subtitles using Whisper models, and generate downloadable videos with embedded subtitles.

## Features

- Download YouTube videos via [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Translate audio to English subtitles using [Faster Whisper XXL](https://github.com/guillaumekln/faster-whisper) or [whisper-ctranslate2](https://github.com/guillaumekln/whisper-ctranslate2)
- Burn subtitles into videos (hard subs) or mux as soft subtitles (see scripts)
- Simple Flask web UI for submitting jobs and downloading results
- Safe concurrent processing with file and thread locks

## Directory Structure

```
.gitignore
requirements.txt
run.sh
scripts/
    faster_whisper.sh
    whisper_ctranslate2.sh
src/
    main.py
videos-downloads/
videos-subtitles/
```

- `src/main.py`: Flask web server and main logic
- `scripts/`: Bash scripts for running Whisper models and muxing subtitles
- `videos-downloads/`: Temporary storage for downloaded videos
- `videos-subtitles/`: Output directory for processed videos with subtitles

## Installation

1. Clone the repository and enter the directory:
    ```sh
    git clone <repo-url>
    cd yt-subtitles
    ```

2. Create a Python virtual environment and install dependencies:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Install [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/) if not already available.

4. Download and set up [Faster Whisper XXL](https://github.com/guillaumekln/faster-whisper) and/or [whisper-ctranslate2](https://github.com/guillaumekln/whisper-ctranslate2) as needed. Update script paths if necessary.

## Usage

Start the web server:

```sh
./run.sh
```

Open [http://localhost:9000](http://localhost:9000) in your browser.

- Paste a YouTube link and select the original language.
- Click "Download & Translate" to process the video.
- Download the processed video with English subtitles from the list.

## Scripts

- `scripts/faster_whisper.sh`: Uses Faster Whisper XXL for translation and muxing.
- `scripts/whisper_ctranslate2.sh`: Uses whisper-ctranslate2 for translation and muxing.

You can run these scripts directly for CLI usage:

```sh
./scripts/faster_whisper.sh <input_file> <language>
./scripts/whisper_ctranslate2.sh <input_file> <language>
```

## Notes

- Output videos are stored in `videos-subtitles/`.
- Temporary downloads are stored in `videos-downloads/` and deleted after processing.
- Only one video is processed at a time (locks prevent concurrent jobs).
- Supported input formats: mp4, mkv, webm, m4a, mp3, wav, flac, aac, ogg.

## License

MIT License

---

**Credits:**  
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)  
- [Faster Whisper XXL](https://github.com/guillaumekln/faster-whisper)  
- [whisper-ctranslate2](https://github.com/Softcatala/whisper-ctranslate2)  
- [Flask](https://flask.palletsprojects.com/)
