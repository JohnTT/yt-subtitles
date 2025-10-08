# Use an official Python runtime as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg etc.)
RUN apt-get update && \
    apt-get install -y ffmpeg bash && \
    rm -rf /var/lib/apt/lists/*

# Copy requirement files first for caching
COPY requirements.cpu.txt ./requirements.txt

# Create virtual environment and install dependencies in one shell
RUN pip install uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip sync requirements.txt

# Copy the application code
COPY src ./src
COPY scripts ./scripts
COPY run.sh .
COPY README.md LICENSE ./

# Make run.sh executable
RUN chmod +x run.sh

# Expose NiceGUI’s default port
EXPOSE 8080

# Environment variables for NiceGUI and Python
ENV PYTHONUNBUFFERED=1 \
    NICEGUI_HOST=0.0.0.0 \
    NICEGUI_PORT=8080

# Run the app
CMD ["./run.sh"]
