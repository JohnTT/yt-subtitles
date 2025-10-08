import os
from whisper.whisper import whisper_model
from nicegui import events, ui

UPLOAD_DIR = 'data/uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_FILE_SIZE_MB = MAX_FILE_SIZE / (1024 ** 2)

os.makedirs(UPLOAD_DIR, exist_ok=True)

def content():
    ui.label('Upload tab')
    ui.upload(
        label='Select file',
        auto_upload=True,
        on_upload=on_upload_handler,
        on_rejected=on_rejected_handler,
        max_file_size=MAX_FILE_SIZE,
    )

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

    # Show download button for SRT file
    with ui.card().classes('p-4'):
        ui.label('🎉 Your translated subtitle file is ready!')
        ui.button(
            '⬇️ Download Translated SRT',
            on_click=lambda p=srt_path: ui.download.file(p)
        )

def on_rejected_handler(e):
    ui.notify(f'ERROR: File larger than {MAX_FILE_SIZE_MB:.0f} MB', color='red')
