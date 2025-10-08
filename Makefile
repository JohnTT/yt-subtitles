MODEL_DIR := models/models--Systran--faster-whisper-small
MODEL_REPO := Systran/faster-whisper-small

.PHONY: download-model
download-model:
	@if [ ! -d "$(MODEL_DIR)" ]; then \
		echo "Model not found. Downloading $(MODEL_REPO)..."; \
		mkdir -p models; \
		hf download $(MODEL_REPO) --local-dir $(MODEL_DIR) --local-dir-use-symlinks False; \
	else \
		echo "Model already exists — skipping download."; \
	fi

.PHONY: image
image: download-model
	docker build -t yt-subtitles:latest .

.PHONY: run
run: image
	docker stop yt_subtitles || true
	docker rm yt_subtitles || true
	docker run --name yt_subtitles -p 8080:8080 -v "$(pwd)/data":/app/data yt-subtitles
