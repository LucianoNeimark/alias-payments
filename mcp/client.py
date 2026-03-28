"""Shared httpx client for calling the AgentPay FastAPI backend."""

import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
from mcp.server.fastmcp.exceptions import ToolError

AGENTPAY_API_URL = os.getenv("AGENTPAY_API_URL", "http://localhost:8000")
AGENTPAY_API_KEY = os.getenv("AGENTPAY_API_KEY", "")


@asynccontextmanager
async def get_client():
    headers = {}
    if AGENTPAY_API_KEY:
        headers["X-API-Key"] = AGENTPAY_API_KEY
    async with httpx.AsyncClient(
        base_url=AGENTPAY_API_URL,
        headers=headers,
        timeout=30.0,
    ) as client:
        yield client


def raise_for_status(response: httpx.Response) -> None:
    """Raise ToolError with the backend's error detail if the response is not 2xx."""
    if response.is_success:
        return
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    raise ToolError(f"{response.status_code}: {detail}")


def format_amount(value: Any) -> float:
    """Convert a numeric value to a float rounded to 2 decimal places."""
    return round(float(value), 2)
