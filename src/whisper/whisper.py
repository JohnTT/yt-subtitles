from faster_whisper import WhisperModel

# Load faster-whipser translation model
whisper_model = WhisperModel(model_size_or_path="small", device="cuda", compute_type="float16")
