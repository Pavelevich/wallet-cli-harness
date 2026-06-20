#!/usr/bin/env python3
"""Hardened runner for the official @ledgerhq/wallet-cli JSON contract.

This wrapper is intentionally conservative. It validates known flags before
launching wallet-cli, appends `--output json` when safe, and reports outcome
from the final JSON object on stdout rather than trusting the process exit code.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from typing import Any


GROUP_COMMANDS = {
    "account": {"discover"},
    "assets": {"token", "token-by-id"},
    "session": {"view", "reset"},
    "swap": {"quote", "status", "execute"},
}

ALLOWED_FLAGS = {
    "account discover": {"--network", "-n", "--output", "--device-timeout", "--help", "-h"},
    "assets token": {"--output", "--help", "-h"},
    "assets token-by-id": {"--output", "--help", "-h"},
    "balances": {"--account", "-a", "--output", "--help", "-h"},
    "genuine-check": {"--output", "--device-timeout", "--help", "-h"},
    "operations": {"--account", "-a", "--limit", "-l", "--cursor", "--output", "--help", "-h"},
    "receive": {"--account", "-a", "--verify", "-v", "--no-verify", "--output", "--device-timeout", "--help", "-h"},
    "send": {
        "--account",
        "-a",
        "--to",
        "-t",
        "--amount",
        "--fee-per-byte",
        "--rbf",
        "--mode",
        "--validator",
        "--stake-account",
        "--memo",
        "--data",
        "--dry-run",
        "--output",
        "--device-timeout",
        "--help",
        "-h",
    },
    "session reset": {"--output", "--help", "-h"},
    "session view": {"--output", "--help", "-h"},
    "swap execute": {
        "--from",
        "-f",
        "--to",
        "-t",
        "--provider",
        "--amount",
        "--account",
        "-a",
        "--to-account",
        "--fee-strategy",
        "--output",
        "--help",
        "-h",
    },
    "swap quote": {
        "--from",
        "-f",
        "--to",
        "-t",
        "--amount",
        "--from-account",
        "--from-fresh-address",
        "--to-account",
        "--to-fresh-address",
        "--output",
        "--help",
        "-h",
    },
    "swap status": {"--swap-id", "--provider", "--output", "--help", "-h"},
}


def emit_error(message: str, **extra: Any) -> int:
    payload = {"ok": False, "error": {"message": message, **extra}}
    print(json.dumps(payload, sort_keys=True))
    return 2


def split_command(args: list[str]) -> tuple[str, list[str]]:
    if not args:
        return "", []
    first = args[0]
    if first in GROUP_COMMANDS:
        if len(args) < 2 or args[1].startswith("-"):
            return first, args[1:]
        return f"{first} {args[1]}", args[2:]
    return first, args[1:]


def has_flag(args: list[str], flag: str) -> bool:
    return any(token == flag or token.startswith(f"{flag}=") for token in args)


def flag_name(token: str) -> str:
    return token.split("=", 1)[0]


def validate_flags(command: str, tail: list[str]) -> str | None:
    allowed = ALLOWED_FLAGS.get(command)
    if allowed is None:
        return f"Unsupported wallet-cli command for this harness: {command or '<empty>'}"
    for token in tail:
        if token.startswith("-") and flag_name(token) not in allowed:
            return f"Unknown or unsupported flag for `{command}`: {flag_name(token)}"
    return None


def is_device_command(command: str, tail: list[str]) -> bool:
    if command in {"account discover", "genuine-check", "swap execute"}:
        return True
    if command == "receive":
        return not has_flag(tail, "--no-verify")
    if command == "send":
        return not has_flag(tail, "--dry-run")
    return False


def final_json_from_stdout(stdout: str) -> tuple[list[Any], Any | None, list[str]]:
    events: list[Any] = []
    final: Any | None = None
    unparsable: list[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            unparsable.append(line)
            continue
        events.append(parsed)
        final = parsed
    return events, final, unparsable


def main() -> int:
    parser = argparse.ArgumentParser(description="Run wallet-cli with Codex safety rails.")
    parser.add_argument("--allow-device", action="store_true", help="Allow USB device-touching wallet-cli commands.")
    parser.add_argument("--allow-live-send", action="store_true", help="Allow send without --dry-run.")
    parser.add_argument("--allow-swap-execute", action="store_true", help="Allow swap execute.")
    parser.add_argument("--no-auto-output-json", action="store_true", help="Do not append --output json.")
    parser.add_argument("wallet_args", nargs=argparse.REMAINDER, help="wallet-cli arguments, optionally after --")
    opts = parser.parse_args()

    wallet_args = list(opts.wallet_args)
    if wallet_args and wallet_args[0] == "--":
        wallet_args = wallet_args[1:]
    if wallet_args and wallet_args[0] == "wallet-cli":
        wallet_args = wallet_args[1:]

    command, tail = split_command(wallet_args)
    error = validate_flags(command, tail)
    if error:
        return emit_error(error, command=command)

    if command == "send" and not has_flag(tail, "--dry-run") and not opts.allow_live_send:
        return emit_error("Refusing live `wallet-cli send` without --allow-live-send.", command=command)
    if command == "swap execute" and not opts.allow_swap_execute:
        return emit_error("Refusing `wallet-cli swap execute` without --allow-swap-execute.", command=command)
    if is_device_command(command, tail) and not opts.allow_device:
        return emit_error(
            "Refusing USB device-touching wallet-cli command on this BLE-only Flex host without --allow-device.",
            command=command,
        )

    if not opts.no_auto_output_json and "--help" not in tail and "-h" not in tail and not has_flag(tail, "--output"):
        wallet_args.extend(["--output", "json"])

    binary = shutil.which("wallet-cli")
    if not binary:
        return emit_error("wallet-cli not found on PATH.")

    proc = subprocess.run([binary, *wallet_args], capture_output=True, text=True)
    events, final, unparsable = final_json_from_stdout(proc.stdout)
    result = {
        "ok": bool(isinstance(final, dict) and final.get("status") == "success"),
        "walletCliExitCode": proc.returncode,
        "command": ["wallet-cli", *wallet_args],
        "events": events,
        "final": final,
        "unparsableStdout": unparsable,
        "stderr": proc.stderr.strip(),
    }
    if isinstance(final, dict) and final.get("ok") is False:
        result["ok"] = False
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
