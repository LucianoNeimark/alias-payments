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

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
