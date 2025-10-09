import logging
from multiprocessing import Process, Queue
from faster_whisper import WhisperModel

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s",
)

task_queue = Queue()
result_queue = Queue()

def whisper_process(task_queue, result_queue):
    """Worker process that waits for transcription tasks."""
    logger = logging.getLogger("whisper_process")
    logger.info("[Worker] Loading Whisper model...")
    whisper_model = WhisperModel(
        model_size_or_path="./models/models--Systran--faster-whisper-small",
        device="cpu",
    )
    logger.info("[Worker] Model loaded. Waiting for tasks...")

    while True:
        msg = task_queue.get()  # blocking wait
        audio_path = msg.get("audio_path")
        logger.info(f"[Worker] Received task for: {audio_path}")

# Start the whisper process
p = Process(target=whisper_process, args=(task_queue, result_queue))
p.start()
