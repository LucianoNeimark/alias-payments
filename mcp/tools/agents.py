"""get_agent_config tool -- consulta configuracion del agente."""

from mcp.server.fastmcp import FastMCP

from client import format_amount, get_client, raise_for_status


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_agent_config(agent_id: str) -> dict:
        """Obtener la configuracion del agente: nombre, limite de gasto, estado.

        Permite al agente conocer sus propios limites antes de solicitar un pago.

        Args:
            agent_id: UUID del agente.
        """
        async with get_client() as client:
            response = await client.get(f"/agents/{agent_id}")
            raise_for_status(response)
            data = response.json()
            result = {
                "id": data["id"],
                "name": data["name"],
                "description": data.get("description"),
                "default_spending_limit": None,
                "is_active": data["is_active"],
            }
            if data.get("default_spending_limit") is not None:
                result["default_spending_limit"] = format_amount(
                    data["default_spending_limit"]
                )
            return result
