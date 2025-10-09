import os
import asyncio
from whisper.whisper import whisper_model
from nicegui import events, ui

UPLOAD_DIR = 'data/uploads'
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_FILE_SIZE_MB = MAX_FILE_SIZE / (1024 ** 2)

os.makedirs(UPLOAD_DIR, exist_ok=True)


def content():
    ui.upload(
        label='Select file',
        auto_upload=True,
        on_upload=on_upload_handler,
        on_rejected=on_rejected_handler,
        max_file_size=MAX_FILE_SIZE,
    )
    show_srt_files()


async def on_upload_handler(e: events.UploadEventArguments):
    filename = e.file.name
    extension = filename.rsplit('.', 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        ui.notify(f'❌ Unsupported file type: {extension}', color='red')
        return

    audio_path = os.path.join(UPLOAD_DIR, filename)
    await e.file.save(audio_path)
    ui.notify(f'✅ Saved: {filename}')

    base_name = os.path.splitext(filename)[0]
    srt_path = os.path.join(UPLOAD_DIR, f"{base_name}.srt")

    # Create a progress card inside the current UI slot
    with ui.card().classes('p-4 my-4') as card:
        ui.label(f'🔄 Translating {filename}... Please wait.')
        progress = ui.linear_progress(value=0).classes('w-full mt-2')
        status_label = ui.label('Starting...')

    # Run translation in background
    asyncio.create_task(run_translation(audio_path, srt_path, progress, status_label, card))


async def run_translation(audio_path, srt_path, progress, status_label, card):
    """Run Whisper translation asynchronously and safely update UI."""
    try:
        # Fake progress updates asynchronously
        async def fake_progress():
            value = 0
            while value < 0.95:
                value += 0.01
                await asyncio.sleep(0.2)
                progress.set_value(value)
                status_label.set_text(f'Processing... {int(value*100)}%')
            status_label.set_text('Almost done...')

        progress_task = asyncio.create_task(fake_progress())

        # Run Whisper in executor thread
        loop = asyncio.get_running_loop()
        segments, info = await loop.run_in_executor(
            None,
            lambda: whisper_model.transcribe(audio_path, beam_size=5, task="translate")
        )

        progress_task.cancel()  # stop fake updates
        progress.set_value(1.0)
        status_label.set_text(f'✅ Translation complete! ({info.language})')

        # Write SRT file
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(segments, start=1):
                def srt_time(seconds):
                    ms = int((seconds % 1) * 1000)
                    s = int(seconds)
                    hrs = s // 3600
                    mins = (s % 3600) // 60
                    secs = s % 60
                    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

                start = srt_time(segment.start)
                end = srt_time(segment.end)
                text = segment.text.strip()
                srt_file.write(f"{i}\n{start} --> {end}\n{text}\n\n")

        # UI updates must happen inside the same slot context
        with card:
            card.clear()
            ui.label(f'🎉 Translation finished: {os.path.basename(srt_path)}').classes('text-lg font-bold')
            ui.button('⬇️ Download SRT', on_click=lambda p=srt_path: ui.download.file(p))

        ui.notify(f'✅ {os.path.basename(srt_path)} translated successfully!')
        show_srt_files()

    except Exception as ex:
        # Notify safely in the main UI thread
        ui.run_later(lambda: ui.notify(f'❌ Error during translation: {ex}', color='red'))


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
    ui.notify(f'ERROR: File larger than {MAX_FILE_SIZE_MB:.0f} MB', color='red')
