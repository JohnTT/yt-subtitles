from nicegui import ui
from tabs import upload, youtube  # import the tab modules

with ui.tabs().classes('w-full') as tabs:
    upload_tab = ui.tab('Upload')
    youtube_tab = ui.tab('YouTube')

with ui.tab_panels(tabs, value=youtube_tab).classes('w-full'):
    with ui.tab_panel(upload_tab):
        upload.content()  # load the Upload tab UI
    with ui.tab_panel(youtube_tab):
        youtube.content()  # load the YouTube tab UI

ui.run()
