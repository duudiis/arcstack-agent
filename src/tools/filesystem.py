import os
from pathlib import Path

from .base import BaseTool, ToolResult
from ..security import validate_path, truncate_output, sanitize_output, SecurityError


class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read file contents"

    async def execute(self, params: dict) -> ToolResult:
        try:
            path = validate_path(params.get("path", ""))
            content = Path(path).read_text(encoding="utf-8", errors="replace")
            return ToolResult(
                success=True,
                output=sanitize_output(truncate_output(content)),
            )
        except SecurityError as e:
            return ToolResult(success=False, output="", error=str(e))
        except FileNotFoundError:
            return ToolResult(success=False, output="", error=f"File not found: {params.get('path')}")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class FileWriteTool(BaseTool):
    name = "file_write"
    description = "Write content to a file"

    async def execute(self, params: dict) -> ToolResult:
        try:
            path = validate_path(params.get("path", ""))
            content = params.get("content", "")

            os.makedirs(os.path.dirname(path), exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")

            return ToolResult(success=True, output=f"Written {len(content)} bytes to {params.get('path')}")
        except SecurityError as e:
            return ToolResult(success=False, output="", error=str(e))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class FileListTool(BaseTool):
    name = "file_list"
    description = "List files in a directory"

    async def execute(self, params: dict) -> ToolResult:
        try:
            path = validate_path(params.get("path", "."))
            p = Path(path)

            if not p.is_dir():
                return ToolResult(success=False, output="", error="Not a directory")

            entries = []
            for entry in sorted(p.iterdir()):
                stat = entry.stat()
                kind = "d" if entry.is_dir() else "f"
                size = stat.st_size
                entries.append(f"{kind}  {size:>10}  {entry.name}")

            output = "\n".join(entries) if entries else "(empty directory)"
            return ToolResult(success=True, output=output)
        except SecurityError as e:
            return ToolResult(success=False, output="", error=str(e))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
