import asyncio
import time

from .base import BaseTool, ToolResult
from ..security import validate_command, truncate_output, sanitize_output, SecurityError
from ..config import settings


class ShellTool(BaseTool):
    name = "shell"
    description = "Execute a shell command"

    async def execute(self, params: dict) -> ToolResult:
        command = params.get("command", "")
        if not command:
            return ToolResult(success=False, output="", error="No command provided")

        try:
            validate_command(command)
        except SecurityError as e:
            return ToolResult(success=False, output="", error=str(e))

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=settings.workspace_dir,
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=settings.command_timeout,
            )

            output = stdout.decode("utf-8", errors="replace")
            err_output = stderr.decode("utf-8", errors="replace")

            combined = output
            if err_output:
                combined += f"\n[stderr]\n{err_output}"

            combined = sanitize_output(truncate_output(combined))

            return ToolResult(
                success=proc.returncode == 0,
                output=combined,
                error=f"Exit code: {proc.returncode}" if proc.returncode != 0 else None,
            )
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                output="",
                error=f"Command timed out after {settings.command_timeout}s",
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
