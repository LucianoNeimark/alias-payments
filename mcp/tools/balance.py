"""get_balance tool -- consulta saldo de wallet."""

from mcp.server.fastmcp import FastMCP

from client import format_amount, get_client, raise_for_status


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_balance(user_id: str) -> dict:
        """Consultar el saldo disponible y reservado de la wallet del usuario.

        Args:
            user_id: UUID del usuario dueno de la wallet.
        """
        async with get_client() as client:
            response = await client.get(f"/wallets/{user_id}")
            raise_for_status(response)
            data = response.json()
            return {
                "wallet_id": data["id"],
                "currency": data["currency"],
                "available_balance": format_amount(data["available_balance"]),
                "reserved_balance": format_amount(data["reserved_balance"]),
            }
