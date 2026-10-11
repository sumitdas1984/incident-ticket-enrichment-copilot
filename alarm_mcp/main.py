# alarm_mcp/main.py — MCP server entry point.

from __future__ import annotations

import asyncio

from alarm_mcp.clients.alarm_api_client import close_alarm_api_client
from alarm_mcp.tools.alarm_tools import mcp


async def _run() -> None:
    try:
        await mcp.run_async()
    finally:
        await close_alarm_api_client()


if __name__ == "__main__":
    asyncio.run(_run())