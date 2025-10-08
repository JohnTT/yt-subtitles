from nicegui import ui

def content():
    ui.label('YouTube tab')
    ui.button('Play video', on_click=lambda: ui.notify('Playing video...'))
