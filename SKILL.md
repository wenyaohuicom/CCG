---
name: CCG
description: Delegate tasks to Codex CLI and Gemini CLI as independent coding agents
---

# CCG - Claude-Codex-Gemini

This skill lets you delegate coding tasks to **Codex CLI** (OpenAI) and **Gemini CLI** (Google) as independent agents.

## First-Time Setup (IMPORTANT)

Before using any CCG commands, you MUST check if CCG is configured. Run this:

```bash
python3 /www/vscproject/skills/CCG/scripts/configure.py --check
```

If the output shows `"configured": false`, you need to run the setup flow:

### Step 1: Check CLI installations

```bash
bash /www/vscproject/skills/CCG/scripts/setup_check.sh
```

This will auto-install missing CLIs (Codex CLI, Gemini CLI) via npm.

### Step 2: Ask user for configuration

Ask the user the following questions using AskUserQuestion:

1. **API Key**: "Please provide your API key for Codex and Gemini endpoints."
2. **Codex Endpoint**: "Which Codex API endpoint to use?" (default: `https://cc.orcai.cc/openai`)
3. **Gemini Endpoint**: "Which Gemini API endpoint to use?" (default: `https://cc.orcai.cc/gemini`)
4. **Codex Model**: "Which Codex model?" (default: `gpt-5.3-codex`)
5. **Gemini Model**: "Which Gemini model?" (default: `gemini-3-pro-preview`)

If the user provides a single API key, use it for both Codex and Gemini.

### Step 3: Save configuration

Run configure.py with the collected values:

```bash
python3 /www/vscproject/skills/CCG/scripts/configure.py --setup \
  --codex-url "ENDPOINT" \
  --codex-key "KEY" \
  --codex-model "MODEL" \
  --gemini-url "ENDPOINT" \
  --gemini-key "KEY" \
  --gemini-model "MODEL"
```

Configuration is saved to `~/.ccg/config.json`. Codex CLI config is auto-written to `~/.codex/config.toml`.

## When to Use Each Agent

- **Codex**: Code generation, bug fixing, refactoring. Supports sandbox isolation and image attachments. Best with OpenAI models (gpt-5.3-codex, o3, o4-mini).
- **Gemini**: Code analysis, documentation, large-context tasks. Supports YOLO (auto-approve) mode. Best with Google models (gemini-3-pro-preview).

## Invoking Codex

```bash
python3 /www/vscproject/skills/CCG/scripts/codex_bridge.py \
  --prompt "YOUR_TASK_HERE" \
  --workdir /path/to/project \
  --full-auto
```

### Codex Parameters

| Parameter | Short | Description |
|-----------|-------|-------------|
| `--prompt` | `-p` | **Required.** Task prompt |
| `--workdir` | `-C` | Working directory |
| `--sandbox` | `-s` | `read-only`, `workspace-write`, `danger-full-access` |
| `--model` | `-m` | Override model (default from config) |
| `--full-auto` | | Auto-approve + workspace-write |
| `--image` | `-i` | Attach image file(s), repeatable |
| `--session-id` | | Resume a previous session |
| `--stream` | | Stream output in real-time |
| `--verbose` | `-v` | Debug info to stderr |

## Invoking Gemini

```bash
python3 /www/vscproject/skills/CCG/scripts/gemini_bridge.py \
  --prompt "YOUR_TASK_HERE" \
  --workdir /path/to/project \
  --yolo
```

### Gemini Parameters

| Parameter | Short | Description |
|-----------|-------|-------------|
| `--prompt` | `-p` | **Required.** Task prompt |
| `--workdir` | `-C` | Working directory (subprocess cwd) |
| `--sandbox` | `-s` | Enable sandbox mode |
| `--yolo` | `-y` | Auto-approve all actions |
| `--model` | `-m` | Override model (default from config) |
| `--resume` | `-r` | Resume session (`latest` or index) |
| `--stream` | | Stream output in real-time |
| `--verbose` | `-v` | Debug info to stderr |

## Output Format

Both bridges return JSON (without `--stream`):

```json
{
  "exit_code": 0,
  "session_id": "session_abc123",
  "message_count": 5,
  "messages": [ ... ],
  "stderr": ""
}
```

With `--stream`, agent text prints to stdout in real-time.

## View / Update Configuration

```bash
python3 /www/vscproject/skills/CCG/scripts/configure.py --show
python3 /www/vscproject/skills/CCG/scripts/configure.py --setup --codex-model gpt-5.3-codex
```

## Default Models

| Agent | Default Model |
|-------|---------------|
| Codex | gpt-5.3-codex |
| Gemini | gemini-3-pro-preview |

## Tips

1. Always specify `--workdir` to ensure the agent operates in the correct project.
2. Use `--stream` for real-time progress.
3. Use `--full-auto` (Codex) or `--yolo` (Gemini) for tasks that modify files.
4. Save `session_id` from output to resume multi-turn conversations.
5. The bridges auto-read `~/.ccg/config.json` — no need to export env vars manually.
