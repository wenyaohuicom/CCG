#!/usr/bin/env bash
set -euo pipefail

# CCG Dependency Check & Auto-Install Script
# Detects and installs: Node.js, npm, Python3, Codex CLI, Gemini CLI
# Also checks CCG configuration status.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

errors=0

echo "=== CCG Dependency Check ==="
echo ""

# --- Node.js ---
if command -v node &>/dev/null; then
    ok "Node.js $(node -v)"
else
    fail "Node.js not found. Please install Node.js 18+ first."
    errors=$((errors + 1))
fi

# --- npm ---
if command -v npm &>/dev/null; then
    ok "npm $(npm -v)"
else
    fail "npm not found. Please install npm."
    errors=$((errors + 1))
fi

# --- Python3 ---
if command -v python3 &>/dev/null; then
    ok "Python3 $(python3 --version 2>&1 | awk '{print $2}')"
else
    fail "Python3 not found. Please install Python 3.8+."
    errors=$((errors + 1))
fi

# Stop if basic dependencies are missing
if [ $errors -gt 0 ]; then
    fail "Missing $errors base dependency(ies). Fix them before continuing."
    exit 1
fi

# --- Codex CLI ---
if command -v codex &>/dev/null; then
    ok "Codex CLI found at $(command -v codex)"
else
    warn "Codex CLI not found. Installing via npm..."
    npm i -g @openai/codex@latest
    if command -v codex &>/dev/null; then
        ok "Codex CLI installed successfully."
    else
        fail "Failed to install Codex CLI."
        errors=$((errors + 1))
    fi
fi

# --- Gemini CLI ---
if command -v gemini &>/dev/null; then
    ok "Gemini CLI found at $(command -v gemini)"
else
    warn "Gemini CLI not found. Installing via npm..."
    npm i -g @google/gemini-cli@latest 2>/dev/null || true
    if command -v gemini &>/dev/null; then
        ok "Gemini CLI installed successfully."
    else
        fail "Could not auto-install Gemini CLI. Try: npm i -g @google/gemini-cli@latest"
        errors=$((errors + 1))
    fi
fi

echo ""

# --- CCG Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if python3 "$SCRIPT_DIR/configure.py" --check >/dev/null 2>&1; then
    ok "CCG configuration found at ~/.ccg/config.json"
else
    warn "CCG not configured yet. Run: python3 $SCRIPT_DIR/configure.py --setup ..."
fi

echo ""
if [ $errors -eq 0 ]; then
    ok "All CLI dependencies satisfied."
else
    fail "$errors dependency(ies) could not be resolved."
    exit 1
fi
