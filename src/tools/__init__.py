from .base import BaseTool, ToolResult
from .shell import ShellTool
from .filesystem import FileReadTool, FileWriteTool, FileListTool
from .system_info import SystemInfoTool
from .process import ProcessListTool, ProcessKillTool

TOOL_MAP: dict[str, BaseTool] = {
    "shell": ShellTool(),
    "file_read": FileReadTool(),
    "file_write": FileWriteTool(),
    "file_list": FileListTool(),
    "system_info": SystemInfoTool(),
    "process_list": ProcessListTool(),
    "process_kill": ProcessKillTool(),
}

__all__ = ["TOOL_MAP", "BaseTool", "ToolResult"]
