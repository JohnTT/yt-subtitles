import os
from whisper.whisper import whisper_model
from nicegui import events, ui

UPLOAD_DIR = 'data/uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_FILE_SIZE_MB = MAX_FILE_SIZE / (1024 ** 2)

os.makedirs(UPLOAD_DIR, exist_ok=True)

def content():
    ui.upload(
        label='Select file',
        auto_upload=True,
        on_upload=on_upload_handler,
        on_rejected=on_rejected_handler,
        max_file_size=MAX_FILE_SIZE,
    )
    # Display all existing SRT files
    show_srt_files()


async def on_upload_handler(e: events.UploadEventArguments):
    filename = e.file.name
    extension = filename.rsplit('.', 1)[-1].lower()

    # Validate file type
    if extension not in ALLOWED_EXTENSIONS:
        ui.notify(f'❌ Unsupported file type: {extension}', color='red')
        return

    # Save uploaded audio
    audio_path = os.path.join(UPLOAD_DIR, filename)
    await e.file.save(audio_path)
    ui.notify(f'✅ Saved: {filename}')

    # Build output SRT file path
    base_name = os.path.splitext(filename)[0]
    srt_path = os.path.join(UPLOAD_DIR, f"{base_name}.srt")

    # Transcribe and translate
    segments, info = whisper_model.transcribe(audio_path, beam_size=5, task="translate")
    print(f"Filename: {filename}, Detected language: {info.language}, Probability: {info.language_probability:.2f}")

    # Write subtitles to SRT
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            def srt_time(seconds):
                ms = int((seconds % 1) * 1000)
                s = int(seconds)
                hrs = s // 3600
                mins = (s % 3600) // 60
                secs = s % 60
                return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

            start = srt_time(segment.start)
            end = srt_time(segment.end)
            text = segment.text.strip()
            srt_file.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    ui.notify(f'✅ Translation complete!')

    # Refresh the SRT file list
    show_srt_files()


def show_srt_files():
    """Displays download buttons for all SRT files in the upload directory."""
    ui.label('🎬 Available Translated SRT Files').classes('text-lg font-bold mt-4')

    # List all .srt files
    srt_files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith('.srt')]
    if not srt_files:
        ui.label('No subtitle files found. Upload an audio file to create one.')
        return

    # Create a download button for each file
    for f in sorted(srt_files):
        srt_path = os.path.join(UPLOAD_DIR, f)
        with ui.card().classes('p-3 my-2 flex justify-between items-center'):
            ui.label(f'📄 {f}')
            ui.button('⬇️ Download', on_click=lambda p=srt_path: ui.download.file(p))


def on_rejected_handler(e):
    ui.notify(f'ERROR: File larger than {MAX_FILE_SIZE_MB:.0f} MB', color='red')
