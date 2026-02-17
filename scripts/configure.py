#!/usr/bin/env python3
"""
CCG Configuration Manager.

Manages API endpoints, keys, and model settings for Codex and Gemini CLIs.
Config is stored at ~/.ccg/config.json.

Usage:
    python3 configure.py --check              # Check if configured
    python3 configure.py --show               # Show current config (keys masked)
    python3 configure.py --setup \\
        --codex-url https://cc.orcai.cc/openai \\
        --codex-key cr_xxx \\
        --codex-model gpt-5.3-codex \\
        --gemini-url https://cc.orcai.cc/gemini \\
        --gemini-key cr_xxx \\
        --gemini-model gemini-3-pro-preview
"""

import argparse
import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".ccg"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "codex": {
        "base_url": "https://cc.orcai.cc/openai",
        "api_key": "",
        "model": "gpt-5.3-codex",
    },
    "gemini": {
        "base_url": "https://cc.orcai.cc/gemini",
        "api_key": "",
        "model": "gemini-3-pro-preview",
    },
}


def load_config() -> dict | None:
    """Load config from ~/.ccg/config.json."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None


def save_config(config: dict):
    """Save config to ~/.ccg/config.json with restricted permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    os.chmod(CONFIG_FILE, 0o600)


def check_config():
    """Check if CCG is properly configured. Outputs JSON status."""
    config = load_config()
    if not config:
        result = {"configured": False, "reason": "No config file found at ~/.ccg/config.json"}
        print(json.dumps(result))
        return False

    missing = []
    for agent in ("codex", "gemini"):
        agent_cfg = config.get(agent, {})
        if not agent_cfg.get("api_key"):
            missing.append(f"{agent}.api_key")
        if not agent_cfg.get("base_url"):
            missing.append(f"{agent}.base_url")

    if missing:
        result = {"configured": False, "missing": missing, "config_path": str(CONFIG_FILE)}
        print(json.dumps(result))
        return False

    # Mask keys for output
    display = mask_keys(config)
    result = {"configured": True, "config": display, "config_path": str(CONFIG_FILE)}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return True


def mask_keys(config: dict) -> dict:
    """Return a copy of config with API keys partially masked."""
    display = json.loads(json.dumps(config))
    for agent in ("codex", "gemini"):
        if agent in display and "api_key" in display[agent]:
            key = display[agent]["api_key"]
            if len(key) > 10:
                display[agent]["api_key"] = key[:6] + "***" + key[-4:]
            elif key:
                display[agent]["api_key"] = "***"
    return display


def setup_config(args):
    """Create or update CCG configuration."""
    config = load_config() or {"codex": dict(DEFAULTS["codex"]), "gemini": dict(DEFAULTS["gemini"])}

    # Update Codex settings
    if args.codex_url is not None:
        config["codex"]["base_url"] = args.codex_url
    if args.codex_key is not None:
        config["codex"]["api_key"] = args.codex_key
    if args.codex_model is not None:
        config["codex"]["model"] = args.codex_model

    # Update Gemini settings
    if args.gemini_url is not None:
        config["gemini"]["base_url"] = args.gemini_url
    if args.gemini_key is not None:
        config["gemini"]["api_key"] = args.gemini_key
    if args.gemini_model is not None:
        config["gemini"]["model"] = args.gemini_model

    # Fill defaults for any missing fields
    for agent in ("codex", "gemini"):
        config.setdefault(agent, {})
        for key, val in DEFAULTS[agent].items():
            config[agent].setdefault(key, val)

    save_config(config)

    # Also configure Codex CLI's config.toml
    configure_codex_toml(config["codex"])

    display = mask_keys(config)
    print(json.dumps({"success": True, "config_path": str(CONFIG_FILE), "config": display}, indent=2))


def configure_codex_toml(codex_cfg: dict):
    """Write ~/.codex/config.toml to use CCG endpoint settings."""
    codex_dir = Path.home() / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    config_file = codex_dir / "config.toml"

    # Back up existing config if present
    if config_file.exists():
        backup = codex_dir / "config.toml.bak"
        if not backup.exists():
            config_file.rename(backup)
            print(f"Backed up existing codex config to {backup}", file=sys.stderr)

    base_url = codex_cfg.get("base_url", DEFAULTS["codex"]["base_url"])
    model = codex_cfg.get("model", DEFAULTS["codex"]["model"])

    toml_content = f'''model_provider = "ccg"
model = "{model}"
model_reasoning_effort = "high"
disable_response_storage = true
preferred_auth_method = "apikey"

[model_providers.ccg]
name = "ccg"
base_url = "{base_url}"
wire_api = "responses"
requires_openai_auth = true
env_key = "CCG_CODEX_KEY"
'''
    config_file.write_text(toml_content)


def show_config():
    """Display current configuration with masked keys."""
    config = load_config()
    if config:
        display = mask_keys(config)
        print(json.dumps(display, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"error": "No configuration found. Run with --setup to configure."}))


def main():
    parser = argparse.ArgumentParser(description="CCG Configuration Manager")
    parser.add_argument("--check", action="store_true", help="Check if configured (JSON output)")
    parser.add_argument("--show", action="store_true", help="Show current config (keys masked)")
    parser.add_argument("--setup", action="store_true", help="Setup or update configuration")
    parser.add_argument("--codex-url", default=None, help="Codex API endpoint URL")
    parser.add_argument("--codex-key", default=None, help="Codex API key")
    parser.add_argument("--codex-model", default=None, help="Codex model name")
    parser.add_argument("--gemini-url", default=None, help="Gemini API endpoint URL")
    parser.add_argument("--gemini-key", default=None, help="Gemini API key")
    parser.add_argument("--gemini-model", default=None, help="Gemini model name")

    args = parser.parse_args()

    if args.check:
        sys.exit(0 if check_config() else 1)
    elif args.show:
        show_config()
    elif args.setup:
        setup_config(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
