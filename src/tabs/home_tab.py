from nicegui import ui

def home_tab():
    ui.label('Welcome to the Home tab!')
    ui.button('Click me', on_click=lambda: ui.notify('Hello from Home tab!'))
