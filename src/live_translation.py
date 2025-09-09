import sounddevice as sd
import numpy as np
import queue
import sys
import time

from faster_whisper import WhisperModel

# Load model (choose size according to GPU/CPU capacity)
model = WhisperModel("large-v2")

# Queue for audio chunks
audio_q = queue.Queue()

# Audio callback for sounddevice
def callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_q.put(indata.copy())

# Start recording stream
samplerate = 16000  # Whisper expects 16kHz mono
blocksize = 16000   # 1 second of audio
stream = sd.InputStream(samplerate=samplerate, channels=1, blocksize=blocksize, callback=callback)
stream.start()

print("🎙️ Listening and translating (press Ctrl+C to stop)...")

try:
    buffer = np.zeros((0,), dtype=np.float32)

    while True:
        # Get next audio block
        audio = audio_q.get()
        audio = audio.flatten().astype(np.float32)

        # Append to buffer
        buffer = np.concatenate([buffer, audio])

        # Process every ~5 seconds of audio
        if len(buffer) > samplerate * 5:
            segment = buffer
            buffer = np.zeros((0,), dtype=np.float32)

            # Translate
            segments, info = model.transcribe(segment, task="translate")

            for seg in segments:
                print(f"[{seg.start:.2f}s -> {seg.end:.2f}s] {seg.text}")

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
    stream.stop()
    stream.close()
