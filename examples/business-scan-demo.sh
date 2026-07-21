#!/usr/bin/env bash
# Example: run a business scan and save results to a timestamped file.
# Usage: bash examples/business-scan-demo.sh "local AI"
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCAN="${SCRIPT_DIR}/hscan"
QUERY="${1:-local AI}"
OUT="${SCRIPT_DIR}/examples/output-$(date +%Y%m%d-%H%M%S).csv"
mkdir -p "$(dirname "$OUT")"
echo "Running business scan for: $QUERY"
"$SCAN" "$QUERY" -n 3 -c market,competitors,clients,partnerships,regulations,signals --csv > "$OUT"
echo "Saved: $OUT"
