#!/usr/bin/env python3
"""
Codex CLI Bridge for CCG Skill.

Wraps `codex exec` with structured JSON output parsing.
Auto-loads configuration from ~/.ccg/config.json.

Usage:
    python3 codex_bridge.py --prompt "Fix the bug in main.py" --workdir /path/to/project
    python3 codex_bridge.py --prompt "Add tests" --sandbox workspace-write --model o3
    python3 codex_bridge.py --prompt "Review code" --image screenshot.png
    python3 codex_bridge.py --session-id <ID> --prompt "Continue the task"
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

CONFIG_FILE = Path.home() / ".ccg" / "config.json"


def load_ccg_config() -> dict | None:
    """Load CCG config from ~/.ccg/config.json."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None


def build_command(args: argparse.Namespace) -> list[str]:
    """Build the codex exec command from parsed arguments."""
    cmd = ["codex", "exec"]

    if args.sandbox:
        cmd.extend(["--sandbox", args.sandbox])

    if args.workdir:
        cmd.extend(["--cd", args.workdir])

    if args.model:
        cmd.extend(["--model", args.model])

    if args.full_auto:
        cmd.append("--full-auto")

    if args.image:
        for img in args.image:
            cmd.extend(["--image", img])

    cmd.append("--json")

    if args.session_id:
        cmd.extend(["resume", "--last"])

    cmd.append("--")
    cmd.append(args.prompt)

    return cmd


def run(args: argparse.Namespace) -> int:
    """Execute codex and stream-parse JSON output."""
    # Load CCG config and prepare environment
    config = load_ccg_config()
    env = os.environ.copy()

    if config and "codex" in config:
        codex_cfg = config["codex"]
        # Set the API key env var that codex config.toml references (CCG_CODEX_KEY)
        if codex_cfg.get("api_key"):
            env["CCG_CODEX_KEY"] = codex_cfg["api_key"]
        # Use config model as default if not specified on command line
        if not args.model and codex_cfg.get("model"):
            args.model = codex_cfg["model"]

    cmd = build_command(args)

    if args.verbose:
        print(f"[codex_bridge] Running: {' '.join(cmd)}", file=sys.stderr)

    session_id = None
    messages = []

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                if args.verbose:
                    print(f"[codex_bridge] Non-JSON line: {line}", file=sys.stderr)
                continue

            etype = event.get("type", "")
            item = event.get("item", {})
            item_type = item.get("type", "")

            # Capture session/thread ID
            if "session_id" in event:
                session_id = event["session_id"]
            elif "thread_id" in event:
                session_id = event["thread_id"]
            elif etype == "session.start" and "id" in event:
                session_id = event["id"]

            # --- Reasoning / Thinking events ---
            if etype in ("reasoning", "thinking", "reasoning.delta"):
                if args.stream:
                    text = event.get("text", "") or event.get("content", "") or event.get("delta", "")
                    if text:
                        print(f"[thinking] {text}", flush=True)
            elif etype == "item.completed" and item_type in ("reasoning", "thinking"):
                if args.stream:
                    text = item.get("text", "") or item.get("content", "")
                    if text:
                        print(f"[thinking] {text}", flush=True)
            elif etype == "item.streaming" and item_type in ("reasoning", "thinking"):
                if args.stream:
                    text = item.get("text", "") or item.get("content", "")
                    if text:
                        print(f"[thinking] {text}", end="", flush=True)
            # --- Reasoning summary (o-series models) ---
            elif etype == "item.completed" and item_type == "reasoning_summary":
                if args.stream:
                    summaries = item.get("summary", item.get("text", ""))
                    if isinstance(summaries, list):
                        for s in summaries:
                            text = s.get("text", str(s)) if isinstance(s, dict) else str(s)
                            print(f"[reasoning] {text}", flush=True)
                    elif summaries:
                        print(f"[reasoning] {summaries}", flush=True)
            # --- Content delta (streaming text chunks) ---
            elif etype in ("content.delta", "response.output_text.delta"):
                if args.stream:
                    delta = event.get("delta", "") or event.get("text", "")
                    if delta:
                        print(delta, end="", flush=True)
            # --- Agent messages ---
            elif etype == "item.completed" and item_type == "agent_message":
                messages.append(item)
                content = item.get("text", "") or item.get("content", "")
                if content and args.stream:
                    print(content, flush=True)
            elif etype == "item.completed" and item_type == "command_execution":
                messages.append(item)
                if args.stream and item.get("aggregated_output"):
                    print(f"[cmd] {item.get('command', '')}", flush=True)
                    print(item["aggregated_output"], end="", flush=True)
            # Fallback for direct top-level events
            elif etype == "agent_message":
                messages.append(event)
                content = event.get("text", "") or event.get("content", "")
                if content and args.stream:
                    print(content, flush=True)
            elif etype == "message" and event.get("role") == "assistant":
                messages.append(event)
                content = event.get("text", "") or event.get("content", "")
                if content and args.stream:
                    print(content, flush=True)
            # --- Catch-all: dump unknown events in verbose mode ---
            elif args.verbose:
                print(f"[codex_bridge] event: {etype} item_type: {item_type}", file=sys.stderr)

        proc.wait()
        stderr_output = proc.stderr.read()

        result = {
            "exit_code": proc.returncode,
            "session_id": session_id,
            "message_count": len(messages),
            "messages": messages,
        }

        if stderr_output.strip():
            result["stderr"] = stderr_output.strip()

        if not args.stream:
            print(json.dumps(result, ensure_ascii=False, indent=2))

        return proc.returncode

    except FileNotFoundError:
        print(json.dumps({
            "error": "codex command not found. Run: bash scripts/setup_check.sh",
            "exit_code": 127,
        }), file=sys.stderr)
        return 127
    except KeyboardInterrupt:
        print("\n[codex_bridge] Interrupted.", file=sys.stderr)
        return 130


def main():
    parser = argparse.ArgumentParser(
        description="Codex CLI Bridge - Execute tasks via Codex agent",
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Task prompt to send to Codex",
    )
    parser.add_argument(
        "--workdir", "-C",
        default=None,
        help="Working directory for the Codex agent",
    )
    parser.add_argument(
        "--sandbox", "-s",
        choices=["read-only", "workspace-write", "danger-full-access"],
        default=None,
        help="Sandbox mode (default: codex default)",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Model to use (e.g., gpt-5.3-codex, o3)",
    )
    parser.add_argument(
        "--full-auto",
        action="store_true",
        help="Enable full-auto mode (workspace-write sandbox, auto-approve)",
    )
    parser.add_argument(
        "--image", "-i",
        action="append",
        help="Image file(s) to attach (can be repeated)",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Resume a previous session by ID",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream agent messages to stdout in real-time",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print debug info to stderr",
    )

    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
