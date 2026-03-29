"""Payment tools -- request_payment, get_payment_request, list_payment_requests."""

from mcp.server.fastmcp import FastMCP

from client import format_amount, get_client, raise_for_status


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def request_payment(
        user_id: str,
        agent_id: str,
        amount: float,
        purpose: str,
        idempotency_key: str,
        currency: str = "ARS",
        destination_cvu: str | None = None,
        destination_alias: str | None = None,
        destination_holder_name: str | None = None,
    ) -> dict:
        """Crear una solicitud de pago a un CVU/CBU o alias destino.

        La solicitud queda en estado 'requested' hasta que el usuario la apruebe
        o rechace desde la web.

        Debe proporcionarse al menos uno de destination_cvu o destination_alias.

        Args:
            user_id: UUID del usuario que financia el pago.
            agent_id: UUID del agente que solicita el pago.
            amount: Monto a pagar (mayor a 0).
            purpose: Motivo legible del pago.
            idempotency_key: Clave unica para evitar duplicados.
            currency: Moneda (default ARS).
            destination_cvu: CVU o CBU destino (obligatorio si no se provee destination_alias).
            destination_alias: Alias destino, ej: proveedor.demo (obligatorio si no se provee destination_cvu).
            destination_holder_name: Nombre del titular destino.
        """
        if not destination_cvu and not destination_alias:
            raise ValueError(
                "Debe proporcionarse al menos uno de destination_cvu o destination_alias."
            )

        payload = {
            "user_id": user_id,
            "agent_id": agent_id,
            "amount": amount,
            "currency": currency,
            "purpose": purpose,
            "idempotency_key": idempotency_key,
        }
        if destination_cvu is not None:
            payload["destination_cvu"] = destination_cvu
        if destination_alias is not None:
            payload["destination_alias"] = destination_alias
        if destination_holder_name is not None:
            payload["destination_holder_name"] = destination_holder_name

        async with get_client() as client:
            response = await client.post("/payment-requests/", json=payload)
            raise_for_status(response)
            data = response.json()
            return {
                "id": data["id"],
                "status": data["status"],
                "amount": format_amount(data["amount"]),
                "currency": data["currency"],
                "destination_cvu": data["destination_cvu"],
                "destination_alias": data.get("destination_alias"),
                "destination_holder_name": data.get("destination_holder_name"),
                "purpose": data["purpose"],
                "created_at": data["created_at"],
            }

    @mcp.tool()
    async def get_payment_request(payment_request_id: str) -> dict:
        """Consultar el estado actual de una solicitud de pago.

        Util para hacer polling despues de crear una solicitud y verificar
        si el usuario ya aprobo, rechazo, o si el pago se completo.

        Args:
            payment_request_id: UUID de la solicitud de pago.
        """
        async with get_client() as client:
            response = await client.get(
                f"/payment-requests/{payment_request_id}"
            )
            raise_for_status(response)
            data = response.json()
            return {
                "id": data["id"],
                "status": data["status"],
                "amount": format_amount(data["amount"]),
                "currency": data["currency"],
                "destination_cvu": data["destination_cvu"],
                "purpose": data["purpose"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
            }

    @mcp.tool()
    async def list_payment_requests(
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Listar las solicitudes de pago del usuario.

        Permite revisar el historial o encontrar pagos pendientes.

        Args:
            user_id: UUID del usuario dueno.
            limit: Cantidad maxima de resultados (default 50, max 100).
            offset: Desplazamiento para paginacion (default 0).
        """
        async with get_client() as client:
            response = await client.get(
                "/payment-requests/",
                params={
                    "user_id": user_id,
                    "limit": limit,
                    "offset": offset,
                },
            )
            raise_for_status(response)
            items = response.json()
            return [
                {
                    "id": item["id"],
                    "status": item["status"],
                    "amount": format_amount(item["amount"]),
                    "destination_cvu": item["destination_cvu"],
                    "purpose": item["purpose"],
                    "created_at": item["created_at"],
                }
                for item in items
            ]
