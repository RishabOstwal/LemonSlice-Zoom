#!/usr/bin/env bash
# Usage: ./dispatch.sh ["<zoom link>"] ["Bot name"]
# Prompts for the Zoom link if it isn't passed as an argument.
set -euo pipefail

cd "$(dirname "$0")"

meeting_url="${1:-}"
bot_name="${2:-Lil Spark}"

if [ -z "$meeting_url" ]; then
  read -r -p "Zoom meeting URL: " meeting_url
fi

if [ -z "$meeting_url" ]; then
  echo "A Zoom meeting URL is required." >&2
  exit 1
fi

uv run python dispatch.py "$meeting_url" --bot-name "$bot_name"
