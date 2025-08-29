#!/usr/bin/env bash
set -euo pipefail

# Resolve the repo root (directory where this script lives)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$REPO_ROOT/.venv/bin/activate"

# Run the main script
python "$REPO_ROOT/src/main.py" "$@"
