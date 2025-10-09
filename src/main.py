from nicegui import ui
from tabs import upload, youtube  # import the tab modules

# Start Web UI
with ui.tabs().classes('w-full') as tabs:
    upload_tab = ui.tab('Upload Audio')
    youtube_tab = ui.tab('Translate YouTube Video')

with ui.tab_panels(tabs, value=upload_tab).classes('w-full'):
    with ui.tab_panel(upload_tab):
        upload.content()
    with ui.tab_panel(youtube_tab):
        youtube.content()

ui.run()
