"""HTTP client for the external Mercado Pago transfer (Selenium) service."""

from __future__ import annotations

import asyncio
import json
import logging
import ssl

import certifi
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PaymentTransferRequest(BaseModel):
    alias: str
    amount: int


class PaymentTransferResponse(BaseModel):
    status: str
    detail: str


class PaymentsServiceError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"PaymentsService {status_code}: {detail}")


# Process-level singleton; set from FastAPI lifespan via set_payments_client().
_payments_client: PaymentsClient | None = None


def get_payments_client() -> PaymentsClient | None:
    return _payments_client


def set_payments_client(client: PaymentsClient | None) -> None:
    global _payments_client
    _payments_client = client


class PaymentsClient:
    """HTTP client for the MP transfer microservice."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 60.0,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        ssl_context: ssl.SSLContext | bool = True
        if verify_ssl:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
        else:
            ssl_context = False
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-API-Key": api_key},
            timeout=httpx.Timeout(timeout, connect=5.0),
            verify=ssl_context,
        )

    async def transfer(self, alias: str, amount: int) -> PaymentTransferResponse:
        resp = await self._client.post(
            "/transfer",
            json={"alias": alias, "amount": amount},
        )
        if resp.status_code != 200:
            detail = _error_detail(resp)
            raise PaymentsServiceError(resp.status_code, detail)
        return PaymentTransferResponse(**resp.json())

    async def health(self) -> bool:
        try:
            resp = await self._client.get("/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        await self._client.aclose()


def _error_detail(resp: httpx.Response) -> str:
    try:
        body = resp.json()
        if isinstance(body, dict) and "detail" in body:
            d = body["detail"]
            if isinstance(d, str):
                return d
            return json.dumps(d)
    except (json.JSONDecodeError, ValueError):
        pass
    return resp.text or resp.reason_phrase


async def transfer_with_retry(
    client: PaymentsClient,
    alias: str,
    amount: int,
    *,
    max_409_retries: int = 3,
) -> PaymentTransferResponse:
    """
    Call transfer with retry policy from spec §6:
    - 409: exponential backoff (base 10s), max 3 retries after first attempt.
    - 500: at most one extra attempt (transfer may have already run).
    - Network timeout: at most one retry (remote lock may still be held).
    """
    attempt_409 = 0
    retried_500 = False
    retried_timeout = False

    while True:
        try:
            return await client.transfer(alias, amount)
        except PaymentsServiceError as e:
            if e.status_code == 409 and attempt_409 < max_409_retries:
                delay = 10 * (2**attempt_409)
                logger.warning(
                    "payments_client: 409 conflict, retry in %ss (attempt %s/%s)",
                    delay,
                    attempt_409 + 1,
                    max_409_retries,
                )
                await asyncio.sleep(delay)
                attempt_409 += 1
                continue
            if e.status_code == 500 and not retried_500:
                logger.warning("payments_client: 500 from service, single retry")
                retried_500 = True
                await asyncio.sleep(2.0)
                continue
            raise
        except httpx.TimeoutException:
            if not retried_timeout:
                logger.warning("payments_client: timeout, single retry")
                retried_timeout = True
                await asyncio.sleep(2.0)
                continue
            raise
