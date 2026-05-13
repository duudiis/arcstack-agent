import time
import logging

from .tools import TOOL_MAP

logger = logging.getLogger("arcstack-agent")


async def dispatch_tool(tool_name: str, params: dict) -> dict:
    tool = TOOL_MAP.get(tool_name)
    if not tool:
        return {
            "success": False,
            "output": "",
            "error": f"Unknown tool: {tool_name}. Available: {', '.join(TOOL_MAP.keys())}",
            "executionTimeMs": 0,
        }

    start = time.monotonic()
    try:
        result = await tool.execute(params)
        elapsed = int((time.monotonic() - start) * 1000)

        logger.info(f"Tool '{tool_name}' executed in {elapsed}ms (success={result.success})")

        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "executionTimeMs": elapsed,
        }
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        logger.error(f"Tool '{tool_name}' failed: {e}")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "executionTimeMs": elapsed,
        }
