import os

from nicegui import ui

UPLOAD_DIR = 'data/youtube'
os.makedirs(UPLOAD_DIR, exist_ok=True)


def content():
    ui.label('YouTube tab')
    ui.button('Play video', on_click=lambda: ui.notify('Playing video...'))
