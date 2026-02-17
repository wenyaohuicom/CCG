#!/usr/bin/env python3
"""
Gemini CLI Bridge for CCG Skill.

Wraps `gemini` CLI with structured JSON output parsing.
Auto-loads configuration from ~/.ccg/config.json.

Usage:
    python3 gemini_bridge.py --prompt "Refactor the utils module" --workdir /path/to/project
    python3 gemini_bridge.py --prompt "Add error handling" --sandbox --yolo
    python3 gemini_bridge.py --prompt "Continue" --resume latest
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
    """Build the gemini command from parsed arguments."""
    cmd = ["gemini"]

    if args.sandbox:
        cmd.append("--sandbox")

    if args.yolo:
        cmd.append("--yolo")

    if args.model:
        cmd.extend(["--model", args.model])

    if args.resume:
        cmd.extend(["--resume", args.resume])

    cmd.extend(["-o", "stream-json"])
    cmd.append(args.prompt)

    return cmd


def run(args: argparse.Namespace) -> int:
    """Execute gemini and stream-parse JSON output."""
    # Load CCG config and prepare environment
    config = load_ccg_config()
    env = os.environ.copy()

    if config and "gemini" in config:
        gemini_cfg = config["gemini"]
        if gemini_cfg.get("api_key"):
            env["GEMINI_API_KEY"] = gemini_cfg["api_key"]
        if gemini_cfg.get("base_url"):
            env["GOOGLE_GEMINI_BASE_URL"] = gemini_cfg["base_url"]
        # Use config model as default if not specified on command line
        if not args.model and gemini_cfg.get("model"):
            args.model = gemini_cfg["model"]

    cmd = build_command(args)

    if args.verbose:
        print(f"[gemini_bridge] Running: {' '.join(cmd)}", file=sys.stderr)

    session_id = None
    messages = []

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=args.workdir,
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
                    print(f"[gemini_bridge] Non-JSON line: {line}", file=sys.stderr)
                continue

            etype = event.get("type", "")

            # Capture session ID
            if "sessionId" in event:
                session_id = event["sessionId"]
            elif "session_id" in event:
                session_id = event["session_id"]

            # Capture agent messages
            if etype in ("modelTurn", "agent_message", "message"):
                messages.append(event)
                # Extract text content
                parts = event.get("parts", [])
                for part in parts:
                    text = part.get("text", "")
                    if text and args.stream:
                        print(text, end="", flush=True)
                # Alternative content field
                content = event.get("content", "")
                if content and args.stream:
                    print(content, flush=True)
            elif etype == "textDelta":
                text = event.get("text", "")
                if text and args.stream:
                    print(text, end="", flush=True)

        proc.wait()
        stderr_output = proc.stderr.read()

        if args.stream:
            print()  # Final newline

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
            "error": "gemini command not found. Run: bash scripts/setup_check.sh",
            "exit_code": 127,
        }), file=sys.stderr)
        return 127
    except KeyboardInterrupt:
        print("\n[gemini_bridge] Interrupted.", file=sys.stderr)
        return 130


def main():
    parser = argparse.ArgumentParser(
        description="Gemini CLI Bridge - Execute tasks via Gemini agent",
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Task prompt to send to Gemini",
    )
    parser.add_argument(
        "--workdir", "-C",
        default=None,
        help="Working directory for the Gemini agent (passed as cwd)",
    )
    parser.add_argument(
        "--sandbox", "-s",
        action="store_true",
        help="Enable sandbox mode",
    )
    parser.add_argument(
        "--yolo", "-y",
        action="store_true",
        help="Auto-approve all actions (YOLO mode)",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Model to use (e.g., gemini-3-pro-preview)",
    )
    parser.add_argument(
        "--resume", "-r",
        default=None,
        help="Resume a previous session ('latest' or session index)",
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
