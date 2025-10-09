import os
from nicegui import ui

UPLOAD_DIR = 'data/youtube'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def content():
    ui.button('YouTube Link', on_click=lambda: ui.notify('Playing video...'))
