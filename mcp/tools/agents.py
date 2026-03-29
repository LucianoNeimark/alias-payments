"""Tools de agentes: alta de sesion y consulta de configuracion."""

from datetime import UTC, datetime

from mcp.server.fastmcp import FastMCP

from client import format_amount, get_client, raise_for_status


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_agent(
        user_id: str,
        name: str | None = None,
        description: str | None = None,
        default_spending_limit: float | None = None,
    ) -> dict:
        """Crear un nuevo agente para esta conversacion (chat nuevo / sesion nueva).

        Cada contexto nuevo (por ejemplo un chat recien abierto en OpenClaw) debe
        llamar esta tool una vez, guardar el `agent_id` devuelto y usarlo junto
        con el `user_id` del titular en get_agent_config y request_payment.
        No reutilices un agent_id de conversaciones anteriores.

        Args:
            user_id: UUID del usuario dueño de la cuenta AgentPay.
            name: Nombre visible del agente (opcional; por defecto un nombre de sesion).
            description: Nota opcional (origen del cliente, etc.).
            default_spending_limit: Tope opcional en pesos por solicitud; si se omite,
                el agente se crea sin limite fijado en este campo.
        """
        payload: dict = {
            "user_id": user_id,
            "name": name
            or f"Sesion {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC",
        }
        if description is not None:
            payload["description"] = description
        if default_spending_limit is not None:
            payload["default_spending_limit"] = default_spending_limit

        async with get_client() as client:
            response = await client.post("/agents/", json=payload)
            raise_for_status(response)
            data = response.json()

        result: dict = {
            "agent_id": data["id"],
            "id": data["id"],
            "user_id": data["user_id"],
            "name": data["name"],
            "description": data.get("description"),
            "is_active": data["is_active"],
            "default_spending_limit": None,
            "created_at": data["created_at"],
        }
        if data.get("default_spending_limit") is not None:
            result["default_spending_limit"] = format_amount(
                data["default_spending_limit"]
            )
        return result

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
