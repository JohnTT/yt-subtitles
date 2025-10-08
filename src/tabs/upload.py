import os

from nicegui import ui

UPLOAD_DIR = 'data/uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def content():
    ui.label('Upload tab')

    def handle_upload(e):
        file = e.content
        path = os.path.join(UPLOAD_DIR, e.name)
        with open(path, 'wb') as f:
            f.write(file.read())
        ui.notify(f'Saved: {e.name}')

    ui.upload(
        label='Select file',
        auto_upload=True,
        on_upload=handle_upload,
    )
