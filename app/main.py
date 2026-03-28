import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import (
    agents,
    funding_orders,
    ledger,
    payment_requests,
    payouts,
    users,
    wallets,
    webhooks,
)
from app.config import get_settings, resolve_payments_service_config
from app.services.payments_client import PaymentsClient, set_payments_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pay_url, pay_key, pay_timeout, pay_verify_ssl = resolve_payments_service_config()
    client: PaymentsClient | None = None
    if pay_url and pay_key:
        logger.info(
            "MP payments client enabled (host=%s, verify_ssl=%s)",
            urlparse(pay_url).hostname or pay_url,
            pay_verify_ssl,
        )
        client = PaymentsClient(
            base_url=pay_url,
            api_key=pay_key,
            timeout=float(pay_timeout),
            verify_ssl=pay_verify_ssl,
        )
    set_payments_client(client)
    try:
        yield
    finally:
        if client is not None:
            await client.close()
        set_payments_client(None)


app = FastAPI(title="Alias Payments API", lifespan=lifespan)

_PUBLIC_PATHS = frozenset({
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/payouts/payments-health",
})


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    settings = get_settings()
    if settings.agentpay_api_key is None:
        return await call_next(request)

    path = request.url.path
    if path in _PUBLIC_PATHS or path.startswith("/webhooks"):
        return await call_next(request)

    if request.headers.get("X-API-Key") != settings.agentpay_api_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key"},
        )
    return await call_next(request)


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
app.include_router(
    funding_orders.router, prefix="/funding-orders", tags=["funding_orders"]
)
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(
    payment_requests.router, prefix="/payment-requests", tags=["payment_requests"]
)
app.include_router(payouts.router, prefix="/payouts", tags=["payouts"])
app.include_router(ledger.router, prefix="/ledger", tags=["ledger"])


@app.get("/")
def root():
    return {"message": "Hello World"}
