import asyncio
import logging
import os

import socketio

from .config import settings
from .dispatcher import dispatch_tool
from .tools.system_info import SystemInfoTool

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("arcstack-agent")

sio = socketio.AsyncClient(
    reconnection=True,
    reconnection_attempts=0,
    reconnection_delay=1,
    reconnection_delay_max=30,
)

arc_id: str | None = None


@sio.event(namespace="/agent")
async def connect():
    logger.info("Connected to backend")
    await sio.emit(
        "agent:register",
        {
            "arcId": settings.agent_token[:8] + "...",
            "capabilities": list(
                ["shell", "file_read", "file_write", "file_list", "system_info", "process_list", "process_kill"]
            ),
        },
        namespace="/agent",
    )


@sio.event(namespace="/agent")
async def disconnect():
    logger.warning("Disconnected from backend")


@sio.on("tool:execute", namespace="/agent")
async def handle_tool_execute(data: dict):
    logger.info(f"Executing tool: {data.get('tool')} (request={data.get('requestId')})")
    result = await dispatch_tool(data["tool"], data.get("params", {}))
    result["arcId"] = data["arcId"]
    result["requestId"] = data["requestId"]
    await sio.emit("tool:result", result, namespace="/agent")


async def heartbeat_loop():
    while True:
        try:
            if sio.connected:
                await sio.emit("agent:heartbeat", namespace="/agent")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
        await asyncio.sleep(settings.heartbeat_interval)


async def metrics_loop():
    while True:
        try:
            if sio.connected:
                metrics = SystemInfoTool.get_metrics()
                metrics["arcId"] = arc_id or ""
                await sio.emit("agent:metrics", metrics, namespace="/agent")
        except Exception as e:
            logger.error(f"Metrics error: {e}")
        await asyncio.sleep(10)


async def main():
    os.makedirs(settings.workspace_dir, exist_ok=True)

    logger.info(f"ArcStack Agent starting, connecting to {settings.ws_url}")
    logger.info(f"Workspace: {settings.workspace_dir}")

    asyncio.create_task(heartbeat_loop())
    asyncio.create_task(metrics_loop())

    await sio.connect(
        settings.ws_url,
        namespaces=["/agent"],
        auth={"token": settings.agent_token},
    )

    await sio.wait()


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent shutting down")


if __name__ == "__main__":
    run()
