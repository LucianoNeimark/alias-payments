"""AgentPay MCP Server -- Streamable HTTP transport."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Ensure the mcp package directory is importable for sibling imports
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from tools.balance import register as register_balance  # noqa: E402
from tools.payments import register as register_payments  # noqa: E402
from tools.agents import register as register_agents  # noqa: E402

mcp = FastMCP(
    "AgentPay",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", os.getenv("MCP_PORT", "8001"))),
    stateless_http=True,
    json_response=True,
)

register_balance(mcp)
register_payments(mcp)
register_agents(mcp)


class _FixAcceptHeaderMiddleware:
    """Inject Accept: application/json when the client omits it.

    The MCP SDK rejects requests without a valid Accept header (406).
    Some clients (e.g. ChatGPT) don't send it, so we default to
    application/json to keep the server accessible.
    """

    _REQUIRED = {b"application/json", b"text/event-stream"}

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            accept = headers.get(b"accept", b"")
            if not any(ct in accept for ct in self._REQUIRED):
                scope = dict(scope)
                scope["headers"] = [
                    (k, v) for k, v in scope["headers"] if k != b"accept"
                ] + [(b"accept", b"application/json")]
        await self.app(scope, receive, send)


if __name__ == "__main__":
    import uvicorn

    app = mcp.streamable_http_app()
    app = _FixAcceptHeaderMiddleware(app)

    uvicorn.run(
        app,
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", os.getenv("MCP_PORT", "8001"))),
    )
