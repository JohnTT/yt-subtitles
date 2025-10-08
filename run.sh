#!/usr/bin/env bash
set -euo pipefail

# Resolve the repo root (directory where this script lives)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the virtual environment
VENV_PATH="$REPO_ROOT/.venv"

# Check if the virtual environment exists
if [[ ! -d "$VENV_PATH" ]]; then
    echo "❌ Error: Virtual environment not found at $VENV_PATH"
    echo "👉 Please create it by running: python3 -m venv .venv"
    exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Run the main script
python "$REPO_ROOT/src/main.py" "$@"
