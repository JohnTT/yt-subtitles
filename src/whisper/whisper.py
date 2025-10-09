import logging
import time
from multiprocessing import Process, Queue
from faster_whisper import WhisperModel

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s",
)

task_queue = Queue()
result_queue = Queue()

def whisper_process(task_queue, result_queue):
    """Background process that performs Whisper translation tasks."""
    logger = logging.getLogger("whisper_process")
    logger.info("Loading Whisper model...")
    whisper_model = WhisperModel(
        model_size_or_path="./models/models--Systran--faster-whisper-small",
        device="cpu",
    )
    logger.info("Model ready.")

    while True:
        msg = task_queue.get()
        if msg == "STOP":
            logger.info("Stopping.")
            break

        audio_path = msg.get("audio_path")
        srt_path = msg.get("srt_path")

        try:
            logger.info(f"Translating {audio_path} → {srt_path}")
            start_time = time.time()

            # Perform translation
            segments, info = whisper_model.transcribe(
                audio_path, beam_size=5, task="translate"
            )

            # Write SRT file
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segments, start=1):
                    start = srt_time(segment.start)
                    end = srt_time(segment.end)
                    text = segment.text.strip()
                    f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

            elapsed = time.time() - start_time
            result_queue.put({
                "status": "success",
                "audio_path": audio_path,
                "srt_path": srt_path,
                "language": info.language,
                "time": elapsed,
            })
            logger.info(f"Finished {audio_path} in {elapsed:.1f}s.")

        except Exception as ex:
            result_queue.put({
                "status": "error",
                "audio_path": audio_path,
                "srt_path": srt_path,
                "error": str(ex),
            })
            logger.info(f"Error: {ex}")

def srt_time(seconds):
    ms = int((seconds % 1) * 1000)
    s = int(seconds)
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

# Start the whisper process
p = Process(target=whisper_process, args=(task_queue, result_queue))
p.start()
