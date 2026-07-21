#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SCRIPT_DIR}/.venv/bin/python"
if [ ! -x "${PYTHON}" ]; then
  python3 -m venv "${SCRIPT_DIR}/.venv"
  "${SCRIPT_DIR}/.venv/bin/python" -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1 || true
  "${SCRIPT_DIR}/.venv/bin/python" -m pip install -r "${SCRIPT_DIR}/requirements.txt" >/dev/null
fi

mkdir -p "$HOME/.cache/web-search"

echo "installer:configure shell aliases"
grep -q "alias hsearch=" "$HOME/.zshrc" 2>/dev/null || printf '%s\n' "alias hsearch='${SCRIPT_DIR}/hsearch'" >> "$HOME/.zshrc"
grep -q "alias hscan=" "$HOME/.zshrc" 2>/dev/null || printf '%s\n' "alias hscan='${SCRIPT_DIR}/hscan'" >> "$HOME/.zshrc"

echo "Installed. Restart shell or run: source ~/.zshrc"
