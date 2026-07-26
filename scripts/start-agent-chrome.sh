#!/usr/bin/env zsh
# Start isolated Google Chrome with remote debugging on fixed port.
# Uses a disposable profile under /tmp/agent-chrome so it does not touch your main browser state.
set -euo pipefail
PORT="${1:-9222}"
USER_DATA_DIR="${2:-/tmp/agent-chrome}"
URL="${3:-https://www.perplexity.ai}"

if ! command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" >/dev/null 2>&1; then
  echo "Chrome not found at default path" >&2
  exit 1
fi

rm -rf "$USER_DATA_DIR"
mkdir -p "$USER_DATA_DIR"

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$USER_DATA_DIR" \
  --no-first-run \
  --disable-default-apps \
  --disable-popup-blocking \
  --disable-translate \
  --disable-sync \
  --disable-extensions \
  "$URL" >/dev/null 2>&1 &
echo "chrome_pid=$!"
echo "debug_url=http://127.0.0.1:${PORT}/json/list"
