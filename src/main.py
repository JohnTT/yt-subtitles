import signal
import sys
from nicegui import ui
from tabs import upload, youtube
from whisper.whisper import stop_whisper_process  # new helper we’ll add

def handle_exit(signum, frame):
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    stop_whisper_process()  # stop background worker cleanly
    ui.shutdown()           # stop NiceGUI server
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# --- Start Web UI ---
with ui.tabs().classes('w-full') as tabs:
    upload_tab = ui.tab('Upload Audio')
    youtube_tab = ui.tab('Translate YouTube Video')

with ui.tab_panels(tabs, value=upload_tab).classes('w-full'):
    with ui.tab_panel(upload_tab):
        upload.content()
    with ui.tab_panel(youtube_tab):
        youtube.content()

ui.run()
