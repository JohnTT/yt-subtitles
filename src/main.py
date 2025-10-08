from faster_whisper import WhisperModel
from nicegui import ui
from tabs import upload, youtube  # import the tab modules

# Load faster-whipser translation model
model = WhisperModel(model_size_or_path="small", device="cuda", compute_type="float16")

# Start Web UI
with ui.tabs().classes('w-full') as tabs:
    upload_tab = ui.tab('Upload')
    youtube_tab = ui.tab('YouTube')

with ui.tab_panels(tabs, value=upload_tab).classes('w-full'):
    with ui.tab_panel(upload_tab):
        upload.content()  # load the Upload tab UI
    with ui.tab_panel(youtube_tab):
        youtube.content()  # load the YouTube tab UI

ui.run()
