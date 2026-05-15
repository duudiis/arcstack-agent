import os
import shlex
from pathlib import Path

from .allowlist import ALLOWED_COMMANDS, BLOCKED_PATTERNS, BLOCKED_PATH_PREFIXES
from ..config import settings


class SecurityError(Exception):
    pass


def validate_command(command: str) -> None:
    for pattern in BLOCKED_PATTERNS:
        if pattern in command:
            raise SecurityError(f"Blocked command pattern: {pattern.strip()}")

    try:
        parts = shlex.split(command)
    except ValueError:
        raise SecurityError("Invalid command syntax")

    if not parts:
        raise SecurityError("Empty command")

    base_cmd = os.path.basename(parts[0])
    if base_cmd not in ALLOWED_COMMANDS:
        raise SecurityError(
            f"Command '{base_cmd}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_COMMANDS))}"
        )

    # When using sudo, also validate the inner command
    if base_cmd == "sudo":
        inner = [p for p in parts[1:] if not p.startswith("-")]
        if inner:
            inner_cmd = os.path.basename(inner[0])
            if inner_cmd not in ALLOWED_COMMANDS:
                raise SecurityError(
                    f"Command '{inner_cmd}' (via sudo) is not allowed. Allowed: {', '.join(sorted(ALLOWED_COMMANDS))}"
                )


def validate_path(path: str) -> str:
    workspace = Path(settings.workspace_dir).resolve()
    resolved = Path(path).resolve()

    if not str(resolved).startswith(str(workspace)):
        resolved = (workspace / path).resolve()

    if not str(resolved).startswith(str(workspace)):
        raise SecurityError(f"Path escapes workspace: {path}")

    for prefix in BLOCKED_PATH_PREFIXES:
        if str(resolved).startswith(prefix):
            raise SecurityError(f"Access to {prefix} is not allowed")

    return str(resolved)


def truncate_output(output: str, max_size: int | None = None) -> str:
    limit = max_size or settings.max_output_size
    if len(output) > limit:
        return output[:limit] + f"\n\n[Output truncated at {limit} bytes]"
    return output
