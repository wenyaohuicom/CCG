# CCG - Claude-Codex-Gemini

A Claude Code Skill that lets Claude delegate tasks to **Codex CLI** (OpenAI) and **Gemini CLI** (Google) as independent coding agents.

## Features

- Unified interface to dispatch tasks to Codex or Gemini agents
- Automatic CLI detection and installation (Codex CLI, Gemini CLI)
- Interactive first-time setup: asks for API keys, endpoints, models
- Structured JSON output with session tracking for multi-turn conversations
- Streaming and batch output modes
- Sandbox isolation support for both agents
- Configuration stored at `~/.ccg/config.json` — no manual env var exports needed

## Installation

```bash
git clone https://github.com/wenyaohuicom/CCG.git
cd CCG
bash install.sh
```

The installer will:
1. Create a symlink at `~/.claude/skills/CCG` pointing to this directory
2. Set executable permissions on all scripts
3. Check and install missing CLIs (Codex CLI, Gemini CLI)
4. Check configuration status

## Configuration

On first use, Claude Code will automatically ask you for:
- **API Key** (used for both Codex and Gemini endpoints)
- **Codex endpoint** (default: `https://cc.orcai.cc/openai`)
- **Gemini endpoint** (default: `https://cc.orcai.cc/gemini`)
- **Models** (default: `gpt-5.3-codex` / `gemini-3-pro-preview`)

Or configure manually:

```bash
python3 scripts/configure.py --setup \
  --codex-url https://cc.orcai.cc/openai \
  --codex-key YOUR_API_KEY \
  --gemini-url https://cc.orcai.cc/gemini \
  --gemini-key YOUR_API_KEY
```

View current config:

```bash
python3 scripts/configure.py --show
```

## File Structure

```
CCG/
├── SKILL.md                  # Skill definition (read by Claude Code)
├── README.md                 # This file
├── install.sh                # Installer: symlink + dependency check
└── scripts/
    ├── setup_check.sh        # CLI detection and auto-install
    ├── configure.py          # Configuration manager (keys, endpoints, models)
    ├── codex_bridge.py       # Codex CLI bridge with JSON output parsing
    └── gemini_bridge.py      # Gemini CLI bridge with JSON output parsing
```

## Default Agent Configuration

| Agent | Default Model | Default Endpoint |
|-------|---------------|------------------|
| Claude Code | Claude Opus 4.6 | Anthropic |
| Codex CLI | gpt-5.3-codex | cc.orcai.cc/openai |
| Gemini CLI | gemini-3-pro-preview | cc.orcai.cc/gemini |

## Usage

Once installed and configured, Claude Code will automatically use the CCG skill. You can ask:

- "Use Codex to fix the bug in main.py"
- "Ask Gemini to refactor the database module"
- "Run Codex with full-auto to write tests for utils.py"

### Manual Usage

```bash
# Codex
python3 scripts/codex_bridge.py -p "Fix the bug" -C /path/to/project --full-auto

# Gemini
python3 scripts/gemini_bridge.py -p "Refactor this module" -C /path/to/project --yolo
```

## Requirements

- Linux
- Node.js 18+
- npm
- Python 3.8+

## License

MIT
