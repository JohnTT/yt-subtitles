import logging
import time
import signal
from multiprocessing import Process, Queue, Manager
from faster_whisper import WhisperModel

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s",
)

task_queue = Queue()
result_queue = Queue()
manager = Manager()

# Shared dictionary for progress
progress = manager.dict({
    "queued": 0,
    "completed": 0,
    "current_task": None,
    "last_result": None,
})

def srt_time(seconds):
    ms = int((seconds % 1) * 1000)
    s = int(seconds)
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def whisper_process(task_queue, result_queue, progress):
    """Background process that performs Whisper translation tasks."""
    logger = logging.getLogger("whisper_process")

    def handle_sigterm(signum, frame):
        logger.info(f"Received signal {signum}, stopping whisper process...")
        task_queue.put("STOP")

    # Register signal handlers for the worker itself
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    logger.info("Loading Whisper model...")
    whisper_model = WhisperModel(
        model_size_or_path="./models/models--Systran--faster-whisper-small",
        device="cpu",
    )
    logger.info("Model ready.")

    while True:
        msg = task_queue.get()
        if msg == "STOP":
            logger.info("Stopping worker process.")
            break

        audio_path = msg.get("audio_path")
        srt_path = msg.get("srt_path")

        # update progress
        progress["current_task"] = audio_path
        if progress["queued"] > 0:
            progress["queued"] -= 1

        try:
            logger.info(f"Translating {audio_path} → {srt_path}")
            start_time = time.time()

            # Perform translation
            segments, info = whisper_model.transcribe(
                audio_path, beam_size=5, task="translate", log_progress=True,
            )

            # Write SRT file
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segments, start=1):
                    start = srt_time(segment.start)
                    end = srt_time(segment.end)
                    text = segment.text.strip()
                    f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

            elapsed = time.time() - start_time
            result = {
                "status": "success",
                "audio_path": audio_path,
                "srt_path": srt_path,
                "language": info.language,
                "time": elapsed,
            }
            result_queue.put(result)
            progress["completed"] += 1
            progress["last_result"] = result
            logger.info(f"Finished {audio_path} in {elapsed:.1f}s.")

        except Exception as ex:
            result = {
                "status": "error",
                "audio_path": audio_path,
                "srt_path": srt_path,
                "error": str(ex),
            }
            result_queue.put(result)
            progress["completed"] += 1
            progress["last_result"] = result
            logger.error(f"Error: {ex}")

        progress["current_task"] = None


# --- Process management ---
p = Process(target=whisper_process, args=(task_queue, result_queue, progress))
p.start()

def add_task(audio_path, srt_path):
    task_queue.put({"audio_path": audio_path, "srt_path": srt_path})
    progress["queued"] += 1

def get_progress():
    """Query current progress status."""
    return dict(progress)

def stop_whisper_process():
    """Stop the Whisper worker gracefully."""
    if p.is_alive():
        logging.info("Sending STOP signal to Whisper process...")
        task_queue.put("STOP")
        p.join(timeout=5)
        if p.is_alive():
            logging.warning("Force terminating Whisper process...")
            p.terminate()
