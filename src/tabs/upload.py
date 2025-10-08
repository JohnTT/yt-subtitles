import os

from nicegui import ui

UPLOAD_DIR = 'data/uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

def content():
    ui.label('Upload tab')

    def handle_upload(e):
        filename = e.name
        extension = filename.rsplit('.', 1)[-1].lower()
        content = e.content.read()
        size = len(content)

        # Validate file type
        if extension not in ALLOWED_EXTENSIONS:
            ui.notify(f'❌ Unsupported file type: {extension}', color='red')
            return

        # Validate file size
        if size > MAX_FILE_SIZE:
            ui.notify(f'❌ File too large: {size/1024/1024:.2f} MB (max 25 MB)', color='red')
            return

        # Save the file
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, 'wb') as f:
            f.write(content)

        ui.notify(f'✅ Saved: {filename}')

    def rejected_handler(e):
        ui.notify(f'❌ Rejected file for unknown reason', color='red')

    ui.upload(
        label='Select file',
        auto_upload=True,
        on_upload=handle_upload,
        on_rejected=rejected_handler,
        max_file_size=MAX_FILE_SIZE,
    )
