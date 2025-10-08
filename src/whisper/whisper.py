from faster_whisper import WhisperModel

# Load faster-whipser translation model
whisper_model = WhisperModel(
    model_size_or_path="./models/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120", 
    device="cpu",
)
