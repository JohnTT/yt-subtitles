from nicegui import ui

with ui.tabs().classes('w-full') as tabs:
    upload = ui.tab('Upload')
    youtube = ui.tab('YouTube')

with ui.tab_panels(tabs, value=youtube).classes('w-full'):
    with ui.tab_panel(upload):
        ui.label('Upload tab')
    with ui.tab_panel(youtube):
        ui.label('YouTube tab')

ui.run()
