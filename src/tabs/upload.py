from nicegui import ui

def content():
    ui.label('Upload tab')
    ui.button('Select file', on_click=lambda: ui.notify('Upload started'))
