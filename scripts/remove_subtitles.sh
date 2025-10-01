#!/bin/bash

# Check if input is provided
if [ -z "$1" ]; then
    echo "Usage: $0 inputfile"
    exit 1
fi

input="$1"
# Extract base name (without extension)
basename="${input%.*}"
# Extract extension
ext="${input##*.}"
# Output file
output="${basename}_Unsubtitled.${ext}"

# Run ffmpeg, copy video/audio, drop subtitles
ffmpeg -i "$input" -map 0:v -map 0:a -c copy "$output"

echo "Created: $output"
