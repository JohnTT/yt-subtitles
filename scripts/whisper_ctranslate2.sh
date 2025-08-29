#!/usr/bin/env bash
set -euo pipefail
source ../.venv/bin/activate

if [[ $# -lt 2 ]]; then
  echo "Usage: $(basename "$0") <input_file> <language>"
  echo "  <language> can be a code like 'en', 'es', 'fr', or a name like 'English'"
  exit 1
fi

INPUT_PATH="$1"
LANGUAGE="$2"

if [[ ! -f "$INPUT_PATH" ]]; then
  echo "ERROR: Input file not found: $INPUT_PATH" >&2
  exit 1
fi

whisper() {
    whisper-ctranslate2 "$@"
}

command -v whisper >/dev/null 2>&1 || { echo "ERROR: 'whisper' CLI not found in PATH."; exit 1; }
command -v ffmpeg  >/dev/null 2>&1 || { echo "ERROR: 'ffmpeg' not found in PATH."; exit 1; }

# Paths & names
INPUT_DIR="$(dirname "$INPUT_PATH")"
INPUT_BASE="$(basename "$INPUT_PATH")"
FNAME_NOEXT="${INPUT_BASE%.*}"
EXT="${INPUT_BASE##*.}"

# Where to place the SRT Whisper generates
SRT_DIR="$INPUT_DIR"

echo ">> Generating English subtitles from $LANGUAGE audio with Whisper..."
whisper \
  "$INPUT_PATH" \
  --model large-v2 \
  --language "$LANGUAGE" \
  --task translate \
  --output_format srt \
  --output_dir "$INPUT_DIR"

# Whisper names the output like: <basename>.<format>
SRT_PATH="$SRT_DIR/$FNAME_NOEXT.srt"
if [[ ! -f "$SRT_PATH" ]]; then
  # try to find any srt whisper might have produced (some versions add language tag)
  alt_srt="$(ls "$SRT_DIR"/"$FNAME_NOEXT"*.srt 2>/dev/null | head -n 1 || true)"
  if [[ -n "${alt_srt}" && -f "${alt_srt}" ]]; then
    SRT_PATH="${alt_srt}"
  else
    echo "ERROR: SRT not found where expected: $SRT_PATH" >&2
    exit 1
  fi
fi

# Normalize language tag for ffmpeg metadata
lang_meta="$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]')"
case "$lang_meta" in
  english|en-us|en-gb|eng|en) lang_meta="en" ;;
  spanish|español|spa|es)     lang_meta="es" ;;
  french|français|fra|fr)     lang_meta="fr" ;;
  german|deutsch|deu|de)      lang_meta="de" ;;
  chinese|中文|zho|cmn|zh)     lang_meta="zh" ;;
  japanese|日本語|jpn|ja)      lang_meta="ja" ;;
  korean|한국어|kor|ko)        lang_meta="ko" ;;
  hindi|हिन्दी|hin|hi)        lang_meta="hi" ;;
  romanian|română|ron|ro)     lang_meta="ro" ;;
  *) : ;;  # leave as-is if not matched
esac

# Decide how to mux subtitles based on container
# - MP4/MOV: use mov_text
# - MKV: keep as SRT
# - Others: default to MKV output to preserve soft subs
OUTPUT_BASENAME="${FNAME_NOEXT}_Subtitles"
shopt -s nocasematch
case "$EXT" in
  mp4|m4v|mov)
    OUTPUT_PATH="$INPUT_DIR/${OUTPUT_BASENAME}.mp4"
    echo ">> Muxing soft subtitles into MP4 (mov_text)..."
    ffmpeg -y \
      -i "$INPUT_PATH" \
      -i "$SRT_PATH" \
      -map 0 \
      -map 1:0 \
      -c copy \
      -c:s mov_text \
      -metadata:s:s:0 language="$lang_meta" \
      "$OUTPUT_PATH"
    ;;
  mkv)
    OUTPUT_PATH="$INPUT_DIR/${OUTPUT_BASENAME}.mkv"
    echo ">> Muxing soft subtitles into MKV (SRT)..."
    ffmpeg -y \
      -i "$INPUT_PATH" \
      -i "$SRT_PATH" \
      -map 0 \
      -map 1:0 \
      -c copy \
      -c:s srt \
      -metadata:s:s:0 language="$lang_meta" \
      "$OUTPUT_PATH"
    ;;
  *)
    # For unsupported/less-friendly containers, write MKV to ensure subs are preserved
    OUTPUT_PATH="$INPUT_DIR/${OUTPUT_BASENAME}.mkv"
    echo ">> Container '$EXT' not ideal for soft subs. Writing MKV with soft SRT..."
    ffmpeg -y \
      -i "$INPUT_PATH" \
      -i "$SRT_PATH" \
      -map 0 \
      -map 1:0 \
      -c copy \
      -c:s srt \
      -metadata:s:s:0 language="$lang_meta" \
      "$OUTPUT_PATH"
    ;;
esac
shopt -u nocasematch

echo "✅ Done. Output written to: $OUTPUT_PATH"

# -------------------------
# If you want HARD (burned-in) subtitles instead, replace the mux step above with:
#   ffmpeg -y -i "$INPUT_PATH" -vf "subtitles=$(printf '%q' "$SRT_PATH")" \
#     -c:v libx264 -crf 18 -preset medium -c:a copy "$OUTPUT_PATH"
# -------------------------
