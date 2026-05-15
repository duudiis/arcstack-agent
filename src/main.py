import asyncio
import json
import logging
import os
from urllib.parse import urlencode, urlparse

import websockets
import websockets.exceptions

from .config import settings
from .dispatcher import dispatch_tool
from .tools.system_info import SystemInfoTool

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("arcstack-agent")


def get_ws_url() -> str:
    parsed = urlparse(settings.ws_url)
    scheme = "wss" if parsed.scheme in ("https", "wss") else "ws"
    host = parsed.hostname or "localhost"
    port = parsed.port
    params = urlencode({"token": settings.agent_token})
    if port:
        return f"{scheme}://{host}:{port}/ws/agent?{params}"
    return f"{scheme}://{host}/ws/agent?{params}"


async def send_msg(ws, msg_type: str, data: dict | None = None):
    payload = {"type": msg_type, **(data or {})}
    await ws.send(json.dumps(payload))


async def heartbeat_loop(ws):
    while True:
        try:
            await send_msg(ws, "agent:heartbeat")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            break
        await asyncio.sleep(settings.heartbeat_interval)


async def metrics_loop(ws, arc_id: str):
    while True:
        try:
            metrics = SystemInfoTool.get_metrics()
            metrics["arcId"] = arc_id
            await send_msg(ws, "agent:metrics", metrics)
        except Exception as e:
            logger.error(f"Metrics error: {e}")
            break
        await asyncio.sleep(10)


async def handle_messages(ws):
    async for raw in ws:
        try:
            msg = json.loads(raw)
            msg_type = msg.get("type")

            if msg_type == "tool:execute":
                logger.info(f"Executing tool: {msg.get('tool')} (request={msg.get('requestId')})")
                result = await dispatch_tool(msg["tool"], msg.get("params", {}))
                result["arcId"] = msg["arcId"]
                result["requestId"] = msg["requestId"]
                await send_msg(ws, "tool:result", result)
            else:
                logger.debug(f"Unknown message type: {msg_type}")
        except json.JSONDecodeError:
            logger.warning("Received non-JSON message")
        except Exception as e:
            logger.error(f"Message handling error: {e}")


async def connect_and_run():
    ws_url = get_ws_url()
    logger.info(f"Connecting to {settings.ws_url}/ws/agent")

    async with websockets.connect(ws_url) as ws:
        logger.info("Connected to backend")

        arc_id = settings.agent_token[:8]

        heartbeat_task = asyncio.create_task(heartbeat_loop(ws))
        metrics_task = asyncio.create_task(metrics_loop(ws, arc_id))

        try:
            await handle_messages(ws)
        finally:
            heartbeat_task.cancel()
            metrics_task.cancel()


async def main():
    os.makedirs(settings.workspace_dir, exist_ok=True)
    logger.info(f"ArcStack Agent starting")
    logger.info(f"Workspace: {settings.workspace_dir}")

    reconnect_delay = 1
    max_delay = 30

    while True:
        try:
            await connect_and_run()
        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(f"Connection closed: {e}")
        except ConnectionRefusedError:
            logger.warning("Connection refused")
        except Exception as e:
            logger.error(f"Connection error: {e}")

        logger.info(f"Reconnecting in {reconnect_delay}s...")
        await asyncio.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 2, max_delay)


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent shutting down")


if __name__ == "__main__":
    run()
