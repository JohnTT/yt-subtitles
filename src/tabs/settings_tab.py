from nicegui import ui

def settings_tab():
    ui.label('Settings')
    ui.switch('Enable notifications', value=True)
    ui.input('Username', placeholder='Enter your username')
