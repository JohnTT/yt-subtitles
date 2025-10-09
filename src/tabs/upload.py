import os
from whisper import whisper
from nicegui import events, ui

UPLOAD_DIR = 'data/uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_FILE_SIZE_MB = MAX_FILE_SIZE / (1024 ** 2)

os.makedirs(UPLOAD_DIR, exist_ok=True)

def content():
    ui.upload(
        label='🎵 Select audio file',
        auto_upload=True,
        on_upload=on_upload_handler,
        on_rejected=on_rejected_handler,
        max_file_size=MAX_FILE_SIZE,
    )

    # Create a section to display progress
    ui.separator()
    ui.label('🧠 Transcription Progress').classes('text-lg font-bold mt-4')

    progress_label = ui.label('No active tasks yet.')
    progress_bar = ui.linear_progress(value=0).props('color=blue stripe animated').classes('w-full mt-2')

    # Periodically update progress bar
    def update_progress():
        progress = whisper.get_progress()
        queued = progress.get('queued', 0)
        completed = progress.get('completed', 0)
        current = progress.get('current_task', None)

        total = queued + completed + (1 if current else 0)
        if total > 0:
            percent = completed / total
            progress_bar.value = percent
        else:
            progress_bar.value = 0

        if current:
            filename = os.path.basename(current)
            progress_label.text = f'🔄 Processing: {filename} | Completed: {completed} | Queued: {queued}'
        else:
            progress_label.text = f'✅ Completed: {completed} | Waiting: {queued}'

    ui.timer(10.0, update_progress)
    ui.separator()
    show_srt_files()


async def on_upload_handler(e: events.UploadEventArguments):
    filename = e.file.name
    extension = filename.rsplit('.', 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        ui.notify(f'❌ Unsupported file type: {extension}', color='red')
        return

    audio_path = os.path.join(UPLOAD_DIR, filename)
    await e.file.save(audio_path)

    base_name = os.path.splitext(filename)[0]
    srt_path = os.path.join(UPLOAD_DIR, f"{base_name}.srt")

    whisper.add_task(audio_path, srt_path)
    ui.notify(f'✅ File uploaded and queued for translation: {filename}')

def show_srt_files():
    ui.label('🎬 Available Translated SRT Files').classes('text-lg font-bold mt-4')

    srt_files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith('.srt')]
    if not srt_files:
        ui.label('No subtitle files found. Upload an audio file to create one.')
        return

    for f in sorted(srt_files):
        srt_path = os.path.join(UPLOAD_DIR, f)
        with ui.card().classes('p-3 my-2 flex justify-between items-center'):
            ui.label(f'📄 {f}')
            ui.button('⬇️ Download', on_click=lambda p=srt_path: ui.download.file(p))

def on_rejected_handler(e):
    ui.notify(f'❌ ERROR: File larger than {MAX_FILE_SIZE_MB:.0f} MB', color='red')
