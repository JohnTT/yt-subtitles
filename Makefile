.PHONY: image
image:
	docker build -t yt-subtitles:latest .

.PHONY: run
run: image
	docker run --name yt_subtitles -p 8080:8080 -v "$(pwd)/data":/app/data yt-subtitles
