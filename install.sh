#!/usr/bin/env bash
set -euo pipefail

echo "🌐 Hermes Web Search — Installer"
echo "=================================="
echo ""

if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 not found."
    exit 1
fi
echo "✓ Python $(python3 --version)"

pip3 install requests beautifulsoup4 --quiet
echo "✓ Dependencies installed"

# Add aliases
SHELL_RC="$HOME/.zshrc"
for alias_cmd in \
    "alias hsearch='python3 $(pwd)/search.py'" \
    "alias hscan='python3 $(pwd)/business/scan.py'"; do
    name="${alias_cmd%%=*}"
    if grep -q "$name" "$SHELL_RC" 2>/dev/null; then
        echo "✓ $name already exists"
    else
        echo "$alias_cmd" >> "$SHELL_RC"
        echo "✓ Added $name"
    fi
done

echo ""
echo "✅ Install complete!"
echo ""
echo "Quick test:"
echo "  python3 search.py \"test\" -n 2 -b brave"
echo ""
echo "Or after restarting terminal:"
echo "  hsearch \"your query\" -n 10"