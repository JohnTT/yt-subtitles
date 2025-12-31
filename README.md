# YouTube Video Translator

This project provides a web interface to download YouTube videos, automatically translate their audio to English subtitles using Whisper models, and generate downloadable videos with embedded subtitles.

## Features

- Download YouTube videos via [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Translate audio to English subtitles using [whisper-ctranslate2](https://github.com/guillaumekln/whisper-ctranslate2)
- Burn subtitles into videos (hard subs) or mux as soft subtitles (see scripts)
- Simple Flask web UI for submitting jobs and downloading results
- Safe concurrent processing with file and thread locks

## Directory Structure

```
.gitignore
requirements.txt
run.sh
scripts/
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

1. If using `CUDA`, install the appropriate Nvidia Drivers.  
    https://github.com/mexersus/debian-nvidia-drivers  
    https://developer.nvidia.com/cudnn

2. Install `ffmpeg`
    ```sh
    jchen@john-Desktop:~/workspaces/yt-subtitles/scripts$ sudo apt install ffmpeg
    ```

3. Clone the repository and enter the directory:
    ```sh
    git clone <repo-url>
    cd yt-subtitles
    ```

4. Create a Python virtual environment and install dependencies:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

5. Install [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/) if not already available.

6. Download and set up [whisper-ctranslate2](https://github.com/guillaumekln/whisper-ctranslate2) as needed. Update script paths if necessary.

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

- `scripts/whisper_ctranslate2.sh`: Uses whisper-ctranslate2 for translation and muxing.

You can run this script directly for CLI usage:

```sh
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
- [whisper-ctranslate2](https://github.com/Softcatala/whisper-ctranslate2)  
- [Flask](https://flask.palletsprojects.com/)
