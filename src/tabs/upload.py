import os
from whisper.whisper import whisper_model

from nicegui import events, ui

UPLOAD_DIR = 'data/uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
MAX_FILE_SIZE_MB = MAX_FILE_SIZE / (1024 ** 2)

os.makedirs(UPLOAD_DIR, exist_ok=True)

def content():
    ui.label('Upload tab')

    async def handle_upload(e: events.UploadEventArguments):
        filename = e.file.name
        extension = filename.rsplit('.', 1)[-1].lower()

        # Validate file type
        if extension not in ALLOWED_EXTENSIONS:
            ui.notify(f'❌ Unsupported file type: {extension}', color='red')

        # Save the file
        path = os.path.join(UPLOAD_DIR, filename)
        await e.file.save(path)
        
        ui.notify(f'✅ Saved: {filename}')

    def rejected_handler(e):
        ui.notify(f'ERROR: File larger than {MAX_FILE_SIZE_MB:.0f} MB', color='red')

    ui.upload(
        label='Select file',
        auto_upload=True,
        on_upload=handle_upload,
        on_rejected=rejected_handler,
        max_file_size=MAX_FILE_SIZE,
    )
