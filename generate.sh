#!/bin/bash
#
# AI Podcast Generator - Launcher Script
# Generates podcast episodes using Chatterbox TTS via Replicate
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATORS_DIR="$SCRIPT_DIR/pipeline/generators"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Check for virtual environment
if [[ ! -f "$VENV_PYTHON" ]]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Please create it with: uv venv && uv pip install -r requirements.txt"
    exit 1
fi

echo "======================================"
echo "   AI Podcast Generator"
echo "======================================"
echo ""
echo "Voice-cloned hosts (Corn & Herman) via Replicate"
echo "Cost: ~\$0.40 per 15-min episode"
echo ""

# Run the generator
"$VENV_PYTHON" "$GENERATORS_DIR/generate_episode.py" "$@"
