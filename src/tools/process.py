import os
import signal

import psutil

from .base import BaseTool, ToolResult


class ProcessListTool(BaseTool):
    name = "process_list"
    description = "List running processes"

    async def execute(self, params: dict) -> ToolResult:
        try:
            filter_str = params.get("filter", "").lower()
            lines = [f"{'PID':>7}  {'CPU%':>5}  {'MEM%':>5}  {'NAME'}"]

            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    info = proc.info
                    name = info.get("name", "")
                    if filter_str and filter_str not in name.lower():
                        continue
                    lines.append(
                        f"{info['pid']:>7}  {info.get('cpu_percent', 0):>5.1f}  "
                        f"{info.get('memory_percent', 0):>5.1f}  {name}"
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return ToolResult(success=True, output="\n".join(lines[:100]))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class ProcessKillTool(BaseTool):
    name = "process_kill"
    description = "Kill a process by PID"

    async def execute(self, params: dict) -> ToolResult:
        pid = params.get("pid")
        if not pid:
            return ToolResult(success=False, output="", error="No PID provided")

        try:
            proc = psutil.Process(int(pid))
            if proc.username() != os.getenv("USER", "arcagent"):
                return ToolResult(
                    success=False,
                    output="",
                    error="Cannot kill processes owned by other users",
                )

            proc.send_signal(signal.SIGTERM)
            return ToolResult(success=True, output=f"Sent SIGTERM to process {pid} ({proc.name()})")
        except psutil.NoSuchProcess:
            return ToolResult(success=False, output="", error=f"Process {pid} not found")
        except psutil.AccessDenied:
            return ToolResult(success=False, output="", error=f"Permission denied for process {pid}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
