#!/usr/bin/env bash
set -euo pipefail

# CCG Skill Installer
# 1. Creates symlink in ~/.claude/skills/
# 2. Sets executable permissions
# 3. Checks CLI dependencies
# 4. Checks configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$HOME/.claude/skills"
LINK_PATH="$SKILL_DIR/CCG"

echo "=== CCG Skill Installer ==="
echo ""

# 1. Create skills directory if needed
mkdir -p "$SKILL_DIR"

# 2. Create or update symlink
if [ -L "$LINK_PATH" ]; then
    current_target="$(readlink "$LINK_PATH")"
    if [ "$current_target" = "$SCRIPT_DIR" ]; then
        echo "Symlink already exists and points to correct location."
    else
        echo "Updating symlink: $LINK_PATH -> $SCRIPT_DIR"
        ln -sfn "$SCRIPT_DIR" "$LINK_PATH"
    fi
elif [ -e "$LINK_PATH" ]; then
    echo "WARNING: $LINK_PATH exists but is not a symlink. Backing up and replacing."
    mv "$LINK_PATH" "${LINK_PATH}.bak.$(date +%s)"
    ln -sfn "$SCRIPT_DIR" "$LINK_PATH"
else
    echo "Creating symlink: $LINK_PATH -> $SCRIPT_DIR"
    ln -sfn "$SCRIPT_DIR" "$LINK_PATH"
fi

# 3. Set executable permissions on scripts
chmod +x "$SCRIPT_DIR/scripts/setup_check.sh"
chmod +x "$SCRIPT_DIR/scripts/codex_bridge.py"
chmod +x "$SCRIPT_DIR/scripts/gemini_bridge.py"
chmod +x "$SCRIPT_DIR/scripts/configure.py"

echo ""

# 4. Run dependency check
bash "$SCRIPT_DIR/scripts/setup_check.sh"

echo ""
echo "=== Installation complete ==="
echo "Skill location: $LINK_PATH -> $SCRIPT_DIR"
echo ""
echo "Next steps:"
echo "  If not yet configured, run:"
echo "    python3 $SCRIPT_DIR/scripts/configure.py --setup \\"
echo "      --codex-url https://cc.orcai.cc/openai \\"
echo "      --codex-key YOUR_KEY \\"
echo "      --gemini-url https://cc.orcai.cc/gemini \\"
echo "      --gemini-key YOUR_KEY"
echo ""
echo "  Or let Claude Code handle setup automatically on first use."
